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
    
    # Criar logger
    print(f"\n2. Inicializando logger...")
    logger = LLMLogger(output_dir=OUTPUT_DIR)
    logger.set_context(article_slug=article_slug)
    print(f"   ✓ Logger criado: session_id={logger.get_session_id()[:8]}...")
    
    # Criar cliente LLM com logger (timeout aumentado para respostas grandes)
    print(f"\n3. Criando cliente LLM...")
    llm_client = HttpLLMClient(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        model="deepseek-chat",
        timeout=180,  # 3 minutos para respostas grandes
        logger=logger,
    )
    print(f"   ✓ Cliente LLM criado: model={llm_client.model}, timeout={llm_client.timeout}s")
    
    # Criar gerador de ideias
    print(f"\n4. Criando gerador de ideias...")
    generator = IdeaGenerator(llm_client)
    print(f"   ✓ Gerador criado")
    
    # Configurar ideation
    print(f"\n5. Configurando parâmetros de ideação...")
    config = IdeationConfig(
        num_ideas_min=5,
        num_ideas_max=8,
        num_insights_min=3,
        num_insights_max=5,
    )
    print(f"   ✓ Configuração:")
    print(f"     - Ideias: {config.num_ideas_min}-{config.num_ideas_max}")
    print(f"     - Insights: {config.num_insights_min}-{config.num_insights_max}")
    
    # Criar diretório de output primeiro
    output_dir = OUTPUT_DIR / article_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    debug_dir = output_dir / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    # Gerar ideias
    print(f"\n6. Gerando ideias (chamada real ao LLM)...")
    print(f"   ⏳ Isso pode levar alguns segundos...")
    
    try:
        # Construir prompt manualmente para debug se necessário
        from src.core.config import POST_IDEATOR_TEMPLATE
        from src.core.utils import build_prompt_from_template
        
        prompt_dict = config.to_prompt_dict()
        prompt_dict["article"] = article_text
        prompt = build_prompt_from_template(POST_IDEATOR_TEMPLATE, prompt_dict)
        
        # Fazer chamada direta para capturar resposta bruta
        print(f"   📝 Tamanho do prompt: {len(prompt)} caracteres")
        
        raw_response = llm_client.generate(
            prompt=prompt,
            max_tokens=8192,  # Aumentar para garantir resposta completa
            temperature=0.2,
        )
        
        # Salvar resposta bruta para debug
        raw_response_path = debug_dir / "raw_llm_response.txt"
        raw_response_path.write_text(raw_response, encoding="utf-8")
        print(f"   ✓ Resposta bruta salva: {raw_response_path}")
        print(f"   📏 Tamanho da resposta: {len(raw_response)} caracteres")
        
        # Tentar parsear e validar
        from src.core.utils import validate_llm_json_response
        
        payload = validate_llm_json_response(
            raw_response=raw_response,
            top_level_keys=["article_summary", "ideas"],
            nested_validations={
                "article_summary": [
                    "title",
                    "main_thesis",
                    "detected_tone",
                    "key_insights",
                    "themes",
                    "keywords",
                    "main_message",
                    "avoid_topics",
                ]
            },
            list_validations={
                "ideas": [
                    "id",
                    "platform",
                    "format",
                    "tone",
                    "persona",
                    "personality_traits",
                    "objective",
                    "angle",
                    "hook",
                    "narrative_arc",
                    "vocabulary_level",
                    "formality",
                    "key_insights_used",
                    "target_emotions",
                    "primary_emotion",
                    "secondary_emotions",
                    "avoid_emotions",
                    "value_proposition",
                    "article_context_for_idea",
                    "idea_explanation",
                    "estimated_slides",
                    "confidence",
                    "rationale",
                    "risks",
                    "keywords_to_emphasize",
                    "pain_points",
                    "desires",
                ],
                "article_summary.key_insights": [
                    "id",
                    "content",
                    "type",
                    "strength",
                    "source_quote",
                ],
            },
        )
        
        print(f"   ✓ JSON validado com sucesso!")
        
    except Exception as e:
        print(f"   ❌ Erro ao gerar ideias: {e}")
        import traceback
        traceback.print_exc()
        
        # Se houver erro, tentar salvar o que foi gerado mesmo assim
        if 'raw_response' in locals():
            print(f"\n   ⚠️  Tentando salvar resposta parcial...")
            try:
                # Tentar extrair JSON mesmo com erros
                import re
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if json_match:
                    partial_json = json_match.group(0)
                    partial_path = debug_dir / "partial_response.json"
                    partial_path.write_text(partial_json, encoding="utf-8")
                    print(f"   ✓ Resposta parcial salva: {partial_path}")
            except:
                pass
        
        return 1
    
    # Validar resultado
    ideas = payload.get("ideas", [])
    article_summary = payload.get("article_summary", {})
    
    print(f"\n7. Resultados:")
    print(f"   ✓ Total de ideias geradas: {len(ideas)}")
    print(f"   ✓ Insights identificados: {len(article_summary.get('key_insights', []))}")
    print(f"   ✓ Título do artigo: {article_summary.get('title', 'N/A')}")
    
    # Salvar JSON
    output_path = output_dir / "phase1_ideas.json"
    print(f"\n8. Salvando resultados...")
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"   ✓ JSON salvo: {output_path}")
    
    # Salvar logs
    print(f"\n9. Salvando logs...")
    log_paths = logger.save_logs(article_slug=article_slug)
    
    if log_paths.get('local'):
        print(f"   ✓ Log local: {log_paths['local']}")
    if log_paths.get('central'):
        print(f"   ✓ Log centralizado: {log_paths['central']}")
    
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
    
    print("\n" + "=" * 70)
    print("✅ GERAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print(f"\n📄 Arquivo de ideias: {output_path}")
    if log_paths.get('local'):
        print(f"📊 Logs disponíveis em: {log_paths['local']}")
    
    return 0

if __name__ == "__main__":
    exit(main())

