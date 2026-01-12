# State Management Architecture

## Framework de Agentes Autônomos — Especificação do Gerenciador de Estado

---

## 1. Visão Geral

Este documento especifica a arquitetura de gerenciamento de estado para o framework de agentes autônomos. O State Manager é o componente central responsável por:

1. **Persistir e recuperar** o estado universal $\Omega$
2. **Abstrair** múltiplos paradigmas de armazenamento sob uma API unificada
3. **Otimizar** operações de acesso conforme a natureza dos dados
4. **Habilitar** projeções de memória $\pi$ eficientes para agentes
5. **Suportar** versionamento temporal e rollback do estado

O design é **agnóstico ao domínio** — aplicações específicas (marketing, atendimento, análise de dados, etc.) estendem o framework com suas próprias entidades e fluxos.

---

## 2. Arquitetura em Camadas

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UNIFIED API LAYER                                  │
│                                                                             │
│   StateManager                                                              │
│   ├── get(key) → Any                                                        │
│   ├── set(key, value) → bool                                                │
│   ├── delete(key) → bool                                                    │
│   ├── query(key, filters) → List[Any]                                       │
│   ├── search(collection, query, limit) → List[Any]    # Semantic           │
│   ├── traverse(node, relation, depth) → List[Any]     # Graph              │
│   ├── project(strategy, query) → Dict[str, Any]       # Memory projection  │
│   ├── snapshot(trigger) → str                         # Temporal version   │
│   └── restore(snapshot_id) → bool                     # Rollback           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INGESTION LAYER                                    │
│                                                                             │
│  Responsável por transformar dados de fontes externas em entidades          │
│  persistidas na camada operacional.                                         │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Filesystem │  │    API      │  │   Stream    │  │   Custom    │        │
│  │   Adapter   │  │   Adapter   │  │   Adapter   │  │   Adapter   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         └────────────────┴────────────────┴────────────────┘                │
│                                   │                                         │
│                                   ▼                                         │
│                    ┌──────────────────────────────┐                         │
│                    │     Ingestion Pipeline       │                         │
│                    │  ┌────────────────────────┐  │                         │
│                    │  │ Parse → Validate →     │  │                         │
│                    │  │ Transform → Embed →    │  │                         │
│                    │  │ Route → Persist        │  │                         │
│                    │  └────────────────────────┘  │                         │
│                    └──────────────────────────────┘                         │
│                                                                             │
│  O filesystem NÃO é um backend operacional — é apenas uma fonte de          │
│  ingestão. Dados são processados e persistidos em backends estruturados.    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OPERATIONAL LAYER                                   │
│                                                                             │
│  Backends especializados por paradigma de dados:                            │
│                                                                             │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │  Vector   │  │   Graph   │  │    SQL    │  │   Cache   │               │
│  │    DB     │  │    DB     │  │    DB     │  │           │               │
│  │           │  │           │  │           │  │           │               │
│  │ Semantic  │  │ Relations │  │ Transac-  │  │ Volatile  │               │
│  │ Search    │  │ Traversal │  │ tional    │  │ State     │               │
│  │           │  │           │  │ ACID      │  │           │               │
│  │ Qdrant    │  │ Neo4j     │  │ Postgres  │  │ Redis     │               │
│  │ ChromaDB  │  │ ArangoDB  │  │ SQLite    │  │ Memory    │               │
│  │ Pinecone  │  │ Memgraph  │  │ MySQL     │  │ Memcached │               │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Análise de Paradigmas de Banco de Dados

### 3.1 Paradigmas Considerados

| Paradigma | Exemplos | Força Principal | Caso de Uso no Framework |
|-----------|----------|-----------------|--------------------------|
| **Relacional (SQL)** | PostgreSQL, SQLite | ACID, queries complexas | Metadados, histórico, auditoria |
| **Graph Database** | Neo4j, ArangoDB | Relações e travessias | Agentes (grafos), execuções |
| **Vector Database** | Qdrant, ChromaDB | Similaridade semântica | Busca em memória $\mathcal{M}$ |
| **Key-Value / Cache** | Redis, Memcached | Velocidade | Estado volátil $\mathcal{O}$ |
| **Document Store** | MongoDB | Flexibilidade de schema | Alternativa ao SQL+JSONB |
| **Object Database** | ZODB | Persistência de objetos | Descartado (complexidade) |
| **Time-Series** | InfluxDB | Dados temporais | Métricas (opcional) |

### 3.2 Justificativa para Arquitetura Polyglot

O estado universal $\Omega$ possui componentes com necessidades heterogêneas:

$$\Omega^{(t)} = \langle \mathcal{M}^{(t)}, \mathcal{I}^{(t)}, \mathcal{G}^{(t)}, \mathcal{T}^{(t)}, \mathcal{A}^{(t)}, \mathcal{O}^{(t)}, \mathcal{H}^{(t)}, \Xi^{(t)} \rangle$$

| Componente | Descrição | Natureza | Operações Principais | Backend Ideal |
|------------|-----------|----------|---------------------|---------------|
| $\mathcal{M}^{(t)}$ | Memória agregada | Texto não-estruturado | Busca semântica | **Vector DB** |
| $\mathcal{I}^{(t)}$ | Instruções (prompts) | Estruturado + versionado | CRUD, histórico | **SQL** |
| $\mathcal{G}^{(t)}$ | Estratégias de memória | Configuração | CRUD | **SQL** |
| $\mathcal{T}^{(t)}$ | Ferramentas | Definições | CRUD, lookup | **SQL** |
| $\mathcal{A}^{(t)}$ | Agentes | **Grafos** | Travessia, pathfinding | **Graph DB** |
| $\mathcal{O}^{(t)}$ | Orquestrador | Estado volátil | Read/write rápido | **Cache** |
| $\mathcal{H}^{(t)}$ | Histórico | Append-only | Auditoria, análise | **SQL** |
| $\Xi^{(t)}$ | Ambiente externo | Variável | Adapters | **Depende** |

### 3.3 Por que Graph Database para Agentes

O framework define agentes como **grafos dirigidos**:

$$A = \langle V, E, \lambda_V, \lambda_E, v_0, \Sigma_A \rangle$$

Onde:
- $V \subseteq \mathcal{I} \cup \mathcal{G} \cup \mathcal{T}$ — vértices dos três pilares
- $E \subseteq V \times V$ — arestas dirigidas
- $\lambda_E: E \rightarrow \{\texttt{data}, \texttt{control}, \texttt{conditional}\}$ — tipos de aresta

A **matriz de adjacência tripolar** é uma estrutura de grafo:

$$\mathbf{A} = \begin{pmatrix} \mathbf{A}_{II} & \mathbf{A}_{IG} & \mathbf{A}_{IT} \\ \mathbf{A}_{GI} & \mathbf{A}_{GG} & \mathbf{A}_{GT} \\ \mathbf{A}_{TI} & \mathbf{A}_{TG} & \mathbf{A}_{TT} \end{pmatrix}$$

**Queries naturais em Graph DB:**

```cypher
-- Definição completa de um agente
MATCH (a:Agent {id: $agentId})-[:CONTAINS]->(v:Vertex)
OPTIONAL MATCH (v)-[e:CONNECTS_TO]->(v2:Vertex)
RETURN a, v, e, v2

-- Caminho de execução de uma query
MATCH path = (start:Vertex {id: $entryId})-[:CONNECTS_TO*]->(end:Vertex)
WHERE NOT (end)-[:CONNECTS_TO]->()
RETURN path

-- Agentes que compartilham componentes
MATCH (a1:Agent)-[:CONTAINS]->(v:Vertex)<-[:CONTAINS]-(a2:Agent)
WHERE a1 <> a2
RETURN a1, a2, collect(v) as shared_components

-- Impacto de modificar uma instrução
MATCH (i:Vertex {pillar: 'instruction', reference_id: $promptId})<-[:CONTAINS]-(a:Agent)
RETURN a.name as affected_agents
```

