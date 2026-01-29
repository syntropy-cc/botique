# Social Media Post Generation Pipeline - Visão Geral

> **Version**: 2.1  
> **Date**: 2026-01-14  
> **Status**: Arquitetura Simplificada + Sistema Baseado em Templates  
> **Author**: José Scott (Revised)  
> **Updates**: Documentação dividida em componentes especializados

---

## 📚 Documentação Detalhada

Esta documentação foi dividida em documentos especializados para melhor compreensão e uso por LLMs:

### Documentos Principais

1. **[Visão Geral do Pipeline](pipeline_overview.md)** - Visão geral simplificada do pipeline de 5 fases
2. **[Agentes AI](agents.md)** - Documentação completa de todos os 5 agentes AI (Post Ideator, Narrative Architect, Copywriter, Visual Composer, Caption Writer)
3. **[Ferramentas (Tools)](tools.md)** - Documentação completa de todas as 11 ferramentas de código (Template Selector, Layout Resolver, Image Compositor, etc.)
4. **[Gerenciamento de Memória](memory_management.md)** - Documentação completa do Coherence Brief e mecanismos de memória/contexto
5. **[Estruturas de Dados](data_structures.md)** - Documentação completa de todas as estruturas de dados principais (JSON schemas)
6. **[Sistema de Branding](branding.md)** - Documentação completa do sistema de branding, perfis de audiência e integração com o pipeline

---

## Resumo Executivo

### Problema

Gerar posts de mídia social de alta qualidade a partir de artigos requer equilibrar análise de conteúdo, ideação, configuração, estrutura narrativa, geração de slides e finalização. O design original estava super-engenheirado com fases de análise redundantes e suposições globais sobre plataforma/tom.

### Solução

Pipeline simplificado de 5 fases orquestrado por código Python:

- **Prompts especializados**: Cada chamada AI foca em uma tarefa.
- **Templates textuais**: 46 templates pré-definidos com seleção semântica para copy consistente e de alta qualidade.
- **Libraries de design**: Visuais pré-validados (paletas, layouts, tipografia).
- **Contexto de coerência**: Documento por post garantindo consistência.
- **Gates de validação**: Verificações de qualidade por fase.

Um artigo gera múltiplos posts, cada um com sua própria plataforma, tom, persona, etc., e 1-12 slides + legenda.

### Objetivos

| Objetivo | Métrica de Sucesso |
|----------|-------------------|
| Qualidade consistente | Posts aderem a libraries, templates e coerência |
| Flexibilidade por post | Cada post tem plataforma/tom/persona únicos |
| Autonomia | Mínimo input do usuário (apenas artigo) |
| Escalabilidade | Geração paralela de posts/slides |
| Debuggabilidade | Fases isoláveis |
| Precisão de templates | 91% de precisão na seleção semântica de templates |

---

## Arquitetura do Sistema

### Pipeline de 5 Fases

```
┌─────────────────────────────────────────────────────────┐
│  Phase 1: IDEATION                                     │
│  Post Ideator (AI) → 3-6 ideias com config por post    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  Phase 2: CONFIGURATION                                 │
│  Coherence Brief Builder + Parameter Resolver (Code)   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  Phase 3: POST CREATION                                │
│  Narrative Architect (AI) → Template Selector (Code)     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  Phase 4: SLIDE GENERATION                             │
│  Copywriter (AI) + Visual Composer (AI) → Compositor     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  Phase 5: FINALIZATION                                 │
│  Caption Writer (AI) → Output Assembler + Validator      │
└─────────────────────────────────────────────────────────┘
```

### Componentes Principais

#### Agentes AI (5)
1. **Post Ideator** - Analisa artigo e gera 3-6 ideias
2. **Narrative Architect** - Cria estrutura narrativa slide-por-slide
3. **Copywriter** - Gera texto seguindo estruturas de templates
4. **Visual Composer** - Gera design (sem texto)
5. **Caption Writer** - Escreve legenda específica da plataforma

**📖 Documentação completa**: [agents.md](agents.md)

