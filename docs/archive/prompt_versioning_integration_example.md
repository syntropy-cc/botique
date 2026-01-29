# Exemplo de Integração do Sistema de Versionamento de Prompts

Este documento mostra como integrar o sistema de versionamento de prompts nas chamadas LLM existentes.

## Padrão Recomendado

### 1. Registrar prompts (versionamento automático)

```python
from pathlib import Path
from core.prompt_registry import register_prompt
from core.config import POST_IDEATOR_TEMPLATE

# Definir chave do prompt
PROMPT_KEY = "post_ideator"

# Registrar o prompt - versão é criada automaticamente (v1, v2, v3...)
# Se o template for idêntico a uma versão existente, retorna a versão existente
prompt_id, version = register_prompt(
    prompt_key=PROMPT_KEY,
    template=POST_IDEATOR_TEMPLATE.read_text(encoding="utf-8"),
    description="Post ideator prompt",
    metadata={"author": "system", "created": "2025-01-01"},
)
# Primeira chamada: retorna (uuid, "v1")
# Segunda chamada com template diferente: retorna (novo_uuid, "v2")
# Terceira chamada com template idêntico ao v1: retorna (uuid_v1, "v1")
```

### 2. Usar o prompt_id nas chamadas LLM

#### Opção A: Modificar HttpLLMClient.generate() para aceitar prompt_id

```python
# No HttpLLMClient.generate()
def generate(
    self,
    prompt: str,
    prompt_id: Optional[str] = None,  # Novo parâmetro
    max_tokens: int = 2048,
    temperature: float = 0.2,
    context: Optional[str] = None,
    save_raw: Optional[bool] = None,
) -> str:
    # ... código existente ...
    
    if self.logger:
        self.logger.log_call(
            prompt=prompt,
            response=log_response,
            model=self.model,
            base_url=self.base_url,
            max_tokens=max_tokens,
            temperature=temperature,
            duration_ms=duration_ms,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            tokens_total=tokens_total,
            status=status,
            error=error_msg,
            prompt_id=prompt_id,  # Passar prompt_id
        )
```

#### Opção B: Usar log_llm_event diretamente após a chamada

```python
# Após chamar self.llm.generate()
response = self.llm.generate(prompt, context=context)

# Se o logger estiver disponível, registrar com prompt_id
if self.llm.logger:
    trace_id = self.llm.logger.current_trace_id or self.llm.logger.session_id
    self.llm.logger.log_llm_event(
        trace_id=trace_id,
        name="post_ideator.generate_ideas",
        model=self.llm.model,
        input_text=prompt,
        input_obj={"prompt": prompt, "temperature": 0.2},
        output_text=response,
        output_obj={"content": response},
        duration_ms=duration_ms,  # Calcular se necessário
        tokens_input=tokens_input,  # Extrair da resposta se disponível
        tokens_output=tokens_output,
        tokens_total=tokens_total,
        prompt_id=prompt_id,  # Usar o prompt_id registrado
    )
```

### 3. Exemplo completo: Refatorando IdeaGenerator

```python
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.config import IdeationConfig, POST_IDEATOR_TEMPLATE
from ..core.llm_client import HttpLLMClient
from ..core.utils import build_prompt_from_template, validate_llm_json_response
from ..core.prompt_registry import register_prompt

# Definir versão do prompt
POST_IDEATOR_PROMPT_KEY = "post_ideator"
POST_IDEATOR_PROMPT_VERSION = "v1"


class IdeaGenerator:
    def __init__(self, llm_client: HttpLLMClient):
        self.llm = llm_client
        
        # Registrar prompt na inicialização
        self.prompt_id = register_prompt(
            prompt_key=POST_IDEATOR_PROMPT_KEY,
            version=POST_IDEATOR_PROMPT_VERSION,
            template=POST_IDEATOR_TEMPLATE.read_text(encoding="utf-8"),
            description="Post ideator prompt for generating social media post ideas",
            metadata={"module": "ideas.generator"},
        )
    
    def generate_ideas(
        self,
        article_text: str,
        config: IdeationConfig,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Build prompt
        prompt_dict = config.to_prompt_dict()
        prompt_dict["article"] = article_text
        prompt = build_prompt_from_template(POST_IDEATOR_TEMPLATE, prompt_dict)
        
        # Chamar LLM com prompt_id
        # Nota: Isso requer modificar HttpLLMClient.generate() para aceitar prompt_id
        # ou usar log_llm_event diretamente após a chamada
        raw_response = self.llm.generate(
            prompt, 
            context=context,
            prompt_id=self.prompt_id,  # Se HttpLLMClient suportar
        )
        
        # ... resto do código ...
```

## Migração Gradual

Para migração gradual sem quebrar código existente:

1. **Fase 1**: Registrar prompts sem exigir prompt_id nas chamadas
2. **Fase 2**: Adicionar prompt_id opcional nas chamadas LLM
3. **Fase 3**: Tornar prompt_id obrigatório para eventos LLM

## Consultas e Análise

Após integrar, use os query helpers para análise:

```python
from core.llm_log_queries import (
    get_prompt_versions_with_usage,
    compare_prompt_versions,
    get_prompt_quality_stats,
)

# Ver todas as versões de um prompt
versions = get_prompt_versions_with_usage("post_ideator")

# Comparar versões
comparison = compare_prompt_versions("post_ideator")

# Estatísticas de qualidade
quality_stats = get_prompt_quality_stats(prompt_key="post_ideator")
```

## Boas Práticas

1. **Versionamento automático**: O sistema cria versões automaticamente (v1, v2, v3...) baseado em timestamp
2. **Idempotência**: Chamar `register_prompt` com o mesmo template retorna a versão existente
3. **Documentar mudanças**: Use `description` para explicar mudanças entre versões
4. **Metadata útil**: Inclua autor, data, experimento, etc. no metadata
5. **Imutabilidade**: Cada versão é imutável - mudanças no template criam nova versão automaticamente
6. **Testes**: Use o script de teste para validar o sistema