**Comparativo SQL vs Graph:**

| Query | SQL | Graph DB |
|-------|-----|----------|
| Travessia de profundidade N | Recursive CTE (complexo) | `[:REL*1..N]` (nativo) |
| Caminho mais curto | Algoritmo manual | `shortestPath()` |
| Todos os caminhos | Exponencialmente complexo | `allShortestPaths()` |
| Subgrafo de um agente | Múltiplos JOINs | Single MATCH |

### 3.4 Por que Vector Database para Memória

A projeção semântica $\pi_{\text{semantic}}$ é fundamental:

$$\pi_{\text{semantic}}(\Omega^{(t)}, q) = \text{top}_k\{m \in \mathcal{M}^{(t)} : \text{sim}(\text{embed}(m), \text{embed}(q)) > \epsilon\}$$

**Casos de uso:**
- Recuperar contexto relevante para prompts
- Few-shot learning de execuções passadas similares
- Buscar instruções por conceito, não palavras-chave

**Capacidades únicas:**

```python
# Busca que SQL não consegue fazer eficientemente
results = vector_db.search(
    collection="memory",
    query_embedding=embed("como lidar com erros de timeout"),
    n_results=5,
    filters={"agent_name": "error_handler"}  # Filtro híbrido
)
```

### 3.5 Por que SQL para Dados Transacionais

- **ACID**: Garantias de consistência para operações críticas
- **Integridade referencial**: Foreign keys entre entidades
- **Queries complexas**: Agregações, window functions, CTEs
- **Maturidade**: Ferramentas de backup, monitoramento, migração
- **Auditoria**: Histórico imutável com timestamps

### 3.6 Por que Cache para Estado Volátil

O estado do orquestrador $\mathcal{O}^{(t)}$ muda frequentemente:
- Sessões de agentes em execução
- Cache de projeções $\pi$ computadas
- Locks e semáforos distribuídos
- Estado de workflows em andamento

Requisitos: **latência < 1ms**, sem necessidade de durabilidade.

---

## 4. Mapeamento de Componentes para Backends

### 4.1 Tabela de Roteamento

| Namespace | Collection | Backend Primário | Secundário | Cache | Justificativa |
|-----------|------------|------------------|------------|-------|---------------|
| `M` | `documents` | Vector | SQL | — | Busca semântica + metadados |
| `M` | `embeddings` | Vector | — | Redis | Embeddings computados |
| `I` | `instructions` | SQL | Vector | Redis | Versionamento + busca |
| `G` | `strategies` | SQL | — | — | Configurações |
| `T` | `tools` | SQL | — | Redis | Definições + hot cache |
| `A` | `agents` | Graph | SQL | Redis | Grafo + backup + hot cache |
| `A` | `executions` | Graph | SQL | — | Travessia + log |
| `A` | `sessions` | Cache | — | — | Volátil |
| `O` | `state` | Cache | — | — | Volátil |
| `O` | `locks` | Cache | — | — | Distribuído |
| `H` | `traces` | SQL | — | — | Append-only |
| `H` | `events` | SQL | — | — | Append-only |
| `H` | `snapshots` | SQL | — | — | Versionamento |

### 4.2 Fluxo de Sincronização

```
                    ┌─────────────┐
                    │ StateManager│
                    │   set()     │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │ Primary │  │Secondary│  │  Cache  │
        │ Backend │  │ Backend │  │ Backend │
        └─────────┘  └─────────┘  └─────────┘
              │            │            │
              │            │            ▼
              │            │      ┌─────────┐
              │            │      │   TTL   │
              │            │      │ Expiry  │
              │            │      └─────────┘
              ▼            ▼
        ┌─────────────────────┐
        │  Consistency Check  │
        │   (async/eventual)  │
        └─────────────────────┘
```

---

## 5. Schema por Backend

### 5.1 Graph Database Schema (Neo4j/ArangoDB)

```cypher
// ============================================
// CONSTRAINTS E ÍNDICES
// ============================================

CREATE CONSTRAINT agent_id IF NOT EXISTS 
FOR (a:Agent) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT vertex_id IF NOT EXISTS 
FOR (v:Vertex) REQUIRE v.id IS UNIQUE;

CREATE CONSTRAINT execution_id IF NOT EXISTS 
FOR (e:Execution) REQUIRE e.id IS UNIQUE;

CREATE INDEX vertex_pillar IF NOT EXISTS 
FOR (v:Vertex) ON (v.pillar);

CREATE INDEX vertex_reference IF NOT EXISTS 
FOR (v:Vertex) ON (v.reference_id);

// ============================================
// SCHEMA DE AGENTES
// ============================================

// Nó: Agent
// Representa um agente A = ⟨V, E, λ_V, λ_E, v_0, Σ_A⟩
(:Agent {
    id: String,              // UUID
    name: String,            // Nome único
    version: Integer,        // Versão do agente
    description: String,     // Descrição opcional
    is_active: Boolean,      // Se está ativo
    created_at: DateTime,
    updated_at: DateTime
})

// Nó: Vertex
// Representa um vértice v ∈ V do grafo do agente
(:Vertex {
    id: String,              // UUID
    pillar: String,          // 'instruction' | 'memory_mgmt' | 'tool'
    reference_id: String,    // FK para entidade no SQL
    config: Map,             // Configurações específicas do vértice
    created_at: DateTime
})

// Relação: CONTAINS
// Associa agente aos seus vértices
(a:Agent)-[:CONTAINS]->(v:Vertex)

// Relação: ENTRY_POINT
// Define o vértice de entrada v_0
(a:Agent)-[:ENTRY_POINT]->(v:Vertex)

// Relação: CONNECTS_TO
// Representa arestas E com labels λ_E
(v1:Vertex)-[:CONNECTS_TO {
    label: String,           // 'data' | 'control' | 'conditional'
    condition: String,       // Expressão para conditional (opcional)
    priority: Integer        // Para ordenação de avaliação
}]->(v2:Vertex)

// ============================================
// SCHEMA DE EXECUÇÃO
// ============================================

// Nó: Execution
// Representa uma execução completa de um agente
(:Execution {
    id: String,              // UUID
    trace_id: String,        // Referência ao trace no SQL
    agent_version: Integer,  // Versão do agente no momento
    input_hash: String,      // Hash do input para deduplicação
    started_at: DateTime,
    completed_at: DateTime,
    status: String,          // 'running' | 'completed' | 'failed'
    error_message: String    // Se failed
})

// Nó: ExecutionStep
// Representa um passo da execução (visita a um vértice)
(:ExecutionStep {
    id: String,
    step_number: Integer,
    input_data: String,      // JSON serializado
    output_data: String,     // JSON serializado
    duration_ms: Float,
    status: String
})

// Relações de execução
(e:Execution)-[:OF_AGENT]->(a:Agent)
(e:Execution)-[:USED_VERSION {version: Integer}]->(a:Agent)
(e:Execution)-[:HAS_STEP]->(s:ExecutionStep)
(s:ExecutionStep)-[:VISITED]->(v:Vertex)
(s:ExecutionStep)-[:NEXT]->(s2:ExecutionStep)
(s:ExecutionStep)-[:BRANCHED_TO]->(s2:ExecutionStep)  // Para parallel

// ============================================
// SCHEMA DE COMPOSIÇÃO
// ============================================

// Relação: COMPOSES
// Para agentes hierárquicos (um agente contém outro)
(parent:Agent)-[:COMPOSES {
    vertex_id: String,       // Vértice onde o sub-agente é invocado
    mapping: Map             // Mapeamento de inputs/outputs
}]->(child:Agent)

// Relação: DEPENDS_ON
// Dependências entre agentes
(a1:Agent)-[:DEPENDS_ON {
    type: String             // 'sequential' | 'parallel' | 'conditional'
}]->(a2:Agent)
```

