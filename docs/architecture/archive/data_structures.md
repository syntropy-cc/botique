# Arquitetura: Estruturas de Dados

> **Versão**: 2.1  
> **Data**: 2026-01-14  
> **Status**: Documentação de Estruturas de Dados  
> **Autor**: Sistema de Documentação Automatizada

---

## Visão Geral

Este documento descreve todas as **estruturas de dados principais** usadas no pipeline. Cada estrutura é definida com seus campos, tipos, e exemplos práticos.

---

## Estruturas Principais

### 1. post_ideas.json

**Fase**: Phase 1 (Ideation)  
**Gerado por**: Post Ideator (AI)  
**Localização**: Output da Phase 1

**Estrutura**:
```json
{
  "ideas": [
    {
      "id": "idea_1",
      "platform": "linkedin",
      "tone": "professional",
      "persona": "C-level execs",
      "angle": "AI failure patterns",
      "hook": "85% of AI projects fail—here's why",
      "narrative_arc": "Hook → Problem → Solution → CTA",
      "key_insights_used": ["insight_1", "insight_2"],
      "estimated_slides": 7,
      "confidence": 0.9
    }
  ],
  "article_summary": {
    "main_thesis": "Organizational alignment is key to AI success",
    "key_insights": [
      {
        "id": "insight_1",
        "content": "85% of AI projects fail primarily due to organizational misalignment",
        "type": "statistic",
        "strength": 10,
        "source_quote": "According to Gartner..."
      }
    ],
    "themes": ["AI", "project management", "organizational alignment"]
  }
}
```

**Campos**:
- `ideas[]`: Lista de ideias geradas
  - `id`: Identificador único da ideia
  - `platform`: Plataforma alvo (linkedin, instagram, etc.)
  - `tone`: Tom (professional, casual, etc.)
  - `persona`: Persona alvo
  - `angle`: Ângulo único da ideia
  - `hook`: Gancho de abertura
  - `narrative_arc`: Arco narrativo alto nível
  - `key_insights_used[]`: IDs dos insights usados
  - `estimated_slides`: Número estimado de slides
  - `confidence`: Confiança da ideia (0.0-1.0)
- `article_summary`: Resumo do artigo
  - `main_thesis`: Tese principal
  - `key_insights[]`: Insights chave extraídos
    - `id`: ID único do insight
    - `content`: Conteúdo do insight
    - `type`: Tipo (statistic, insight, quote, etc.)
    - `strength`: Força do insight (1-10)
    - `source_quote`: Citação da fonte (opcional)
  - `themes[]`: Temas identificados

---

### 2. post_config.json

**Fase**: Phase 2 (Configuration)  
**Gerado por**: Parameter Resolver (Code)  
**Localização**: Output da Phase 2

**Estrutura**:
```json
{
  "post_id": "post_001",
  "idea_ref": "idea_1",
  "platform": "linkedin",
  "tone": "professional",
  "persona": "C-level execs",
  "palette_id": "dark_professional_01",
  "typography_id": "inter_clean",
  "canvas": {
    "width": 1080,
    "height": 1350,
    "aspect_ratio": "4:5"
  },
  "brand": {
    "handle": "@syntropy",
    "tagline": "Go deep or go home"
  }
}
```

**Campos**:
- `post_id`: Identificador único do post
- `idea_ref`: Referência à ideia origem
- `platform`: Plataforma alvo
- `tone`: Tom
- `persona`: Persona alvo
- `palette_id`: ID da paleta selecionada
- `typography_id`: ID da tipografia selecionada
- `canvas`: Dimensões do canvas
  - `width`: Largura em pixels
  - `height`: Altura em pixels
  - `aspect_ratio`: Proporção (ex: "4:5")
- `brand`: Assets da marca
  - `handle`: Handle da marca (ex: "@syntropy")
  - `tagline`: Tagline da marca

---

### 3. coherence_brief.json

