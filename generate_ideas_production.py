#!/usr/bin/env python3
"""
Script de produção para gerar ideias de posts a partir de um artigo.

Usa o workflow completo de produção com logging integrado.
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from src.core.config import IdeationConfig, OUTPUT_DIR
from src.core.llm_client import HttpLLMClient
from src.core.llm_logger import LLMLogger
from src.core.prompt_registry import get_latest_prompt
from src.ideas.generator import IdeaGenerator

# Carregar variáveis de ambiente
load_dotenv()

def main():
    print("=" * 70)
    print("GERAÇÃO DE IDEIAS - PRODUÇÃO")
    print("=" * 70)
    
    # Caminhos
    article_path = Path("articles/why-tradicional-learning-fails.md")
    
    if not article_path.exists():
        print(f"❌ ERRO: Artigo não encontrado: {article_path}")
        return 1
    
    print(f"✓ Artigo encontrado: {article_path}")
    
    # Verificar API key
    api_key = os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ ERRO: LLM_API_KEY ou DEEPSEEK_API_KEY não encontrada no .env")
        return 1
    
    print(f"✓ API Key encontrada: {api_key[:10]}...")
    
    # Ler artigo
    print(f"\n1. Lendo artigo...")
    article_text = article_path.read_text(encoding="utf-8")
    article_slug = article_path.stem
    print(f"   ✓ Artigo lido: {len(article_text)} caracteres")
    print(f"   ✓ Article slug: {article_slug}")
    
    # Criar logger with SQL backend
    print(f"\n2. Inicializando logger...")
    logger = LLMLogger(use_sql=True)
    logger.set_context(article_slug=article_slug)
    
    # Create trace for this execution
    trace_id = logger.create_trace(
        name="generate_ideas",
        metadata={"article_slug": article_slug, "article_path": str(article_path)},
    )
    print(f"   ✓ Logger criado: session_id={logger.get_session_id()[:8]}...")
    print(f"   ✓ Trace criado: trace_id={trace_id[:8]}...")
    print(f"   ✓ SQL logging: habilitado")
    
    # Criar diretório de output primeiro
    output_dir = OUTPUT_DIR / article_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    debug_dir = output_dir / "debug"
    
    # Criar cliente LLM com logger (timeout aumentado para respostas grandes)
    # Configurar para salvar respostas brutas automaticamente
    print(f"\n3. Criando cliente LLM...")
    llm_client = HttpLLMClient(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        model="deepseek-chat",
        timeout=180,  # 3 minutos para respostas grandes
        logger=logger,
        save_raw_responses=True,  # Habilitar salvamento automático
        raw_responses_dir=debug_dir,  # Diretório específico para este artigo
    )
    print(f"   ✓ Cliente LLM criado: model={llm_client.model}, timeout={llm_client.timeout}s")
    print(f"   ✓ Salvamento automático de respostas brutas: habilitado")
    
    # Verificar se o prompt está registrado no banco de dados
    print(f"\n4. Verificando prompt no banco de dados...")
    prompt_key = "post_ideator"
    prompt_data = get_latest_prompt(prompt_key)
    if not prompt_data:
        print(f"   ❌ ERRO: Prompt '{prompt_key}' não encontrado no banco de dados!")
        print(f"   📝 Por favor, registre o prompt primeiro usando:")
        print(f"      python -m src.cli.commands prompts register prompts/post_ideator.md")
        print(f"   ou use o script de registro de prompts.")
        return 1
    
    prompt_version = prompt_data.get("version", "N/A")
    print(f"   ✓ Prompt encontrado: {prompt_key} (versão {prompt_version})")
    
    # Criar gerador de ideias
    print(f"\n5. Criando gerador de ideias...")
    generator = IdeaGenerator(llm_client)
    print(f"   ✓ Gerador criado")
    
    # Configurar ideation
    print(f"\n6. Configurando parâmetros de ideação...")
    config = IdeationConfig(
        num_ideas_min=5,
        num_ideas_max=8,
        num_insights_min=3,
        num_insights_max=5,
    )
    print(f"   ✓ Configuração:")
    print(f"     - Ideias: {config.num_ideas_min}-{config.num_ideas_max}")
    print(f"     - Insights: {config.num_insights_min}-{config.num_insights_max}")
    
    # Gerar ideias (resposta bruta será salva automaticamente pelo HttpLLMClient)
    print(f"\n7. Gerando ideias (chamada real ao LLM)...")
    print(f"   ⏳ Isso pode levar alguns segundos...")
    print(f"   📝 A resposta bruta será salva automaticamente em: {debug_dir}")
    
    try:
        payload = generator.generate_ideas(
            article_text,
            config,
            context=article_slug,  # Contexto para organizar respostas salvas
        )
        print(f"   ✓ Ideias geradas com sucesso!")
        
        # Verificar se a resposta bruta foi salva
        raw_files = list(debug_dir.glob("raw_response_*.txt"))
        if raw_files:
            latest_raw = max(raw_files, key=lambda p: p.stat().st_mtime)
            print(f"   ✓ Resposta bruta salva automaticamente: {latest_raw.name}")
        
    except Exception as e:
        print(f"   ❌ Erro ao gerar ideias: {e}")
        import traceback
        traceback.print_exc()
        
        # Verificar se a resposta bruta foi salva mesmo com erro
        raw_files = list(debug_dir.glob("raw_response_*.txt"))
        if raw_files:
            latest_raw = max(raw_files, key=lambda p: p.stat().st_mtime)
            print(f"\n   ✓ Resposta bruta salva mesmo com erro: {latest_raw.name}")
        
        return 1
    
    # Validar resultado
    ideas = payload.get("ideas", [])
    article_summary = payload.get("article_summary", {})
    
    print(f"\n8. Resultados:")
    print(f"   ✓ Total de ideias geradas: {len(ideas)}")
    print(f"   ✓ Insights identificados: {len(article_summary.get('key_insights', []))}")
    print(f"   ✓ Título do artigo: {article_summary.get('title', 'N/A')}")
    
    # Salvar JSON
    output_path = output_dir / "phase1_ideas.json"
    print(f"\n9. Salvando resultados...")
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"   ✓ JSON salvo: {output_path}")
    
    # Resumo das ideias
    print(f"\n10. Resumo das ideias geradas:")
    for idx, idea in enumerate(ideas, 1):
        print(f"   {idx}. {idea.get('id', 'N/A')}: {idea.get('platform', 'N/A')} - {idea.get('tone', 'N/A')}")
        print(f"      Hook: {idea.get('hook', 'N/A')[:60]}...")
        print(f"      Slides estimados: {idea.get('estimated_slides', 'N/A')}")
        print(f"      Confiança: {idea.get('confidence', 0):.2f}")
    
    # Resumo de uso LLM
    if logger.calls:
        total_calls = len(logger.calls)
        total_tokens = sum(
            call["metrics"]["tokens_total"]
            for call in logger.calls
            if call["metrics"]["tokens_total"] is not None
        )
        total_cost = sum(
            call["metrics"]["cost_estimate"]
            for call in logger.calls
            if call["metrics"]["cost_estimate"] is not None
        )
        
        print(f"\n11. Uso LLM:")
        print(f"   ✓ Total de chamadas: {total_calls}")
        if total_tokens:
            print(f"   ✓ Total de tokens: {total_tokens:,}")
        if total_cost:
            print(f"   ✓ Custo estimado: ${total_cost:.6f}")
    
    # Verify SQL database
    print(f"\n12. Verificando banco de dados SQL...")
    try:
        from src.core.llm_log_queries import get_trace_with_events, get_cost_summary
        from src.core.llm_log_db import get_db_path
        
        db_path = get_db_path()
        trace_data = get_trace_with_events(trace_id, db_path)
        
        if trace_data:
            event_count = len(trace_data.get("events", []))
            print(f"   ✓ Trace encontrado no banco: {trace_id[:8]}...")
            print(f"   ✓ Eventos salvos: {event_count}")
            
            # Get cost summary for this trace
            cost_summary = get_cost_summary(
                filters={"trace_id": trace_id},
                db_path=db_path,
            )
            if cost_summary["summary"]["total_cost"]:
                print(f"   ✓ Custo total (do banco): ${cost_summary['summary']['total_cost']:.6f}")
        else:
            print(f"   ⚠️  Trace não encontrado no banco")
    except Exception as e:
        print(f"   ⚠️  Erro ao verificar banco: {e}")
    
    print("\n" + "=" * 70)
    print("✅ GERAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print(f"\n📄 Arquivo de ideias: {output_path}")
    print(f"📊 Trace ID: {trace_id}")
    
    return 0

if __name__ == "__main__":
    exit(main())