### 5.2 Vector Database Schema (Qdrant/ChromaDB)

```python
# ============================================
# COLLECTIONS
# ============================================

# Collection: memory
# Armazena conteúdo da memória M para busca semântica
{
    "name": "memory",
    "vectors": {
        "size": 1536,          # Dimensão do embedding (modelo-dependente)
        "distance": "Cosine"   # Ou "Euclid", "Dot"
    },
    "payload_schema": {
        # Identificação
        "id": {"type": "keyword"},
        "source_id": {"type": "keyword"},      # FK para SQL
        "type": {"type": "keyword"},           # Tipo de documento
        
        # Metadados para filtering
        "namespace": {"type": "keyword"},
        "collection": {"type": "keyword"},
        "created_at": {"type": "datetime"},
        "updated_at": {"type": "datetime"},
        
        # Campos customizáveis por aplicação
        "tags": {"type": "keyword[]"},
        "metadata": {"type": "object"}         # JSONB-like
    },
    "optimizers_config": {
        "indexing_threshold": 20000
    }
}

# Collection: instructions
# Embeddings de instruções para busca por conceito
{
    "name": "instructions",
    "vectors": {
        "size": 1536,
        "distance": "Cosine"
    },
    "payload_schema": {
        "id": {"type": "keyword"},
        "instruction_key": {"type": "keyword"},
        "version": {"type": "integer"},
        "description": {"type": "text"},
        "input_schema": {"type": "keyword[]"},   # Campos esperados
        "output_schema": {"type": "keyword[]"}
    }
}

# Collection: executions
# Embeddings de execuções para few-shot retrieval
{
    "name": "executions",
    "vectors": {
        "size": 1536,
        "distance": "Cosine"
    },
    "payload_schema": {
        "id": {"type": "keyword"},
        "trace_id": {"type": "keyword"},
        "agent_name": {"type": "keyword"},
        "success": {"type": "bool"},
        "duration_ms": {"type": "float"},
        "input_summary": {"type": "text"},
        "output_summary": {"type": "text"},
        "created_at": {"type": "datetime"}
    }
}
```

### 5.3 SQL Database Schema (PostgreSQL)