**Fase**: Phase 1-5 (Evolutivo)  
**Gerado por**: Coherence Brief Builder + Agentes (Code + AI)  
**Localização**: `src/coherence/brief.py`

**Estrutura Completa**: Ver `docs/architecture/memory_management.md` para estrutura completa.

**Estrutura Resumida**:
```json
{
  "metadata": {
    "post_id": "post_article_slug_idea_1",
    "idea_id": "idea_1",
    "platform": "linkedin",
    "format": "carousel"
  },
  "voice": {
    "tone": "professional",
    "personality_traits": ["authoritative", "insightful"],
    "vocabulary_level": "sophisticated",
    "formality": "formal"
  },
  "visual": {
    "palette_id": "brand_dark_professional",
    "palette": {"primary": "#000000", "accent": "#0060FF", "theme": "dark"},
    "typography_id": "brand_professional",
    "style": "clean_professional_data_focused",
    "mood": "dramatic_focused",
    "canvas": {"width": 1080, "height": 1350, "aspect_ratio": "4:5"}
  },
  "emotions": {
    "primary": "urgency",
    "secondary": ["curiosity"],
    "avoid": ["fear"]
  },
  "content": {
    "keywords_to_emphasize": ["AI", "failure"],
    "themes": ["AI", "project management"],
    "main_message": "Organizational alignment is key to AI success",
    "angle": "Uncovering hidden organizational pitfalls",
    "hook": "Shocking: 85% of AI projects fail—but it's not the tech's fault"
  },
  "audience": {
    "persona": "Tech leaders and executives",
    "pain_points": ["wasted budgets", "project delays"],
    "desires": ["successful AI implementation", "competitive edge"]
  },
  "context": {
    "article_context": "The article highlights that 85% of AI projects fail...",
    "key_insights_used": ["insight_1", "insight_2"],
    "key_insights_content": [
      {
        "id": "insight_1",
        "content": "85% of AI projects fail primarily due to organizational misalignment",
        "type": "statistic",
        "strength": 10,
        "source_quote": "According to Gartner..."
      }
    ]
  },
  "brand": {
    "values": ["go_deep_or_go_home"],
    "assets": {
      "handle": "@syntropy",
      "tagline": "Go deep or go home"
    }
  },
  "evolution": {
    "narrative_structure": { /* ver abaixo */ },
    "narrative_pacing": "moderate",
    "transition_style": "smooth",
    "copy_guidelines": { /* ver abaixo */ },
    "cta_guidelines": { /* ver abaixo */ },
    "visual_preferences": { /* ver abaixo */ },
    "platform_constraints": { /* ver abaixo */ }
  }
}
```

**Referência Completa**: `docs/architecture/memory_management.md`

---

### 4. narrative_structure.json

**Fase**: Phase 3 (Post Creation)  
**Gerado por**: Narrative Architect (AI) + Template Selector (Code)  
**Localização**: Output da Phase 3

**Estrutura Inicial (após Narrative Architect)**:
```json
{
  "post_id": "post_001",
  "arc": "Hook → Problem → Value → CTA",
  "narrative_pacing": "moderate",
  "transition_style": "smooth",
  "arc_refined": "Hook → Problem → Value → CTA",
  "slides": [
    {
      "slide_number": 1,
      "template_type": "hook",
      "value_subtype": null,
      "purpose": "Grab attention with stat",
      "target_emotions": ["shock"],
      "copy_direction": "Open with contrast highlighting gap between certificates and actual skills...",
      "key_elements": ["certificates", "skills"],
      "content_slots": {
        "headline": {"max_chars": 60}
      }
    },
    {
      "slide_number": 2,
      "template_type": "value",
      "value_subtype": "data",
      "purpose": "Present quantified evidence",
      "target_emotions": ["recognition"]
    }
  ],
  "rationale": {
    "pacing_choice": "Moderate pacing allows for...",
    "transition_style": "Smooth transitions maintain...",
    "emotional_arc": "Builds from shock to recognition..."
  }
}
```

