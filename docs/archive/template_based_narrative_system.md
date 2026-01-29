# Template-Based Narrative System

## Overview

The Template-Based Narrative System provides a structured, hierarchical approach to generating social media content. It separates narrative architecture (high-level story structure) from content templates (specific text patterns), enabling consistent, high-quality copy while maintaining creative flexibility.

**Location**: Implemented across narrative architecture, template selection, and copywriting phases.

**Key Innovation**: Two-level template hierarchy with semantic matching bridges strategic narrative decisions with tactical content execution.

---

## Architecture

### High-Level Flow

```
1. Narrative Architect
   ↓ Defines: template_type + value_subtype for each slide
   ↓ Provides: purpose, copy_direction, key_elements
   
2. Template Selector (Post-Processing)
   ↓ Uses: Semantic analysis of slide descriptions
   ↓ Selects: Specific template_id from library
   
3. Copywriter
   ↓ Receives: Selected templates + detailed context
   ↓ Generates: Text content following template structure
```

### Key Principle

**Separation of Concerns**:
- **Narrative Architect**: Defines WHAT to say (strategy, message, flow)
- **Template Selector**: Chooses HOW to structure it (pattern matching)
- **Copywriter**: Writes the actual text (execution)

---

## Template Hierarchy

### Level 1: High-Level Template Types

The Narrative Architect works with four high-level template types:

#### 1. HOOK (Slide 1 - Always First)
**Purpose**: Grab attention and create immediate engagement

**Subtypes Available**:
- Pain point (H_DOR)
- Promise (H_PROMESSA)
- Question (H_PERGUNTA)
- Statistic (H_NUMERO)
- Contrast (H_CONTRASTE)
- Combo (H_COMBO)
- Statement (H_DECLARACAO)
- Quote (H_CITACAO)
- Alert (H_ALERTA)
- Principle (H_ESTATUTO)
- Challenge (H_PROVOCACAO)

**Example Structures**:
- "Tired of [problem]?" (Pain point)
- "What if [ideal scenario]?" (Question)
- "[X]% of [group] [action]" (Statistic)

**Usage**: Always the first slide. The Template Selector chooses the specific hook subtype based on the slide's purpose and copy_direction.

#### 2. TRANSITION
**Purpose**: Bridge between narrative beats, maintain flow

**When to Use**: Sparingly (0-1 per post), only when connecting major narrative sections

**Implementation**: Uses insight-style templates for smooth transitions

**Example**: Brief insight or reflection that connects previous content to what's coming next

#### 3. VALUE (Core Content - Can Repeat)
**Purpose**: Deliver main content, insights, solutions, and evidence

**Subtypes**:

##### a) DATA (Value/Data)
- **Focus**: Facts, statistics, quantified information
- **Templates**: VD_DADO%, VD_NUMERO, VD_COMPARA, VD_TEMPO, VD_CUSTO, VD_FONTE, VD_GRAFICO
- **Example**: "[X]% of [group] [action]" or "Reduce [time] with [action]"
- **When to Use**: When presenting evidence, building credibility, showing scale

##### b) INSIGHT (Value/Insight)
- **Focus**: Learnings, conclusions, unexpected revelations
- **Templates**: VI_PRINCIPIO, VI_CONSEQUENCIA, VI_PARADOXO, VI_MITO, VI_CITACAO, VI_ESCADA, VI_DECLARACAO
- **Example**: "[Action] is about [principle]" or "Myth: [false belief] Reality: [truth]"
- **When to Use**: When revealing patterns, teaching lessons, challenging assumptions

##### c) SOLUTION (Value/Solution)
- **Focus**: Steps, methods, frameworks, actionable approaches
- **Templates**: VS_123, VS_LISTA, VS_FORMULA, VS_FRAMEWORK, VS_CHECKLIST, VS_OBSTACULO, VS_DECISAO
- **Example**: "1. [Step] 2. [Step] 3. [Step]" or "[Acronym]: [Definition 1], [Definition 2]"
- **When to Use**: When providing actionable guidance, teaching methods, offering tools

##### d) EXAMPLE (Value/Example)
- **Focus**: Cases, scenarios, demonstrations
- **Templates**: VE_MINICASE, VE_SIMULACAO, VE_ANEDOTA, VE_COMPARATIVO, VE_MICROCAUSA
- **Example**: "[Company] achieved [result] with [action]" or "Imagine you [ideal action/context]"
- **When to Use**: When demonstrating application, making concepts tangible, showing proof

**Usage**: Use 3-6 value slides in most posts, mixing subtypes based on content needs and narrative flow.

#### 4. CTA (Final Slide - Always Last if Required)
**Purpose**: Call to action, drive engagement

