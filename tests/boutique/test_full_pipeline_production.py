#!/usr/bin/env python3
"""
Teste de produção completo para o código refatorado.

Testa o pipeline completo: Ideation -> Narrative -> Copywriting
usando o BoutiqueOrchestrator e verifica:
- Se todas as funcionalidades estão funcionando
- Se as instruções, state managers e tools estão funcionando
- Se o estado está evoluindo corretamente em cada fase
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Adiciona o diretório raiz do projeto ao PYTHONPATH
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from boutique.orchestrator.boutique_orchestrator import BoutiqueOrchestrator
from boutique.state_management.boutique_state import BoutiqueState
from boutique.state_management.models.coherence_brief import CoherenceBrief
from boutique.state_management.strategies.brief_strategy import (
    BriefEpisodicStrategy,
    BriefHierarchicalStrategy,
)
from framework.core.state_management import EpisodicStrategy
from framework.llm.http_client import HttpLLMClient
from framework.llm.logger import LLMLogger


def print_section(title: str, width: int = 70) -> None:
    """Imprime seção formatada."""
    print("\n" + "=" * width)
    print(title)
    print("=" * width)


def print_step(step_num: int, description: str) -> None:
    """Imprime passo formatado."""
    print(f"\n{step_num}. {description}")


def validate_state_evolution(
    state: BoutiqueState,
    phase_name: str,
    expected_briefs: int = 0,
    article_slug: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Valida evolução do estado após uma fase.
    
    Args:
        state: BoutiqueState
        phase_name: Nome da fase
        expected_briefs: Número esperado de briefs
        article_slug: Slug do artigo para filtrar
        
    Returns:
        Dict com resultados da validação
    """
    validation = {
        "phase": phase_name,
        "briefs_count": 0,
        "briefs": {},
        "state_metadata": {
            "article_slug": state.article_slug,
            "cache_size": len(state._cache),
        },
    }
    
    # Conta briefs
    if article_slug:
        briefs = state.get_all_briefs(article_slug=article_slug)
    else:
        briefs = state.get_all_briefs()
    
    validation["briefs_count"] = len(briefs)
    validation["briefs"] = {post_id: brief for post_id, brief in briefs.items()}
    
    # Valida evolução de cada brief
    for post_id, brief in briefs.items():
        if isinstance(brief, CoherenceBrief):
            brief_evolution = {
                "post_id": brief.post_id,
                "has_narrative": brief.narrative_structure is not None,
                "has_copy_guidelines": brief.copy_guidelines is not None,
                "has_cta_guidelines": brief.cta_guidelines is not None,
                "estimated_slides": getattr(brief, "estimated_slides", 0),
            }
            validation["brief_evolution"] = brief_evolution
    
    return validation