**Estrutura Enriquecida (após Template Selector)**:
```json
{
  "post_id": "post_001",
  "arc": "Hook → Problem → Value → CTA",
  "narrative_pacing": "moderate",
  "transition_style": "smooth",
  "arc_refined": "Hook → Problem → Value → CTA",
  "slides": [
    {
      "slide_number": 1,
      "template_type": "hook",
      "value_subtype": null,
      "template_id": "H_CONTRASTE",              // ADICIONADO pelo Template Selector
      "template_justification": "Semantic Analysis | Professional tone...",  // ADICIONADO
      "template_confidence": 0.87,              // ADICIONADO
      "purpose": "Grab attention with stat",
      "target_emotions": ["shock"],
      "copy_direction": "Open with contrast highlighting gap...",
      "key_elements": ["certificates", "skills"],
      "content_slots": {
        "headline": {"max_chars": 60}
      }
    },
    {
      "slide_number": 2,
      "template_type": "value",
      "value_subtype": "data",
      "template_id": "VD_FONTE",                 // ADICIONADO pelo Template Selector
      "template_justification": "Semantic Analysis | Professional tone...",  // ADICIONADO
      "template_confidence": 0.84,               // ADICIONADO
      "purpose": "Present quantified evidence",
      "target_emotions": ["recognition"]
    }
  ]
}
```

**Campos**:
- `post_id`: Identificador do post
- `arc`: Arco narrativo (alto nível)
- `narrative_pacing`: Ritmo ("fast", "moderate", "deliberate")
- `transition_style`: Estilo de transição ("abrupt", "smooth", "dramatic")
- `arc_refined`: Arco narrativo refinado
- `slides[]`: Lista de slides
  - `slide_number`: Número do slide (1-indexed)
  - `template_type`: Tipo de template ("hook", "value", "cta", "transition")
  - `value_subtype`: Subtipo de valor ("data", "insight", "solution", "example") - apenas para `template_type="value"`
  - `template_id`: ID específico do template (adicionado pelo Template Selector)
  - `template_justification`: Justificativa da seleção (adicionado pelo Template Selector)
  - `template_confidence`: Confiança da seleção 0.0-1.0 (adicionado pelo Template Selector)
  - `purpose`: Propósito do slide
  - `target_emotions[]`: Emoções alvo
  - `copy_direction`: Direção de copy (50-300 palavras)
  - `key_elements[]`: Elementos chave
  - `content_slots{}`: Slots de conteúdo com constraints
    - `headline`: {max_chars: int}
    - `subtitle`: {max_chars: int} (opcional)
    - `body`: {max_chars: int} (opcional)
  - `insights_referenced[]`: IDs dos insights referenciados (opcional)
- `rationale`: Justificativa das decisões (opcional)

---

### 5. slide_content.json

**Fase**: Phase 4 (Slide Generation)  
**Gerado por**: Copywriter (AI)  
**Localização**: Output da Phase 4

**Estrutura**:
```json
{
  "slides": [
    {
      "slide_number": 1,
      "title": {
        "content": "Certificados acumulam poeira. Suas habilidades não.",
        "emphasis": ["certificados", "habilidades"]
      }
    },
    {
      "slide_number": 2,
      "title": {
        "content": "85% das empresas falham em IA – McKinsey",
        "emphasis": ["85%", "IA", "McKinsey"]
      },
      "subtitle": {
        "content": "Mas não é culpa da tecnologia",
        "emphasis": []
      }
    }
  ]
}
```

**Campos**:
- `slides[]`: Lista de conteúdo por slide
  - `slide_number`: Número do slide
  - `title`: Título do slide
    - `content`: Texto do título
    - `emphasis[]`: Lista de palavras/frases a enfatizar
  - `subtitle`: Subtítulo (opcional)
    - `content`: Texto do subtítulo
    - `emphasis[]`: Lista de palavras/frases a enfatizar
  - `body`: Corpo do texto (opcional)
    - `content`: Texto do corpo
    - `emphasis[]`: Lista de palavras/frases a enfatizar