```sql
-- ============================================
-- EXTENSÕES
-- ============================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- TIPOS ENUMERADOS
-- ============================================

CREATE TYPE pillar_type AS ENUM ('instruction', 'memory_mgmt', 'tool');
CREATE TYPE edge_label AS ENUM ('data', 'control', 'conditional');
CREATE TYPE execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
CREATE TYPE event_type AS ENUM ('llm', 'tool', 'step', 'preprocess', 'postprocess', 'system');

-- ============================================
-- INSTRUÇÕES (PILLAR I)
-- ============================================

CREATE TABLE instructions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    instruction_key TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Template e configuração
    template TEXT NOT NULL,
    description TEXT,
    
    -- Configuração LLM (θ)
    model TEXT,
    temperature FLOAT,
    max_tokens INTEGER,
    stop_sequences TEXT[],
    
    -- Schemas de I/O
    input_schema JSONB,
    output_schema JSONB,
    
    -- Requisitos de memória (κ)
    memory_requirements JSONB,
    
    -- Referências externas
    vector_id TEXT,                    -- ID no Vector DB
    
    -- Métricas
    char_count INTEGER GENERATED ALWAYS AS (length(template)) STORED,
    estimated_tokens INTEGER,
    
    -- Auditoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT,
    
    UNIQUE(instruction_key, version)
);

CREATE INDEX idx_instructions_key ON instructions(instruction_key);
CREATE INDEX idx_instructions_version ON instructions(instruction_key, version DESC);

-- ============================================
-- ESTRATÉGIAS DE MEMÓRIA (PILLAR G)
-- ============================================

CREATE TABLE memory_strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    strategy_type TEXT NOT NULL,       -- 'episodic', 'semantic', 'hierarchical', 'hybrid'
    
    -- Configuração da estratégia
    config JSONB NOT NULL DEFAULT '{}',
    
    -- Descrição
    description TEXT,
    
    -- Cache settings
    cache_ttl INTEGER DEFAULT 300,     -- TTL em segundos
    
    -- Auditoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- FERRAMENTAS (PILLAR T)
-- ============================================

CREATE TABLE tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    
    -- Localização da função
    module_path TEXT NOT NULL,         -- e.g., 'myapp.tools.search'
    function_name TEXT NOT NULL,       -- e.g., 'execute_search'
    
    -- Schemas
    input_schema JSONB NOT NULL,
    output_schema JSONB,
    
    -- Características
    is_deterministic BOOLEAN DEFAULT true,
    has_side_effects BOOLEAN DEFAULT false,
    side_effect_types TEXT[],          -- ['network', 'filesystem', 'database', 'external_api']
    
    -- Limites
    timeout_ms INTEGER DEFAULT 30000,
    max_retries INTEGER DEFAULT 3,
    
    -- Auditoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- AGENTES (BACKUP DO GRAPH DB)
-- ============================================

CREATE TABLE agents (
    id UUID PRIMARY KEY,               -- Mesmo ID do Graph DB
    name TEXT NOT NULL UNIQUE,
    version INTEGER NOT NULL DEFAULT 1,
    description TEXT,
    
    -- Snapshot da definição (para sync/backup)
    graph_definition JSONB,            -- {vertices: [...], edges: [...]}
    
    -- Configuração
    config JSONB DEFAULT '{}',
    
    -- Estado
    is_active BOOLEAN DEFAULT true,
    
    -- Auditoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT
);

CREATE INDEX idx_agents_name ON agents(name);
CREATE INDEX idx_agents_active ON agents(is_active) WHERE is_active = true;

-- ============================================
-- TRACES E EVENTOS (HISTÓRICO H)
-- ============================================

CREATE TABLE traces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificação
    name TEXT,
    agent_id UUID REFERENCES agents(id),
    agent_version INTEGER,
    
    -- Contexto
    user_id TEXT,
    tenant_id TEXT,
    session_id TEXT,
    correlation_id TEXT,               -- Para rastreamento distribuído
    
    -- Tags e metadados
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    
    -- Input/Output
    input_data JSONB,
    output_data JSONB,
    
    -- Métricas agregadas
    tokens_input_total INTEGER DEFAULT 0,
    tokens_output_total INTEGER DEFAULT 0,
    cost_total NUMERIC(12, 6) DEFAULT 0,
    duration_ms FLOAT,
    
    -- Status
    status execution_status DEFAULT 'pending',
    error_message TEXT,
    error_stack TEXT,
    
    -- Referências
    state_snapshot_id UUID,            -- Snapshot do estado no início
    graph_execution_id TEXT,           -- ID da execução no Graph DB
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_traces_agent ON traces(agent_id);
CREATE INDEX idx_traces_status ON traces(status);
CREATE INDEX idx_traces_created ON traces(created_at DESC);
CREATE INDEX idx_traces_user ON traces(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_traces_tenant ON traces(tenant_id) WHERE tenant_id IS NOT NULL;
CREATE INDEX idx_traces_correlation ON traces(correlation_id) WHERE correlation_id IS NOT NULL;

CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trace_id UUID NOT NULL REFERENCES traces(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES events(id),
    
    -- Identificação
    type event_type NOT NULL,
    name TEXT NOT NULL,
    
    -- Dados
    input_data JSONB,
    output_data JSONB,
    
    -- Para eventos LLM
    model TEXT,
    tokens_input INTEGER,
    tokens_output INTEGER,
    cost NUMERIC(10, 6),
    
    -- Métricas
    duration_ms FLOAT,
    
    -- Status
    status TEXT DEFAULT 'success',     -- 'success', 'error', 'skipped'
    error_message TEXT,
    
    -- Referências
    instruction_id UUID REFERENCES instructions(id),
    tool_id UUID REFERENCES tools(id),
    vertex_id TEXT,                    -- ID do vértice no Graph DB
    step_number INTEGER,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_events_trace ON events(trace_id);
CREATE INDEX idx_events_parent ON events(parent_id) WHERE parent_id IS NOT NULL;
CREATE INDEX idx_events_type ON events(type);
CREATE INDEX idx_events_created ON events(created_at DESC);

-- ============================================
-- SNAPSHOTS DE ESTADO
-- ============================================

CREATE TABLE state_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Timestamp do snapshot
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Hash para deduplicação
    state_hash TEXT NOT NULL,
    
    -- Snapshot incremental (delta)
    parent_snapshot_id UUID REFERENCES state_snapshots(id),
    is_full_snapshot BOOLEAN DEFAULT true,
    
    -- Componentes serializados
    components JSONB NOT NULL,         -- {M, I, G, T, A, O}
    
    -- Metadados
    trigger TEXT NOT NULL,             -- 'manual', 'auto', 'pre_evolution', 'scheduled'
    description TEXT,
    
    -- Tamanho
    size_bytes INTEGER,
    
    -- Auditoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT,
    
    -- Expiração
    expires_at TIMESTAMPTZ             -- Para auto-cleanup
);

CREATE INDEX idx_snapshots_timestamp ON state_snapshots(timestamp DESC);
CREATE INDEX idx_snapshots_hash ON state_snapshots(state_hash);
CREATE INDEX idx_snapshots_parent ON state_snapshots(parent_snapshot_id) 
    WHERE parent_snapshot_id IS NOT NULL;

-- ============================================
-- TABELA DE METADADOS DO DOMÍNIO
-- ============================================

-- Tabela genérica para entidades de domínio
-- Aplicações específicas podem criar tabelas próprias ou usar esta
CREATE TABLE domain_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL,         -- Tipo definido pela aplicação
    entity_key TEXT,                   -- Chave natural opcional
    
    -- Dados
    data JSONB NOT NULL,
    
    -- Referências externas
    vector_id TEXT,                    -- ID no Vector DB
    graph_node_id TEXT,                -- ID no Graph DB
    
    -- Auditoria
    checksum TEXT,                     -- SHA256 para detectar mudanças
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(entity_type, entity_key)
);

CREATE INDEX idx_domain_entities_type ON domain_entities(entity_type);
CREATE INDEX idx_domain_entities_key ON domain_entities(entity_type, entity_key);

-- ============================================
-- CONFIGURAÇÃO DO SISTEMA
-- ============================================

CREATE TABLE system_config (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT
);

-- ============================================
-- TRIGGERS
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER memory_strategies_updated_at
    BEFORE UPDATE ON memory_strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tools_updated_at
    BEFORE UPDATE ON tools
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER domain_entities_updated_at
    BEFORE UPDATE ON domain_entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- FUNÇÕES UTILITÁRIAS
-- ============================================

-- Função para calcular custo total de um trace
CREATE OR REPLACE FUNCTION calculate_trace_cost(p_trace_id UUID)
RETURNS NUMERIC AS $$
    SELECT COALESCE(SUM(cost), 0)
    FROM events
    WHERE trace_id = p_trace_id AND cost IS NOT NULL;
$$ LANGUAGE SQL STABLE;

-- Função para contar tokens totais de um trace
CREATE OR REPLACE FUNCTION calculate_trace_tokens(p_trace_id UUID)
RETURNS TABLE(input_total INTEGER, output_total INTEGER) AS $$
    SELECT 
        COALESCE(SUM(tokens_input), 0)::INTEGER,
        COALESCE(SUM(tokens_output), 0)::INTEGER
    FROM events
    WHERE trace_id = p_trace_id;
$$ LANGUAGE SQL STABLE;
```

### 5.4 Cache Schema (Redis)

```python
# ============================================
# ESTRUTURAS DE CACHE
# ============================================

# Formato das chaves: {namespace}:{collection}:{id}

# ----- ESTADO DO ORQUESTRADOR -----

# Estado global do orquestrador
"O:state:global" = {
    "active_executions": ["exec_id_1", "exec_id_2"],
    "pending_tasks": [],
    "last_activity": "2024-01-15T12:00:00Z",
    "healthy": true
}
# TTL: None (persistente enquanto sistema ativo)

# Locks distribuídos
"O:locks:{resource_id}" = {
    "holder": "worker_id",
    "acquired_at": "2024-01-15T12:00:00Z",
    "expires_at": "2024-01-15T12:05:00Z"
}
# TTL: Configurável (default 300s)

# ----- SESSÕES DE AGENTES -----

# Sessão de execução de um agente
"A:sessions:{agent_id}:{session_id}" = {
    "current_vertex": "vertex_uuid",
    "visited_vertices": ["v0", "v1", "v2"],
    "accumulated_data": {...},
    "local_state": {...},              # Σ_A
    "started_at": "2024-01-15T12:00:00Z"
}
# TTL: 1800 (30 min)

# ----- CACHE DE PROJEÇÕES π -----

# Resultado de projeção de memória
"cache:projections:{strategy_type}:{params_hash}" = {
    "result": {...},
    "computed_at": "2024-01-15T12:00:00Z",
    "hit_count": 42
}
# TTL: Definido pela estratégia (default 300s)

# ----- CACHE DE EMBEDDINGS -----

# Embedding computado (evita recomputação)
"cache:embeddings:{content_hash}" = [0.1, 0.2, ...]
# TTL: 86400 (24h)

# ----- HOT CACHE DE ENTIDADES -----

# Agente frequentemente acessado
"cache:agents:{agent_id}" = {
    "definition": {...},
    "version": 3,
    "cached_at": "..."
}
# TTL: 3600 (1h)

# Instrução frequentemente usada
"cache:instructions:{instruction_key}:latest" = {
    "id": "uuid",
    "version": 5,
    "template": "...",
    "config": {...}
}
# TTL: 600 (10 min)

# Ferramenta
"cache:tools:{tool_name}" = {
    "id": "uuid",
    "module_path": "...",
    "function_name": "...",
    "input_schema": {...}
}
# TTL: 3600 (1h)

# ----- RATE LIMITING -----

# Contador de rate limit por recurso
"ratelimit:{resource}:{window}" = count
# TTL: Duração da janela

# ----- MÉTRICAS EM TEMPO REAL -----

# Contadores de execução (para dashboards)
"metrics:executions:total" = count
"metrics:executions:success" = count
"metrics:executions:failed" = count
"metrics:tokens:input" = count
"metrics:tokens:output" = count
"metrics:cost:total" = float
# TTL: None (ou reset periódico)
```

