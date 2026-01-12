# Arquitetura do Projeto

Este documento descreve a arquitetura do projeto após a refatoração que separa o **Framework** reutilizável do projeto específico **Boutique**.

## Visão Geral

O projeto foi reorganizado em duas partes principais:

1. **Framework** (`framework/`): Componentes genéricos e reutilizáveis para criação de sistemas de agentes autônomos
2. **Boutique** (`boutique/`): Implementação específica do sistema de geração de posts para redes sociais

## Separação Framework vs Boutique

### Framework (`framework/`)

O Framework fornece componentes genéricos baseados na especificação formal definida em `docs/framework.md`. Ele é projetado para ser reutilizável em outros projetos.

#### Estrutura do Framework

```
framework/
├── core/                    # Componentes fundamentais
│   ├── agent.py            # Agente como grafo direcionado
│   ├── instruction.py      # Instrução formal (prompts)
│   ├── state_management.py # Estratégias de gerenciamento de estado
│   ├── tool.py             # Ferramentas executáveis
│   ├── universal_state.py  # Estado universal genérico
│   └── orchestrator.py    # Orquestrador genérico
│
├── llm/                     # Integração LLM genérica
│   ├── client.py           # Interface abstrata LLMClient
│   ├── http_client.py      # Implementação HTTP
│   ├── logger.py           # Logging de chamadas LLM
│   ├── pricing.py          # Cálculo de custos
│   ├── queries.py          # Consultas ao histórico
│   └── prompt_helpers.py   # Helpers para prompts
│
├── storage/                  # Sistema de armazenamento unificado
│   ├── base.py             # Interface StorageBackend
│   ├── manager.py          # Gerenciador unificado
│   ├── registry.py         # Registry de backends
│   └── adapters/           # Adaptadores específicos
│       ├── sqlite_adapter.py  # SQLite (histórico/eventos)
│       ├── json_adapter.py    # JSON (objetos complexos)
│       ├── memory_adapter.py  # Memória (classes Python)
│       └── hybrid_adapter.py  # Híbrido (múltiplos backends)
│
└── docs/                    # Documentação do framework
    ├── README.md
    ├── architecture.md
    └── examples/
```

#### Princípios do Framework

- **Genérico**: Não depende de domínios específicos
- **Extensível**: Permite extensão através de herança e composição
- **Formal**: Baseado em especificação matemática formal
- **Reutilizável**: Pode ser usado em diferentes projetos

### Boutique (`boutique/`)

O Boutique é a implementação específica do sistema de geração de posts, organizada segundo os três pilares do framework:

#### Estrutura do Boutique

```
boutique/
├── instructions/            # Pilar I: Instruções
│   ├── templates/          # Templates de prompts
│   ├── post_ideator.py     # Instrução de ideação
│   ├── narrative_architect.py
│   ├── copywriter.py
│   ├── visual_composer.py
│   └── caption_writer.py
│
├── state_management/         # Pilar S: Gerenciamento de Estado
│   ├── models/             # Modelos de dados
│   │   ├── coherence_brief.py
│   │   └── brand/          # Modelos de brand
│   ├── storage/            # Storages específicos
│   │   ├── coherence_brief_storage.py
│   │   └── brand_storage.py
│   ├── strategies/         # Estratégias de projeção
│   │   ├── brief_strategy.py
│   │   └── brand_strategy.py
│   └── boutique_state.py   # Estado específico do boutique
│
├── tools/                   # Pilar T: Ferramentas
│   ├── parameter_resolver.py
│   ├── palette_selector.py
│   ├── layout_resolver.py
│   ├── image_compositor.py
│   └── validators.py
│
├── agents/                  # Agentes compostos
│   ├── post_ideator_agent.py
│   ├── narrative_architect_agent.py
│   ├── copywriter_agent.py
│   ├── visual_composer_agent.py
│   └── caption_writer_agent.py
│
└── orchestrator/           # Orquestração específica
    ├── boutique_orchestrator.py
    └── pipelines/
        ├── ideation_pipeline.py
        ├── post_creation_pipeline.py
        └── slide_generation_pipeline.py
```