**Nota**: O Copywriter gera conteúdo para **TODOS os slides** em uma única chamada LLM para garantir coerência.

---

### 6. visual_specs.json

**Fase**: Phase 4 (Slide Generation)  
**Gerado por**: Visual Composer (AI)  
**Localização**: Output da Phase 4

**Estrutura**:
```json
{
  "slide_number": 1,
  "background": {
    "type": "gradient",
    "colors": ["#1A1A2E", "#0A0A0A"],
    "direction": "vertical"
  },
  "elements": [
    {
      "type": "glow",
      "position": {"x": 540, "y": 580},
      "color": "#0060FF",
      "intensity": 0.7,
      "radius": 200
    },
    {
      "type": "shape",
      "shape": "circle",
      "position": {"x": 200, "y": 300},
      "color": "#FF6B6B",
      "opacity": 0.5
    }
  ]
}
```

**Campos**:
- `slide_number`: Número do slide
- `background`: Especificação do fundo
  - `type`: Tipo ("gradient", "solid", "image")
  - `colors[]`: Lista de cores (para gradient)
  - `direction`: Direção do gradiente ("vertical", "horizontal", "radial")
  - `image_url`: URL da imagem (se type="image")
- `elements[]`: Lista de elementos visuais
  - `type`: Tipo ("glow", "shape", "line", etc.)
  - `position`: Posição {x: int, y: int}
  - `color`: Cor em hex
  - `intensity`: Intensidade 0.0-1.0 (para glow)
  - `radius`: Raio em pixels (para glow/shape)
  - `opacity`: Opacidade 0.0-1.0
  - `shape`: Forma ("circle", "rectangle", etc.) - para type="shape"

**Nota**: Visual Composer gera design **SEM texto**. O texto é adicionado depois pelo Image Compositor.

---

### 7. text_overlay.json

**Fase**: Phase 4 (Slide Generation)  
**Gerado por**: Prompt Builder (Text) (Code)  
**Localização**: Output da Phase 4

**Estrutura**:
```json
{
  "slide_number": 1,
  "texts": [
    {
      "slot": "headline",
      "content": "85% Fail",
      "position": {"x": 540, "y": 200},
      "font": "Inter Bold",
      "size": 72,
      "color": "#FFFFFF",
      "alignment": "center",
      "emphasis": [
        {
          "text": "85%",
          "color": "#FF6B6B"
        },
        {
          "text": "Fail",
          "color": "#FF6B6B"
        }
      ]
    }
  ]
}
```

**Campos**:
- `slide_number`: Número do slide
- `texts[]`: Lista de textos a renderizar
  - `slot`: Slot do layout ("headline", "subtitle", "body")
  - `content`: Texto a renderizar
  - `position`: Posição {x: int, y: int}
  - `font`: Nome da fonte
  - `size`: Tamanho da fonte em pixels
  - `color`: Cor base em hex
  - `alignment`: Alinhamento ("left", "center", "right")
  - `emphasis[]`: Lista de ênfases
    - `text`: Texto a enfatizar
    - `color`: Cor de ênfase em hex

---

### 8. caption.json

**Fase**: Phase 5 (Finalization)  
**Gerado por**: Caption Writer (AI)  
**Localização**: Output da Phase 5

**Estrutura**:
```json
{
  "platform": "linkedin",
  "full_caption": "85% of AI projects fail—but it's not the tech's fault. Here's what really causes these failures and how to avoid them...",
  "character_count": 1247,
  "hashtags": ["#AI", "#Leadership", "#DigitalTransformation"],
  "mentions": ["@syntropy"]
}
```

**Campos**:
- `platform`: Plataforma alvo
- `full_caption`: Legenda completa
- `character_count`: Contagem de caracteres
- `hashtags[]`: Lista de hashtags sugeridas
- `mentions[]`: Lista de menções (opcional)

