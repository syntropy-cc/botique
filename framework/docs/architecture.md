# Arquitetura do Framework

Este documento descreve a arquitetura interna do framework para sistemas de agentes autônomos.

## Visão Geral da Arquitetura

O framework é organizado em camadas:

```
┌─────────────────────────────────────────┐
│         Application Layer                │
│  (Boutique, ou outro projeto)           │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Orchestrator Layer               │
│  (Coordenação de agentes)               │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Agent Layer                     │
│  (Grafos de execução)                   │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│    I     │ │    S      │ │    T     │
│ Pillar   │ │  Pillar  │ │  Pillar  │
└──────────┘ └──────────┘ └──────────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
┌─────────────────────────────────────────┐
│         State Layer                     │
│  (Universal State + Storage)           │
└─────────────────────────────────────────┘
```

## Camadas de Arquitetura

### 1. State Layer (Camada de Estado)

**Componentes:**
- `UniversalState`: Estado universal Ω
- `StorageManager`: Gerenciador unificado de storage
- `StorageBackend`: Interface para backends

**Responsabilidades:**
- Armazenar e recuperar dados
- Gerenciar histórico de execuções
- Prover acesso unificado a diferentes backends

### 2. Pillar Layer (Camada de Pilares)

#### Instruction Pillar (I)

**Componentes:**
- `Instruction`: Instrução formal i = ⟨p, θ, φ_in, φ_out, κ⟩

**Responsabilidades:**
- Encapsular prompts LLM
- Preprocessar dados de entrada
- Pós-processar respostas LLM
- Gerenciar configurações LLM

#### State Management Pillar (S)

**Componentes:**
- `StateManagementStrategy`: Base para estratégias
- `EpisodicStrategy`: Projeção episódica
- `HierarchicalStrategy`: Projeção hierárquica
- `SemanticStrategy`: Projeção semântica

**Responsabilidades:**
- Projetar estado universal em views específicas
- Filtrar e transformar dados de estado
- Gerenciar contexto de execução

#### Tool Pillar (T)

**Componentes:**
- `Tool`: Ferramenta formal t = ⟨sig, f, effects, pre, post⟩

**Responsabilidades:**
- Executar funções determinísticas
- Validar precondições e pós-condições
- Declarar efeitos colaterais

### 3. Agent Layer (Camada de Agentes)

**Componentes:**
- `Agent`: Agente como grafo A = ⟨V, E, λ_V, λ_E, v_0, Σ_A⟩

**Responsabilidades:**
- Coordenar execução através do grafo
- Gerenciar transições entre vértices
- Manter estado local do agente

### 4. Orchestrator Layer (Camada de Orquestração)

**Componentes:**
- `Orchestrator`: Orquestrador O = ⟨R, π, dispatch, aggregate, Γ⟩

**Responsabilidades:**
- Registrar agentes disponíveis
- Selecionar agentes apropriados para queries
- Distribuir tarefas
- Agregar resultados

### 5. Application Layer (Camada de Aplicação)

**Componentes:**
- Projetos específicos (ex: Boutique)
- Orquestradores específicos
- Agentes específicos

**Responsabilidades:**
- Implementar lógica de domínio
- Compor agentes, instruções e tools
- Definir pipelines de execução

## Fluxo de Dados

### Execução de Agente

```
Query → Orchestrator → Agent Selection
                          ↓
                    Agent Execution
                          ↓
                    Instruction/Tool Execution
                          ↓
                    State Update
                          ↓
                    Result Aggregation
                          ↓
                    Response
```

### Acesso a Estado

```
Agent → StateManagementStrategy → Project(Ω)
                                          ↓
                                    StorageManager
                                          ↓
                                    StorageBackend
                                          ↓
                                    Data
```

## Padrões de Design

### Strategy Pattern

Usado em:
- `StateManagementStrategy`: Diferentes estratégias de projeção
- `StorageBackend`: Diferentes backends de armazenamento

### Factory Pattern

Usado em:
- `StorageRegistry`: Criação de backends
- `Agent`: Criação de vértices

### Observer Pattern

Usado em:
- `LLMLogger`: Observação de chamadas LLM
- `Orchestrator`: Observação de execuções

### Template Method Pattern

Usado em:
- `Instruction`: Template de execução de instrução
- `Agent`: Template de execução de agente

## Extensibilidade

### Pontos de Extensão

1. **Novos Backends de Storage**
   - Implementar `StorageBackend`
   - Registrar no `StorageRegistry`

2. **Novas Estratégias de State Management**
   - Estender `StateManagementStrategy`
   - Implementar método `project()`

3. **Novos Tipos de Vértices**
   - Adicionar ao `VertexType` enum
   - Atualizar lógica de execução em `Agent`

4. **Novas Políticas de Seleção**
   - Estender `Orchestrator.select_agents()`
   - Implementar lógica de seleção

## Performance

### Otimizações

- **Cache em UniversalState**: Cache de objetos frequentemente acessados
- **Lazy Loading**: Carregamento sob demanda de dados
- **Batch Operations**: Operações em lote quando possível

### Escalabilidade

- **Stateless Agents**: Agentes podem ser executados em paralelo
- **Distributed Storage**: Backends podem ser distribuídos
- **Async Execution**: Suporte para execução assíncrona (futuro)

## Segurança

### Considerações

- **Validação de Precondições**: Tools validam precondições
- **Validação de Pós-condições**: Tools validam pós-condições
- **Isolamento de Estado**: Cada agente tem estado local isolado
- **Sanitização de Inputs**: Inputs são sanitizados antes do processamento

## Testabilidade

### Estratégias de Teste

- **Unit Tests**: Testes de componentes individuais
- **Integration Tests**: Testes de integração entre componentes
- **Mock Backends**: Backends mock para testes
- **Test Fixtures**: Fixtures para estados de teste

## Referências

- `docs/framework.md`: Especificação formal completa
- `framework/docs/README.md`: Documentação geral
- `framework/docs/examples/`: Exemplos de uso
