#!/usr/bin/env python3
"""
Script para registrar automaticamente todos os prompts do diretório prompts/

Analisa cada arquivo .md no diretório, calcula métricas importantes e registra
na tabela prompts com metadata rico incluindo informações sobre tamanho,
complexidade e outras métricas que influenciam performance e custo.

Location: scripts/register_prompts_from_directory.py
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Try new locations first, fallback to old locations
try:
    from framework.llm.prompt_helpers import register_prompt, find_existing_prompt
    from framework.llm.logger import init_database, get_db_path
except ImportError:
    from core.prompt_registry import register_prompt, find_existing_prompt
    from core.llm_log_db import init_database, get_db_path


def extract_placeholders(template: str) -> Set[str]:
    """
    Extrai todos os placeholders do template (padrão {variavel}).
    
    Foca em placeholders simples que são variáveis do template,
    ignorando placeholders complexos dentro de exemplos JSON.
    
    Args:
        template: Template string
        
    Returns:
        Set de placeholders encontrados (apenas variáveis simples)
    """
    # Padrão para placeholders simples: {variavel} ou {variavel_min}
    # Ignora placeholders dentro de strings JSON complexas
    pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*(?:_(?:min|max|examples|list|word_limit|types|content|used))?)\}'
    matches = re.findall(pattern, template)
    
    # Filtrar placeholders que parecem ser variáveis de template
    # (não strings JSON ou estruturas complexas)
    valid_placeholders = set()
    for match in matches:
        # Ignorar se parece ser parte de um JSON de exemplo
        if not any(char in match for char in ['"', "'", '[', ']', '{', '}']):
            valid_placeholders.add(match)
    
    return valid_placeholders


def calculate_template_metrics(template: str) -> Dict[str, any]:
    """
    Calcula métricas importantes do template.
    
    Args:
        template: Template string
        
    Returns:
        Dicionário com métricas calculadas
    """
    # Métricas básicas
    char_count = len(template)
    char_count_no_spaces = len(template.replace(' ', ''))
    line_count = len(template.splitlines())
    word_count = len(template.split())
    
    # Placeholders
    placeholders = extract_placeholders(template)
    placeholder_count = len(placeholders)
    
    # Complexidade estimada
    # Baseado em: tamanho, número de placeholders, estrutura
    complexity_score = 0
    complexity_score += min(char_count / 1000, 10)  # Tamanho (max 10 pontos)
    complexity_score += min(placeholder_count * 2, 10)  # Placeholders (max 10 pontos)
    complexity_score += min(line_count / 50, 5)  # Estrutura (max 5 pontos)
    
    # Estimativa de tokens (aproximada: 1 token ≈ 4 caracteres)
    estimated_tokens = char_count / 4
    
    # Categorias de complexidade
    if complexity_score < 5:
        complexity_level = "low"
    elif complexity_score < 15:
        complexity_level = "medium"
    elif complexity_score < 25:
        complexity_level = "high"
    else:
        complexity_level = "very_high"
    
    return {
        "char_count": char_count,
        "char_count_no_spaces": char_count_no_spaces,
        "line_count": line_count,
        "word_count": word_count,
        "placeholder_count": placeholder_count,
        "placeholders": sorted(list(placeholders)),
        "complexity_score": round(complexity_score, 2),
        "complexity_level": complexity_level,
        "estimated_tokens": round(estimated_tokens, 0),
    }


def extract_document_metadata(template: str) -> Dict[str, str]:
    """
    Extrai metadados do documento se presente (tags como [ROLE], [CONTEXT], etc.).
    
    Args:
        template: Template string
        
    Returns:
        Dicionário com metadados extraídos
    """
    metadata = {}
    
    # Extrair filename se presente
    filename_match = re.search(r'<DOCUMENT filename="([^"]+)">', template)
    if filename_match:
        metadata["document_filename"] = filename_match.group(1)
    
    # Extrair seções principais
    sections = {}
    section_patterns = {
        "role": r'\[ROLE\]\s*(.*?)(?=\[|$)',
        "context": r'\[CONTEXT\]\s*(.*?)(?=\[|$)',
        "task": r'\[TASK\]\s*(.*?)(?=\[|$)',
        "constraints": r'\[CONSTRAINTS\]\s*(.*?)(?=\[|$)',
        "output": r'\[OUTPUT\]\s*(.*?)(?=\[|$)',
    }
    
    for section_name, pattern in section_patterns.items():
        match = re.search(pattern, template, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            sections[section_name] = {
                "present": True,
                "length": len(content),
            }
        else:
            sections[section_name] = {"present": False}
    
    if sections:
        metadata["sections"] = sections
    
    return metadata


def update_prompt_metadata(
    prompt_id: str,
    metadata: Dict[str, any],
    db_path: Path,
) -> None:
    """
    Atualiza metadados de um prompt existente.
    
    Args:
        prompt_id: ID do prompt a atualizar
        metadata: Novos metadados
        db_path: Caminho para o banco de dados
    """
    import json
    from core.llm_log_db import db_connection
    
    # Preservar template_hash se já existir
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT metadata_json FROM prompts WHERE id = ?", (prompt_id,))
        row = cursor.fetchone()
        
        if row and row["metadata_json"]:
            try:
                existing_metadata = json.loads(row["metadata_json"])
                # Preservar template_hash se existir
                if "template_hash" in existing_metadata:
                    metadata["template_hash"] = existing_metadata["template_hash"]
            except (json.JSONDecodeError, TypeError):
                pass  # Se metadata existente for inválido, usar apenas o novo
    
    metadata_json = json.dumps(metadata)
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE prompts 
            SET metadata_json = ?
            WHERE id = ?
        """, (metadata_json, prompt_id))
        conn.commit()