---

### 9. validation_report.json

**Fase**: Phase 5 (Finalization)  
**Gerado por**: Quality Validator (Code)  
**Localização**: Output da Phase 5

**Estrutura**:
```json
{
  "post_id": "post_001",
  "score": 0.85,
  "breakdown": {
    "coherence": 0.9,
    "visual": 0.8,
    "textual": 0.85,
    "completeness": 1.0
  },
  "passed": true,
  "warnings": [
    "Slide 3: Text slightly exceeds recommended length"
  ],
  "errors": []
}
```

**Campos**:
- `post_id`: Identificador do post
- `score`: Score geral (0.0-1.0)
- `breakdown{}`: Breakdown por categoria
  - `coherence`: Score de coerência
  - `visual`: Score visual
  - `textual`: Score textual
  - `completeness`: Score de completude
- `passed`: Se passou na validação (boolean)
- `warnings[]`: Lista de avisos
- `errors[]`: Lista de erros

---

## Estruturas de Templates

### TextualTemplate

**Localização**: `src/templates/textual_templates.py`

**Estrutura**:
```python
TextualTemplate(
    id="H_CONTRASTE",                    # Identificador único
    module_type="hook",                  # Categoria
    function="Show clear contrast",      # Descrição do propósito
    structure="[Antes] vs. [Depois]",   # Padrão de texto com placeholders
    length_range=(50, 80),              # Limites de caracteres
    tone="binary and clear",            # Tom recomendado
    example="Manual vs. automated",      # Exemplo de uso
    keywords=["vs", "contrast", ...],   # Palavras-chave para matching
    semantic_description="Clear contrast between before and after..."  # Para matching semântico
)
```

**Campos**:
- `id`: ID único do template (ex: "H_CONTRASTE")
- `module_type`: Tipo de módulo ("hook", "valor_dado", "valor_insight", "valor_solucao", "valor_exemplo", "cta", "transition")
- `function`: Descrição do propósito
- `structure`: Padrão de texto com placeholders (ex: "[Antes] vs. [Depois]")
- `length_range`: Tupla (min, max) de caracteres
- `tone`: Tom recomendado
- `example`: Exemplo de uso
- `keywords[]`: Lista de palavras-chave para matching
- `semantic_description`: Descrição semântica para matching com embeddings

**Total**: 46 templates pré-definidos

---

## Estruturas de Libraries

### Palette

**Localização**: `libraries/palettes/`

**Estrutura**:
```json
{
  "dark_professional_01": {
    "theme": "dark",
    "primary": "#000000",
    "accent": "#0060FF",
    "cta": "#FF6B6B",
    "background": "#0A0A0A",
    "text": "#FFFFFF",
    "text_secondary": "#CCCCCC"
  }
}
```

### Typography

**Localização**: `libraries/typography/`

**Estrutura**:
```json
{
  "inter_clean": {
    "heading_font": "Inter Bold",
    "body_font": "Inter Regular",
    "sizes": {
      "heading": 72,
      "subtitle": 48,
      "body": 24
    },
    "line_height": 1.2
  }
}
```

### Layout

**Localização**: `libraries/layouts/`

**Estrutura**:
```json
{
  "centered_headline": {
    "slots": [
      {
        "name": "headline",
        "position": {"x": 540, "y": 400},
        "max_chars": 60,
        "alignment": "center"
      }
    ]
  }
}
```

---

## Referências

- **Código**:
  - `src/coherence/brief.py` - CoherenceBrief
  - `src/templates/textual_templates.py` - TextualTemplate
  - `src/templates/library.py` - Template Library Manager

- **Documentação Relacionada**:
  - `docs/architecture/memory_management.md` - Coherence Brief detalhado
  - `docs/architecture/agents.md` - Agentes que usam essas estruturas
  - `docs/architecture/tools.md` - Ferramentas que processam essas estruturas
