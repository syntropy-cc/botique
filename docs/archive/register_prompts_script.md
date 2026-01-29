# Script de Registro Automático de Prompts

## Visão Geral

O script `register_prompts_from_directory.py` registra automaticamente todos os prompts do diretório `prompts/` na tabela `prompts` do banco de dados, calculando métricas importantes e preenchendo metadados automaticamente.

## Uso Básico

```bash
# Registrar todos os prompts do diretório prompts/
python scripts/register_prompts_from_directory.py

# Especificar diretório customizado
python scripts/register_prompts_from_directory.py --prompts-dir /caminho/para/prompts

# Atualizar metadados de prompts existentes
python scripts/register_prompts_from_directory.py --update-metadata

# Modo silencioso
python scripts/register_prompts_from_directory.py --quiet
```

## Funcionalidades

### ✅ Registro Automático
- Escaneia todos os arquivos `.md` no diretório
- Extrai `prompt_key` do nome do arquivo (sem extensão)
- Registra automaticamente com versionamento

### ✅ Cálculo de Métricas
O script calcula automaticamente:

- **Tamanho**:
  - Caracteres totais
  - Caracteres sem espaços
  - Número de linhas
  - Número de palavras

- **Placeholders**:
  - Contagem de variáveis (`{variavel}`)
  - Lista de todos os placeholders encontrados

- **Complexidade**:
  - Score de complexidade (0-25+)
  - Nível: `low`, `medium`, `high`, `very_high`
  - Baseado em tamanho, placeholders e estrutura

- **Estimativas**:
  - Tokens estimados (~1 token = 4 caracteres)
  - Útil para estimar custos

### ✅ Metadados Ricos
Cada prompt é registrado com metadata completo:

```json
{
  "source_file": "/caminho/para/prompts/post_ideator.md",
  "source_filename": "post_ideator.md",
  "registered_by": "register_prompts_from_directory",
  "char_count": 10054,
  "char_count_no_spaces": 8523,
  "line_count": 143,
  "word_count": 1177,
  "placeholder_count": 27,
  "placeholders": ["article", "num_ideas_min", ...],
  "complexity_score": 22.86,
  "complexity_level": "high",
  "estimated_tokens": 2514,
  "document_filename": "post_ideator.md",
  "sections": {
    "role": {"present": true, "length": 667},
    "context": {"present": true, "length": 613},
    "task": {"present": true, "length": 1424}
  }
}
```

### ✅ Prevenção de Duplicatas
- Verifica se template idêntico já existe
- Retorna versão existente (não cria duplicata)
- Usa hash SHA256 para busca eficiente

### ✅ Atualização de Metadados
Com `--update-metadata`:
- Atualiza metadados de prompts existentes
- Não cria novas versões
- Preserva `template_hash` existente

## Exemplo de Saída

```
======================================================================
REGISTRO AUTOMÁTICO DE PROMPTS
======================================================================

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

✅ Processamento concluído!
```

## Opções de Linha de Comando

| Opção | Descrição |
|-------|-----------|
| `--prompts-dir PATH` | Diretório contendo arquivos .md (padrão: `prompts/`) |
| `--db-path PATH` | Caminho para banco de dados (padrão: `llm_logs.db`) |
| `--update-metadata` | Atualiza metadados de prompts existentes |
| `--quiet` | Modo silencioso (menos output) |
| `--help` | Mostra ajuda |

## Casos de Uso

### 1. Registro Inicial
```bash
# Primeira vez registrando todos os prompts
python scripts/register_prompts_from_directory.py
```

### 2. Atualizar Metadados
```bash
# Se prompts foram criados antes do script, atualizar metadados
python scripts/register_prompts_from_directory.py --update-metadata
```

### 3. Adicionar Novos Prompts
```bash
# Após adicionar novos arquivos .md, registrar novamente
python scripts/register_prompts_from_directory.py
# Script detecta novos e ignora existentes automaticamente
```

### 4. CI/CD Pipeline
```bash
# Em pipeline de deploy, garantir que todos os prompts estão registrados
python scripts/register_prompts_from_directory.py --quiet
```

## Integração com Sistema de Versionamento

O script usa o sistema de versionamento automático:
- **Primeira chamada**: Cria v1
- **Template idêntico**: Retorna v1 existente (sem duplicata)
- **Template diferente**: Cria v2 automaticamente

## Métricas Calculadas

### Complexidade Score
Fórmula aproximada:
```
complexity = min(chars / 1000, 10) + 
             min(placeholders * 2, 10) + 
             min(lines / 50, 5)
```

### Níveis de Complexidade
- **low**: score < 5
- **medium**: 5 ≤ score < 15
- **high**: 15 ≤ score < 25
- **very_high**: score ≥ 25

### Estimativa de Tokens
```
estimated_tokens = char_count / 4
```
(aproximação: 1 token ≈ 4 caracteres)

## Estrutura de Metadados

### Campos Principais
- `source_file`: Caminho completo do arquivo
- `source_filename`: Nome do arquivo
- `registered_by`: Identificador do script
- `char_count`: Total de caracteres
- `word_count`: Total de palavras
- `line_count`: Total de linhas
- `placeholder_count`: Número de variáveis
- `placeholders`: Lista de placeholders
- `complexity_score`: Score de complexidade
- `complexity_level`: Nível de complexidade
- `estimated_tokens`: Tokens estimados

### Campos de Documento
- `document_filename`: Nome do documento (se presente)
- `sections`: Informações sobre seções ([ROLE], [CONTEXT], etc.)

## Boas Práticas

1. **Execute após adicionar novos prompts**: Garanta que todos estão registrados
2. **Use `--update-metadata` periodicamente**: Mantenha metadados atualizados
3. **Verifique output**: Confirme que prompts foram registrados corretamente
4. **Integre em CI/CD**: Automatize registro em pipelines

## Troubleshooting

### Prompt não é registrado
- Verifique se arquivo tem extensão `.md`
- Confirme que diretório está correto
- Verifique permissões de leitura

### Metadados não aparecem
- Use `--update-metadata` para atualizar prompts existentes
- Verifique se prompt foi criado antes do script existir

### Duplicatas criadas
- Sistema previne duplicatas automaticamente
- Se ocorrer, verifique se templates são realmente idênticos
- Use `find_existing_prompt()` para verificar antes


