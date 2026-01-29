# Prevenção de Duplicatas no Sistema de Versionamento

## Visão Geral

O sistema de versionamento de prompts foi melhorado para **prevenir duplicatas** de forma eficiente. Quando um prompt com o mesmo nome (`prompt_key`) e conteúdo idêntico é registrado, o sistema retorna a versão existente em vez de criar uma nova entrada na tabela.

## Como Funciona

### 1. Verificação em Duas Etapas

O sistema usa uma estratégia de verificação em duas etapas para máxima eficiência e precisão:

```python
def find_existing_prompt(prompt_key, template):
    # Etapa 1: Busca rápida por hash (indexada)
    candidates = db.query("WHERE prompt_key = ? AND template_hash = ?")
    
    # Etapa 2: Verificação exata do conteúdo (evita colisões de hash)
    for candidate in candidates:
        if candidate.template == template:
            return candidate  # Template idêntico encontrado
    
    return None  # Template não existe
```

### 2. Fluxo de Registro

```python
# 1. Normaliza o template (remove espaços extras)
template = template.rstrip()

# 2. Verifica se template idêntico já existe
existing = find_existing_prompt(prompt_key, template)
if existing:
    return existing  # Retorna versão existente (sem criar duplicata)

# 3. Se não existe, cria nova versão
version_number = count_existing_versions() + 1
create_new_version(f"v{version_number}")
```

## Características

### ✅ Prevenção de Duplicatas
- **Verificação por hash**: Busca rápida usando SHA256 hash do template
- **Verificação exata**: Compara conteúdo completo para evitar falsos positivos
- **Normalização**: Remove espaços extras antes da comparação

### ✅ Performance Otimizada
- **Índice composto**: `(prompt_key, template_hash)` para buscas rápidas
- **Duas etapas**: Hash para filtrar candidatos, comparação exata para validar
- **Sem duplicatas**: Evita popular tabela com entradas redundantes

### ✅ Idempotência Garantida
- Chamadas repetidas com mesmo template retornam mesma versão
- Não cria múltiplas versões para templates idênticos
- Mantém integridade dos dados

## Exemplo Prático

```python
from core.prompt_registry import register_prompt

# Primeira chamada - cria v1
prompt_id_1, version_1 = register_prompt(
    prompt_key="summarize",
    template="Summarize: {text}"
)
# Retorna: (uuid_1, "v1")

# Segunda chamada com template idêntico - retorna v1 (sem duplicata)
prompt_id_2, version_2 = register_prompt(
    prompt_key="summarize",
    template="Summarize: {text}"  # Idêntico ao anterior
)
# Retorna: (uuid_1, "v1") - MESMO ID, não cria duplicata

# Terceira chamada com template diferente - cria v2
prompt_id_3, version_3 = register_prompt(
    prompt_key="summarize",
    template="You are an expert. Summarize: {text}"  # Diferente
)
# Retorna: (uuid_3, "v2") - Nova versão criada

# Verificar quantas versões existem
from core.prompt_registry import list_prompt_versions
versions = list_prompt_versions("summarize")
# Retorna: 2 versões (v1 e v2) - sem duplicatas!
```

## Estrutura do Banco de Dados

### Coluna `template_hash`

A tabela `prompts` agora inclui uma coluna `template_hash`:

```sql
CREATE TABLE prompts (
    id TEXT PRIMARY KEY,
    prompt_key TEXT NOT NULL,
    version TEXT NOT NULL,
    template TEXT NOT NULL,
    template_hash TEXT NOT NULL,  -- ← Nova coluna para busca eficiente
    description TEXT,
    created_at TEXT NOT NULL,
    metadata_json TEXT,
    UNIQUE(prompt_key, version)
);

-- Índice para busca rápida
CREATE INDEX idx_prompts_key_hash ON prompts(prompt_key, template_hash);
```

### Migração Automática

O sistema detecta automaticamente se a coluna `template_hash` existe e:
- Se não existe, adiciona a coluna
- Calcula e preenche hash para registros existentes
- Cria índice para performance

## Vantagens

1. **Sem Duplicatas**: Tabela não é populada com prompts redundantes
2. **Performance**: Busca por hash é muito mais rápida que comparação de texto
3. **Precisão**: Verificação exata garante que não há falsos positivos
4. **Idempotência**: Chamadas repetidas são seguras e previsíveis
5. **Integridade**: Mantém dados limpos e organizados

## Casos de Uso

### Caso 1: Deploy Repetido
```python
# Deploy 1: Registra prompt
register_prompt("api_handler", template="...")

# Deploy 2: Mesmo código, mesmo template
register_prompt("api_handler", template="...")  # Retorna versão existente
# ✅ Não cria duplicata
```

### Caso 2: Testes
```python
# Teste 1: Registra prompt
register_prompt("test", template="Test: {input}")

# Teste 2: Mesmo prompt
register_prompt("test", template="Test: {input}")  # Retorna existente
# ✅ Não polui tabela com duplicatas de teste
```

### Caso 3: Evolução de Prompt
```python
# Versão 1
register_prompt("summarize", template="Summarize: {text}")  # v1

# Versão 2 (template diferente)
register_prompt("summarize", template="Expert summary: {text}")  # v2

# Tentativa de re-registrar v1
register_prompt("summarize", template="Summarize: {text}")  # Retorna v1
# ✅ Não cria nova versão, retorna v1 existente
```

## Função Helper

```python
from core.prompt_registry import find_existing_prompt

# Verificar se prompt já existe antes de registrar
existing = find_existing_prompt("summarize", "Summarize: {text}")
if existing:
    prompt_id, version = existing
    print(f"Prompt já existe: {version}")
else:
    prompt_id, version = register_prompt("summarize", "Summarize: {text}")
    print(f"Novo prompt criado: {version}")
```

## Detalhes Técnicos

- **Hash Algorithm**: SHA256
- **Normalização**: Remove trailing whitespace (`rstrip()`)
- **Comparação**: Case-sensitive (preserva maiúsculas/minúsculas)
- **Colisões**: Verificação exata previne falsos positivos de hash
- **Performance**: O(1) lookup por hash, O(n) verificação exata (onde n = candidatos)

## Conclusão

O sistema de prevenção de duplicatas garante que:
- ✅ Tabela não é populada com prompts redundantes
- ✅ Performance é otimizada com busca por hash
- ✅ Precisão é mantida com verificação exata
- ✅ Idempotência é garantida para chamadas repetidas

