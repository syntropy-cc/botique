# Botique

Sistema multi-agente para gestão de marca pessoal e geração de conteúdo para redes sociais.

## Funcionalidades

- **Pipeline completo**: Geração de ideias e briefs de coerência a partir de artigos
- **Versionamento de prompts**: Sistema automático de versionamento com prevenção de duplicatas
- **Logging de LLM**: Rastreamento completo de chamadas LLM com métricas de custo e performance
- **CLI integrado**: Interface de linha de comando para todas as operações

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

# Caminho customizado para banco de dados (opcional)
export LLM_LOGS_DB_PATH="/caminho/para/llm_logs.db"
```

## Estrutura do Projeto

```
botique/
├── src/
│   ├── cli/              # Interface de linha de comando
│   ├── core/             # Módulos core (logging, prompts, etc.)
│   ├── coherence/        # Sistema de coerência
│   ├── ideas/            # Geração de ideias
│   └── phases/           # Fases do pipeline
├── prompts/              # Templates de prompts (.md)
├── articles/             # Artigos de entrada
├── output/               # Resultados do pipeline
├── scripts/              # Scripts utilitários
└── docs/                 # Documentação
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

- [Comandos CLI](./docs/cli_commands.md) - Guia completo de comandos
- [Versionamento de Prompts](./docs/prompt_versioning_automatic.md) - Sistema de versionamento
- [Arquitetura do Pipeline](./docs/pipeline_architecture.md) - Visão geral do sistema

## Desenvolvimento

```bash
# Executar testes
python scripts/test_prompt_versioning.py

# Registrar prompts para desenvolvimento
python -m src.cli.commands prompts --update-metadata
```

## Licença

[Adicione informações de licença aqui]
