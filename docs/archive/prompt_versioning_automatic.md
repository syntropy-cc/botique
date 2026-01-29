# Sistema de Versionamento Automático de Prompts

## Visão Geral

O sistema de versionamento de prompts agora funciona de forma **totalmente automática**. Você não precisa mais especificar versões manualmente - o sistema cria versões automaticamente (v1, v2, v3...) baseado em timestamp quando o mesmo `prompt_key` é registrado com templates diferentes.

## Como Funciona

### 1. Primeira Registração

```python
from core.prompt_registry import register_prompt

prompt_id, version = register_prompt(
    prompt_key="post_ideator",
    template="Analyze the article: {article}",
    description="Post ideator prompt"
)
# Retorna: (uuid, "v1")
```

### 2. Segunda Registração (Template Diferente)

```python
# Template modificado
prompt_id, version = register_prompt(
    prompt_key="post_ideator",
    template="You are an expert. Analyze: {article}",  # Template diferente
    description="Enhanced version"
)
# Retorna: (novo_uuid, "v2") - Nova versão criada automaticamente
```

### 3. Registração com Template Idêntico (Idempotência)

```python
# Mesmo template da primeira chamada
prompt_id, version = register_prompt(
    prompt_key="post_ideator",
    template="Analyze the article: {article}",  # Template idêntico ao v1
    description="Post ideator prompt"
)
# Retorna: (uuid_v1, "v1") - Retorna versão existente
```

## Características Principais

### ✅ Versionamento Automático
- Versões são criadas automaticamente: v1, v2, v3, v4...
- Baseado em timestamp (ordem de criação)
- Não precisa especificar versão manualmente

### ✅ Prevenção de Duplicatas
- **Verificação eficiente**: Usa hash SHA256 para busca rápida
- **Verificação exata**: Compara conteúdo completo para evitar falsos positivos
- **Sem redundâncias**: Templates idênticos não criam novas versões
- **Idempotência garantida**: Chamadas repetidas retornam mesma versão

### ✅ Idempotência Inteligente
- Se o template for **idêntico** a uma versão existente, retorna a versão existente
- Se o template for **diferente**, cria nova versão automaticamente
- Comparação é feita por hash (rápido) + conteúdo exato (preciso)

### ✅ Rastreabilidade Completa
- Cada versão tem timestamp único (`created_at`)
- Todas as versões são preservadas (imutáveis)
- Eventos LLM são ligados à versão específica usada

## Exemplo de Uso Completo

```python
from core.prompt_registry import register_prompt
from core.llm_logger import LLMLogger

# Registrar prompt (versão automática)
prompt_id, version = register_prompt(
    prompt_key="summarize",
    template="Summarize: {text}",
    description="Simple summarization",
    metadata={"author": "system"}
)

# Usar em chamada LLM
logger.log_llm_event(
    trace_id=trace_id,
    name="summarize.generate",
    model="deepseek-chat",
    input_text=final_prompt,
    output_text=response,
    prompt_id=prompt_id,  # Liga evento à versão
    # ... outros parâmetros
)

# Eventos são armazenados na tabela `events` do banco de dados,
# ligados à versão do prompt via `prompt_id`

# Mais tarde, se o template mudar...
prompt_id_v2, version_v2 = register_prompt(
    prompt_key="summarize",
    template="You are an expert. Summarize: {text}",  # Template diferente
    description="Enhanced version"
)
# Automaticamente cria v2
```

## Consultas e Análise

```python
from core.llm_log_queries import (
    get_prompt_versions_with_usage,
    compare_prompt_versions,
)

# Ver todas as versões e uso
versions = get_prompt_versions_with_usage("summarize")
# Retorna: [{"version": "v1", "usage_count": 10}, {"version": "v2", "usage_count": 5}]

# Comparar versões
comparison = compare_prompt_versions("summarize")
# Retorna: custo, tokens, qualidade por versão
```

## Vantagens

1. **Simplicidade**: Não precisa gerenciar versões manualmente
2. **Automático**: Sistema detecta mudanças e cria versões
3. **Idempotente**: Chamadas repetidas com mesmo template são seguras
4. **Rastreável**: Histórico completo de todas as versões
5. **Comparável**: Fácil comparar performance entre versões

## Migração de Código Existente

Se você tinha código usando versões manuais:

**Antes:**
```python
prompt_id = register_prompt(
    prompt_key="post_ideator",
    version="v1",  # ← Remover este parâmetro
    template=template,
)
```

**Depois:**
```python
prompt_id, version = register_prompt(  # ← Agora retorna tupla
    prompt_key="post_ideator",
    template=template,  # ← Versão é automática
)
```

## Detalhes Técnicos

- **Comparação de templates**: Feita por comparação exata de conteúdo (string)
- **Hash de template**: Armazenado em metadata para referência futura
- **Ordenação**: Versões são ordenadas por `created_at` (timestamp)
- **Imutabilidade**: Versões existentes nunca são modificadas