---

## 6. Implementação do StateManager

### 6.1 Interface Principal

```python
"""
State Manager - Interface unificada para gerenciamento de estado.

Este módulo implementa o gerenciador de estado universal Ω do framework,
coordenando múltiplos backends de armazenamento sob uma API unificada.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Union
from dataclasses import dataclass, field
import asyncio
import hashlib
import json
import uuid
from datetime import datetime

T = TypeVar('T')


class Backend(Enum):
    """Backends de armazenamento disponíveis."""
    VECTOR = "vector"    # Qdrant, ChromaDB, Pinecone
    GRAPH = "graph"      # Neo4j, ArangoDB, Memgraph
    SQL = "sql"          # PostgreSQL, SQLite, MySQL
    CACHE = "cache"      # Redis, Memcached, In-memory


@dataclass(frozen=True)
class StateKey:
    """
    Chave unificada para acesso ao estado.
    
    Attributes:
        namespace: Componente do estado universal (M, I, G, T, A, O, H)
        collection: Subcoleção dentro do namespace
        id: Identificador único opcional do item
    """
    namespace: str
    collection: str
    id: Optional[str] = None
    
    def __str__(self) -> str:
        if self.id:
            return f"{self.namespace}:{self.collection}:{self.id}"
        return f"{self.namespace}:{self.collection}"
    
    @classmethod
    def from_string(cls, key_str: str) -> 'StateKey':
        parts = key_str.split(":")
        if len(parts) == 3:
            return cls(namespace=parts[0], collection=parts[1], id=parts[2])
        elif len(parts) == 2:
            return cls(namespace=parts[0], collection=parts[1])
        raise ValueError(f"Invalid key format: {key_str}")


@dataclass
class RoutingConfig:
    """Configuração de roteamento para uma collection."""
    primary: Backend
    secondary: List[Backend] = field(default_factory=list)
    cache: Optional[Backend] = None
    cache_ttl: int = 300  # segundos


class BackendAdapter(ABC):
    """Interface abstrata para adaptadores de backend."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Estabelece conexão com o backend."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Encerra conexão com o backend."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Verifica saúde do backend."""
        pass
    
    @abstractmethod
    async def get(self, key: StateKey) -> Optional[Any]:
        """Recupera item por chave."""
        pass
    
    @abstractmethod
    async def set(self, key: StateKey, value: Any, **kwargs) -> bool:
        """Armazena item."""
        pass
    
    @abstractmethod
    async def delete(self, key: StateKey) -> bool:
        """Remove item."""
        pass
    
    @abstractmethod
    async def exists(self, key: StateKey) -> bool:
        """Verifica existência."""
        pass
    
    @abstractmethod
    async def query(
        self, 
        key: StateKey, 
        filters: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[Any]:
        """Consulta com filtros."""
        pass


class VectorBackendAdapter(BackendAdapter):
    """Extensão para backends vetoriais."""
    
    @abstractmethod
    async def search(
        self,
        collection: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Busca por similaridade vetorial."""
        pass
    
    @abstractmethod
    async def upsert_vectors(
        self,
        collection: str,
        vectors: List[Dict[str, Any]]
    ) -> bool:
        """Insere ou atualiza vetores em batch."""
        pass


class GraphBackendAdapter(BackendAdapter):
    """Extensão para backends de grafo."""
    
    @abstractmethod
    async def traverse(
        self,
        start_node: str,
        relationship: str,
        direction: str = "outgoing",
        depth: int = 1,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Travessia de grafo."""
        pass
    
    @abstractmethod
    async def shortest_path(
        self,
        start_node: str,
        end_node: str,
        relationship_types: Optional[List[str]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Encontra caminho mais curto."""
        pass
    
    @abstractmethod
    async def execute_query(
        self, 
        query: str, 
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Executa query nativa (Cypher, AQL, etc.)."""
        pass
    
    @abstractmethod
    async def create_node(
        self,
        labels: List[str],
        properties: Dict[str, Any]
    ) -> str:
        """Cria nó e retorna ID."""
        pass
    
    @abstractmethod
    async def create_relationship(
        self,
        from_node: str,
        to_node: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """Cria relacionamento e retorna ID."""
        pass


class CacheBackendAdapter(BackendAdapter):
    """Extensão para backends de cache."""
    
    @abstractmethod
    async def get_with_ttl(
        self, 
        key: StateKey
    ) -> tuple[Optional[Any], Optional[int]]:
        """Retorna valor e TTL restante."""
        pass
    
    @abstractmethod
    async def set_with_ttl(
        self, 
        key: StateKey, 
        value: Any, 
        ttl: int
    ) -> bool:
        """Define valor com TTL."""
        pass
    
    @abstractmethod
    async def increment(
        self, 
        key: StateKey, 
        amount: int = 1
    ) -> int:
        """Incrementa contador atômico."""
        pass
    
    @abstractmethod
    async def acquire_lock(
        self,
        resource: str,
        holder: str,
        ttl: int = 30
    ) -> bool:
        """Adquire lock distribuído."""
        pass
    
    @abstractmethod
    async def release_lock(
        self,
        resource: str,
        holder: str
    ) -> bool:
        """Libera lock distribuído."""
        pass


class StateManager:
    """
    Gerenciador unificado de estado.
    
    Coordena múltiplos backends para implementar o estado universal Ω.
    
    Attributes:
        adapters: Mapeamento de backends para adaptadores
        routing: Configuração de roteamento por namespace:collection
        embedding_fn: Função para gerar embeddings
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        embedding_fn: Optional[callable] = None
    ):
        """
        Inicializa o StateManager.
        
        Args:
            config: Configuração dos backends e roteamento
            embedding_fn: Função async para gerar embeddings
        """
        self.config = config
        self.adapters: Dict[Backend, BackendAdapter] = {}
        self.routing: Dict[str, RoutingConfig] = {}
        self.embedding_fn = embedding_fn
        self._initialized = False
    
    async def initialize(self) -> None:
        """Inicializa conexões com todos os backends."""
        if self._initialized:
            return
        
        await self._init_adapters()
        self._init_routing()
        self._initialized = True
    
    async def shutdown(self) -> None:
        """Encerra conexões com todos os backends."""
        for adapter in self.adapters.values():
            await adapter.disconnect()
        self._initialized = False
    
    def _init_routing(self) -> None:
        """Inicializa tabela de roteamento."""
        default_routing = {
            # Memória M
            "M:documents": RoutingConfig(
                primary=Backend.VECTOR,
                secondary=[Backend.SQL]
            ),
            "M:embeddings": RoutingConfig(
                primary=Backend.VECTOR,
                cache=Backend.CACHE,
                cache_ttl=86400
            ),
            
            # Instruções I
            "I:instructions": RoutingConfig(
                primary=Backend.SQL,
                secondary=[Backend.VECTOR],
                cache=Backend.CACHE,
                cache_ttl=600
            ),
            
            # Estratégias G
            "G:strategies": RoutingConfig(primary=Backend.SQL),
            
            # Ferramentas T
            "T:tools": RoutingConfig(
                primary=Backend.SQL,
                cache=Backend.CACHE,
                cache_ttl=3600
            ),
            
            # Agentes A
            "A:agents": RoutingConfig(
                primary=Backend.GRAPH,
                secondary=[Backend.SQL],
                cache=Backend.CACHE,
                cache_ttl=3600
            ),
            "A:executions": RoutingConfig(
                primary=Backend.GRAPH,
                secondary=[Backend.SQL]
            ),
            "A:sessions": RoutingConfig(
                primary=Backend.CACHE,
                cache_ttl=1800
            ),
            
            # Orquestrador O
            "O:state": RoutingConfig(primary=Backend.CACHE),
            "O:locks": RoutingConfig(primary=Backend.CACHE),
            
            # Histórico H
            "H:traces": RoutingConfig(primary=Backend.SQL),
            "H:events": RoutingConfig(primary=Backend.SQL),
            "H:snapshots": RoutingConfig(primary=Backend.SQL),
        }
        
        # Merge com config customizada
        custom_routing = self.config.get("routing", {})
        self.routing = {**default_routing, **custom_routing}
    
    def _get_routing(self, key: StateKey) -> RoutingConfig:
        """Obtém configuração de roteamento para uma chave."""
        route_key = f"{key.namespace}:{key.collection}"
        return self.routing.get(
            route_key, 
            RoutingConfig(primary=Backend.SQL)
        )
    
    async def get(self, key: StateKey) -> Optional[Any]:
        """
        Recupera item do estado.
        
        Ordem de busca: Cache → Primary Backend
        
        Args:
            key: Chave do item
            
        Returns:
            Item encontrado ou None
        """
        routing = self._get_routing(key)
        
        # Tenta cache primeiro
        if routing.cache:
            cached = await self.adapters[routing.cache].get(key)
            if cached is not None:
                return cached
        
        # Backend primário
        result = await self.adapters[routing.primary].get(key)
        
        # Popula cache se encontrou
        if result is not None and routing.cache:
            await self.adapters[routing.cache].set_with_ttl(
                key, result, routing.cache_ttl
            )
        
        return result
    
    async def set(
        self,
        key: StateKey,
        value: Any,
        sync_secondary: bool = True,
        update_cache: bool = True
    ) -> bool:
        """
        Armazena item no estado.
        
        Args:
            key: Chave do item
            value: Valor a armazenar
            sync_secondary: Se deve sincronizar backends secundários
            update_cache: Se deve atualizar cache
            
        Returns:
            True se sucesso
        """
        routing = self._get_routing(key)
        
        # Escreve no primário
        success = await self.adapters[routing.primary].set(key, value)
        if not success:
            return False
        
        # Sincroniza secundários (async, eventual consistency)
        if sync_secondary and routing.secondary:
            tasks = [
                self.adapters[backend].set(
                    key, 
                    self._transform_for_backend(value, backend)
                )
                for backend in routing.secondary
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Atualiza cache
        if update_cache and routing.cache:
            await self.adapters[routing.cache].set_with_ttl(
                key, value, routing.cache_ttl
            )
        
        return True
    
    async def delete(self, key: StateKey) -> bool:
        """Remove item de todos os backends relevantes."""
        routing = self._get_routing(key)
        
        # Remove do primário
        success = await self.adapters[routing.primary].delete(key)
        
        # Remove dos secundários
        for backend in routing.secondary:
            await self.adapters[backend].delete(key)
        
        # Invalida cache
        if routing.cache:
            await self.adapters[routing.cache].delete(key)
        
        return success
    
    async def query(
        self,
        key: StateKey,
        filters: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[Any]:
        """
        Consulta com filtros.
        
        Args:
            key: Namespace e collection
            filters: Filtros a aplicar
            limit: Máximo de resultados
            offset: Deslocamento para paginação
            
        Returns:
            Lista de itens encontrados
        """
        routing = self._get_routing(key)
        return await self.adapters[routing.primary].query(
            key, filters, limit, offset
        )
    
    async def search(
        self,
        collection: str,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca semântica via Vector DB.
        
        Args:
            collection: Nome da collection no Vector DB
            query: Texto da query
            limit: Máximo de resultados
            filters: Filtros adicionais
            score_threshold: Score mínimo de similaridade
            
        Returns:
            Lista de resultados com scores
        """
        if not self.embedding_fn:
            raise ValueError("Embedding function not configured")
        
        # Gera embedding
        query_vector = await self.embedding_fn(query)
        
        # Busca no Vector DB
        adapter = self.adapters.get(Backend.VECTOR)
        if not adapter or not isinstance(adapter, VectorBackendAdapter):
            raise ValueError("Vector backend not configured")
        
        return await adapter.search(
            collection=collection,
            query_vector=query_vector,
            limit=limit,
            filters=filters,
            score_threshold=score_threshold
        )
    
    async def traverse(
        self,
        start_node: str,
        relationship: str,
        depth: int = 1,
        direction: str = "outgoing",
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Travessia de grafo via Graph DB.
        
        Args:
            start_node: ID do nó inicial
            relationship: Tipo de relacionamento a seguir
            depth: Profundidade máxima
            direction: 'outgoing', 'incoming', ou 'both'
            filters: Filtros para nós
            
        Returns:
            Lista de nós encontrados
        """
        adapter = self.adapters.get(Backend.GRAPH)
        if not adapter or not isinstance(adapter, GraphBackendAdapter):
            raise ValueError("Graph backend not configured")
        
        return await adapter.traverse(
            start_node=start_node,
            relationship=relationship,
            direction=direction,
            depth=depth,
            filters=filters
        )
    
    async def project(
        self,
        strategy: 'MemoryStrategy',
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executa projeção π sobre o estado.
        
        π: Ω → M_view
        
        Args:
            strategy: Estratégia de projeção
            query: Query opcional para contexto
            
        Returns:
            Visão projetada da memória
        """
        # Verifica cache de projeção
        cache_key = StateKey(
            namespace="cache",
            collection="projections",
            id=strategy.cache_key(query)
        )
        
        if Backend.CACHE in self.adapters:
            cached = await self.adapters[Backend.CACHE].get(cache_key)
            if cached is not None:
                return cached
        
        # Computa projeção
        projection = await strategy.project(self, query)
        
        # Armazena em cache
        if Backend.CACHE in self.adapters:
            await self.adapters[Backend.CACHE].set_with_ttl(
                cache_key,
                projection,
                strategy.cache_ttl
            )
        
        return projection
    
    async def snapshot(
        self,
        trigger: str = "manual",
        description: Optional[str] = None,
        namespaces: Optional[List[str]] = None
    ) -> str:
        """
        Cria snapshot do estado atual.
        
        Args:
            trigger: Motivo do snapshot
            description: Descrição opcional
            namespaces: Namespaces a incluir (None = todos)
            
        Returns:
            ID do snapshot
        """
        snapshot_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Namespaces a capturar
        target_namespaces = namespaces or ["M", "I", "G", "T", "A"]
        
        # Coleta componentes
        components = {}
        for namespace in target_namespaces:
            components[namespace] = await self._collect_namespace(namespace)
        
        # Calcula hash para deduplicação
        state_hash = hashlib.sha256(
            json.dumps(components, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        # Armazena snapshot
        await self.adapters[Backend.SQL].set(
            StateKey(namespace="H", collection="snapshots", id=snapshot_id),
            {
                "id": snapshot_id,
                "timestamp": timestamp.isoformat(),
                "state_hash": state_hash,
                "components": components,
                "trigger": trigger,
                "description": description,
                "size_bytes": len(json.dumps(components).encode())
            }
        )
        
        return snapshot_id
    
    async def restore(self, snapshot_id: str) -> bool:
        """
        Restaura estado a partir de snapshot.
        
        rollback(t_target) = Ω^(t_target)
        
        Args:
            snapshot_id: ID do snapshot a restaurar
            
        Returns:
            True se sucesso
        """
        snapshot = await self.adapters[Backend.SQL].get(
            StateKey(namespace="H", collection="snapshots", id=snapshot_id)
        )
        
        if not snapshot:
            return False
        
        # Restaura cada namespace
        for namespace, data in snapshot["components"].items():
            await self._restore_namespace(namespace, data)
        
        return True
    
    async def _collect_namespace(self, namespace: str) -> Dict[str, Any]:
        """Coleta todos os dados de um namespace."""
        # Implementação depende do namespace
        # Retorna dict serializável
        pass
    
    async def _restore_namespace(
        self, 
        namespace: str, 
        data: Dict[str, Any]
    ) -> None:
        """Restaura dados de um namespace."""
        # Implementação depende do namespace
        pass
    
    def _transform_for_backend(
        self, 
        value: Any, 
        backend: Backend
    ) -> Any:
        """Transforma valor para formato específico do backend."""
        # Vector DB: extrai texto para embedding
        # Graph DB: extrai estrutura de grafo
        # SQL: serializa para JSONB se necessário
        return value


class MemoryStrategy(ABC):
    """
    Base para estratégias de projeção de memória.
    
    Implementa π: Ω → M_view
    """
    
    cache_ttl: int = 300  # TTL padrão em segundos
    
    @abstractmethod
    async def project(
        self,
        state_manager: StateManager,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executa projeção sobre o estado.
        
        Args:
            state_manager: Gerenciador de estado
            query: Query opcional para contexto
            
        Returns:
            Visão projetada da memória
        """
        pass
    
    def cache_key(self, query: Optional[str] = None) -> str:
        """Gera chave de cache para a projeção."""
        base = f"{self.__class__.__name__}"
        if query:
            query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
            return f"{base}:{query_hash}"
        return base
```