def register_prompt_from_file(
    file_path: Path,
    db_path: Path,
    verbose: bool = True,
    update_metadata: bool = False,
) -> Dict[str, any]:
    """
    Registra um prompt a partir de um arquivo.
    
    Args:
        file_path: Caminho para o arquivo .md
        db_path: Caminho para o banco de dados
        verbose: Se True, imprime informações detalhadas
        
    Returns:
        Dicionário com informações sobre o registro
    """
    # Ler arquivo
    template = file_path.read_text(encoding="utf-8")
    
    # Extrair prompt_key do nome do arquivo (sem extensão)
    prompt_key = file_path.stem
    
    # Calcular métricas
    metrics = calculate_template_metrics(template)
    
    # Extrair metadados do documento
    doc_metadata = extract_document_metadata(template)
    
    # Verificar se já existe
    existing = find_existing_prompt(prompt_key, template, db_path)
    
    if existing:
        prompt_id, version = existing
        
        # Se update_metadata está ativado, atualizar metadados
        if update_metadata:
            # Criar metadata completo
            doc_metadata = extract_document_metadata(template)
            metadata = {
                "source_file": str(file_path),
                "source_filename": file_path.name,
                "registered_by": "register_prompts_from_directory",
                "metadata_updated": True,
                **metrics,
                **doc_metadata,
            }
            update_prompt_metadata(prompt_id, metadata, db_path)
            if verbose:
                print(f"  🔄 {prompt_key}: {version} existente - metadados atualizados")
        else:
            if verbose:
                print(f"  ⚠️  {prompt_key}: Já existe {version} (não criou duplicata)")
        
        return {
            "prompt_key": prompt_key,
            "prompt_id": prompt_id,
            "version": version,
            "status": "existing" if not update_metadata else "updated",
            "metrics": metrics,
        }
    
    # Criar description baseada no arquivo
    description = f"Prompt from {file_path.name}"
    if doc_metadata.get("document_filename"):
        description += f" ({doc_metadata['document_filename']})"
    
    # Criar metadata completo
    metadata = {
        "source_file": str(file_path),
        "source_filename": file_path.name,
        "registered_by": "register_prompts_from_directory",
        **metrics,
        **doc_metadata,
    }
    
    # Registrar prompt
    prompt_id, version = register_prompt(
        prompt_key=prompt_key,
        template=template,
        description=description,
        metadata=metadata,
        db_path=db_path,
    )
    
    if verbose:
        print(f"  ✅ {prompt_key}: {version} registrado")
        print(f"     - Tamanho: {metrics['char_count']:,} chars, {metrics['word_count']:,} palavras, {metrics['line_count']} linhas")
        placeholder_preview = ', '.join(metrics['placeholders'][:8])
        if len(metrics['placeholders']) > 8:
            placeholder_preview += f" ... (+{len(metrics['placeholders']) - 8} mais)"
        print(f"     - Placeholders: {metrics['placeholder_count']} ({placeholder_preview})")
        print(f"     - Complexidade: {metrics['complexity_level']} (score: {metrics['complexity_score']})")
        print(f"     - Tokens estimados: ~{int(metrics['estimated_tokens']):,}")
    
    return {
        "prompt_key": prompt_key,
        "prompt_id": prompt_id,
        "version": version,
        "status": "created",
        "metrics": metrics,
    }


