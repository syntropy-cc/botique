# Framework Formal - Guia de Uso

## Visão Geral

Este framework formal implementa o modelo teórico definido em `docs/framework.md` como **MVP mínimo**. O framework fornece abstrações formais sobre o código existente **sem breaking changes** - todo código existente continua funcionando normalmente.

## Componentes Principais

### 1. Estado Universal (Ω)

**Arquivo**: `src/core/universal_state.py`

Encapsula o estado universal do sistema:
- **Memória Contextual**: `CoherenceBrief` objects (memória ativa por post)
- **Memória Persistente**: SQLite database (histórico de execuções)

```python
from src.core.universal_state import UniversalState
from src.coherence.brief import CoherenceBrief

# Criar estado universal
state = UniversalState()

# Armazenar brief
brief = CoherenceBrief(...)
state.store_brief(brief)

# Recuperar brief
retrieved = state.get_brief("post_001")

# Consultar histórico
history = state.query_history(limit=10)
```

### 2. Instruções Formais (i = ⟨p, θ, φ_in, φ_out, κ⟩)

**Arquivo**: `src/core/instruction.py`

Formaliza instruções como entidades completas:
- **p**: Template de prompt
- **θ**: Configuração LLM (model, temperature, max_tokens)
- **φ_in**: Função de pré-processamento
- **φ_out**: Função de pós-processamento
- **κ**: Requisitos de contexto de memória

```python
from src.core.instruction import Instruction
from src.core.llm_client import HttpLLMClient

# Criar instrução
instruction = Instruction(
    prompt_key="post_ideator",
    prompt_template="Analyze: {article}",
    model="deepseek-chat",
    temperature=0.2,
    max_tokens=2048,
)

# Executar instrução
llm_client = HttpLLMClient(...)
result = instruction.execute(
    input_data={"article": "..."},
    llm_client=llm_client,
    memory_context={"brief": brief} if memory_strategy else None,
)
```

### 3. Estratégias de Memória (π)

**Arquivo**: `src/core/memory_strategies.py`

Define como agentes acessam o estado universal através de projeções π: Ω → M_view

```python
from src.core.memory_strategies import (
    EpisodicStrategy,
    HierarchicalStrategy,
    create_strategy,
)

# Estratégia episódica: apenas o brief do post atual
strategy = EpisodicStrategy(post_id="post_001")
view = strategy.project(state)

# Estratégia hierárquica: todos os briefs do artigo
strategy = HierarchicalStrategy(article_slug="article_slug")
view = strategy.project(state)

# Factory function
strategy = create_strategy("episodic", "post_001")
```

### 4. Agentes (A = ⟨V, E, λ_V, λ_E, v_0, Σ_A⟩)

**Arquivo**: `src/core/agent.py`

Wrappers sobre funções de fases existentes como agentes formais.

```python
from src.core.agent import (
    create_ideation_agent,
    create_selection_agent,
    create_coherence_agent,
)
from src.phases.phase1_ideation import run as run_phase1

# Criar agente a partir de fase existente
agent = create_ideation_agent(run_phase1)

# Executar agente
state = UniversalState()
result = agent.execute(
    input_data={
        "article_path": Path("article.md"),
        "config": IdeationConfig(),
        "llm_client": llm_client,
    },
    state=state,
    memory_strategy=EpisodicStrategy(post_id="post_001"),
)
```

### 5. Orquestrador Formal (O = ⟨R, π, dispatch, aggregate, Γ⟩)

**Arquivo**: `src/core/orchestrator_formal.py`

Orquestrador que coordena múltiplos agentes.

```python
from src.core.orchestrator_formal import FormalOrchestrator
from src.core.agent import (
    create_ideation_agent,
    create_selection_agent,
    create_coherence_agent,
)
from src.phases.phase1_ideation import run as run_phase1
from src.phases.phase2_selection import run as run_phase2
from src.phases.phase3_coherence import run as run_phase3

# Criar orquestrador
orchestrator = FormalOrchestrator()

# Registrar agentes
orchestrator.register_agent(create_ideation_agent(run_phase1))
orchestrator.register_agent(create_selection_agent(run_phase2))
orchestrator.register_agent(create_coherence_agent(run_phase3))

# Orquestrar pipeline completo
result = orchestrator.orchestrate(
    query="full pipeline",
    initial_data={
        "article_path": Path("article.md"),
        "config": IdeationConfig(),
        "llm_client": llm_client,
    },
)
```

## Exemplo Completo: Usando Framework Formal Opcionalmente

O framework pode ser usado **opcionalmente** sem alterar o código existente:

```python
# Opção 1: Usar código existente (como sempre)
from src.orchestrator import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.run_full_pipeline(article_path)

# Opção 2: Usar framework formal (novo, opcional)
from src.core.orchestrator_formal import FormalOrchestrator
from src.core.agent import (
    create_ideation_agent,
    create_selection_agent,
    create_coherence_agent,
)
from src.phases.phase1_ideation import run as run_phase1
from src.phases.phase2_selection import run as run_phase2
from src.phases.phase3_coherence import run as run_phase3

formal_orchestrator = FormalOrchestrator()
formal_orchestrator.register_agent(create_ideation_agent(run_phase1))
formal_orchestrator.register_agent(create_selection_agent(run_phase2))
formal_orchestrator.register_agent(create_coherence_agent(run_phase3))

result = formal_orchestrator.orchestrate(
    query="full pipeline",
    initial_data={
        "article_path": article_path,
        "config": IdeationConfig(),
        "llm_client": llm_client,
    },
)
```

## Correspondência com Framework Teórico

| Componente Teórico | Implementação | Arquivo |
|-------------------|---------------|---------|
| Estado Universal Ω | `UniversalState` | `src/core/universal_state.py` |
| Instrução i = ⟨p,θ,φ_in,φ_out,κ⟩ | `Instruction` | `src/core/instruction.py` |
| Estratégia de Memória g = ⟨π,ρ,ω,γ⟩ | `MemoryStrategy` | `src/core/memory_strategies.py` |
| Projeção π: Ω → M_view | `strategy.project()` | `src/core/memory_strategies.py` |
| Agente A = ⟨V,E,λ_V,λ_E,v_0,Σ_A⟩ | `Agent` | `src/core/agent.py` |
| Orquestrador O = ⟨R,π,dispatch,aggregate,Γ⟩ | `FormalOrchestrator` | `src/core/orchestrator_formal.py` |

## Limitações do MVP

- **Grafos simples**: Agentes são wrappers lineares (uma fase = um agente)
- **Agentes fixos**: Sem evolução autônoma (conforme solicitado)
- **Estratégias básicas**: Apenas EpisodicStrategy e HierarchicalStrategy
- **Orquestrador simples**: Seleção rule-based, sem LLM-based selection
- **Pipeline sequencial**: Execução sequencial apenas (sem paralelo)

## Extensões Futuras

O framework foi projetado para evoluir:
- Grafos com arestas condicionais
- Busca semântica por embeddings no histórico
- Composição paralela de agentes
- Auto-seleção de agentes via LLM
- Evolução autônoma (fora do escopo do MVP)

## Testes

Testes unitários estão disponíveis em `tests/`:
- `test_universal_state.py`
- `test_memory_strategies.py`
- `test_agent.py`
- `test_orchestrator_formal.py`

Execute os testes com:
```bash
python -m pytest tests/
```