### 6.2 Estratégias de Memória

```python
"""
Estratégias de projeção de memória.

Implementam diferentes padrões de acesso ao estado universal Ω.
"""

class EpisodicStrategy(MemoryStrategy):
    """
    Estratégia episódica: foco temporal.
    
    π_episodic(Ω^(t)) = {m ∈ M^(t) : t - τ_m < Δ_window}
    
    Retorna itens dentro de uma janela temporal.
    """
    
    def __init__(
        self,
        collection: str,
        window_seconds: int = 3600,
        cache_ttl: int = 300
    ):
        self.collection = collection
        self.window_seconds = window_seconds
        self.cache_ttl = cache_ttl
    
    async def project(
        self,
        state_manager: StateManager,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(seconds=self.window_seconds)
        
        results = await state_manager.query(
            StateKey(namespace="M", collection=self.collection),
            filters={"created_at": {"$gte": cutoff.isoformat()}}
        )
        
        return {
            "strategy": "episodic",
            "window_seconds": self.window_seconds,
            "results": results,
            "count": len(results)
        }


class SemanticStrategy(MemoryStrategy):
    """
    Estratégia semântica: foco em similaridade.
    
    π_semantic(Ω^(t), q) = top_k{m ∈ M^(t) : sim(embed(m), embed(q)) > ε}
    
    Retorna itens semanticamente similares à query.
    """
    
    def __init__(
        self,
        collection: str,
        k: int = 5,
        threshold: float = 0.7,
        cache_ttl: int = 600
    ):
        self.collection = collection
        self.k = k
        self.threshold = threshold
        self.cache_ttl = cache_ttl
    
    async def project(
        self,
        state_manager: StateManager,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        if not query:
            raise ValueError("SemanticStrategy requires a query")
        
        results = await state_manager.search(
            collection=self.collection,
            query=query,
            limit=self.k,
            score_threshold=self.threshold
        )
        
        return {
            "strategy": "semantic",
            "query": query,
            "results": results,
            "count": len(results)
        }


class HierarchicalStrategy(MemoryStrategy):
    """
    Estratégia hierárquica: múltiplos níveis de abstração.
    
    π_hierarchical(Ω^(t)) = ⋃_{l=0}^{L} abstract_l(M^(t))
    
    Agrega informação em diferentes níveis.
    """
    
    def __init__(
        self,
        collection: str,
        group_by: str,
        cache_ttl: int = 600
    ):
        self.collection = collection
        self.group_by = group_by
        self.cache_ttl = cache_ttl
    
    async def project(
        self,
        state_manager: StateManager,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        # Busca todos os itens
        all_items = await state_manager.query(
            StateKey(namespace="M", collection=self.collection),
            filters={}
        )
        
        # Agrupa por campo
        groups = {}
        for item in all_items:
            key = item.get(self.group_by, "unknown")
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        
        return {
            "strategy": "hierarchical",
            "group_by": self.group_by,
            "groups": groups,
            "total_count": len(all_items),
            "group_count": len(groups)
        }


class GraphTraversalStrategy(MemoryStrategy):
    """
    Estratégia de travessia: segue relações no grafo.
    
    Útil para contexto baseado em estrutura do agente.
    """
    
    def __init__(
        self,
        start_node: str,
        relationship: str,
        depth: int = 2,
        cache_ttl: int = 600
    ):
        self.start_node = start_node
        self.relationship = relationship
        self.depth = depth
        self.cache_ttl = cache_ttl
    
    async def project(
        self,
        state_manager: StateManager,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        nodes = await state_manager.traverse(
            start_node=self.start_node,
            relationship=self.relationship,
            depth=self.depth
        )
        
        return {
            "strategy": "graph_traversal",
            "start_node": self.start_node,
            "relationship": self.relationship,
            "depth": self.depth,
            "nodes": nodes,
            "count": len(nodes)
        }


class HybridStrategy(MemoryStrategy):
    """
    Estratégia híbrida: combina múltiplas estratégias.
    
    Útil para queries complexas que precisam de múltiplas perspectivas.
    """
    
    def __init__(
        self,
        strategies: List[MemoryStrategy],
        merge_fn: Optional[callable] = None,
        cache_ttl: int = 300
    ):
        self.strategies = strategies
        self.merge_fn = merge_fn or self._default_merge
        self.cache_ttl = cache_ttl
    
    async def project(
        self,
        state_manager: StateManager,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        # Executa todas as estratégias em paralelo
        tasks = [
            strategy.project(state_manager, query)
            for strategy in self.strategies
        ]
        results = await asyncio.gather(*tasks)
        
        # Merge dos resultados
        merged = self.merge_fn(results)
        
        return {
            "strategy": "hybrid",
            "sub_strategies": [s.__class__.__name__ for s in self.strategies],
            "merged_results": merged
        }
    
    def _default_merge(self, results: List[Dict]) -> Dict[str, Any]:
        """Merge padrão: concatena resultados."""
        all_results = []
        for r in results:
            if "results" in r:
                all_results.extend(r["results"])
            elif "nodes" in r:
                all_results.extend(r["nodes"])
        return {"items": all_results, "count": len(all_results)}
```

