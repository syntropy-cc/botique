#!/usr/bin/env python3
"""
Script de produção para testar a geração de Coherence Briefs.

Carrega ideias de um arquivo phase1_ideas.json existente e gera
os coherence briefs correspondentes usando Phase 3.

Usa o workflow completo de produção com validação integrada.
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from src.core.config import OUTPUT_DIR
from src.phases.phase3_coherence import run as run_phase3

# Carregar variáveis de ambiente
load_dotenv()


def main():
    print("=" * 70)
    print("GERAÇÃO DE COHERENCE BRIEFS - PRODUÇÃO")
    print("=" * 70)
    
    # Caminhos
    article_slug = "why-tradicional-learning-fails"
    ideas_json_path = OUTPUT_DIR / article_slug / "phase1_ideas.json"
    
    if not ideas_json_path.exists():
        print(f"❌ ERRO: Arquivo de ideias não encontrado: {ideas_json_path}")
        print(f"   Execute primeiro o script generate_ideas_production.py para gerar as ideias.")
        return 1
    
    print(f"✓ Arquivo de ideias encontrado: {ideas_json_path}")
    
    # Ler payload de ideias
    print(f"\n1. Carregando ideias...")
    try:
        ideas_payload = json.loads(ideas_json_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ ERRO ao ler arquivo JSON: {e}")
        return 1
    
    article_summary = ideas_payload.get("article_summary", {})
    all_ideas = ideas_payload.get("ideas", [])
    
    print(f"   ✓ Payload carregado com sucesso")
    print(f"   ✓ Total de ideias disponíveis: {len(all_ideas)}")
    print(f"   ✓ Título do artigo: {article_summary.get('title', 'N/A')}")
    
    if not all_ideas:
        print(f"❌ ERRO: Nenhuma ideia encontrada no arquivo")
        return 1
    
    # Selecionar ideias para testar (primeiras 3 para teste rápido, ou todas)
    # Pode ser configurado via argumento ou variável de ambiente
    max_ideas_to_test = int(os.getenv("MAX_IDEAS_TO_TEST", "3"))
    
    if max_ideas_to_test > 0 and max_ideas_to_test < len(all_ideas):
        selected_ideas = all_ideas[:max_ideas_to_test]
        print(f"\n2. Selecionando ideias para teste...")
        print(f"   ✓ Selecionadas {len(selected_ideas)} ideias (de {len(all_ideas)} disponíveis)")
    else:
        selected_ideas = all_ideas
        print(f"\n2. Usando todas as ideias...")
        print(f"   ✓ {len(selected_ideas)} ideias serão processadas")
    
    # Mostrar preview das ideias selecionadas
    print(f"\n   Ideias selecionadas:")
    for idx, idea in enumerate(selected_ideas, 1):
        idea_id = idea.get("id", "N/A")
        platform = idea.get("platform", "N/A")
        format_type = idea.get("format", "N/A")
        tone = idea.get("tone", "N/A")
        hook = idea.get("hook", "N/A")[:60] + "..." if len(idea.get("hook", "")) > 60 else idea.get("hook", "N/A")
        print(f"     {idx}. {idea_id}: {platform}/{format_type} - {tone}")
        print(f"        Hook: {hook}")
    
    # Criar diretório de output
    output_dir = OUTPUT_DIR / article_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Gerar coherence briefs
    print(f"\n3. Gerando coherence briefs (Phase 3)...")
    print(f"   ⏳ Construindo briefs a partir das ideias selecionadas...")
    
    try:
        phase3_result = run_phase3(
            selected_ideas=selected_ideas,
            article_summary=article_summary,
            article_slug=article_slug,
            output_dir=OUTPUT_DIR,
        )
        
        print(f"   ✓ Briefs gerados com sucesso!")
        
    except Exception as e:
        print(f"   ❌ Erro ao gerar briefs: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Validar resultado
    briefs = phase3_result.get("briefs", [])
    briefs_dict = phase3_result.get("briefs_dict", [])
    briefs_count = phase3_result.get("briefs_count", 0)
    output_path = phase3_result.get("output_path", "")
    
    print(f"\n4. Resultados:")
    print(f"   ✓ Total de briefs gerados: {briefs_count}")
    print(f"   ✓ Arquivo consolidado: {output_path}")
    
    if briefs_count == 0:
        print(f"   ⚠️  AVISO: Nenhum brief foi gerado")
        return 1
    
    # Validar cada brief individualmente
    print(f"\n5. Validação dos briefs...")
    validation_errors = []
    
    for idx, brief in enumerate(briefs, 1):
        errors = brief.validate()
        if errors:
            validation_errors.append({
                "brief_index": idx,
                "post_id": brief.post_id,
                "errors": errors
            })
            print(f"   ❌ Brief {idx} ({brief.post_id}): {len(errors)} erro(s)")
            for error in errors:
                print(f"      - {error}")
        else:
            print(f"   ✓ Brief {idx} ({brief.post_id}): válido")
    
    if validation_errors:
        print(f"\n   ⚠️  AVISO: {len(validation_errors)} brief(s) com erros de validação")
    else:
        print(f"\n   ✓ Todos os briefs passaram na validação!")
    
    # Resumo detalhado dos briefs
    print(f"\n6. Resumo detalhado dos coherence briefs:")
    print("=" * 70)
    
    for idx, brief in enumerate(briefs, 1):
        print(f"\n📋 BRIEF {idx}: {brief.post_id}")
        print(f"   ID da Ideia: {brief.idea_id}")
        print(f"   Plataforma: {brief.platform} | Formato: {brief.format}")
        print(f"")
        print(f"   VOZ:")
        print(f"     - Tom: {brief.tone}")
        print(f"     - Traços de personalidade: {', '.join(brief.personality_traits[:3])}")
        print(f"     - Nível de vocabulário: {brief.vocabulary_level}")
        print(f"     - Formalidade: {brief.formality}")
        print(f"")
        print(f"   VISUAL:")
        print(f"     - Paleta ID: {brief.palette_id}")
        print(f"     - Tema da paleta: {brief.palette.get('theme', 'N/A')}")
        print(f"     - Cor primária: {brief.palette.get('primary', 'N/A')}")
        print(f"     - Cor de destaque: {brief.palette.get('accent', 'N/A')}")
        print(f"     - Tipografia ID: {brief.typography_id}")
        print(f"     - Fonte de título: {brief.typography.get('heading_font', 'N/A')}")
        print(f"     - Estilo visual: {brief.visual_style}")
        print(f"     - Humor visual: {brief.visual_mood}")
        print(f"     - Canvas: {brief.canvas.get('width', 'N/A')}x{brief.canvas.get('height', 'N/A')} ({brief.canvas.get('aspect_ratio', 'N/A')})")
        print(f"")
        print(f"   EMOÇÕES:")
        print(f"     - Emoção primária: {brief.primary_emotion}")
        print(f"     - Emoções secundárias: {', '.join(brief.secondary_emotions[:3])}")
        print(f"     - Emoções a evitar: {', '.join(brief.avoid_emotions[:3]) if brief.avoid_emotions else 'N/A'}")
        print(f"")
        print(f"   CONTEÚDO:")
        print(f"     - Mensagem principal: {brief.main_message[:80]}..." if len(brief.main_message) > 80 else f"     - Mensagem principal: {brief.main_message}")
        print(f"     - Proposta de valor: {brief.value_proposition[:80]}..." if len(brief.value_proposition) > 80 else f"     - Proposta de valor: {brief.value_proposition}")
        print(f"     - Hook: {brief.hook[:80]}..." if len(brief.hook) > 80 else f"     - Hook: {brief.hook}")
        print(f"     - Ângulo: {brief.angle[:80]}..." if len(brief.angle) > 80 else f"     - Ângulo: {brief.angle}")
        print(f"     - Palavras-chave: {', '.join(brief.keywords_to_emphasize[:5])}")
        print(f"")
        print(f"   AUDIÊNCIA:")
        print(f"     - Persona: {brief.persona}")
        print(f"     - Pontos de dor: {', '.join(brief.pain_points[:3]) if brief.pain_points else 'N/A'}")
        print(f"     - Desejos: {', '.join(brief.desires[:3]) if brief.desires else 'N/A'}")
        print(f"")
        print(f"   ESTRUTURA:")
        print(f"     - Objetivo: {brief.objective}")
        print(f"     - Arco narrativo: {brief.narrative_arc}")
        print(f"     - Slides estimados: {brief.estimated_slides}")
        print(f"")
        print(f"   CONTEXTO:")
        print(f"     - Insights usados: {len(brief.key_insights_used)} insight(s)")
        print(f"     - Conteúdo de insights: {len(brief.key_insights_content)} item(s)")
        print(f"")
        print(f"   MARCA:")
        print(f"     - Valores da marca: {', '.join(brief.brand_values) if brief.brand_values else 'N/A'}")
        print(f"     - Handle: {brief.brand_assets.get('handle', 'N/A')}")
        print(f"     - Tagline: {brief.brand_assets.get('tagline', 'N/A')}")
        print(f"")
        print(f"   EVOLUÇÃO (campos adicionados por fases posteriores):")
        print(f"     - Estrutura narrativa: {'✓' if brief.narrative_structure else '✗'} (Phase 3)")
        print(f"     - Guidelines de copy: {'✓' if brief.copy_guidelines else '✗'} (Phase 4)")
        print(f"     - Preferências visuais: {'✓' if brief.visual_preferences else '✗'} (Phase 4)")
        print(f"     - Constraints da plataforma: {'✓' if brief.platform_constraints else '✗'} (Phase 5)")
        print("-" * 70)
    
    # Verificar arquivos salvos
    print(f"\n7. Verificando arquivos salvos...")
    
    consolidated_path = Path(output_path)
    if consolidated_path.exists():
        file_size = consolidated_path.stat().st_size
        print(f"   ✓ Arquivo consolidado existe: {consolidated_path}")
        print(f"     Tamanho: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
    
    # Verificar briefs individuais
    for brief in briefs:
        post_dir = output_dir / brief.post_id
        brief_path = post_dir / "coherence_brief.json"
        if brief_path.exists():
            file_size = brief_path.stat().st_size
            print(f"   ✓ Brief individual: {brief_path.relative_to(OUTPUT_DIR)} ({file_size:,} bytes)")
        else:
            print(f"   ⚠️  Brief individual não encontrado: {brief_path}")
    
    # Estatísticas gerais
    print(f"\n8. Estatísticas gerais:")
    
    # Distribuição por plataforma
    platforms = {}
    for brief in briefs:
        platform = brief.platform
        platforms[platform] = platforms.get(platform, 0) + 1
    
    print(f"   Distribuição por plataforma:")
    for platform, count in platforms.items():
        print(f"     - {platform}: {count} brief(s)")
    
    # Distribuição por formato
    formats = {}
    for brief in briefs:
        format_type = brief.format
        formats[format_type] = formats.get(format_type, 0) + 1
    
    print(f"   Distribuição por formato:")
    for format_type, count in formats.items():
        print(f"     - {format_type}: {count} brief(s)")
    
    # Distribuição por tom
    tones = {}
    for brief in briefs:
        tone = brief.tone
        tones[tone] = tones.get(tone, 0) + 1
    
    print(f"   Distribuição por tom:")
    for tone, count in tones.items():
        print(f"     - {tone}: {count} brief(s)")
    
    # Paletas usadas
    palettes = {}
    for brief in briefs:
        palette_id = brief.palette_id
        palettes[palette_id] = palettes.get(palette_id, 0) + 1
    
    print(f"   Paletas usadas:")
    for palette_id, count in palettes.items():
        print(f"     - {palette_id}: {count} brief(s)")
    
    # Valores de marca detectados
    all_brand_values = set()
    for brief in briefs:
        all_brand_values.update(brief.brand_values)
    
    print(f"   Valores de marca detectados: {', '.join(sorted(all_brand_values))}")
    
    print("\n" + "=" * 70)
    print("✅ GERAÇÃO DE COHERENCE BRIEFS CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print(f"\n📄 Arquivo consolidado: {output_path}")
    print(f"📁 Diretório de output: {output_dir}")
    
    if validation_errors:
        print(f"\n⚠️  AVISOS:")
        print(f"   - {len(validation_errors)} brief(s) com erros de validação")
        print(f"   - Revise os erros acima antes de usar em produção")
    
    return 0


if __name__ == "__main__":
    exit(main())

