# Framework para Sistemas de Agentes Autônomos

Framework reutilizável para criação de sistemas de agentes autônomos baseado em especificação formal.

## Visão Geral

Este framework implementa um sistema de agentes autônomos baseado em grafos direcionados sobre três pilares fundamentais:

1. **Instructions (I)**: Instruções formais que encapsulam prompts LLM
2. **State Management (S)**: Estratégias de gerenciamento e projeção de estado
3. **Tools (T)**: Ferramentas executáveis determinísticas

## Componentes Principais

### Core (`framework/core/`)

- **`agent.py`**: Agente como grafo direcionado A = ⟨V, E, λ_V, λ_E, v_0, Σ_A⟩
- **`instruction.py`**: Instrução formal i = ⟨p, θ, φ_in, φ_out, κ⟩
- **`state_management.py`**: Estratégias de gerenciamento de estado s = ⟨π, ρ, ω, γ⟩
- **`tool.py`**: Ferramenta formal t = ⟨sig, f, effects, pre, post⟩
- **`universal_state.py`**: Estado universal Ω que engloba todos os componentes
- **`orchestrator.py`**: Orquestrador O = ⟨R, π, dispatch, aggregate, Γ⟩

### LLM (`framework/llm/`)

- **`client.py`**: Interface abstrata para clientes LLM
- **`http_client.py`**: Implementação HTTP de cliente LLM
- **`logger.py`**: Sistema de logging de chamadas LLM
- **`pricing.py`**: Cálculo de custos de chamadas LLM
- **`queries.py`**: Consultas ao histórico de execuções
- **`prompt_helpers.py`**: Helpers para registro e recuperação de prompts

### Storage (`framework/storage/`)

- **`base.py`**: Interface `StorageBackend` para backends de armazenamento
- **`manager.py`**: `StorageManager` unificado que roteia operações
- **`registry.py`**: Registry de backends disponíveis
- **`adapters/`**: Implementações específicas:
  - `sqlite_adapter.py`: Para histórico, eventos, prompts
  - `json_adapter.py`: Para objetos complexos serializáveis
  - `memory_adapter.py`: Para classes Python em memória
  - `hybrid_adapter.py`: Para múltiplos backends

## Conceitos Fundamentais

### Agente

Um agente A é um grafo direcionado onde:
- Vértices (V) são elementos dos três pilares (I, S, T)
- Arestas (E) definem transições entre vértices
- Execução segue caminhos probabilísticos através do grafo

### Estado Universal

O estado universal Ω engloba:
- M^(t): Memória contextual (objetos armazenados)
- H^(t): Histórico de execuções (traces/eventos)
- I^(t): Instruções (prompts) disponíveis
- Outros componentes do sistema

### Projeção de Estado

Estratégias de state management implementam funções de projeção π:
- `EpisodicStrategy`: Foco em entidade atual
- `HierarchicalStrategy`: Todas as entidades do contexto atual
- `SemanticStrategy`: Traces históricos por similaridade

### Orquestração

O orquestrador coordena execução de múltiplos agentes:
- Registry (R): Mapeia agentes a descrições de capacidade
- Selection Policy (π): Determina quais agentes lidam com queries
- Dispatch: Distribui tarefas para agentes
- Aggregate: Combina resultados de múltiplos agentes

## Uso Básico

### Criar um Agente

```python
from framework.core.agent import Agent, VertexType
from framework.core.instruction import Instruction
from framework.core.tool import Tool

# Criar instrução
instruction = Instruction(
    prompt_key="my_instruction",
    prompt_template="...",
    model="deepseek-chat",
)

# Criar tool
def my_function(input_data):
    return {"result": "processed"}

tool = Tool(
    sig=("input", "output"),
    f=my_function,
    name="my_tool",
)

# Criar agente
agent = Agent(
    name="my_agent",
    entry_vertex="instruction",
    vertices={
        "instruction": VertexType.INSTRUCTION,
        "tool": VertexType.TOOL,
    },
    edges=[("instruction", "tool", "data")],
    vertex_objects={
        "instruction": instruction,
        "tool": tool,
    },
)
```

### Executar Agente

```python
from framework.core.universal_state import UniversalState

state = UniversalState()
result = agent.execute(
    input_data={"input": "data"},
    state=state,
)
```

### Usar Storage

```python
from framework.storage.manager import StorageManager

storage = StorageManager()

# Armazenar
storage.store("brief", "post_001", {"content": "..."})

# Recuperar
brief = storage.retrieve("brief", "post_001")

# Query
briefs = storage.query("brief", {"post_id": "post_001"})
```

## Extensibilidade

### Criar Nova Estratégia de State Management

```python
from framework.core.state_management import StateManagementStrategy

class MyStrategy(StateManagementStrategy):
    def project(self, state, context=None):
        # Implementar lógica de projeção
        return view
```

### Criar Novo Backend de Storage

```python
from framework.storage.base import StorageBackend

class MyBackend(StorageBackend):
    def store(self, key, value, metadata=None):
        # Implementar armazenamento
        return key
    
    def retrieve(self, key):
        # Implementar recuperação
        return value
    
    def query(self, query):
        # Implementar query
        return results
    
    def delete(self, key):
        # Implementar deleção
        return True
```

## Referências

- `docs/framework.md`: Especificação formal completa
- `framework/docs/architecture.md`: Arquitetura detalhada
- `framework/docs/examples/`: Exemplos de uso