---

## 7. Camada de Ingestão

```python
"""
Pipeline de ingestão para processar dados de fontes externas.

O filesystem NÃO é um backend operacional - dados são processados
e persistidos em backends estruturados.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import hashlib


class DataSource(ABC):
    """Interface para fontes de dados."""
    
    @abstractmethod
    async def read(self) -> Tuple[bytes, Dict[str, Any]]:
        """
        Lê dados da fonte.
        
        Returns:
            Tupla (conteúdo, metadados)
        """
        pass
    
    @abstractmethod
    def checksum(self) -> str:
        """Retorna checksum do conteúdo."""
        pass


class FileSource(DataSource):
    """Fonte de dados do filesystem."""
    
    def __init__(self, path: Path):
        self.path = path
    
    async def read(self) -> Tuple[bytes, Dict[str, Any]]:
        content = self.path.read_bytes()
        metadata = {
            "source": "filesystem",
            "path": str(self.path),
            "filename": self.path.name,
            "extension": self.path.suffix,
            "size_bytes": len(content)
        }
        return content, metadata
    
    def checksum(self) -> str:
        return hashlib.sha256(self.path.read_bytes()).hexdigest()


class APISource(DataSource):
    """Fonte de dados de API."""
    
    def __init__(self, url: str, headers: Optional[Dict] = None):
        self.url = url
        self.headers = headers or {}
    
    async def read(self) -> Tuple[bytes, Dict[str, Any]]:
        # Implementação com httpx/aiohttp
        pass
    
    def checksum(self) -> str:
        # Hash do conteúdo baixado
        pass


class IngestionPipeline:
    """
    Pipeline de ingestão genérico.
    
    Processa dados de qualquer fonte e persiste nos backends apropriados.
    """
    
    def __init__(
        self,
        state_manager: StateManager,
        parsers: Dict[str, 'Parser'],
        validators: List['Validator']
    ):
        self.state_manager = state_manager
        self.parsers = parsers
        self.validators = validators
    
    async def ingest(
        self,
        source: DataSource,
        entity_type: str,
        namespace: str = "M",
        collection: str = "documents"
    ) -> str:
        """
        Ingere dados de uma fonte.
        
        Args:
            source: Fonte de dados
            entity_type: Tipo da entidade
            namespace: Namespace de destino
            collection: Collection de destino
            
        Returns:
            ID da entidade criada
        """
        # 1. Verifica duplicatas
        checksum = source.checksum()
        existing = await self._find_by_checksum(checksum)
        if existing:
            return existing["id"]
        
        # 2. Lê dados
        content, source_metadata = await source.read()
        
        # 3. Parse
        parser = self.parsers.get(entity_type)
        if not parser:
            raise ValueError(f"No parser for entity type: {entity_type}")
        parsed_data, entity_metadata = await parser.parse(content)
        
        # 4. Validate
        for validator in self.validators:
            await validator.validate(parsed_data, entity_metadata)
        
        # 5. Generate IDs
        entity_id = str(uuid.uuid4())
        vector_id = str(uuid.uuid4())
        
        # 6. Generate embedding (se aplicável)
        embedding = None
        if self.state_manager.embedding_fn and parsed_data.get("text"):
            embedding = await self.state_manager.embedding_fn(
                parsed_data["text"]
            )
        
        # 7. Persist to Vector DB
        if embedding:
            await self.state_manager.adapters[Backend.VECTOR].upsert_vectors(
                collection=collection,
                vectors=[{
                    "id": vector_id,
                    "vector": embedding,
                    "payload": {
                        "type": entity_type,
                        "source_id": entity_id,
                        **entity_metadata
                    }
                }]
            )
        
        # 8. Persist to SQL
        await self.state_manager.set(
            StateKey(namespace=namespace, collection=collection, id=entity_id),
            {
                "id": entity_id,
                "type": entity_type,
                "data": parsed_data,
                "metadata": {**source_metadata, **entity_metadata},
                "vector_id": vector_id if embedding else None,
                "checksum": checksum
            }
        )
        
        # 9. Create Graph node (se aplicável)
        if Backend.GRAPH in self.state_manager.adapters:
            await self.state_manager.adapters[Backend.GRAPH].create_node(
                labels=[entity_type],
                properties={"id": entity_id, **entity_metadata}
            )
        
        return entity_id
    
    async def _find_by_checksum(self, checksum: str) -> Optional[Dict]:
        """Busca entidade por checksum."""
        results = await self.state_manager.query(
            StateKey(namespace="M", collection="documents"),
            filters={"checksum": checksum}
        )
        return results[0] if results else None


class Parser(ABC):
    """Interface para parsers de conteúdo."""
    
    @abstractmethod
    async def parse(
        self, 
        content: bytes
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Parseia conteúdo.
        
        Returns:
            Tupla (dados_parseados, metadados)
        """
        pass


class Validator(ABC):
    """Interface para validadores."""
    
    @abstractmethod
    async def validate(
        self, 
        data: Dict[str, Any], 
        metadata: Dict[str, Any]
    ) -> None:
        """
        Valida dados.
        
        Raises:
            ValidationError se inválido
        """
        pass
```

