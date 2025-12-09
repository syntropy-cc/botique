# Social Media Post Generation Pipeline - English.md

> **Version**: 2.0  
> **Date**: 2025-12-08  
> **Status**: Simplified Architecture  
> **Author**: José Scott (Revised)

---

## Summary

- [[#Overview]]
    
- [[#Design Principles]]
    
- [[#System Architecture]]
    
- [[#Data Flow]]
    
- [[#Detailed Components]]
    
- [[#Coherence System]]
    
- [[#Design Libraries]]
    
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
    
- **Design libraries**: Pre-validated visuals (palettes, layouts, typography).
    
- **Coherence context**: Per-post document ensuring consistency.
    
- **Validation gates**: Quality checks per phase.

One article inputs generate multiple posts, each with its own platform, tone, persona, etc., and 1–12 slides + caption.

### Objectives

|Objective|Success Metric|
|---|---|
|Consistent quality|Posts adhere to design libraries and coherence|
|Per-post flexibility|Each post has unique platform/tone/persona|
|Autonomy|Minimal user input (article only)|
|Scalability|Parallel post/slide generation|
|Debuggability|Isolatable phases|

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
│  │  Defines n_slides, purposes, emotions per slide                     │    │
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
│  │ Generates text       │        │ Generates design       │                 │
│  │ structure per slot   │        │ (bg, elements, no text)│                 │
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

### Component Table

|#|Component|Type|Inputs|Outputs|Responsibility|
|---|---|---|---|---|---|
|0|User Input|Manual|Article|`article.txt`|Single required input|
|1|Post Ideator|AI|`article.txt`|`post_ideas.json`|Analyze + ideate 3–6 per-post ideas|
|2|Idea Selector|Code/User|`post_ideas.json`|`selected_ideas.json`|Pick top N|
|3|Parameter Resolver|Code|`selected_idea`, `libraries/`|`post_config.json`|Per-post params (palette, etc.)|
|4|Coherence Brief Builder|Code|`post_config.json`, `selected_idea`|`coherence_brief.json`|Per-post cohesion doc|
|5|Narrative Architect|AI|`post_config.json`, `coherence_brief.json`, `article.txt`|`narrative_structure.json`|Slide-by-slide skeleton|
|6|Layout Resolver|Code|`narrative_structure.json`, `libraries/layouts`|`slide_layouts.json`|Per-slide layouts|
|7|Copywriter|AI|`slide_layout`, `coherence_brief.json`, `article.txt`|`slide_content.json`|Text per slot|
|8|Visual Composer|AI|`slide_layout`, `post_config.json`, `coherence_brief.json`|`visual_specs.json`|Design (no text)|
|9|Prompt Builder (Image)|Code|`visual_specs.json`, `post_config.json`|`image_prompt.txt`|Image gen prompt|
|10|Image Generator|AI-Image|`image_prompt.txt`|`background.png`|Background image|
|11|Prompt Builder (Text)|Code|`slide_content.json`, `slide_layout`|`text_overlay.json`|Text rendering specs|
|12|Image Compositor|Code|`background.png`, `text_overlay.json`, `brand_assets`|`final_slide.png`|Combine elements|
|13|Caption Writer|AI|`post_config.json`, `all_slide_contents`, `coherence_brief.json`|`caption.json`|Per-post caption|
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

#### coherence_brief.json (Per-post)

```json
{
  "voice": {"tone": "professional", "vocabulary_level": "sophisticated"},
  "emotions": {"primary": "urgency", "secondary": ["curiosity"]},
  "visual": {"palette_id": "dark_professional_01", "mood": "dramatic"},
  "content": {"keywords": ["AI", "failure"], "main_message": "string"},
  "audience": {"persona": "C-level execs", "pain_points": ["wasted budgets"]}
}
```

#### narrative_structure.json (Slide-by-slide skeleton)

```json
{
  "post_id": "post_001",
  "arc": "Hook → Problem → Value → CTA",
  "slides": [
    {
      "number": 1,
      "module": "hook",
      "purpose": "Grab attention with stat",
      "emotions": ["shock"],
      "content_slots": {"headline": {"max_chars": 60}},
      "visual_mood": "dramatic"
    },
    {
      "number": 2,
      "module": "transition",
      "purpose": "Bridge to problem",
      "emotions": ["curiosity"]
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

### Coherence Brief (Per-Post)

Created in Phase 2, travels through Phases 3–5. Ensures per-post consistency in voice, visuals, etc.

|Component|Fields Used By|Purpose|
|---|---|---|
|Post Ideator|N/A (pre-brief)|Initial alignment|
|Narrative Architect|voice, emotions, content|Arc per slide|
|Copywriter|voice, content, audience|Text tone|
|Visual Composer|visual, emotions|Design mood|
|Caption Writer|voice, platform|Caption fit|

Example in prompt:

```text
COHERENCE BRIEF:
- Tone: Professional
- Primary emotion: Urgency
- Keywords: AI, failure
- Persona: C-level execs

TASK: Write headline for slide 1 (hook). Max 60 chars.
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

## Prompt Strategy

### Prompt Map (Simplified)

|Prompt|Input|Output|Context|
|---|---|---|---|
|Post Ideator|Article|Ideas + summary|None|
|Narrative Architect|Config + brief + article|Slide skeleton|Full brief|
|Copywriter|Layout + brief + article|Text JSON|Voice/emotions|
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
- **Phase 3**: ≥5 slides? Arc logical?
- **Phase 4**: Text in limits? Design no-text? Image dims correct?
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
│   ├── utils/
│   │   ├── ai_client.py
│   │   └── validators.py
├── libraries/  # Unchanged
├── prompts/    # Simplified: 5 files
├── output/
└── config.yaml
```

### Performance/Costs

Parallel: Posts independent; slides parallel.

Costs per post (7 slides): ~15 calls, ~12k tokens, ~$0.50 (reduced from original).

### Modes

- **Auto**: Article → all posts.
- **Guided**: Select ideas/configs.

### Extensibility

Add: New modules/layouts in libs; new prompts/phases.

---

## Next Steps

### Phase 1: Ideation Core

- Implement Post Ideator prompt.
- Basic selector.

### Phase 2: Config + Skeleton

- Code resolvers/builders.
- Narrative Architect.

### Phase 3: Generation

- Parallel slide gen/composition.
- Image integration.

### Phase 4: Final + UI

- Caption/validation.
- CLI for input/output.

### Phase 5: Optimize

- Caching, metrics.

---

## References

- [[Prompts]] – Core 5 prompts.
- [[Libraries]] – Docs.
- [[Examples]] – Sample runs.

---

> **Note**: Simplified for clarity; focuses on per-post flow and reduced components. Changes reflected in all sections.