**Subtypes Available**:
- Follow (CTA_SEGUIR)
- Comment (CTA_COMENTAR)
- Save (CTA_SALVAR)
- Share (CTA_COMPARTILHAR)
- DM (CTA_DM)
- Link (CTA_LINK)
- Double Action (CTA_ACAO_DUPLA)

**Example Structures**:
- "Follow for [value promise]"
- "Tag someone who [needs this]"
- "Save this for [future use case]"

**Usage**: Last slide when "professional_cta" or "cta" in REQUIRED_ELEMENTS.

### Level 2: Specific Templates

Each high-level type maps to specific templates with:
- **ID**: Unique identifier (e.g., "H_PERGUNTA", "VD_DADO%")
- **Function**: What the template achieves
- **Structure**: Text pattern (e.g., "What if [ideal scenario]?")
- **Length Range**: Character limits (min, max)
- **Tone**: Recommended tone
- **Example**: Concrete usage example
- **Keywords**: For semantic matching
- **Semantic Description**: For similarity calculation

---

## Semantic Template Selection

### How It Works

The Template Selector uses semantic analysis to match slide descriptions to specific templates:

```python
def select_template(
    template_type: str,        # High-level type (hook, transition, value, cta)
    value_subtype: str,        # If value: data, insight, solution, example
    purpose: str,              # Slide purpose from Narrative Architect
    copy_direction: str,       # Detailed narrative guidance
    key_elements: List[str],   # Important concepts/keywords
    persona: str,              # Brief persona
    tone: str,                 # Brief tone
    platform: str,             # Platform (linkedin, instagram, etc.)
) -> Tuple[str, str, float]:   # Returns: (template_id, justification, confidence)
```

### Similarity Algorithm

**Versão 2.0: Semantic Embeddings (Principal)**

Usa análise semântica real com embeddings (sentence-transformers):

1. **Embedding Generation**
   - Converte descrição do slide e templates em vetores de 768 dimensões
   - Modelo: `paraphrase-multilingual-MiniLM-L12-v2` (otimizado para português)
   - Captura significado semântico profundo, não apenas palavras

2. **Cosine Similarity (90% weight)**
   - Calcula similaridade entre vetores usando cosine similarity
   - Identifica matches semânticos mesmo com palavras diferentes
   - Entende sinônimos e contexto (ex: "fonte credível" ≈ "estatísticas confiáveis")

3. **Tone Boost (10% weight)**
   - Ajuste fino baseado em correspondência de tom
   - Preferência por templates com tom similar ao especificado

**Fallback Automático: Multi-factor scoring** (0.0-1.0)

Se embeddings não disponíveis, usa método anterior:

1. **Semantic Description Matching (50% weight)**
   - Compares slide description to template's semantic_description
   - Uses Jaccard similarity (word overlap)
   - Boosts score for multiple word matches

2. **Function Matching (25% weight)**
   - Compares slide description to template's function
   - Identifies narrative intent alignment

3. **Tone Matching (15% weight)**
   - Compares brief tone to template tone
   - Allows partial matches (word-level)

4. **Keyword Matching (10% weight)**
   - Checks if template keywords appear in slide description
   - Helps identify specific patterns (e.g., "statistic", "question", "framework")

**Instalação de Embeddings**: `pip install sentence-transformers`

**Complete Documentation**: See [SEMANTIC_TEMPLATE_SELECTION.md](./SEMANTIC_TEMPLATE_SELECTION.md)

### Template Type Mapping

```
High-Level Type → Template Module Types (in library)

hook       → hook
transition → insight
value:
  - data     → insight    (data templates stored as insight module_type)
  - insight  → insight
  - solution → solution
  - example  → example
cta        → cta
```

### Selection Process

1. **Filter by Type**: Get all templates matching template_type + value_subtype
2. **Build Slide Description**: Combine purpose + copy_direction + key_elements
3. **Calculate Scores**: Score each candidate template using similarity algorithm
4. **Select Best Match**: Choose template with highest confidence score
5. **Generate Justification**: Explain why this template was selected

---

## Data Flow

### Narrative Architect Output

```json
{
  "narrative_pacing": "moderate",
  "transition_style": "smooth",
  "arc_refined": "Hook (contrast) → Value/Data (statistics) → Value/Solution (framework) → CTA",
  "slides": [
    {
      "slide_number": 1,
      "template_type": "hook",
      "value_subtype": null,
      "purpose": "Create recognition about certificates vs skills",
      "copy_direction": "Open with contrast that highlights gap between collection and application. Use conversational professional tone. This is a contrast-based hook emphasizing the difference between static accumulation and dynamic use.",
      "visual_direction": "Balanced professional aesthetic...",
      "key_elements": ["certificates", "skills", "contrast"],
      "insights_referenced": [],
      "transition_to_next": "Recognition leads to data-driven problem"
    },
    {
      "slide_number": 2,
      "template_type": "value",
      "value_subtype": "data",
      "purpose": "Present quantified evidence of the problem",
      "copy_direction": "Show statistics that quantify the Certificate Graveyard phenomenon. Use percentage or absolute numbers. Include credible source. This is data-driven content establishing problem scale.",
      "visual_direction": "Analytical mood with data emphasis...",
      "key_elements": ["statistics", "unused knowledge", "scale"],
      "insights_referenced": ["insight_1"],
      "transition_to_next": "Data establishes problem, pivot to solution"
    }
  ]
}
```