def register_all_prompts(
    prompts_dir: Path,
    db_path: Optional[Path] = None,
    verbose: bool = True,
    update_metadata: bool = False,
) -> Dict[str, any]:
    """
    Registra todos os prompts do diretório.
    
    Args:
        prompts_dir: Diretório contendo arquivos .md de prompts
        db_path: Caminho para o banco de dados (usa padrão se None)
        verbose: Se True, imprime informações detalhadas
        
    Returns:
        Dicionário com resumo do registro
    """
    if db_path is None:
        db_path = get_db_path()
    
    # Inicializar banco
    init_database(db_path)
    
    # Encontrar todos os arquivos .md
    prompt_files = sorted(prompts_dir.glob("*.md"))
    
    if not prompt_files:
        if verbose:
            print(f"⚠️  Nenhum arquivo .md encontrado em {prompts_dir}")
        return {
            "total_files": 0,
            "created": 0,
            "existing": 0,
            "results": [],
        }
    
    if verbose:
        print(f"📁 Diretório: {prompts_dir}")
        print(f"📄 Arquivos encontrados: {len(prompt_files)}")
        print()
    
    results = []
    created_count = 0
    existing_count = 0
    
    for file_path in prompt_files:
        result = register_prompt_from_file(file_path, db_path, verbose, update_metadata)
        results.append(result)
        
        if result["status"] == "created":
            created_count += 1
        elif result["status"] == "updated":
            existing_count += 1  # Conta como atualizado, não como novo
        else:
            existing_count += 1
        
        if verbose:
            print()
    
    # Resumo
    if verbose:
        print("=" * 70)
        print("📊 RESUMO")
        print("=" * 70)
        print(f"Total de arquivos: {len(prompt_files)}")
        print(f"  ✅ Novos registros: {created_count}")
        if update_metadata:
            updated_count = sum(1 for r in results if r["status"] == "updated")
            print(f"  🔄 Metadados atualizados: {updated_count}")
            print(f"  ⚠️  Sem alterações: {existing_count - updated_count}")
        else:
            print(f"  ⚠️  Já existentes: {existing_count}")
        print()
        
        # Métricas agregadas
        if results:
            total_chars = sum(r["metrics"]["char_count"] for r in results)
            total_placeholders = sum(r["metrics"]["placeholder_count"] for r in results)
            avg_complexity = sum(r["metrics"]["complexity_score"] for r in results) / len(results)
            
            print("📈 Métricas Agregadas:")
            print(f"  - Total de caracteres: {total_chars:,}")
            print(f"  - Total de placeholders: {total_placeholders}")
            print(f"  - Complexidade média: {avg_complexity:.2f}")
            print()
    
    return {
        "total_files": len(prompt_files),
        "created": created_count,
        "existing": existing_count,
        "results": results,
    }


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Registra automaticamente todos os prompts do diretório prompts/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--prompts-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "prompts",
        help="Diretório contendo arquivos .md de prompts (padrão: prompts/)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="Caminho para o banco de dados (padrão: llm_logs.db no root)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Modo silencioso (menos output)",
    )
    parser.add_argument(
        "--update-metadata",
        action="store_true",
        help="Atualiza metadados de prompts existentes (sem criar novas versões)",
    )
    
    args = parser.parse_args()
    
    if not args.prompts_dir.exists():
        print(f"❌ Erro: Diretório não encontrado: {args.prompts_dir}")
        sys.exit(1)
    
    print("=" * 70)
    print("REGISTRO AUTOMÁTICO DE PROMPTS")
    print("=" * 70)
    print()
    
    try:
        result = register_all_prompts(
            prompts_dir=args.prompts_dir,
            db_path=args.db_path,
            verbose=not args.quiet,
            update_metadata=args.update_metadata,
        )
        
        if result["total_files"] == 0:
            print("⚠️  Nenhum prompt foi processado")
            sys.exit(1)
        
        print("✅ Processamento concluído!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

