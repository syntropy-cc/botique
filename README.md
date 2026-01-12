# Botique

Sistema multi-agente para gestão de marca pessoal e geração de conteúdo para redes sociais.

## Arquitetura

O projeto foi reorganizado em duas partes principais:

1. **Framework** (`framework/`): Componentes genéricos e reutilizáveis para criação de sistemas de agentes autônomos
2. **Boutique** (`boutique/`): Implementação específica do sistema de geração de posts para redes sociais

### Framework

O Framework fornece componentes genéricos baseados em especificação formal:
- **Agentes como grafos**: Agentes definidos como grafos direcionados sobre três pilares
- **Estado universal**: Sistema unificado de gerenciamento de estado
- **Storage flexível**: Backends múltiplos (SQLite, JSON, Memory)
- **Orquestração**: Sistema de coordenação de agentes

### Boutique

O Boutique implementa o sistema específico de geração de posts:
- **Instructions**: Prompts específicos para cada fase
- **State Management**: Gerenciamento de briefs, brand, e contexto
- **Tools**: Ferramentas específicas (palette selector, layout resolver, etc.)
- **Agents**: Agentes compostos para cada fase do pipeline
- **Orchestrator**: Orquestração específica do pipeline

## Funcionalidades

- **Pipeline completo**: Geração de ideias e briefs de coerência a partir de artigos
- **Versionamento de prompts**: Sistema automático de versionamento com prevenção de duplicatas
- **Event Logging**: Database-based logging system tracking all workflow events (LLM calls and non-LLM steps) with cost metrics, performance, and quality tracking
- **CLI integrado**: Interface de linha de comando para todas as operações
- **Framework reutilizável**: Base genérica para outros projetos de agentes autônomos

## Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd botique

# Instale dependências (se necessário)
pip install -r requirements.txt
```

## Uso Rápido

### 1. Registrar Prompts

Primeiro, registre todos os prompts no banco de dados:

```bash
python -m src.cli.commands prompts
```

### 2. Executar Pipeline

```bash
# Pipeline completo
python -m src.cli.commands full --article articles/artigo.md

# Ou fases separadas
python -m src.cli.commands ideas --article articles/artigo.md
python -m src.cli.commands briefs --ideas-json output/slug/phase1_ideas.json
```

## Comandos CLI

### `prompts` - Gerenciar Prompts

Registra e atualiza prompts do diretório `prompts/` no banco de dados.

```bash
# Registrar todos os prompts
python -m src.cli.commands prompts

# Atualizar metadados de prompts existentes
python -m src.cli.commands prompts --update-metadata

# Especificar diretório customizado
python -m src.cli.commands prompts --prompts-dir /caminho/para/prompts
```

**Recursos:**
- ✅ Versionamento automático (v1, v2, v3...)
- ✅ Prevenção de duplicatas
- ✅ Cálculo automático de métricas (tamanho, complexidade, tokens)
- ✅ Metadados completos armazenados

### `full` - Pipeline Completo

Executa o pipeline completo: Artigo → Ideias → Briefs.

```bash
python -m src.cli.commands full \
  --article articles/artigo.md \
  --min-ideas 5 \
  --max-ideas 8 \
  --max-posts 3
```

### `ideas` - Fase 1: Geração de Ideias

Gera ideias de posts a partir de um artigo.

```bash
python -m src.cli.commands ideas \
  --article articles/artigo.md \
  --min-ideas 3 \
  --max-ideas 6
```

### `briefs` - Fases 2 e 3: Briefs de Coerência

Gera briefs de coerência a partir de ideias selecionadas.

```bash
python -m src.cli.commands briefs \
  --ideas-json output/slug/phase1_ideas.json \
  --strategy diverse \
  --max-posts 3
```

## Configuração

### Variáveis de Ambiente

```bash
# Chave da API LLM (obrigatória)
export LLM_API_KEY="sua-chave-aqui"

# Caminho customizado para banco de dados SQLite (opcional)
export LLM_LOGS_DB_PATH="/caminho/para/llm_logs.db"

# Para usar PostgreSQL ao invés de SQLite (opcional)
export DB_URL="postgresql://user:password@localhost/dbname"
```

## Estrutura do Projeto

```
botique/
├── framework/            # Framework reutilizável
│   ├── core/            # Componentes fundamentais (Agent, Instruction, Tool, etc.)
│   ├── llm/             # Integração LLM genérica
│   ├── storage/         # Sistema de armazenamento unificado
│   └── docs/            # Documentação do framework
│
├── boutique/            # Implementação específica
│   ├── instructions/   # Pilar I: Instruções específicas
│   ├── state_management/# Pilar S: Gerenciamento de estado
│   ├── tools/           # Pilar T: Ferramentas específicas
│   ├── agents/          # Agentes compostos
│   └── orchestrator/    # Orquestração específica
│
├── src/                 # Código legado (compatibilidade)
│   ├── cli/             # Interface de linha de comando
│   ├── core/            # Módulos core (logging, prompts, etc.)
│   ├── coherence/       # Sistema de coerência
│   ├── ideas/           # Geração de ideias
│   └── phases/          # Fases do pipeline
│
├── prompts/              # Templates de prompts (.md) - migrado para boutique/instructions/templates/
├── articles/             # Artigos de entrada
├── output/               # Resultados do pipeline
├── scripts/              # Scripts utilitários
└── docs/                 # Documentação
    ├── framework.md      # Especificação formal do framework
    ├── pipeline_architecture.md  # Arquitetura do pipeline original
    └── architecture.md   # Arquitetura após refatoração
```

## Sistema de Versionamento de Prompts

O sistema oferece versionamento automático de prompts:

- **Automático**: Versões criadas automaticamente (v1, v2, v3...)
- **Sem duplicatas**: Templates idênticos retornam versão existente
- **Métricas**: Calcula tamanho, complexidade, tokens estimados
- **Rastreável**: Cada evento LLM ligado à versão específica do prompt

```bash
# Registrar prompts (primeira vez)
python -m src.cli.commands prompts

# Atualizar metadados (após modificar prompts)
python -m src.cli.commands prompts --update-metadata
```

## Documentação

### Documentação Geral
- [Arquitetura do Projeto](./docs/architecture.md) - Separação Framework vs Boutique
- [Arquitetura do Pipeline](./docs/pipeline_architecture.md) - Visão geral do sistema original
- [Especificação do Framework](./docs/framework.md) - Especificação formal completa

### Documentação do Framework
- [README do Framework](./framework/docs/README.md) - Visão geral do framework
- [Arquitetura do Framework](./framework/docs/architecture.md) - Arquitetura interna
- [Exemplos](./framework/docs/examples/) - Exemplos de uso

### Documentação do Boutique
- [Comandos CLI](./docs/cli_commands.md) - Guia completo de comandos
- [Event Logging](./docs/event_logging.md) - Sistema de logging de eventos
- [Versionamento de Prompts](./docs/prompt_versioning_automatic.md) - Sistema de versionamento

## Desenvolvimento

```bash
# Executar testes
python scripts/test_prompt_versioning.py

# Registrar prompts para desenvolvimento
python -m src.cli.commands prompts --update-metadata
```

## Licença

[Adicione informações de licença aqui]