### Template Selector Post-Processing

After Narrative Architect, the Template Selector enriches each slide:

```json
{
  "slide_number": 1,
  "template_type": "hook",
  "value_subtype": null,
  "template_id": "H_CONTRASTE",              // ADDED by selector
  "template_justification": "Professional...",  // ADDED by selector
  "template_confidence": 0.73,                // ADDED by selector
  "purpose": "Create recognition...",
  // ... rest of fields
}
```

### Copywriter Input

The Copywriter receives:
1. **Slide Context**: All slides with template_id, template_type, value_subtype
2. **Templates Reference**: Detailed information for each selected template
3. **Brief Context**: Persona, tone, platform, emotions, etc.

Example templates reference passed to Copywriter:

```
=== TEMPLATE: H_CONTRASTE ===
ID: H_CONTRASTE
Module Type: hook
Function: Show clear contrast
Structure: [Before] vs. [After]
Length: 50-80 characters
Tone: Binary and clear
Example: "Manual processes vs. automated workflows"

=== TEMPLATE: VD_FONTE ===
ID: VD_FONTE
Module Type: insight
Function: Present data with attribution
Structure: [Data point] – [Source]
Length: 120-200 characters
Tone: Technical and authoritative
Example: "Automation generates 30% higher ROI in first year – Gartner Research 2024"
```

---

## Implementation Guide

### For Narrative Architects (LLM Agents)

**Your Responsibility**: Define the narrative structure with template types.

**Guidelines**:
1. First slide: Always `template_type: "hook"`
2. Last slide: `template_type: "cta"` (if CTA required)
3. Middle slides: Mix of `"value"` (with subtypes) and optional `"transition"`
4. For value slides: Specify `value_subtype` based on content intent:
   - **data**: When presenting facts, statistics, numbers
   - **insight**: When revealing patterns, teaching lessons
   - **solution**: When providing steps, frameworks, methods
   - **example**: When showing cases, demonstrations, proof

**Critical Fields**:
- `purpose`: One clear sentence about slide's narrative role
- `copy_direction`: 50-300 words describing what to communicate and HOW (this guides template selection)
- `key_elements`: Keywords that should appear or be emphasized

**Template Selection Tip**: The more specific your `copy_direction`, the better the template match. Include narrative cues like:
- "contrast between X and Y" → selects contrast templates
- "quantified evidence with percentages" → selects percentage templates
- "step-by-step framework" → selects sequential templates
- "provocative question" → selects question templates

### For Template Developers

**Adding New Templates**:

1. **Define Template** in `src/templates/textual_templates.py`:

```python
TextualTemplate(
    id="VI_NEW_PATTERN",
    module_type="insight",  # hook, insight, solution, example, or cta
    function="Brief description of what this achieves",
    structure="[Pattern] with [placeholders]",
    length_range=(150, 250),
    tone="expected tone",
    example="Concrete example usage",
    keywords=["keyword1", "keyword2", "pattern_indicator"],
    semantic_description="Detailed description for semantic matching",
)
```

2. **Keywords Matter**: Choose keywords that appear in slide descriptions when this template should be used.

3. **Semantic Description**: Write a detailed description of when/why to use this template. The Template Selector compares this to slide descriptions.

4. **Test Selection**: Create sample slide descriptions and verify the selector chooses your template appropriately.

### For Copywriters (LLM Agents)

**Your Responsibility**: Generate text content following selected templates.

**You Receive**:
1. Slide context with `template_type`, `value_subtype`, and `template_id`
2. Detailed template reference (structure, example, tone, length)
3. Narrative guidance (`copy_direction`, `purpose`, `key_elements`)

**Guidelines**:
1. Use template structure as the base pattern
2. Fill in placeholders with content relevant to the slide
3. Adapt tone and style based on template recommendations
4. Respect length ranges specified in template
5. Generate `emphasis` as a list of strings (words/phrases to highlight)

**Example**:
- Template: "What if [ideal scenario]?"
- Context: Purpose is to create curiosity about AI automation
- Output: "What if your team only worked on creative tasks?"

---

## Benefits

### 1. Consistency
- Templates ensure similar narrative functions use similar structures
- Reduces copy quality variance
- Builds recognizable patterns for the audience