#### Princípios do Boutique

- **Específico**: Implementa lógica de domínio específica
- **Organizado por Pilares**: Segue a arquitetura do framework
- **Extensível**: Pode adicionar novos agentes, instruções, tools

## Sistema de Storage

O sistema de storage unificado permite gerenciar diferentes tipos de dados usando backends apropriados:

### Arquitetura de Storage

```
StorageManager
    ├── SQLiteBackend    → Histórico, eventos, prompts
    ├── JSONBackend      → Briefs, ideias, estruturas narrativas
    └── MemoryBackend    → Brand, palettes, typography (classes)
```

### Roteamento Automático

O `StorageManager` roteia automaticamente operações para o backend apropriado baseado no tipo de entidade:

- **"trace"**, **"event"**, **"prompt"** → SQLite
- **"brief"**, **"idea"**, **"narrative"** → JSON
- **"brand"**, **"palette"**, **"typography"** → Memory

### Exemplo de Uso

```python
from boutique.state_management.boutique_state import BoutiqueState
from boutique.state_management.models.coherence_brief import CoherenceBrief

# Cria estado
state = BoutiqueState()

# Armazena brief (usa JSON backend automaticamente)
brief = CoherenceBrief(...)
state.store_brief(brief)

# Recupera brief
retrieved_brief = state.get_brief("post_001")

# Query histórico (usa SQLite backend automaticamente)
traces = state.query_history(filters={"name": "ideation"})
```

## Fluxo de Execução

### Pipeline Completo

1. **Ideation Pipeline** (`boutique/orchestrator/pipelines/ideation_pipeline.py`)
   - Usa `PostIdeatorAgent`
   - Gera ideias de posts a partir de artigos
   - Armazena resultados em `BoutiqueState`

2. **Post Creation Pipeline** (`boutique/orchestrator/pipelines/post_creation_pipeline.py`)
   - Usa `NarrativeArchitectAgent`
   - Cria estrutura narrativa
   - Enriquece `CoherenceBrief`

3. **Slide Generation Pipeline** (`boutique/orchestrator/pipelines/slide_generation_pipeline.py`)
   - Usa `CopywriterAgent` e `VisualComposerAgent`
   - Gera conteúdo e especificações visuais
   - Compõe slides finais

### Orquestração

O `BoutiqueOrchestrator` coordena a execução dos pipelines:

```python
from boutique.orchestrator.boutique_orchestrator import BoutiqueOrchestrator

orchestrator = BoutiqueOrchestrator()
result = orchestrator.run_full_pipeline(
    article_path=Path("articles/article.md"),
    ideation_config=IdeationConfig(),
    selection_config=SelectionConfig(),
)
```

## Compatibilidade com Código Legado

Para facilitar a migração gradual, o código em `src/` mantém compatibilidade:

- Imports com fallback para novos caminhos
- Aliases temporários em `src/__init__.py`
- Wrapper `Orchestrator` em `src/orchestrator.py` que pode usar `BoutiqueOrchestrator`

## Extensibilidade

### Adicionar Novo Agente

1. Criar instrução em `boutique/instructions/`
2. Criar tools necessários em `boutique/tools/`
3. Criar agente em `boutique/agents/`
4. Registrar no `BoutiqueOrchestrator`

### Adicionar Novo Tipo de Storage

1. Criar adapter em `framework/storage/adapters/`
2. Registrar no `StorageRegistry`
3. Atualizar routing no `StorageManager`

### Usar Framework em Outro Projeto

1. Copiar `framework/` para novo projeto
2. Criar estrutura específica seguindo padrão de `boutique/`
3. Implementar instruções, tools e agentes específicos
4. Criar orquestrador específico estendendo `Orchestrator`

## Referências

- `docs/framework.md`: Especificação formal do framework
- `docs/pipeline_architecture.md`: Arquitetura do pipeline original
- `framework/docs/`: Documentação detalhada do framework