def test_full_pipeline() -> int:
    """
    Testa pipeline completo de produção.
    
    Returns:
        Exit code (0 para sucesso, 1 para falha)
    """
    print_section("TESTE DE PRODUÇÃO - PIPELINE COMPLETO (CÓDIGO REFATORADO)")
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Configuração
    article_path = Path(
        os.getenv("ARTICLE_PATH", "articles/why-tradicional-learning-fails.md")
    )
    article_slug = article_path.stem if article_path.suffix else "why-tradicional-learning-fails"
    max_ideas_to_test = int(os.getenv("MAX_IDEAS_TO_TEST", "2"))
    
    # Verifica arquivo do artigo
    print_step(1, "Carregando artigo...")
    if not article_path.exists():
        print(f"❌ ERRO: Arquivo do artigo não encontrado: {article_path}")
        return 1
    
    try:
        article_text = article_path.read_text(encoding="utf-8")
        print(f"   ✓ Artigo carregado: {len(article_text)} caracteres")
    except Exception as exc:
        print(f"❌ ERRO ao ler artigo: {exc}")
        return 1
    
    # Verifica API key
    print_step(2, "Inicializando cliente LLM...")
    api_key = os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ ERRO: LLM_API_KEY ou DEEPSEEK_API_KEY não encontrado no ambiente")
        return 1
    
    # Inicializa logger
    logger = LLMLogger(use_sql=True)
    
    # Cria trace para esta execução
    trace_id = logger.create_trace(
        name="full_pipeline_test_refactored",
        metadata={
            "article_slug": article_slug,
            "article_path": str(article_path),
            "script": "test_full_pipeline_production",
        },
    )
    logger.set_context(article_slug=article_slug)
    
    print(f"   ✓ Trace criado: {trace_id[:8]}...")
    print(f"   ✓ SQL logging: habilitado")
    
    # Inicializa cliente LLM
    llm_client = HttpLLMClient(
        api_key=api_key,
        base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"),
        model=os.getenv("LLM_MODEL", "deepseek-chat"),
        timeout=int(os.getenv("LLM_TIMEOUT", "180")),
        logger=logger,
        save_raw_responses=True,
        raw_responses_dir=Path("output") / article_slug / "debug",
    )
    
    print(f"   ✓ Cliente LLM criado: model={llm_client.model}, timeout={llm_client.timeout}s")
    
    # Prepara diretório de saída
    output_dir = Path("output") / article_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    debug_dir = output_dir / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    # =====================================================================
    # INICIALIZA ORQUESTRADOR E ESTADO
    # =====================================================================
    print_section("INICIALIZAÇÃO")
    
    print_step(3, "Criando BoutiqueOrchestrator...")
    orchestrator = BoutiqueOrchestrator()
    
    # Verifica agentes registrados
    registry = orchestrator.get_registry()
    print(f"   ✓ Agentes registrados: {len(registry)}")
    for agent_name in registry.keys():
        print(f"      - {agent_name}")
    
    print_step(4, "Criando BoutiqueState...")
    state = BoutiqueState()
    state.article_slug = article_slug
    state.current_trace_id = trace_id
    print(f"   ✓ Estado criado: article_slug={state.article_slug}")
    
    # Validação inicial do estado
    initial_validation = validate_state_evolution(state, "initial", 0, article_slug)
    print(f"   ✓ Estado inicial: {initial_validation['briefs_count']} briefs")
    
    # =====================================================================
    # FASE 1: IDEATION
    # =====================================================================
    print_section("FASE 1: IDEATION (PostIdeatorAgent)")
    
    print_step(5, "Executando ideation...")
    print(f"   ⏳ Isso pode levar um tempo...")
    
    # Configuração de ideation
    ideation_config = {
        "num_ideas_min": 3,
        "num_ideas_max": 5,
        "num_insights_min": 3,
        "num_insights_max": 5,
    }
    
    try:
        # Usa dispatch diretamente para o agente post_ideator
        ideation_result = orchestrator.dispatch(
            agent=orchestrator.registry["post_ideator"],
            task={
                "article": article_text,
                "article_slug": article_slug,
                "config": ideation_config,
                "article_path": str(article_path),
                "llm_client": llm_client,
            },
            state=state,
        )
        
        print("   ✓ Ideation executado com sucesso!")
        
        # Salva resultado
        ideas_json_path = output_dir / "phase1_ideas.json"
        ideas_json_path.write_text(
            json.dumps(ideation_result, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        print(f"   ✓ Resultados salvos: {ideas_json_path}")
        
    except Exception as exc:
        error_msg = str(exc)
        print(f"   ❌ ERRO na ideation: {error_msg}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Extrai resultados
    article_summary = ideation_result.get("article_summary", {})
    all_ideas = ideation_result.get("ideas", [])
    
    print(f"   ✓ Total de ideias geradas: {len(all_ideas)}")
    print(f"   ✓ Título do artigo: {article_summary.get('title', 'N/A')}")
    
    # Seleciona ideias para processar
    if 0 < max_ideas_to_test < len(all_ideas):
        selected_ideas = all_ideas[:max_ideas_to_test]
        print(f"\n   Selecionadas {len(selected_ideas)} ideias para teste completo")
    else:
        selected_ideas = all_ideas
        print(f"\n   Usando todas as {len(selected_ideas)} ideias para teste completo")
    
    # Validação do estado após ideation
    ideation_validation = validate_state_evolution(state, "ideation", 0, article_slug)
    print(f"   ✓ Estado após ideation: {ideation_validation['briefs_count']} briefs")
    
    # =====================================================================
    # FASE 2: CRIAÇÃO DE BRIEFS
    # =====================================================================
    print_section("FASE 2: CRIAÇÃO DE BRIEFS")
    
    print_step(6, "Criando coherence briefs a partir das ideias...")
    
    briefs = []
    
    # Importa dependências necessárias
    from boutique.state_management.models.brand.library import BrandLibrary
    from boutique.state_management.models.brand.audience import (
        get_audience_profile,
        enrich_idea_with_audience,
    )
    
    for idx, idea in enumerate(selected_ideas, 1):
        idea_id = idea.get("id", f"unknown_{idx}")
        post_id = f"post_{article_slug}_{idx:03d}"
        
        print(f"   [{idx}/{len(selected_ideas)}] Criando brief para {idea_id}...", end=" ")
        
        try:
            # Resolve parâmetros
            platform = idea.get("platform", "linkedin")
            tone = idea.get("tone", "professional")
            persona = idea.get("persona", "professional")
            format_type = idea.get("format", "carousel")
            
            # Seleciona brand elements
            palette = BrandLibrary.select_palette(platform, tone, persona)
            typography = BrandLibrary.select_typography(platform, persona)
            canvas = BrandLibrary.get_canvas_config(platform, format_type)
            
            # Enrich com audience
            audience_profile = get_audience_profile(persona)
            if audience_profile:
                idea = enrich_idea_with_audience(idea, audience_profile)
            
            # Cria brief
            brief = CoherenceBrief(
                post_id=post_id,
                idea_id=idea_id,
                platform=platform,
                format=format_type,
                tone=tone,
                personality_traits=idea.get("personality_traits", []),
                vocabulary_level=idea.get("vocabulary_level", "moderate"),
                formality=idea.get("formality", "neutral"),
                palette_id=palette.id if hasattr(palette, "id") else "",
                palette=palette.__dict__ if hasattr(palette, "__dict__") else {},
                typography_id=typography.id if hasattr(typography, "id") else "",
                typography=typography.__dict__ if hasattr(typography, "__dict__") else {},
                visual_style="",
                visual_mood="",
                canvas=canvas.__dict__ if hasattr(canvas, "__dict__") else {},
                primary_emotion=idea.get("primary_emotion", ""),
                secondary_emotions=idea.get("secondary_emotions", []),
                avoid_emotions=idea.get("avoid_emotions", []),
                target_emotions=idea.get("target_emotions", []),
                keywords_to_emphasize=idea.get("keywords", []),
                themes=article_summary.get("themes", []),
                main_message=idea.get("main_message", ""),
                value_proposition=idea.get("value_proposition", ""),
                angle=idea.get("angle", ""),
                hook=idea.get("hook", ""),
                persona=persona,
                pain_points=idea.get("pain_points", []),
                desires=idea.get("desires", []),
                avoid_topics=[],
                required_elements=[],
                objective=idea.get("objective", ""),
                narrative_arc=idea.get("narrative_arc", ""),
                estimated_slides=idea.get("estimated_slides", 7),
                article_context=article_summary.get("main_thesis", ""),
                key_insights_used=idea.get("key_insights_used", []),
                key_insights_content=article_summary.get("key_insights", []),
            )
            
            # Armazena brief no estado
            stored_post_id = state.store_brief(brief)
            briefs.append(brief)
            print("✓")
            
        except Exception as exc:
            error_msg = str(exc)
            print(f"❌ ({error_msg[:60]}...)")
            import traceback
            traceback.print_exc()
            return 1
    
    print(f"   ✓ {len(briefs)} coherence brief(s) criados com sucesso")
    
    # Validação do estado após criação de briefs
    briefs_validation = validate_state_evolution(state, "briefs_created", len(briefs), article_slug)
    print(f"   ✓ Estado após criação de briefs: {briefs_validation['briefs_count']} briefs")
    
    # =====================================================================
    # FASE 3: NARRATIVE ARCHITECT
    # =====================================================================
    print_section("FASE 3: NARRATIVE ARCHITECT")
    
    print_step(7, "Gerando estruturas narrativas...")
    
    narrative_results = []
    
    for idx, brief in enumerate(briefs, 1):
        print(f"   [{idx}/{len(briefs)}] Gerando narrativa para {brief.post_id}...", end=" ")
        
        try:
            # Cria estratégia episódica para este brief
            state_strategy = BriefEpisodicStrategy(post_id=brief.post_id)
            
            # Executa narrative architect
            narrative_result = orchestrator.dispatch(
                agent=orchestrator.registry["narrative_architect"],
                task={
                    "brief": brief,
                    "article_text": article_text,
                    "llm_client": llm_client,
                },
                state=state,
                state_strategy=state_strategy,
            )
            
            narrative_results.append({
                "brief": brief,
                "narrative_payload": narrative_result,
            })
            
            print("✓")
            
            # Salva brief atualizado (com evolução narrativa)
            post_dir = output_dir / brief.post_id
            post_dir.mkdir(parents=True, exist_ok=True)
            brief_path = post_dir / "coherence_brief.json"
            brief_path.write_text(
                json.dumps(brief.to_dict(), indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            
            # Salva estrutura narrativa
            narrative_path = post_dir / "narrative_structure.json"
            narrative_path.write_text(
                json.dumps(narrative_result, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            
        except Exception as exc:
            error_msg = str(exc)
            print(f"❌ ({error_msg[:60]}...)")
            import traceback
            traceback.print_exc()
            return 1
    
    print(f"   ✓ {len(narrative_results)} estrutura(s) narrativa(s) gerada(s) com sucesso")
    
    # Validação do estado após narrative architect
    narrative_validation = validate_state_evolution(
        state, "narrative_architect", len(briefs), article_slug
    )
    print(f"   ✓ Estado após narrative architect: {narrative_validation['briefs_count']} briefs")
    
    # Verifica evolução dos briefs
    for post_id, brief in narrative_validation["briefs"].items():
        if isinstance(brief, CoherenceBrief):
            has_narrative = brief.narrative_structure is not None
            print(f"      - {post_id}: narrative_structure={'✓' if has_narrative else '✗'}")
    
    # =====================================================================
    # FASE 4: COPYWRITER
    # =====================================================================
    print_section("FASE 4: COPYWRITER")
    
    print_step(8, "Gerando copy para todos os slides...")
    
    all_copy_results = []
    
    for result_idx, result in enumerate(narrative_results, 1):
        brief = result["brief"]
        narrative_payload = result["narrative_payload"]
        slides = narrative_payload.get("slides", [])
        
        print(f"\n   Post {result_idx}/{len(narrative_results)}: {brief.post_id} ({len(slides)} slides)")
        
        post_copy_results = []
        
        for slide_idx, slide_info in enumerate(slides, 1):
            slide_number = slide_info.get("slide_number", slide_idx)
            print(f"      Slide {slide_idx}/{len(slides)} (slide_number={slide_number})...", end=" ")
            
            try:
                # Cria estratégia episódica para este brief
                state_strategy = BriefEpisodicStrategy(post_id=brief.post_id)
                
                # Executa copywriter
                slide_content = orchestrator.dispatch(
                    agent=orchestrator.registry["copywriter"],
                    task={
                        "brief": brief,
                        "slide_info": slide_info,
                        "article_text": article_text,
                        "llm_client": llm_client,
                    },
                    state=state,
                    state_strategy=state_strategy,
                )
                
                post_copy_results.append({
                    "slide_number": slide_number,
                    "slide_info": slide_info,
                    "slide_content": slide_content,
                })
                
                print("✓")
                
                # Salva conteúdo do slide
                post_dir = output_dir / brief.post_id
                slide_content_path = post_dir / f"slide_{slide_number}_content.json"
                slide_content_path.write_text(
                    json.dumps(slide_content, indent=2, ensure_ascii=False, default=str),
                    encoding="utf-8",
                )
                
            except Exception as exc:
                error_msg = str(exc)
                print(f"❌ ({error_msg[:60]}...)")
                import traceback
                traceback.print_exc()
                return 1
        
        all_copy_results.append({
            "brief": brief,
            "narrative_payload": narrative_payload,
            "slide_contents": post_copy_results,
        })
        
        # Salva brief atualizado (com evolução de copywriting)
        post_dir = output_dir / brief.post_id
        brief_path = post_dir / "coherence_brief.json"
        brief_path.write_text(
            json.dumps(brief.to_dict(), indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        
        print(f"      ✓ {len(post_copy_results)} slide(s) processado(s)")
    
    total_slides = sum(len(r["slide_contents"]) for r in all_copy_results)
    print(f"\n   ✓ {total_slides} slide(s) total(is) processado(s) com sucesso")
    
    # Validação do estado após copywriter
    copywriter_validation = validate_state_evolution(
        state, "copywriter", len(briefs), article_slug
    )
    print(f"   ✓ Estado após copywriter: {copywriter_validation['briefs_count']} briefs")
    
    # Verifica evolução dos briefs
    for post_id, brief in copywriter_validation["briefs"].items():
        if isinstance(brief, CoherenceBrief):
            has_narrative = brief.narrative_structure is not None
            has_copy = brief.copy_guidelines is not None
            has_cta = brief.cta_guidelines is not None
            print(f"      - {post_id}:")
            print(f"        narrative_structure={'✓' if has_narrative else '✗'}")
            print(f"        copy_guidelines={'✓' if has_copy else '✗'}")
            print(f"        cta_guidelines={'✓' if has_cta else '✗'}")
    
    # =====================================================================
    # RESUMO E VALIDAÇÃO FINAL
    # =====================================================================
    print_section("RESUMO E VALIDAÇÃO FINAL")
    
    print_step(9, "Resumo do pipeline:")
    
    print(f"\n   Fase 1 (Ideation):")
    print(f"     ✓ Ideias geradas: {len(all_ideas)}")
    print(f"     ✓ Ideias processadas: {len(selected_ideas)}")
    
    print(f"\n   Fase 2 (Coherence Briefs):")
    print(f"     ✓ Briefs criados: {len(briefs)}")
    
    print(f"\n   Fase 3 (Narrative Architect):")
    print(f"     ✓ Estruturas narrativas: {len(narrative_results)}")
    for idx, result in enumerate(narrative_results, 1):
        slides_count = len(result["narrative_payload"].get("slides", []))
        print(f"       - Brief {idx}: {slides_count} slides")
    
    print(f"\n   Fase 4 (Copywriter):")
    print(f"     ✓ Total de slides com copy: {total_slides}")
    for idx, result in enumerate(all_copy_results, 1):
        slides_count = len(result["slide_contents"])
        print(f"       - Post {idx}: {slides_count} slides")
    
    # Validação final da evolução do estado
    print_step(10, "Validando evolução dos coherence briefs...")
    
    final_validation = validate_state_evolution(state, "final", len(briefs), article_slug)
    
    for idx, brief in enumerate(briefs, 1):
        has_narrative = brief.narrative_structure is not None
        has_copy_guidelines = brief.copy_guidelines is not None
        has_cta_guidelines = brief.cta_guidelines is not None
        
        print(f"   Brief {idx} ({brief.post_id}):")
        print(f"     - Narrative structure: {'✓' if has_narrative else '✗'}")
        print(f"     - Copy guidelines: {'✓' if has_copy_guidelines else '✗'}")
        print(f"     - CTA guidelines: {'✓' if has_cta_guidelines else '✗'}")
    
    # Salva resultados consolidados
    print_step(11, "Salvando resultados consolidados...")
    
    consolidated_briefs = [brief.to_dict() for brief in briefs]
    consolidated_path = output_dir / "coherence_briefs_final.json"
    consolidated_path.write_text(
        json.dumps(consolidated_briefs, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    print(f"   ✓ Briefs consolidados: {consolidated_path}")
    
    # Salva todos os conteúdos de slides por post
    for result in all_copy_results:
        brief = result["brief"]
        post_dir = output_dir / brief.post_id
        all_slides_content = {
            "post_id": brief.post_id,
            "slides": [
                {
                    "slide_number": sc["slide_number"],
                    "content": sc["slide_content"],
                }
                for sc in result["slide_contents"]
            ],
        }
        all_slides_path = post_dir / "all_slides_content.json"
        all_slides_path.write_text(
            json.dumps(all_slides_content, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        print(f"   ✓ Conteúdo de todos os slides: {all_slides_path}")
    
    # Verifica banco de dados SQL
    print_step(12, "Verificando banco de dados SQL...")
    try:
        trace_data = state.get_trace_details(trace_id)
        
        if trace_data:
            events = trace_data.get("events", [])
            print(f"   ✓ Trace encontrado: {trace_id[:8]}..., eventos: {len(events)}")
            
            # Breakdown de eventos por tipo
            event_types = {}
            for event in events:
                etype = event.get("type", "unknown")
                event_types[etype] = event_types.get(etype, 0) + 1
            
            print("   ✓ Breakdown de eventos:")
            for etype, count in event_types.items():
                print(f"     - {etype}: {count}")
        else:
            print("   ⚠️  Trace não encontrado no banco de dados")
    except Exception as exc:
        print(f"   ⚠️  Erro ao verificar banco de dados: {exc}")
    
    # Relatório final
    print_section("TESTE CONCLUÍDO COM SUCESSO!")
    
    print(f"\n📄 Diretório de saída: {output_dir}")
    print(f"📊 Trace ID: {trace_id}")
    print(f"📈 Total de slides processados: {total_slides}")
    print(f"📦 Briefs no estado: {final_validation['briefs_count']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(test_full_pipeline())