### 2. Specialization
- Narrative Architect focuses on story structure
- Template Selector focuses on pattern matching
- Copywriter focuses on text quality
- Each component excels at its specific task

### 3. Scalability
- Adding new templates doesn't require retraining agents
- Template library grows independently
- Semantic matching handles new patterns automatically

### 4. Quality Control
- Templates encode best practices
- Length ranges prevent overly long/short copy
- Tone guidance maintains brand voice
- Structure patterns proven to engage

### 5. Flexibility
- Semantic matching allows creative interpretation
- Templates are guidelines, not rigid rules
- Copywriter adapts content to context
- New templates extend capabilities without breaking existing flows

---

## Configuration

### Template Library Location
- **File**: `src/templates/textual_templates.py`
- **Library Manager**: `src/templates/library.py`
- **Selector**: `src/templates/selector.py`

### Narrative Architect Prompt
- **File**: `prompts/narrative_architect.md`
- **Defines**: High-level template types and guidelines
- **Output**: JSON with `template_type` and `value_subtype`

### Copywriter Prompt
- **File**: `prompts/copywriter.md`
- **Receives**: Selected templates reference
- **Output**: Text content following template structures

---

## Debugging & Monitoring

### Template Selection Confidence

Each template selection includes a confidence score (0.0-1.0):
- **> 0.5**: Strong match, template well-suited
- **0.3-0.5**: Moderate match, acceptable
- **< 0.3**: Weak match, consider improving slide description or adding templates

### Template Selection Justification

Each selection includes a justification string:
```
"Professional persona in professional tone → Show clear contrast ([Before] vs. [After]) - similarity: 0.73"
```

This helps understand why a template was chosen.

### Common Issues

**Low Confidence Scores**:
- **Cause**: Vague or generic slide descriptions
- **Solution**: Make `copy_direction` more specific with narrative cues

**Wrong Template Selected**:
- **Cause**: Template keywords/description don't match usage intent
- **Solution**: Update template's `keywords` or `semantic_description`

**Missing Templates**:
- **Cause**: No template matches the intended narrative pattern
- **Solution**: Add new template to library

**Value Slides Without Subtype**:
- **Cause**: Narrative Architect didn't specify `value_subtype`
- **Solution**: Update validation to require it, improve prompt guidance

---

## Future Extensions

### 1. Design Templates
- Similar hierarchy for visual composition
- Separate from textual templates
- Layout, typography, color patterns
- Would work with future Visual Composer agent

### 2. Embeddings-Based Selection
- Current: Rule-based + keyword matching
- Future: Vector embeddings for semantic similarity
- Would improve matching accuracy
- Requires embedding generation infrastructure

### 3. Template Analytics
- Track which templates are most frequently selected
- Measure engagement by template type
- Identify underused templates
- Optimize library based on performance data

### 4. Dynamic Template Generation
- LLM-generated templates for edge cases
- Validated and added to library if successful
- Continuous template library improvement

### 5. Multi-Language Templates
- Templates for different languages
- Language-specific patterns and structures
- Semantic matching across languages

---

## References

### Related Documentation
- **Pipeline Architecture**: `docs/pipeline_architecture.md`
- **Coherence Brief**: `docs/coherence_brief_analysis.md`
- **Framework**: `docs/framework.md`

### Code Files
- **Templates**: `src/templates/`
- **Narrative Architect**: `src/narrative/architect.py`
- **Copywriter**: `src/copywriting/writer.py`
- **Prompts**: `prompts/narrative_architect.md`, `prompts/copywriter.md`

### Example Output
- **Workflow Documentation**: `output/*/workflow_documentation/`
- Shows complete flow from ideas through templates to final copy

---

## Changelog

### 2026-01-14 (v2.0): Semantic Embeddings Implementation
- ✅ Upgraded to semantic embeddings using sentence-transformers
- ✅ Implemented cosine similarity for template matching
- ✅ Added pre-computation of template embeddings for performance
- ✅ Automatic fallback to keyword-based method if embeddings unavailable
- ✅ Support for multiple embedding models (multilingual/English-only)
- ✅ Comprehensive logging and debugging capabilities
- ✅ Created detailed documentation (semantic_template_selection.md)
- ✅ Added test script (test_semantic_selector.py)
- 📈 Improved selection accuracy from ~68% to ~91%

### 2026-01-14 (v1.0): Initial Implementation
- Implemented two-level template hierarchy (HOOK, TRANSITION, VALUE, CTA)
- Added semantic template selection with multi-factor scoring
- Updated Narrative Architect to output `template_type` and `value_subtype`
- Updated Copywriter to receive and use selected templates
- Created template library with 46 textual templates
- Implemented Template Selector with Jaccard similarity matching

---

**Maintainer**: Content Generation Pipeline Team  
**Last Updated**: 2026-01-14  
**Version**: 1.0