#### Ferramentas de Código (11)
1. **Idea Selector** - Filtra/seleciona ideias
2. **Coherence Brief Builder** - Constrói brief inicial
3. **Parameter Resolver** - Resolve parâmetros (paleta, tipografia)
4. **Template Selector** - Seleciona templates via análise semântica (91% precisão)
5. **Layout Resolver** - Atribui layouts por slide
6. **Prompt Builder (Image)** - Constrói prompt de imagem
7. **Image Generator** - Gera background (DALL-E 3)
8. **Prompt Builder (Text)** - Constrói especificações de texto
9. **Image Compositor** - Combina background + elementos + texto
10. **Output Assembler** - Empacota outputs
11. **Quality Validator** - Valida e pontua qualidade

**📖 Documentação completa**: [tools.md](tools.md)

#### Mecanismos de Memória
- **Coherence Brief**: Documento evolutivo que garante consistência per-post
  - Criado na Phase 1 com informações de alto nível
  - Enriquecido incrementalmente por cada fase (3-5)
  - Métodos de contexto especializados por agente

**📖 Documentação completa**: [memory_management.md](memory_management.md)

#### Libraries
- **Palettes** - Paletas de cores pré-validadas
- **Typography** - Configurações de tipografia
- **Layouts** - Layouts pré-definidos
- **Templates** - 46 templates textuais pré-definidos com seleção semântica

---

## Princípios de Design

### 1. Single Responsibility Prompts

Cada prompt lida com uma tarefa:
- ✅ Prompt 1: "Do artigo, gere 3-6 ideias de posts com config por post"
- ✅ Prompt 2: "Para ideia selecionada, construa esqueleto narrativo por slide"
- ✅ Prompt 3: "Escreva copy para slots de texto de um slide"

### 2. Code Decides, AI Creates

Código lida com consistência:

| Código Decide | AI Cria |
|--------------|---------|
| Seleção de paleta/tipografia | Ideias de posts / arcos narrativos |
| Posições de layout | Copy / descrições visuais |
| Composição de slides | Hooks / CTAs |

### 3. Per-Post Context

Cada post recebe contexto personalizado (plataforma, tom, etc.) desde a ideação. Sem suposições globais.

### 4. Coherence Through Constraint

- **Coherence Brief**: JSON por post que viaja pelas fases
- **Libraries**: LLM seleciona de opções, não inventa
- **Gates**: Valida antes de avançar

### 5. Graceful Defaults

Input: Apenas artigo. Sistema auto-sugere/atribui parâmetros por post.

---

## Fluxo de Dados

### Coherence Brief Evolution

```
Phase 1: Ideation
  ↓
Brief Inicial (Alto Nível)
  ↓
Phase 3: Narrative Architect
  ↓
Brief + Estrutura Narrativa (template_type + value_subtype)
  ↓
Template Selector (Code)
  ↓
Brief + template_id por slide
  ↓
Phase 4: Copywriter + Visual Composer
  ↓
Brief + Diretrizes de Copy + Preferências Visuais
  ↓
Phase 5: Caption Writer
  ↓
Brief Completo (Baixo Nível)
```

**📖 Documentação completa**: [memory_management.md](memory_management.md)

### Estruturas de Dados Principais

- `post_ideas.json` - Ideias geradas pelo Post Ideator
- `coherence_brief.json` - Brief evolutivo de coerência
- `narrative_structure.json` - Estrutura narrativa com templates
- `slide_content.json` - Texto gerado pelo Copywriter
- `visual_specs.json` - Design gerado pelo Visual Composer
- `caption.json` - Legenda gerada pelo Caption Writer

**📖 Documentação completa**: [data_structures.md](data_structures.md)

---

## Sistema de Templates Textuais

### Visão Geral

Pipeline usa **hierarquia de templates em dois níveis**:

1. **Tipos de Templates de Alto Nível** (definidos pelo Narrative Architect): `hook`, `transition`, `value`, `cta`
2. **Templates Textuais Específicos** (selecionados pelo Template Selector): 46 templates pré-definidos com estruturas específicas

### Seleção Semântica

- **Tecnologia**: `sentence-transformers` (modelo: `all-MiniLM-L6-v2`)
- **Precisão**: 91% (vs. 68% com keyword matching)
- **Performance**: ~100ms por slide (com embeddings) ou ~5ms (fallback)
- **Fallback**: Keyword matching + Jaccard similarity se embeddings não disponíveis

### Processo

1. **Narrative Architect** define `template_type` e `value_subtype` (estratégia)
2. **Template Selector** seleciona `template_id` específico via análise semântica
3. **Copywriter** usa estrutura do template para gerar texto

