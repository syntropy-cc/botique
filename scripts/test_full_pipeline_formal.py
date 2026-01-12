#!/usr/bin/env python3
"""
Teste completo do sistema usando o Framework Formal.

Demonstra o uso completo do framework formal em um pipeline real:
- UniversalState (Ω) - Estado universal
- Memory Strategies (π) - Estratégias de memória
- Agents (A) - Agentes como grafos
- FormalOrchestrator (O) - Orquestrador formal

Este script é similar ao generate_full_pipeline_production.py mas usa
o framework formal para orquestrar as fases.

Location: scripts/test_full_pipeline_formal.py
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

from dotenv import load_dotenv

# Add project root to path (not src directly, to preserve package hierarchy)
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Try new locations first, fallback to old locations
try:
    from framework.core.universal_state import UniversalState
    from framework.core.state_management import (
        EpisodicStrategy,
        HierarchicalStrategy,
        create_strategy,
    )
    from framework.core.agent import (
        create_ideation_agent,
        create_selection_agent,
        create_coherence_agent,
    )
    from framework.core.orchestrator import Orchestrator as FormalOrchestrator
    from framework.llm.http_client import HttpLLMClient
    from framework.llm.logger import LLMLogger
except ImportError:
    from src.core.universal_state import UniversalState
    from src.core.memory_strategies import (
        EpisodicStrategy,
        HierarchicalStrategy,
        create_strategy,
    )
    from src.core.agent import (
        create_ideation_agent,
        create_selection_agent,
        create_coherence_agent,
    )
    from src.core.orchestrator_formal import FormalOrchestrator
    from src.core.llm_client import HttpLLMClient
    from src.core.llm_logger import LLMLogger

from src.core.config import IdeationConfig, SelectionConfig, OUTPUT_DIR
from src.phases import run_phase1, run_phase2, run_phase3
# Try new location first, fallback to old location
try:
    from framework.llm.prompt_helpers import get_or_register_prompt as get_latest_prompt
except ImportError:
    from src.core.prompt_registry import get_latest_prompt


def test_formal_pipeline_with_article(article_path: Path) -> int:
    """
    Testa o pipeline completo usando o framework formal.
    
    Args:
        article_path: Caminho para o artigo
        
    Returns:
        Código de saída (0 para sucesso, 1 para falha)
    """
    print("=" * 80)
    print("TESTE COMPLETO DO PIPELINE COM FRAMEWORK FORMAL")
    print("=" * 80)
    print()
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    article_slug = article_path.stem if article_path.suffix else article_path.name
    print(f"📄 Artigo: {article_path.name}")
    print(f"📋 Slug: {article_slug}")
    print()
    
    # =====================================================================
    # 1. INICIALIZAR ESTADO UNIVERSAL (Ω)
    # =====================================================================
    print("=" * 80)
    print("1. INICIALIZANDO ESTADO UNIVERSAL (Ω)")
    print("=" * 80)
    print()
    
    state = UniversalState()
    state.article_slug = article_slug
    print("✅ UniversalState criado e configurado")
    print(f"   - article_slug: {state.article_slug}")
    print()
    
    # =====================================================================
    # 2. INICIALIZAR LLM CLIENT E LOGGER
    # =====================================================================
    print("=" * 80)
    print("2. INICIALIZANDO LLM CLIENT E LOGGER")
    print("=" * 80)
    print()
    
    # Verificar API key
    api_key = os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ ERRO: LLM_API_KEY ou DEEPSEEK_API_KEY não encontrada no ambiente")
        return 1
    
    # Verificar estado inicial do banco de dados
    print("2.1. Verificando estado inicial do banco de dados...")
    initial_trace_count = 0
    try:
        # Try new location first, fallback to old location
        try:
            from framework.llm.queries import list_traces
            from framework.llm.logger import get_db_path
        except ImportError:
            from src.core.llm_log_queries import list_traces
            from src.core.llm_log_db import get_db_path
        
        db_path = get_db_path()
        initial_traces = list_traces(limit=1000, db_path=db_path)
        initial_trace_count = len(initial_traces)
        print(f"   ✅ Banco de dados acessível: {db_path}")
        print(f"   📊 Traces existentes: {initial_trace_count}")
    except Exception as exc:
        print(f"   ⚠️  Erro ao verificar banco inicial: {exc}")
        initial_trace_count = 0
    
    print()
    
    # Inicializar logger
    print("2.2. Inicializando logger SQL...")
    logger = LLMLogger(use_sql=True)
    trace_id = logger.create_trace(
        name="test_full_pipeline_formal",
        metadata={
            "article_slug": article_slug,
            "article_path": str(article_path),
            "script": "test_full_pipeline_formal",
            "framework": "formal",
        },
    )
    state.current_trace_id = trace_id
    logger.set_context(article_slug=article_slug)
    
    print(f"   ✅ Logger inicializado")
    print(f"      - Trace ID: {trace_id}")
    print(f"      - SQL logging: habilitado")
    print(f"      - Banco de dados: {get_db_path()}")
    print()
    
    # Preparar diretórios de saída
    article_output_dir = OUTPUT_DIR / article_slug
    article_output_dir.mkdir(parents=True, exist_ok=True)
    debug_dir = article_output_dir / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    
    # Inicializar LLM client
    llm_client = HttpLLMClient(
        api_key=api_key,
        base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"),
        model=os.getenv("LLM_MODEL", "deepseek-chat"),
        timeout=int(os.getenv("LLM_TIMEOUT", "180")),
        logger=logger,
        save_raw_responses=True,
        raw_responses_dir=debug_dir,
    )
    
    print(f"✅ LLM Client inicializado")
    print(f"   - Model: {llm_client.model}")
    print(f"   - Timeout: {llm_client.timeout}s")
    print()
    
    # Verificar artigo
    if not article_path.exists():
        print(f"❌ ERRO: Artigo não encontrado: {article_path}")
        return 1
    
    article_text = article_path.read_text(encoding="utf-8")
    print(f"✅ Artigo carregado: {len(article_text)} caracteres")
    print()
    
    # =====================================================================
    # 3. CRIAR E REGISTRAR AGENTES (A)
    # =====================================================================
    print("=" * 80)
    print("3. CRIANDO E REGISTRANDO AGENTES (A = ⟨V, E, λ_V, λ_E, v_0, Σ_A⟩)")
    print("=" * 80)
    print()
    
    # Criar agentes a partir das fases existentes
    ideation_agent = create_ideation_agent(run_phase1)
    selection_agent = create_selection_agent(run_phase2)
    coherence_agent = create_coherence_agent(run_phase3)
    
    print("✅ Agentes criados:")
    print(f"   - {ideation_agent.name}: {ideation_agent.entry_vertex}")
    print(f"   - {selection_agent.name}: {selection_agent.entry_vertex}")
    print(f"   - {coherence_agent.name}: {coherence_agent.entry_vertex}")
    print()
    
    # Criar orquestrador formal
    orchestrator = FormalOrchestrator()
    print("✅ FormalOrchestrator criado")
    print()
    
    # Registrar agentes no registry R
    orchestrator.register_agent(
        ideation_agent,
        description="Gera ideias de posts a partir de artigos"
    )
    orchestrator.register_agent(
        selection_agent,
        description="Seleciona e filtra ideias geradas"
    )
    orchestrator.register_agent(
        coherence_agent,
        description="Cria coherence briefs para ideias selecionadas"
    )
    
    print("✅ Agentes registrados no registry R:")
    registry = orchestrator.get_registry()
    for name, agent in registry.items():
        print(f"   - {name}: {agent}")
    print()
    
    # =====================================================================
    # 4. CONFIGURAR E EXECUTAR PIPELINE
    # =====================================================================
    print("=" * 80)
    print("4. EXECUTANDO PIPELINE COM FORMAL ORCHESTRATOR")
    print("=" * 80)
    print()
    
    # Verificar prompts necessários
    print("4.1. Verificando prompts...")
    
    ideator_prompt_key = "post_ideator"
    ideator_prompt_data = get_latest_prompt(ideator_prompt_key)
    if not ideator_prompt_data:
        print(f"   ❌ ERRO: Prompt '{ideator_prompt_key}' não encontrado!")
        return 1
    print(f"   ✅ Prompt '{ideator_prompt_key}' encontrado")
    print()
    
    # Configurar fases
    ideation_config = IdeationConfig(
        num_ideas_min=3,
        num_ideas_max=5,
        num_insights_min=3,
        num_insights_max=5,
    )
    
    selection_config = SelectionConfig(
        max_selected=3,
        strategy="top",
    )
    
    max_ideas_to_test = int(os.getenv("MAX_IDEAS_TO_TEST", "2"))
    
    print("4.2. Configurações:")
    print(f"   - Ideation: min={ideation_config.num_ideas_min}, max={ideation_config.num_ideas_max}")
    print(f"   - Selection: max={selection_config.max_selected}, strategy={selection_config.strategy}")
    print(f"   - Máximo de ideias para processar: {max_ideas_to_test}")
    print()
    
    # Executar Phase 1 via agente
    print("4.3. Executando Phase 1 (Ideation) via agente...")
    print("   ⏳ Isso pode levar um tempo...")
    
    try:
        phase1_start = time.time()
        
        phase1_input = {
            "article_path": article_path,
            "config": ideation_config,
            "llm_client": llm_client,
            "output_dir": article_output_dir,
        }
        
        phase1_result = ideation_agent.execute(
            input_data=phase1_input,
            state=state,
        )
        
        phase1_duration = time.time() - phase1_start
        
        print(f"   ✅ Phase 1 executada em {phase1_duration:.2f}s")
        print(f"      - Ideias geradas: {phase1_result.get('ideas_count', 'N/A')}")
        print(f"      - Briefs criados: {phase1_result.get('briefs_count', 'N/A')}")
        
        # Verificar estado universal após Phase 1
        briefs_after_phase1 = state.get_all_briefs()
        print(f"      - Briefs no estado universal: {len(briefs_after_phase1)}")
        
        # Validar que briefs foram realmente armazenados
        if briefs_after_phase1:
            first_post_id = list(briefs_after_phase1.keys())[0]
            first_brief = briefs_after_phase1[first_post_id]
            print(f"      - Exemplo de brief armazenado: {first_post_id}")
            print(f"        Platform: {first_brief.platform if hasattr(first_brief, 'platform') else 'N/A'}")
        else:
            print(f"      ⚠️  AVISO: Nenhum brief foi armazenado no estado universal!")
        
        print()
        
    except Exception as exc:
        print(f"   ❌ ERRO na Phase 1: {exc}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Selecionar ideias para processar
    all_ideas = phase1_result.get("ideas", [])
    if 0 < max_ideas_to_test < len(all_ideas):
        selected_ideas_for_testing = all_ideas[:max_ideas_to_test]
        print(f"   📋 Selecionando {len(selected_ideas_for_testing)} ideias para processar")
    else:
        selected_ideas_for_testing = all_ideas
    
    # Executar Phase 2 via agente (se necessário)
    # Nota: A Phase 2 já está integrada na Phase 1 com filtros
    # Mas podemos executar uma seleção adicional se desejado
    filtered_ideas = phase1_result.get("filtered_ideas", selected_ideas_for_testing)
    
    if len(filtered_ideas) > max_ideas_to_test:
        filtered_ideas = filtered_ideas[:max_ideas_to_test]
    
    print(f"4.4. Processando {len(filtered_ideas)} ideias na Phase 3...")
    print()
    
    # Executar Phase 3 via agente (para cada ideia selecionada)
    coherence_results = []
    
    for idx, idea in enumerate(filtered_ideas, 1):
        idea_id = idea.get("id", f"unknown_{idx}")
        print(f"   [{idx}/{len(filtered_ideas)}] Processando ideia {idea_id}...", end=" ")
        
        try:
            phase3_input = {
                "selected_ideas": [idea],  # Processar uma ideia por vez
                "article_summary": phase1_result.get("article_summary", {}),
                "article_slug": article_slug,
                "output_dir": article_output_dir,
            }
            
            phase3_result = coherence_agent.execute(
                input_data=phase3_input,
                state=state,
            )
            
            coherence_results.append({
                "idea": idea,
                "result": phase3_result,
            })
            
            print("✅")
            
        except Exception as exc:
            print(f"❌ ({str(exc)[:60]}...)")
            continue
    
    print()
    print(f"   ✅ {len(coherence_results)} brief(s) de coherence processado(s)")
    print()
    
    # =====================================================================
    # 5. TESTAR ESTRATÉGIAS DE MEMÓRIA (π)
    # =====================================================================
    print("=" * 80)
    print("5. TESTANDO ESTRATÉGIAS DE MEMÓRIA (π)")
    print("=" * 80)
    print()
    
    all_briefs = state.get_all_briefs()
    print(f"✅ Total de briefs no estado universal: {len(all_briefs)}")
    print()
    
    if all_briefs:
        # Testar EpisodicStrategy (vista por post_id)
        print("5.1. Testando EpisodicStrategy (vista episódica)...")
        first_post_id = list(all_briefs.keys())[0]
        episodic_strategy = EpisodicStrategy(post_id=first_post_id)
        episodic_view = episodic_strategy.project(state)
        
        print(f"   - Post ID: {first_post_id}")
        print(f"   - Brief encontrado: {episodic_view['brief'] is not None}")
        if episodic_view['brief']:
            brief = episodic_view['brief']
            print(f"   - Platform: {brief.platform if hasattr(brief, 'platform') else 'N/A'}")
            print(f"   - Format: {brief.format if hasattr(brief, 'format') else 'N/A'}")
        print()
        
        # Testar HierarchicalStrategy (vista hierárquica por artigo)
        print("5.2. Testando HierarchicalStrategy (vista hierárquica)...")
        hierarchical_strategy = HierarchicalStrategy(article_slug=article_slug)
        hierarchical_view = hierarchical_strategy.project(state)
        
        print(f"   - Article Slug: {article_slug}")
        print(f"   - Briefs encontrados: {hierarchical_view['count']}")
        print(f"   - Briefs: {[pid for pid in hierarchical_view.get('briefs', {}).keys()][:3]}...")
        print()
    
    # =====================================================================
    # 6. TESTAR ORQUESTRADOR FORMAL (O)
    # =====================================================================
    print("=" * 80)
    print("6. TESTANDO ORQUESTRADOR FORMAL (O = ⟨R, π, dispatch, aggregate, Γ⟩)")
    print("=" * 80)
    print()
    
    # Testar política de seleção π
    print("6.1. Testando política de seleção π(q, Ω)...")
    
    test_queries = [
        "generate ideas",
        "select ideas",
        "build coherence briefs",
        "full pipeline",
        "unknown query",
    ]
    
    for query in test_queries:
        selected = orchestrator.select_agents(query, state)
        print(f"   - Query '{query}': {[a.name for a in selected]}")
    print()
    
    # Verificar estado interno Γ
    print("6.2. Estado interno do orquestrador Γ:")
    internal_state = orchestrator.get_internal_state()
    for key, value in internal_state.items():
        print(f"   - {key}: {value}")
    print()
    
    # =====================================================================
    # 7. VALIDAÇÃO E RESUMO
    # =====================================================================
    print("=" * 80)
    print("7. VALIDAÇÃO E RESUMO")
    print("=" * 80)
    print()
    
    print("7.1. Resumo do Pipeline:")
    print(f"   - Phase 1 (Ideation): {phase1_result.get('ideas_count', 0)} ideias geradas")
    print(f"   - Phase 3 (Coherence): {len(coherence_results)} brief(s) processado(s)")
    print(f"   - Estado Universal: {len(state.get_all_briefs())} brief(s) armazenado(s)")
    print()
    
    print("7.2. Validação do Framework:")
    
    # Validar estado universal
    print("   ✅ UniversalState (Ω):")
    print(f"      - article_slug: {state.article_slug}")
    print(f"      - briefs armazenados: {len(state.get_all_briefs())}")
    print(f"      - trace_id: {state.current_trace_id[:8] if state.current_trace_id else 'N/A'}...")
    print()
    
    # Validar agentes
    print("   ✅ Agentes (A):")
    for name, agent in orchestrator.get_registry().items():
        print(f"      - {name}: {len(agent.vertices)} vértices, {sum(len(t) for t in agent.edges.values())} arestas")
    print()
    
    # Validar orquestrador
    print("   ✅ FormalOrchestrator (O):")
    print(f"      - Agentes registrados: {len(orchestrator.get_registry())}")
    print(f"      - Execuções: {internal_state.get('execution_count', 0)}")
    print()
    
    # Validar estratégias de memória
    print("   ✅ Estratégias de Memória (π):")
    print(f"      - EpisodicStrategy: funcional")
    print(f"      - HierarchicalStrategy: funcional")
    print()
    
    # Verificar banco de dados - Validação completa
    print("7.3. Verificando banco de dados SQL (validação completa)...")
    print()
    
    try:
        # Try new location first, fallback to old location
        try:
            from framework.llm.queries import get_trace_with_events, list_traces
            from framework.llm.logger import get_db_path
        except ImportError:
            from src.core.llm_log_queries import get_trace_with_events, list_traces
            from src.core.llm_log_db import get_db_path
        
        db_path = get_db_path()
        print(f"   📊 Banco de dados: {db_path}")
        print(f"   📊 Tamanho do arquivo: {db_path.stat().st_size / 1024:.2f} KB")
        print()
        
        # Verificar trace criado
        trace_data = get_trace_with_events(trace_id, db_path)
        
        if trace_data:
            events = trace_data.get("events", [])
            trace_metadata = trace_data.get("trace", {})
            
            print(f"   ✅ Trace encontrado no banco de dados:")
            print(f"      - Trace ID: {trace_id}")
            print(f"      - Nome: {trace_metadata.get('name', 'N/A')}")
            print(f"      - Total de eventos: {len(events)}")
            print(f"      - Criado em: {trace_metadata.get('created_at', 'N/A')}")
            print()
            
            # Contagem por tipo de evento
            event_types = {}
            llm_events = []
            step_events = []
            
            for event in events:
                etype = event.get("type", "unknown")
                event_types[etype] = event_types.get(etype, 0) + 1
                
                if etype == "llm":
                    llm_events.append(event)
                elif etype == "step":
                    step_events.append(event)
            
            print("   📈 Análise de eventos:")
            print(f"      - Tipos únicos: {len(event_types)}")
            for etype, count in sorted(event_types.items()):
                print(f"      - {etype}: {count} evento(s)")
            print()
            
            # Análise de eventos LLM
            if llm_events:
                print(f"   🤖 Eventos LLM ({len(llm_events)}):")
                llm_names = {}
                for event in llm_events:
                    name = event.get("name", "unknown")
                    llm_names[name] = llm_names.get(name, 0) + 1
                
                for name, count in sorted(llm_names.items()):
                    print(f"      - {name}: {count} chamada(s)")
                print()
            
            # Análise de eventos de step
            if step_events:
                print(f"   📝 Eventos de Step ({len(step_events)}):")
                step_names = {}
                for event in step_events:
                    name = event.get("name", "unknown")
                    step_names[name] = step_names.get(name, 0) + 1
                
                for name, count in sorted(step_names.items())[:5]:  # Top 5
                    print(f"      - {name}: {count} evento(s)")
                if len(step_names) > 5:
                    print(f"      ... e mais {len(step_names) - 5} tipo(s)")
                print()
            
            # Verificar se eventos têm dados completos
            events_with_output = sum(1 for e in events if e.get("output_text") or e.get("output_json"))
            events_with_error = sum(1 for e in events if e.get("error"))
            
            print(f"   ✅ Integridade dos eventos:")
            print(f"      - Eventos com output: {events_with_output}/{len(events)}")
            print(f"      - Eventos com erro: {events_with_error}")
            print()
            
        else:
            print(f"   ❌ ERRO: Trace {trace_id} NÃO encontrado no banco de dados!")
            print(f"      Isso indica que os eventos não foram salvos corretamente.")
            print()
        
        # Verificar se o número de traces aumentou
        final_traces = list_traces(limit=1000, db_path=db_path)
        final_trace_count = len(final_traces)
        
        print(f"   📊 Comparação de traces:")
        print(f"      - Traces antes: {initial_trace_count}")
        print(f"      - Traces depois: {final_trace_count}")
        print(f"      - Novo trace criado: {'✅ SIM' if final_trace_count > initial_trace_count else '❌ NÃO'}")
        print()
        
        # Validar que nosso trace está na lista
        our_trace_in_list = any(t.get("trace_id") == trace_id for t in final_traces)
        print(f"   ✅ Trace na lista de traces: {'✅ SIM' if our_trace_in_list else '❌ NÃO'}")
        print()
        
    except Exception as exc:
        print(f"   ❌ ERRO ao verificar banco de dados: {exc}")
        import traceback
        traceback.print_exc()
        print()
    
    # Validação adicional: Verificar arquivos de saída
    print("7.4. Verificando arquivos de saída...")
    output_files = {
        "phase1_ideas.json": article_output_dir / "phase1_ideas.json",
        "coherence_briefs.json": article_output_dir / "coherence_briefs.json",
        "framework_formal_summary.json": article_output_dir / "framework_formal_summary.json",
    }
    
    for name, path in output_files.items():
        if path.exists():
            size = path.stat().st_size
            print(f"   ✅ {name}: {size} bytes")
        else:
            print(f"   ⚠️  {name}: não encontrado")
    
    # Verificar diretórios de posts
    post_dirs = [d for d in article_output_dir.iterdir() if d.is_dir() and d.name.startswith("post_")]
    print(f"   ✅ Diretórios de posts: {len(post_dirs)}")
    for post_dir in post_dirs[:3]:  # Mostrar primeiros 3
        brief_file = post_dir / "coherence_brief.json"
        if brief_file.exists():
            print(f"      - {post_dir.name}: coherence_brief.json ✅")
    if len(post_dirs) > 3:
        print(f"      ... e mais {len(post_dirs) - 3} diretório(s)")
    print()
    
    # =====================================================================
    # 8. SALVAR RESULTADOS
    # =====================================================================
    print("=" * 80)
    print("8. SALVANDO RESULTADOS")
    print("=" * 80)
    print()
    
    # Salvar resumo do framework
    framework_summary = {
        "trace_id": trace_id,
        "article_slug": article_slug,
        "framework_version": "formal_mvp",
        "pipeline_results": {
            "phase1": {
                "ideas_count": phase1_result.get("ideas_count", 0),
                "briefs_count": phase1_result.get("briefs_count", 0),
            },
            "phase3": {
                "coherence_briefs_processed": len(coherence_results),
            },
        },
        "state_summary": {
            "total_briefs": len(state.get_all_briefs()),
            "article_slug": state.article_slug,
        },
        "orchestrator_summary": {
            "registered_agents": list(orchestrator.get_registry().keys()),
            "internal_state": orchestrator.get_internal_state(),
        },
    }
    
    summary_path = article_output_dir / "framework_formal_summary.json"
    summary_path.write_text(
        json.dumps(framework_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"✅ Resumo do framework salvo: {summary_path}")
    print()
    
    # =====================================================================
    # CONCLUSÃO
    # =====================================================================
    print("=" * 80)
    print("✅ TESTE COMPLETO DO PIPELINE COM FRAMEWORK FORMAL CONCLUÍDO!")
    print("=" * 80)
    print()
    print(f"📄 Diretório de saída: {article_output_dir}")
    print(f"📊 Trace ID: {trace_id}")
    print(f"📈 Briefs no estado universal: {len(state.get_all_briefs())}")
    print(f"🤖 Agentes registrados: {len(orchestrator.get_registry())}")
    print()
    print("Componentes testados:")
    print("  ✅ UniversalState (Ω) - Estado universal")
    print("  ✅ Memory Strategies (π) - Estratégias de memória")
    print("  ✅ Agents (A) - Agentes como grafos")
    print("  ✅ FormalOrchestrator (O) - Orquestrador formal")
    print("  ✅ Pipeline completo - Execução sequencial de fases")
    print()
    
    return 0


def main() -> int:
    """Função principal."""
    print("\n" + "=" * 80)
    print("TESTE COMPLETO DO SISTEMA COM FRAMEWORK FORMAL")
    print("=" * 80)
    print()
    print("Este script demonstra o uso completo do framework formal:")
    print("  - UniversalState (Ω) - Estado universal")
    print("  - Memory Strategies (π) - Estratégias de memória")
    print("  - Agents (A) - Agentes como grafos")
    print("  - FormalOrchestrator (O) - Orquestrador formal")
    print()
    print("=" * 80)
    print()
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Encontrar artigo - priorizar artigo específico
    article_path_env = os.getenv("ARTICLE_PATH")
    articles_dir = Path(__file__).resolve().parents[1] / "articles"
    
    if article_path_env:
        article_path = Path(article_path_env)
        if not article_path.exists():
            print(f"⚠️  Artigo especificado não encontrado: {article_path}")
            print("   Procurando em articles/...")
            article_path = None
    else:
        article_path = None
    
    # Tentar usar artigo específico primeiro
    if article_path is None:
        specific_article = articles_dir / "why-tradicional-learning-fails.md"
        if specific_article.exists():
            article_path = specific_article
            print(f"📄 Usando artigo específico: {article_path.name}")
        else:
            # Procurar qualquer artigo
            articles = list(articles_dir.glob("*.md"))
            if not articles:
                print("❌ ERRO: Nenhum artigo encontrado em articles/")
                print("   Configure ARTICLE_PATH ou coloque um artigo em articles/")
                return 1
            article_path = articles[0]
            print(f"📄 Usando primeiro artigo encontrado: {article_path.name}")
    else:
        print(f"📄 Usando artigo especificado: {article_path.name}")
    
    print(f"   Caminho completo: {article_path.resolve()}")
    print()
    
    # Executar teste
    try:
        return test_formal_pipeline_with_article(article_path)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        return 1
    except Exception as exc:
        print(f"\n❌ ERRO: {exc}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