---

## 8. Configuração e Deploy

### 8.1 Configuração do StateManager

```python
# Exemplo de configuração
config = {
    "backends": {
        "vector": {
            "type": "qdrant",
            "host": "localhost",
            "port": 6333,
            "api_key": None  # Para managed
        },
        "graph": {
            "type": "neo4j",
            "uri": "bolt://localhost:7687",
            "user": "neo4j",
            "password": "password"
        },
        "sql": {
            "type": "postgresql",
            "url": "postgresql://user:pass@localhost/dbname"
        },
        "cache": {
            "type": "redis",
            "url": "redis://localhost:6379/0"
        }
    },
    "embedding": {
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        # Ou: "openai/text-embedding-3-small"
    },
    "routing": {
        # Customizações de roteamento
    }
}

# Inicialização
state_manager = StateManager(config)
await state_manager.initialize()
```

### 8.2 Docker Compose (Desenvolvimento)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: framework
      POSTGRES_USER: framework
      POSTGRES_PASSWORD: framework
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U framework"]
      interval: 5s
      timeout: 5s
      retries: 5

  neo4j:
    image: neo4j:5-community
    environment:
      NEO4J_AUTH: neo4j/framework123
      NEO4J_PLUGINS: '["apoc"]'
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
    healthcheck:
      test: ["CMD", "neo4j", "status"]
      interval: 10s
      timeout: 10s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  neo4j_data:
  qdrant_data:
  redis_data:
```

---

## 9. Extensibilidade

### 9.1 Adicionando Novos Backends

```python
class CustomBackendAdapter(BackendAdapter):
    """Template para implementar novos backends."""
    
    async def connect(self) -> None:
        # Estabelece conexão
        pass
    
    async def get(self, key: StateKey) -> Optional[Any]:
        # Implementa lógica de get
        pass
    
    # ... implementar demais métodos
```

### 9.2 Adicionando Novas Estratégias

```python
class CustomStrategy(MemoryStrategy):
    """Template para estratégias customizadas."""
    
    cache_ttl = 300
    
    async def project(
        self,
        state_manager: StateManager,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        # Implementa lógica de projeção
        pass
```

### 9.3 Adicionando Entidades de Domínio

Aplicações específicas definem suas entidades:

```python
# Exemplo: Aplicação de Marketing
class MarketingEntities:
    ARTICLE = "article"
    IDEA = "idea"
    BRIEF = "brief"
    POST = "post"

# Exemplo: Aplicação de Atendimento
class SupportEntities:
    TICKET = "ticket"
    CUSTOMER = "customer"
    INTERACTION = "interaction"
    RESOLUTION = "resolution"
```

---

## 10. Referências

- Framework de Agentes Autônomos: `docs/framework.md`
- BDI Architecture: Rao & Georgeff, 1995
- SOAR Cognitive Architecture: Laird, 2012
- Vector Similarity Search: Johnson et al., 2019
- Graph Databases: Robinson et al., 2015