**📖 Documentação completa**: 
- [tools.md](tools.md) - Template Selector detalhado
- `docs/SEMANTIC_TEMPLATE_SELECTION.md` - Guia de seleção semântica
- `docs/template_based_narrative_system.md` - Visão geral do sistema

---

## Validação e Qualidade

### Gates (Por Fase)

- **Phase 1**: ≥3 ideias? Distintas?
- **Phase 2**: Config completo? Brief válido?
- **Phase 3**: ≥5 slides? Arc lógico? Todos têm `template_type`? Slides de valor têm `value_subtype`?
- **Phase 3a**: Todos têm `template_id`? Confidence >0.5?
- **Phase 4**: Texto dentro dos limites? Texto segue estrutura do template? Design sem texto? Dimensões corretas?
- **Phase 5**: Tamanho da legenda OK? Score >0.7?

Retry: 2 tentativas com feedback; fallback para defaults.

### Quality Score (Por Post)

```json
{
  "post_id": "post_001",
  "score": 0.85,
  "breakdown": {"coherence": 0.9, "visual": 0.8},
  "passed": true
}
```

---

## Performance e Custos

**Por post (7 slides)**:
- **Chamadas LLM**: ~15 chamadas
- **Tokens**: ~12k tokens
- **Custo**: ~$0.50

**Template Selection**:
- Inicialização: ~2-3 segundos (pre-compute embeddings, uma vez por processo)
- Por slide: ~100ms (análise semântica) ou ~5ms (fallback keyword)
- Total para 7 slides: ~700ms (com embeddings) ou ~35ms (fallback)

**Paralelização**: Posts independentes; slides paralelos.

---

## Estrutura de Diretórios

```
social-media-pipeline/
├── src/
│   ├── phases/              # Implementações das fases
│   ├── narrative/           # Narrative Architect
│   ├── copywriting/         # Copywriter
│   ├── templates/           # Template system
│   │   ├── textual_templates.py  # 46 template definitions
│   │   ├── library.py          # Template library manager
│   │   └── selector.py         # Semantic template selector
│   ├── coherence/           # Coherence Brief
│   └── core/               # Core utilities
├── libraries/               # Design libraries (palettes, typography, layouts)
├── prompts/                 # 5 core prompts
│   ├── post_ideator.md
│   ├── narrative_architect.md
│   └── copywriter.md
└── output/                  # Generated posts
```

---

## Extensibilidade

Adicionar:
- **Novos templates** em `src/templates/textual_templates.py` (automaticamente integrado via semantic matching)
- **Novos módulos/layouts** em design libraries
- **Novos prompts/fases**
- **Modelos de embedding customizados** para template selection (ver `TemplateSelector` configuration)

---

## Referências

### Documentação de Arquitetura

- **[Visão Geral do Pipeline](pipeline_overview.md)** - Visão geral simplificada
- **[Agentes AI](agents.md)** - Todos os 5 agentes detalhados
- **[Ferramentas](tools.md)** - Todas as 11 ferramentas detalhadas
- **[Gerenciamento de Memória](memory_management.md)** - Coherence Brief completo
- **[Estruturas de Dados](data_structures.md)** - Todos os schemas JSON
- **[Sistema de Branding](branding.md)** - Sistema de branding completo e integração com pipeline

### Documentação de Sistema

- `docs/SEMANTIC_TEMPLATE_SELECTION.md` - Guia de seleção semântica de templates
- `docs/template_based_narrative_system.md` - Visão geral do sistema de templates
- `docs/IMPLEMENTATION_SUMMARY.md` - Detalhes de implementação e métricas

### Código

- `src/templates/textual_templates.py` - 46 definições de templates
- `src/templates/library.py` - Gerenciador de library de templates
- `src/templates/selector.py` - Selecionador semântico de templates com embeddings
- `src/coherence/brief.py` - Classe CoherenceBrief
- `src/coherence/builder.py` - CoherenceBriefBuilder
- `src/narrative/architect.py` - Narrative Architect
- `src/copywriting/writer.py` - Copywriter

---

> **Nota**: Esta documentação foi simplificada e dividida em componentes especializados para melhor compreensão e uso por LLMs. Para detalhes completos, consulte os documentos especializados listados acima.
