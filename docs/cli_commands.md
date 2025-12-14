# CLI Commands - Guia de Uso

Este documento descreve todos os comandos disponíveis na interface de linha de comando (CLI) do projeto.

## Visão Geral

O CLI oferece comandos para executar o pipeline completo ou fases individuais, além de gerenciar prompts no banco de dados.

## Comandos Disponíveis

### 1. `prompts` - Gerenciar Prompts no Banco de Dados

Registra e atualiza prompts do diretório `prompts/` no banco de dados com versionamento automático e métricas.

#### Uso Básico

```bash
# Registrar todos os prompts do diretório padrão (prompts/)
python -m src.cli.commands prompts

# Especificar diretório customizado
python -m src.cli.commands prompts --prompts-dir /caminho/para/prompts

# Atualizar metadados de prompts existentes
python -m src.cli.commands prompts --update-metadata

# Modo silencioso
python -m src.cli.commands prompts --quiet
```

#### Opções

| Opção | Descrição |
|-------|-----------|
| `--prompts-dir PATH` | Diretório contendo arquivos .md (padrão: `prompts/`) |
| `--update-metadata` | Atualiza metadados de prompts existentes sem criar novas versões |
| `--quiet` | Modo silencioso (menos output) |

#### O que faz

- **Escaneia** todos os arquivos `.md` no diretório
- **Calcula métricas** automaticamente:
  - Tamanho (caracteres, palavras, linhas)
  - Placeholders (variáveis do template)
  - Complexidade (score e nível)
  - Tokens estimados
- **Registra** com versionamento automático (v1, v2, v3...)
- **Previne duplicatas** - templates idênticos retornam versão existente
- **Armazena metadados** completos no banco de dados

#### Exemplo de Saída

```
📁 Diretório: /home/user/botique/prompts
📄 Arquivos encontrados: 2

  ✅ narrative_architect: v1 registrado
     - Tamanho: 14,011 chars, 1,620 palavras, 243 linhas
     - Placeholders: 24 (article_context, avoid_emotions, ...)
     - Complexidade: high (score: 24.86)
     - Tokens estimados: ~3,503

  ✅ post_ideator: v1 registrado
     - Tamanho: 10,054 chars, 1,177 palavras, 143 linhas
     - Placeholders: 27 (article, num_ideas_min, ...)
     - Complexidade: high (score: 22.86)
     - Tokens estimados: ~2,514

======================================================================
📊 RESUMO
======================================================================
Total de arquivos: 2
  ✅ Novos registros: 2
  ⚠️  Já existentes: 0

📈 Métricas Agregadas:
  - Total de caracteres: 24,065
  - Total de placeholders: 51
  - Complexidade média: 23.86
```

### 2. `full` - Pipeline Completo

Executa o pipeline completo: Artigo → Ideias → Briefs.

```bash
python -m src.cli.commands full --article articles/artigo.md
```

**Opções:**
- `--article, -a`: Caminho para arquivo do artigo (obrigatório)
- `--min-ideas`: Mínimo de ideias (padrão: 3)
- `--max-ideas`: Máximo de ideias (padrão: 5)
- `--min-confidence`: Threshold de confiança (padrão: 0.7)
- `--max-posts`: Máximo de posts (padrão: 3)
- `--strategy`: Estratégia de seleção: `diverse` ou `top` (padrão: diverse)

### 3. `ideas` - Fase 1: Geração de Ideias

Executa apenas a Fase 1: geração de ideias a partir de um artigo.

```bash
python -m src.cli.commands ideas --article articles/artigo.md
```

**Opções:**
- `--article, -a`: Caminho para arquivo do artigo (obrigatório)
- `--min-ideas`: Mínimo de ideias (padrão: 3)
- `--max-ideas`: Máximo de ideias (padrão: 5)

### 4. `briefs` - Fases 2 e 3: Briefs de Coerência

Executa Fases 2 e 3: seleção de ideias e geração de briefs de coerência.

```bash
python -m src.cli.commands briefs --ideas-json output/slug/phase1_ideas.json
```

**Opções:**
- `--ideas-json`: Caminho para `phase1_ideas.json` (obrigatório)
- `--min-confidence`: Threshold de confiança (padrão: 0.7)
- `--max-posts`: Máximo de posts (padrão: 3)
- `--strategy`: Estratégia de seleção: `diverse` ou `top` (padrão: diverse)

## Opções Globais

Estas opções estão disponíveis para todos os comandos:

| Opção | Descrição |
|-------|-----------|
| `--output-dir PATH` | Diretório de saída (padrão: `output/`) |
| `--llm-base-url URL` | URL base da API LLM (padrão: DeepSeek) |
| `--llm-model MODEL` | Nome do modelo LLM (padrão: `deepseek-chat`) |

## Fluxo de Trabalho Recomendado

### 1. Registrar Prompts (Primeira Vez)

```bash
# Registrar todos os prompts no banco de dados
python -m src.cli.commands prompts
```

### 2. Executar Pipeline

```bash
# Opção A: Pipeline completo
python -m src.cli.commands full --article articles/artigo.md

# Opção B: Fases separadas
python -m src.cli.commands ideas --article articles/artigo.md
python -m src.cli.commands briefs --ideas-json output/slug/phase1_ideas.json
```

### 3. Atualizar Prompts (Quando Modificados)

```bash
# Se você modificou prompts, atualize metadados
python -m src.cli.commands prompts --update-metadata
```

## Integração com Versionamento de Prompts

O comando `prompts` integra-se automaticamente com o sistema de versionamento:

- **Versionamento automático**: Cria v1, v2, v3... automaticamente
- **Prevenção de duplicatas**: Templates idênticos não criam novas versões
- **Métricas completas**: Calcula e armazena métricas importantes
- **Rastreabilidade**: Cada prompt é versionado e rastreável

## Variáveis de Ambiente

- `LLM_API_KEY`: Chave da API LLM (obrigatória)
- `LLM_LOGS_DB_PATH`: Caminho customizado para banco de dados (opcional)

## Exemplos Completos

### Exemplo 1: Setup Inicial

```bash
# 1. Registrar prompts
python -m src.cli.commands prompts

# 2. Executar pipeline
python -m src.cli.commands full \
  --article articles/meu-artigo.md \
  --min-ideas 5 \
  --max-ideas 8 \
  --max-posts 3
```

### Exemplo 2: Workflow Incremental

```bash
# 1. Gerar ideias
python -m src.cli.commands ideas \
  --article articles/artigo.md \
  --min-ideas 3 \
  --max-ideas 6

# 2. Revisar phase1_ideas.json manualmente

# 3. Gerar briefs apenas para ideias selecionadas
python -m src.cli.commands briefs \
  --ideas-json output/artigo-slug/phase1_ideas.json \
  --strategy top \
  --max-posts 2
```

### Exemplo 3: Atualizar Prompts

```bash
# Após modificar prompts no diretório
python -m src.cli.commands prompts --update-metadata
```

## Troubleshooting

### Erro: "Prompts directory not found"
- Verifique se o diretório `prompts/` existe
- Use `--prompts-dir` para especificar caminho customizado

### Erro: "No prompt files found"
- Verifique se há arquivos `.md` no diretório
- Confirme que os arquivos têm extensão `.md`

### Erro: "Script not found"
- Verifique se `scripts/register_prompts_from_directory.py` existe
- Execute do diretório raiz do projeto

## Referências

- [Sistema de Versionamento de Prompts](./prompt_versioning_automatic.md)
- [Prevenção de Duplicatas](./prompt_versioning_duplicate_prevention.md)
- [Script de Registro](./register_prompts_script.md)

