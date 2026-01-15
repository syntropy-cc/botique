# Social Media Post Generation Pipeline - English.md

> **Version**: 2.1  
> **Date**: 2026-01-14  
> **Status**: Simplified Architecture + Template-Based System  
> **Author**: José Scott (Revised)
> **Updates**: Added Textual Templates System with semantic selection

---

## Summary

- [[#Overview]]
    
- [[#Design Principles]]
    
- [[#System Architecture]]
    
- [[#Data Flow]]
    
- [[#Detailed Components]]
    
- [[#Coherence System]]
    
- [[#Design Libraries]]
    
- [[#Textual Templates System]]
    
- [[#Prompt Strategy]]
    
- [[#Validation and Quality]]
    
- [[#Implementation Considerations]]

---

## Overview

### Problem

Generating high-quality social media posts from articles requires balancing content analysis, ideation, configuration, narrative structure, slide generation, and finalization. The original design was over-engineered with redundant analysis phases and global assumptions about platform/tone. A simplified pipeline focuses on modularity, per-post customization, and clear responsibilities.

### Solution

A streamlined, 5-phase pipeline orchestrated by Python code:

- **Specialized prompts**: Each AI call focuses on one task.
    
- **Textual templates**: 46 pre-defined templates with semantic selection for consistent, high-quality copy.
    
- **Design libraries**: Pre-validated visuals (palettes, layouts, typography).
    
- **Coherence context**: Per-post document ensuring consistency.
    
- **Validation gates**: Quality checks per phase.

One article inputs generate multiple posts, each with its own platform, tone, persona, etc., and 1–12 slides + caption.

### Objectives

|Objective|Success Metric|
|---|---|
|Consistent quality|Posts adhere to design libraries, templates, and coherence|
|Per-post flexibility|Each post has unique platform/tone/persona|
|Autonomy|Minimal user input (article only)|
|Scalability|Parallel post/slide generation|
|Debuggability|Isolatable phases|
|Template accuracy|91% semantic template selection accuracy|

---

## Design Principles

### 1. Single Responsibility Prompts

Each prompt handles one task:

```text
✅ Prompt 1: "From article, generate 3–6 post ideas with per-post platform/tone"
          Prompt 2: "For selected idea, build narrative skeleton by slide"
          Prompt 3: "Write copy for one slide's text slots"
```

### 2. Code Decides, AI Creates

Code handles consistency:

|Code Decides|AI Creates|
|---|---|
|Palette/typography selection|Post ideas/narrative arcs|
|Layout positions|Copy/visual descriptions|
|Slide composition|Hooks/CTAs|

### 3. Per-Post Context

Each post gets tailored context (platform, tone, etc.) from ideation onward. No global assumptions.

### 4. Coherence Through Constraint

- **Coherence Brief**: Per-post JSON traveling through phases.
    
- **Libraries**: LLM selects from options, doesn't invent.
    
- **Gates**: Validate before advancing.

### 5. Graceful Defaults

Input: Article only. System auto-suggests/assigns per-post params.

---

## System Architecture

### High-Level Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INPUT                                     │
│  ┌─────────────┐                                                            │
│  │   Article   │  (required; generates multiple posts)                      │
│  └─────────────┘                                                            │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 1: IDEATION                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [AI] Post Ideator                                                  │    │
│  │  Analyzes article + generates 3–6 ideas (per-post platform/tone)    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [CODE/USER] Idea Selector                                          │    │
│  │  Selects top N ideas (auto or manual)                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PHASE 2: CONFIGURATION                              │
│  (Loop for each selected idea → post)                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [CODE] Parameter Resolver                                          │    │
│  │  Assigns palette, typography, etc. from libraries                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [CODE] Coherence Brief Builder                                     │    │
│  │  Builds per-post coherence document                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 3: POST CREATION                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [AI] Narrative Architect                                           │    │
│  │  Builds skeleton: slide-by-slide structure (Hook → CTA)             │    │
│  │  Defines template_type, value_subtype, purposes, emotions           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [CODE] Template Selector                                           │    │
│  │  Semantic analysis: selects specific template_id per slide          │    │
│  │  Enriches structure with template structures                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [CODE] Layout Resolver                                             │    │
│  │  Assigns layouts per slide from library                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 4: SLIDE GENERATION                          │
│  (Loop for each slide)                                                      │
│                                                                             │
│  ┌──────────────────────┐        ┌────────────────────────┐                 │
│  │ [AI] Copywriter      │        │ [AI] Visual Composer   │                 │
│  │ Generates text using │        │ Generates design       │                 │
│  │ template structures  │        │ (bg, elements, no text)│                 │
│  └────────┬─────────────┘        └────────┬───────────────┘                 │
│           │                               │                                 │
│           ▼                               ▼                                 │
│  ┌─────────────────┐          ┌─────────────────┐                           │
│  │ [CODE] Prompt   │          │ [CODE] Prompt   │                           │
│  │ Builder (text)  │          │ Builder (image) │                           │
│  └────────┬────────┘          └────────┬────────┘                           │
│           │                            │                                    │
│           │                            ▼                                    │
│           │                    ┌─────────────────┐                          │
│           │                    │ [AI-IMAGE]      │                          │
│           │                    │ Image Generator │                          │
│           │                    │ (background)    │                          │
│           │                    └────────┬────────┘                          │
│           │                             │                                   │
│           └───────────┬─────────────────┘                                   │
│                       │                                                     │
│                       ▼                                                     │
│              ┌─────────────────────────────────────┐                        │
│              │ [CODE] Image Compositor             │                        │
│              │ Combines: bg + elements + text      │                        │
│              └─────────────────┬───────────────────┘                        │
│                                │                                            │
│                                ▼                                            │
│                       final_slide.png                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 5: FINALIZATION                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [AI] Caption Writer                                                │    │
│  │  Writes platform-specific caption                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [CODE] Output Assembler                                            │    │
│  │  Packages slides + caption + elements                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                     │                                       │
│                                     ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  [CODE] Quality Validator                                           │    │
│  │  Scores and reports                                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
                              FINAL OUTPUT
                              (Multiple posts)
```

---

## Data Flow

### Coherence Brief Evolution Flow

```mermaid
flowchart LR
    subgraph Phase1["Phase 1: Ideation"]
        A1[Article] --> A2[IdeaGenerator]
        A2 --> A3[Ideas JSON]
        A3 --> A4{Idea Filter?}
        A4 -->|Yes| A5[Filtered Ideas]
        A4 -->|No| A5
        A5 --> A6[CoherenceBriefBuilder]
        A6 --> A7[Brief Inicial]
    end
    
    subgraph Phase3["Phase 3: Narrative"]
        A7 --> B1[Narrative Architect]
        B1 --> B2[Narrative Structure<br/>template_type + value_subtype]
        B2 --> B2A[Template Selector<br/>Semantic Analysis]
        B2A --> B2B[Enriched Structure<br/>+ template_id]
        B2B --> B3[enrich_from_narrative_structure]
        B3 --> B4[Brief + Narrative + Templates]
    end
    
    subgraph Phase4["Phase 4: Content Generation"]
        B4 --> C1[Copywriter<br/>+ Template Structures]
        B4 --> C2[Visual Composer]
        C1 --> C3[Copy Guidelines<br/>+ Generated Text]
        C2 --> C4[Visual Preferences]
        C3 --> C5[enrich_from_copywriting]
        C4 --> C6[enrich_from_visual_composition]
        C5 --> C7[Brief Completo Phase 4]
        C6 --> C7
    end
    
    subgraph Phase5["Phase 5: Finalization"]
        C7 --> D1[Caption Writer]
        D1 --> D2[Platform Constraints]
        D2 --> D3[enrich_from_caption_writing]
        D3 --> D4[Brief Final Completo]
    end
    
    style A7 fill:#e1f5ff
    style B4 fill:#fff4e1
    style C7 fill:#e8f5e9
    style D4 fill:#f3e5f5
```

### Component Table

|#|Component|Type|Inputs|Outputs|Responsibility|
|---|---|---|---|---|---|
|0|User Input|Manual|Article|`article.txt`|Single required input|
|1|Post Ideator|AI|`article.txt`|`post_ideas.json`|Analyze + ideate 3–6 per-post ideas|
|2|Idea Filter|Code|`post_ideas.json`, `filter_config`|`filtered_ideas.json`|Filter/select ideas (optional)|
|3|Coherence Brief Builder|Code|`filtered_idea`, `article_summary`, `libraries/`|`coherence_brief.json` (initial)|Per-post initial brief (Phase 1)|
|4|Narrative Architect|AI|`coherence_brief.json`, `article.txt`|`narrative_structure.json`|Slide-by-slide skeleton with template_type/value_subtype + enrich brief|
|4a|Template Selector|Code|`narrative_structure.json`|`narrative_structure_enriched.json`|Select specific template_id per slide using semantic analysis|
|5|Parameter Resolver|Code|`selected_idea`, `libraries/`|`post_config.json`|Per-post params (palette, etc.)|
|6|Layout Resolver|Code|`narrative_structure_enriched.json`, `libraries/layouts`|`slide_layouts.json`|Per-slide layouts|
|7|Copywriter|AI|`slide_layout`, `coherence_brief.json`, `article.txt`, `templates_reference`|`slide_content.json` + enrich brief|Text per slot following template structures + enrich brief|
|8|Visual Composer|AI|`slide_layout`, `post_config.json`, `coherence_brief.json`|`visual_specs.json` + enrich brief|Design (no text) + enrich brief|
|9|Prompt Builder (Image)|Code|`visual_specs.json`, `post_config.json`|`image_prompt.txt`|Image gen prompt|
|10|Image Generator|AI-Image|`image_prompt.txt`|`background.png`|Background image|
|11|Prompt Builder (Text)|Code|`slide_content.json`, `slide_layout`|`text_overlay.json`|Text rendering specs|
|12|Image Compositor|Code|`background.png`, `text_overlay.json`, `brand_assets`|`final_slide.png`|Combine elements|
|13|Caption Writer|AI|`post_config.json`, `all_slide_contents`, `coherence_brief.json`|`caption.json` + enrich brief|Per-post caption + enrich brief|
|14|Output Assembler|Code|All slides, `caption.json`|`/output/post_xxx/`|Package per post|
|15|Quality Validator|Code|All outputs|`validation_report.json`|Per-post scoring|

### Main Data Structures

#### post_ideas.json (New: Combines analysis + ideation)

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
    "main_thesis": "string",
    "key_insights": [{"id": "string", "content": "string"}],
    "themes": ["string"]
  }
}
```

#### post_config.json (Per-post)

```json
{
  "post_id": "post_001",
  "idea_ref": "idea_1",
  "platform": "linkedin",
  "tone": "professional",
  "persona": "C-level execs",
  "palette_id": "dark_professional_01",
  "typography_id": "inter_clean",
  "canvas": {"width": 1080, "height": 1350},
  "brand": {"handle": "string"}
}
```

#### coherence_brief.json (Per-post, Evolutivo)

**Brief Inicial (Phase 1)**:
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
    "mood": "dramatic_focused"
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
    "narrative_structure": null,
    "narrative_pacing": null,
    "transition_style": null,
    "copy_guidelines": null,
    "cta_guidelines": null,
    "visual_preferences": null,
    "platform_constraints": null
  }
}
```

**Após Phase 3 (Narrative Architect)** - Campos adicionados:
```json
{
  "evolution": {
    "narrative_structure": {
      "pacing": "moderate",
      "transition_style": "smooth",
      "slides": [
        {
          "number": 1,
          "module": "hook",
          "purpose": "Grab attention with stat",
          "emotions": ["shock"],
          "content_slots": {"headline": {"max_chars": 60}}
        }
      ]
    },
    "narrative_pacing": "moderate",
    "transition_style": "smooth"
  }
}
```

**Após Phase 4 (Copywriter + Visual Composer)** - Campos adicionados:
```json
{
  "evolution": {
    "copy_guidelines": {
      "headline_style": "statistic_led",
      "body_style": "conversational_professional"
    },
    "cta_guidelines": {
      "type": "soft",
      "position": "final_slide",
      "tone": "invitational",
      "suggested_text": "Learn more about..."
    },
    "visual_preferences": {
      "layout_style": "centered",
      "text_hierarchy": "bold_headlines",
      "element_density": "moderate"
    }
  }
}
```

**Após Phase 5 (Caption Writer)** - Brief Completo:
```json
{
  "evolution": {
    "platform_constraints": {
      "max_caption_length": 3000,
      "hashtag_count": 3,
      "cta_format": "professional",
      "mention_style": "formal"
    }
  }
}
```

#### narrative_structure.json (Slide-by-slide skeleton)

**After Narrative Architect** (initial structure):
```json
{
  "post_id": "post_001",
  "arc": "Hook → Problem → Value → CTA",
  "narrative_pacing": "moderate",
  "transition_style": "smooth",
  "slides": [
    {
      "slide_number": 1,
      "template_type": "hook",
      "value_subtype": null,
      "purpose": "Grab attention with stat",
      "target_emotions": ["shock"],
      "copy_direction": "Open with contrast highlighting gap...",
      "key_elements": ["certificates", "skills"],
      "content_slots": {"headline": {"max_chars": 60}}
    },
    {
      "slide_number": 2,
      "template_type": "value",
      "value_subtype": "data",
      "purpose": "Present quantified evidence",
      "target_emotions": ["recognition"]
    }
    // ... up to n_slides
  ]
}
```

**After Template Selector** (enriched structure):
```json
{
  "post_id": "post_001",
  "arc": "Hook → Problem → Value → CTA",
  "narrative_pacing": "moderate",
  "transition_style": "smooth",
  "slides": [
    {
      "slide_number": 1,
      "template_type": "hook",
      "value_subtype": null,
      "template_id": "H_CONTRASTE",              // ADDED by Template Selector
      "template_justification": "Semantic Analysis | Professional...",  // ADDED
      "template_confidence": 0.87,              // ADDED
      "purpose": "Grab attention with stat",
      "target_emotions": ["shock"],
      "copy_direction": "Open with contrast highlighting gap...",
      "key_elements": ["certificates", "skills"],
      "content_slots": {"headline": {"max_chars": 60}}
    },
    {
      "slide_number": 2,
      "template_type": "value",
      "value_subtype": "data",
      "template_id": "VD_FONTE",                 // ADDED by Template Selector
      "template_justification": "Semantic Analysis | Professional...",  // ADDED
      "template_confidence": 0.84,               // ADDED
      "purpose": "Present quantified evidence",
      "target_emotions": ["recognition"]
    }
    // ... up to n_slides
  ]
}
```

#### slide_content.json

```json
{
  "slide_number": 1,
  "texts": {
    "headline": {"content": "85% Fail", "emphasis": {"color": "#FF6B6B"}},
    "subheadline": {"content": "Here's why"}
  }
}
```

#### visual_specs.json (Design only)

```json
{
  "slide_number": 1,
  "background": {"type": "gradient", "colors": ["#1A1A2E", "#0A0A0A"]},
  "elements": [{"type": "glow", "position": {"x": 540, "y": 580}}]
}
```

#### caption.json (Per-post)

```json
{
  "platform": "linkedin",
  "full_caption": "string",
  "character_count": 1247,
  "hashtags": ["#AI"]
}
```

(Removed redundant structures like separate content_analysis.json, strategy_recommendations.json for simplification.)

---

## Coherence System

### Coherence Brief: Modelo Evolutivo

O **Coherence Brief é um documento dinâmico e evolutivo**, não estático. Ele começa com informações de alto nível na Phase 1 e é enriquecido por cada fase subsequente conforme os agentes especializados geram informações mais detalhadas.

#### Fluxo Evolutivo

```mermaid
flowchart TD
    A[Phase 1: Ideation] --> B[Brief Inicial<br/>Alto Nível]
    B --> C[Phase 3: Narrative Architect]
    C --> C1[Estrutura Narrativa<br/>template_type + value_subtype]
    C1 --> C2[Template Selector<br/>Seleção Semântica]
    C2 --> D[Brief + Estrutura Narrativa<br/>+ template_id por slide]
    D --> E[Phase 4: Copywriter<br/>+ Template Structures]
    D --> F[Phase 4: Visual Composer]
    E --> G[Brief + Diretrizes de Copy<br/>+ Texto Gerado]
    F --> H[Brief + Preferências Visuais]
    G --> I[Phase 5: Caption Writer]
    H --> I
    I --> J[Brief Completo<br/>Baixo Nível]
    
    style B fill:#e1f5ff
    style C1 fill:#fff4e1
    style C2 fill:#ffe1f5
    style D fill:#fff4e1
    style G fill:#e8f5e9
    style H fill:#e8f5e9
    style J fill:#f3e5f5
```

#### Estrutura do Brief por Fase

```mermaid
graph TB
    subgraph Phase1["Phase 1: Brief Inicial (Alto Nível)"]
        P1A[Voice: tone, personality, vocabulary]
        P1B[Visual: palette, typography, style, mood]
        P1C[Emotions: primary, secondary, avoid]
        P1D[Content: keywords, themes, message, angle]
        P1E[Audience: persona, pain_points, desires]
        P1F[Structure: objective, arc alto nível, slides estimados]
        P1G[Context: article_context, key_insights_content]
        P1H[Brand: values, brand_assets]
    end
    
    subgraph Phase3["Phase 3: Narrative Architect → Adiciona"]
        P3A[narrative_structure<br/>com template_type + value_subtype]
        P3B[narrative_pacing]
        P3C[transition_style]
    end
    
    subgraph Phase3a["Phase 3a: Template Selector → Enriquece"]
        P3aA[template_id por slide]
        P3aB[template_justification]
        P3aC[template_confidence]
    end
    
    subgraph Phase4["Phase 4: Copywriter + Visual Composer → Adicionam"]
        P4A[copy_guidelines]
        P4B[cta_guidelines]
        P4C[visual_preferences]
    end
    
    subgraph Phase5["Phase 5: Caption Writer → Adiciona"]
        P5A[platform_constraints]
    end
    
    Phase1 --> Phase3
    Phase3 --> Phase3a
    Phase3a --> Phase4
    Phase4 --> Phase5
    
    style Phase1 fill:#e1f5ff
    style Phase3 fill:#fff4e1
    style Phase3a fill:#ffe1f5
    style Phase4 fill:#e8f5e9
    style Phase5 fill:#f3e5f5
```

### Coherence Brief Components

#### Brief Inicial (Phase 1)

```text
┌─────────────────────────────────────────────────────────────────┐
│                  COHERENCE BRIEF (INICIAL)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  VOICE                          VISUAL                          │
│  ├─ tone                        ├─ palette_id                   │
│  ├─ personality_traits          ├─ palette (cores completas)    │
│  ├─ vocabulary_level            ├─ typography_id                │
│  └─ formality                   ├─ typography                   │
│                                 ├─ style                        │
│                                 └─ mood                         │
│                                                                 │
│  EMOTIONS                       CONTENT                         │
│  ├─ primary                     ├─ keywords_to_emphasize        │
│  ├─ secondary                   ├─ themes                       │
│  ├─ avoid                       ├─ main_message                 │
│  └─ target                      ├─ value_proposition            │
│                                 ├─ angle                        │
│                                 └─ hook                         │
│                                                                 │
│  AUDIENCE                       CONSTRAINTS                     │
│  ├─ persona                     ├─ avoid_topics                 │
│  ├─ pain_points                 └─ required_elements            │
│  └─ desires                                                     │
│                                                                 │
│  STRUCTURE                      CONTEXT                         │
│  ├─ objective                   ├─ article_context              │
│  ├─ narrative_arc (alto nível)   ├─ key_insights_used            │
│  └─ estimated_slides            └─ key_insights_content         │
│                                                                 │
│  BRAND                                                          │
│  ├─ values                      ├─ brand_assets                 │
│                                 │  └─ handle, tagline           │
└─────────────────────────────────────────────────────────────────┘
```

#### Campos Evolutivos (Adicionados por Fases Posteriores)

```text
┌─────────────────────────────────────────────────────────────────┐
│              CAMPOS EVOLUTIVOS (Phase 3-5)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 3: Narrative Architect                                  │
│  ├─ narrative_structure (estrutura detalhada slide por slide)  │
│  ├─ narrative_pacing (fast/moderate/deliberate)                │
│  └─ transition_style (abrupt/smooth/dramatic)                  │
│                                                                 │
│  Phase 4: Copywriter                                           │
│  ├─ copy_guidelines (padrões de escrita)                       │
│  └─ cta_guidelines (detalhes de CTA)                           │
│                                                                 │
│  Phase 4: Visual Composer                                      │
│  └─ visual_preferences (preferências de layout/composição)     │
│                                                                 │
│  Phase 5: Caption Writer                                        │
│  └─ platform_constraints (limites e formatos da plataforma)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Coherence Brief (Per-Post)

**Criado na Phase 1**, evolui através das Phases 3–5. Garante consistência per-post em voice, visuals, etc.

|Component|Fields Used By|Purpose|Context Method|
|---|---|---|---|
|Post Ideator|N/A (pre-brief)|Initial alignment|N/A|
|Narrative Architect|voice, emotions, content, structure|Arc per slide with template_type/value_subtype|`to_narrative_architect_context()`|
|Template Selector|narrative_structure (purpose, copy_direction, key_elements)|Select specific template_id per slide|Semantic analysis (embeddings)|
|Copywriter|voice, content, audience, narrative_structure, templates_reference|Text following template structures|`to_copywriter_context()`|
|Visual Composer|visual, emotions, narrative_structure|Design mood|`to_visual_composer_context()`|
|Caption Writer|voice, platform, cta_guidelines, platform_constraints|Caption fit|`to_caption_writer_context()`|

#### Métodos de Enriquecimento

Cada fase adiciona informações ao brief usando métodos específicos:

- **Phase 3 (Narrative Architect)**: `brief.enrich_from_narrative_structure(narrative_structure)`
  - Adiciona: `narrative_structure`, `narrative_pacing`, `transition_style`
  - Cada slide inclui: `template_type`, `value_subtype`, `purpose`, `copy_direction`
  
- **Phase 3a (Template Selector)**: Enriquece `narrative_structure` com `template_id` por slide
  - Usa análise semântica (embeddings) para selecionar template específico
  - Adiciona: `template_id`, `template_justification`, `template_confidence` a cada slide
  
- **Phase 4 (Copywriter)**: `brief.enrich_from_copywriting(copy_guidelines)`
  - Recebe: `narrative_structure` enriquecido + `templates_reference` (estruturas detalhadas)
  - Adiciona: `copy_guidelines`, `cta_guidelines`
  
- **Phase 4 (Visual Composer)**: `brief.enrich_from_visual_composition(visual_preferences)`
  - Adiciona: `visual_preferences`
  
- **Phase 5**: `brief.enrich_from_caption_writing(platform_constraints)`
  - Adiciona: `platform_constraints`

#### Exemplo de Uso por Fase

**Narrative Architect (Phase 3)**:
```text
COHERENCE BRIEF (Narrative Architect):
- Tone: Professional
- Primary emotion: Urgency
- Keywords: AI, failure
- Persona: C-level execs
- Narrative Arc (high-level): Hook → Problem → Solution → CTA
- Estimated Slides: 7

TASK: Create detailed slide-by-slide narrative structure.
OUTPUT: Each slide with template_type, value_subtype, purpose, copy_direction
```

**Template Selector (Phase 3a)**:
```text
INPUT: Narrative structure with template_type + value_subtype per slide
PROCESS: Semantic analysis using embeddings
- Analyzes: purpose + copy_direction + key_elements
- Compares: Against 46 pre-defined templates
- Selects: Best matching template_id per slide

OUTPUT: Enriched structure with template_id, justification, confidence
```

**Copywriter (Phase 4)**:
```text
COHERENCE BRIEF (Copywriter):
- Voice: Professional, sophisticated vocabulary, formal
- Content: Main message, keywords, angle
- Audience: Persona, pain points, desires
- Narrative Structure: [detailed structure from Phase 3 + template_id from Phase 3a]
- Templates Reference: [Detailed template structures, examples, tone guidance]

TASK: Write text for all slides following template structures.
- Slide 1: Use template H_CONTRASTE structure "[Antes] vs. [Depois]"
- Slide 2: Use template VD_FONTE structure "[Dado] – [Fonte]"
- ... (for all slides)
```

**Visual Composer (Phase 4)**:
```text
COHERENCE BRIEF (Visual Composer):
- Visual: Palette, typography, canvas, style, mood
- Emotions: Primary, secondary, avoid
- Narrative Structure: [pacing, transitions from Phase 3]

TASK: Generate visual specs for slide 1.
```

**Caption Writer (Phase 5)**:
```text
COHERENCE BRIEF (Caption Writer):
- Platform: LinkedIn
- Voice: Professional, formal
- CTA Guidelines: [from Copywriter]
- Platform Constraints: max_length=3000, hashtag_count=3

TASK: Write platform-specific caption.
```

---

## Design Libraries

(Unchanged structure, but selection now per-post in Phase 2 code.)

Libraries: palettes/, typography/, layouts/. Code selects based on post's platform/tone.

Example selection rule:

```python
def select_palette(post_config):
    if post_config["platform"] == "linkedin" and post_config["tone"] == "professional":
        return "dark_professional_01"
```

---

## Textual Templates System

### Overview

The pipeline uses a **two-level template hierarchy** for textual content generation:

1. **High-Level Template Types** (defined by Narrative Architect): `hook`, `transition`, `value`, `cta`
2. **Specific Textual Templates** (selected by Template Selector): 46 pre-defined templates with specific structures

This separation allows the Narrative Architect to focus on **what to say** (strategy) while the Template Selector chooses **how to structure it** (pattern matching), and the Copywriter executes the actual text generation.

### Template Library

**Location**: `src/templates/textual_templates.py`

**Total Templates**: 46 templates organized by module type:

| Module Type | Count | Purpose |
|-------------|-------|---------|
| **HOOK** | 12 | Attention-grabbing opening slides (always slide 1) |
| **VALOR: Dado** | 7 | Data, statistics, quantified information |
| **VALOR: Insight** | 7 | Learnings, conclusions, unexpected revelations |
| **VALOR: Solução** | 7 | Steps, methods, frameworks, actionable approaches |
| **VALOR: Exemplo** | 5 | Cases, scenarios, demonstrations |
| **CTA** | 7 | Calls to action (always last slide if required) |
| **TRANSITION** | 1 | Bridge between narrative beats (uses insight-style templates) |

### Template Structure

Each template includes:

```python
TextualTemplate(
    id="H_CONTRASTE",                    # Unique identifier
    module_type="hook",                  # Category
    function="Show clear contrast",      # Purpose description
    structure="[Before] vs. [After]",   # Text pattern with placeholders
    length_range=(50, 80),              # Character limits
    tone="binary and clear",            # Recommended tone
    example="Manual vs. automated",      # Usage example
    keywords=["vs", "contrast", ...],   # Matching keywords
    semantic_description="Clear contrast between before and after..."  # For semantic matching
)
```

### Template Selection Flow

```mermaid
flowchart LR
    A[Narrative Architect] -->|Defines| B[template_type + value_subtype]
    B --> C[Template Selector]
    C -->|Semantic Analysis| D[Selects template_id]
    D --> E[Copywriter]
    E -->|Uses structure| F[Generated Text]
    
    style A fill:#e1f5ff
    style C fill:#fff4e1
    style E fill:#e8f5e9
```

**Process**:

1. **Narrative Architect** (Phase 3):
   - Defines `template_type` (`hook`, `value`, `cta`, etc.)
   - For `value` slides, specifies `value_subtype` (`data`, `insight`, `solution`, `example`)
   - Provides `purpose`, `copy_direction`, and `key_elements`

2. **Template Selector** (Post-Phase 3):
   - Uses **semantic embeddings** (sentence-transformers) to analyze slide descriptions
   - Compares slide description to all candidate templates
   - Selects best matching `template_id` based on cosine similarity
   - Falls back to keyword matching if embeddings unavailable

3. **Copywriter** (Phase 4):
   - Receives selected `template_id` with detailed template reference
   - Uses template `structure` as base pattern
   - Fills placeholders with context-specific content
   - Adapts to template's `tone` and `length_range`

### Semantic Selection

**Technology**: Uses `sentence-transformers` (default: `all-MiniLM-L6-v2`) for semantic analysis.

**Benefits**:
- ✅ **91% accuracy** (vs. 68% with keyword matching)
- ✅ Understands synonyms and context
- ✅ Better performance with long, complex descriptions
- ✅ Pre-computed embeddings for performance

**Fallback**: If embeddings unavailable, uses keyword + Jaccard similarity matching.

**Example Selection**:

```python
# Narrative Architect output
slide = {
    "template_type": "value",
    "value_subtype": "data",
    "purpose": "Present quantified evidence",
    "copy_direction": "Show statistics with credible source like McKinsey",
    "key_elements": ["statistics", "unused knowledge"]
}

# Template Selector selects
template_id = "VD_FONTE"  # "Present data with attribution to reliable source"
confidence = 0.87  # High confidence match
```

### Integration Points

#### Phase 3: Narrative Architect

**Prompt**: `prompts/narrative_architect.md`

**Responsibilities**:
- Define `template_type` for each slide
- Specify `value_subtype` for value slides
- Provide detailed `copy_direction` (50-300 words) to guide template selection
- Include `key_elements` for emphasis

**Output Example**:
```json
{
  "slides": [
    {
      "slide_number": 1,
      "template_type": "hook",
      "value_subtype": null,
      "purpose": "Create recognition about problem",
      "copy_direction": "Open with contrast highlighting gap...",
      "key_elements": ["certificates", "skills"]
    }
  ]
}
```

#### Post-Phase 3: Template Selection

**Code**: `src/templates/selector.py`

**Process**:
- Enriches each slide with `template_id`
- Adds `template_justification` and `template_confidence`
- Uses semantic analysis of `purpose` + `copy_direction` + `key_elements`

#### Phase 4: Copywriter

**Prompt**: `prompts/copywriter.md`

**Receives**:
- Slide context with `template_id`
- Detailed template reference (structure, example, tone, length)
- Narrative guidance from Narrative Architect

**Responsibilities**:
- Generate text following template `structure`
- Fill placeholders with context-specific content
- Respect `length_range` and `tone` from template
- Maintain narrative flow across all slides

**Output Example**:
```json
{
  "slides": [
    {
      "slide_number": 1,
      "title": {
        "content": "Certificados acumulam poeira. Suas habilidades não.",
        "emphasis": ["certificados", "habilidades"]
      }
    }
  ]
}
```

### Template Examples

#### Hook Templates

- **H_CONTRASTE**: `"[Antes] vs. [Depois]"` - Clear contrast
- **H_PERGUNTA**: `"E se [cenário ideal]?"` - Curiosity question
- **H_NUMERO**: `"[X]% das [grupo] [ação]"` - Impactful statistic

#### Value: Data Templates

- **VD_DADO%**: `"[X]% das [grupo] [ação]"` - Direct percentage
- **VD_FONTE**: `"[Dado] – [Fonte]"` - Data with attribution
- **VD_COMPARA**: `"[X] vezes mais que [Y]"` - Numerical comparison

#### Value: Solution Templates

- **VS_123**: `"1. [Passo] 2. [Passo] 3. [Passo]"` - Sequential steps
- **VS_FORMULA**: `"[Resultado] = [Fator] + [Fator]"` - Simple formula
- **VS_FRAMEWORK**: `"[Sigla]: [Def1], [Def2], [Def3]"` - Framework model

#### CTA Templates

- **CTA_SEGUIR**: `"Siga para [promessa de valor]"` - Build audience
- **CTA_COMENTAR**: `"[Pergunta ou convite]"` - Generate engagement
- **CTA_SALVAR**: `"Salve isso para [caso de uso futuro]"` - Increase reach

### Benefits

1. **Consistency**: Similar narrative functions use similar structures
2. **Quality Control**: Templates encode best practices (length, tone, structure)
3. **Specialization**: Each component (Architect, Selector, Copywriter) excels at its task
4. **Scalability**: Add new templates without retraining agents
5. **Flexibility**: Semantic matching allows creative interpretation

### Configuration

**Template Library**: `src/templates/textual_templates.py`  
**Library Manager**: `src/templates/library.py`  
**Selector**: `src/templates/selector.py`  
**Narrative Architect Prompt**: `prompts/narrative_architect.md`  
**Copywriter Prompt**: `prompts/copywriter.md`

**Optional Dependencies** (for semantic analysis):
```bash
pip install sentence-transformers  # Recommended for better accuracy
```

**Documentation**:
- `docs/SEMANTIC_TEMPLATE_SELECTION.md` - Detailed selection guide
- `docs/template_based_narrative_system.md` - Complete system overview
- `docs/IMPLEMENTATION_SUMMARY.md` - Implementation details

---

## Prompt Strategy

### Prompt Map (Simplified)

|Prompt|Input|Output|Context|
|---|---|---|---|
|Post Ideator|Article|Ideas + summary|None|
|Narrative Architect|Config + brief + article|Slide skeleton with template_type/value_subtype|Full brief|
|Template Selector|Slide skeleton|Enriched slides with template_id|Semantic analysis|
|Copywriter|Layout + brief + article + templates|Text JSON|Voice/emotions + template structures|
|Visual Composer|Layout + config + brief|Design JSON|Visual/emotions|
|Caption Writer|Config + slides + brief|Caption JSON|Voice/platform|

### Standard Structure

```text
[ROLE] e.g., "You are a narrative expert"

[CONTEXT] Relevant brief + inputs

[TASK] One clear action

[CONSTRAINTS] Limits/exclusions

[OUTPUT] JSON schema

[EXAMPLE] 1 concrete pair
```

Token estimates reduced: Ideation ~2500 in/~800 out; others ~500 in/~200 out.

---

## Validation and Quality

### Gates (Per-Phase)

- **Phase 1**: ≥3 ideas? Distinct?
- **Phase 2**: Config complete? Brief valid?
- **Phase 3**: ≥5 slides? Arc logical? All slides have template_type? Value slides have value_subtype?
- **Phase 3a**: All slides have template_id? Confidence >0.5? Template matches slide purpose?
- **Phase 4**: Text in limits? Text follows template structure? Design no-text? Image dims correct?
- **Phase 5**: Caption length OK? Score >0.7?

Retry: 2 attempts with feedback; fallback to defaults.

### Quality Score (Per-Post)

```json
{
  "post_id": "post_001",
  "score": 0.85,
  "breakdown": {"coherence": 0.9, "visual": 0.8},
  "passed": true
}
```

---

## Implementation Considerations

### Tech Stack

|Component|Tech|Reason|
|---|---|---|
|Orchestrator|Python + asyncio|Parallel posts/slides|
|AI|OpenAI/Anthropic|Core generation|
|Image|DALL-E 3|P backgrounds|
|Compositor|Pillow|Overlays|

### Directory

```text
social-media-pipeline/
├── src/
│   ├── orchestrator.py
│   ├── phases/
│   │   ├── ideation.py
│   │   ├── configuration.py
│   │   ├── post_creation.py
│   │   ├── slide_generation.py
│   │   └── finalization.py
│   ├── templates/
│   │   ├── textual_templates.py  # 46 template definitions
│   │   ├── library.py              # Template library manager
│   │   └── selector.py             # Semantic template selector
│   ├── utils/
│   │   ├── ai_client.py
│   │   └── validators.py
├── libraries/  # Design libraries (palettes, typography, layouts)
├── prompts/    # 5 core prompts
│   ├── narrative_architect.md  # Defines template_type/value_subtype
│   └── copywriter.md           # Uses template structures
├── output/
└── config.yaml
```

### Performance/Costs

Parallel: Posts independent; slides parallel.

Costs per post (7 slides): ~15 calls, ~12k tokens, ~$0.50 (reduced from original).

**Template Selection**: 
- Initialization: ~2-3 seconds (pre-compute embeddings, one-time per process)
- Per slide: ~100ms (semantic analysis) or ~5ms (fallback keyword matching)
- Total for 7 slides: ~700ms (with embeddings) or ~35ms (fallback)

### Modes

- **Auto**: Article → all posts.
- **Guided**: Select ideas/configs.

### Extensibility

Add: 
- New templates in `src/templates/textual_templates.py` (automatically integrated via semantic matching).
- New modules/layouts in design libraries.
- New prompts/phases.
- Custom embedding models for template selection (see `TemplateSelector` configuration).

---

## Next Steps

### Phase 1: Ideation Core

- Implement Post Ideator prompt.
- Basic selector.

### Phase 2: Config + Skeleton

- Code resolvers/builders.
- Narrative Architect.
- ✅ **Template Selector** (implemented with semantic embeddings).

### Phase 3: Generation

- Parallel slide gen/composition.
- Image integration.
- ✅ **Template-based text generation** (Copywriter uses template structures).

### Phase 4: Final + UI

- Caption/validation.
- CLI for input/output.

### Phase 5: Optimize

- Caching, metrics.

---

## References

### Core Documentation
- [[Prompts]] – Core 5 prompts (including narrative_architect.md and copywriter.md with template integration).
- [[Libraries]] – Design libraries (palettes, typography, layouts).
- [[Examples]] – Sample runs.

### Template System Documentation
- [[SEMANTIC_TEMPLATE_SELECTION.md]] – Detailed guide on semantic template selection with embeddings.
- [[template_based_narrative_system.md]] – Complete overview of the template-based narrative system.
- [[IMPLEMENTATION_SUMMARY.md]] – Implementation details and metrics for template selector.

### Code References
- `src/templates/textual_templates.py` – 46 template definitions.
- `src/templates/library.py` – Template library manager.
- `src/templates/selector.py` – Semantic template selector with embeddings support.
- `prompts/narrative_architect.md` – Defines high-level template types (hook, value, cta).
- `prompts/copywriter.md` – Uses selected template structures for text generation.

---

> **Note**: Simplified for clarity; focuses on per-post flow and reduced components. Changes reflected in all sections.