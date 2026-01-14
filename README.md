# Botique

Multi-agent system for personal brand management and social media content generation.

## Features

- **Complete Pipeline**: Generate ideas and coherence briefs from articles
- **Prompt Versioning**: Automatic versioning system with duplicate prevention
- **Event Logging**: Database-based logging system tracking all workflow events (LLM calls and non-LLM steps) with cost metrics, performance, and quality tracking
- **Semantic Template Selection**: Advanced template matching using embeddings for 91% accuracy
- **Integrated CLI**: Command-line interface for all operations

## Installation

```bash
# Clone repository
git clone <repo-url>
cd botique

# Install dependencies (if needed)
pip install -r requirements.txt

# (Optional) For advanced semantic template analysis
pip install -r requirements_templates.txt
```

### Semantic Template Analysis

The system uses embeddings for intelligent template selection based on real meaning, not just keywords:

- ✅ **With embeddings** (recommended): `pip install sentence-transformers`
- ⚠️ **Without embeddings**: Automatic fallback to keyword-based method

See [detailed documentation](./docs/SEMANTIC_TEMPLATE_SELECTION.md) about the semantic selection system.

## Quick Usage

### 1. Register Prompts

First, register all prompts in the database:

```bash
python -m src.cli.commands prompts
```

### 2. Run Pipeline

```bash
# Complete pipeline
python -m src.cli.commands full --article articles/article.md

# Or separate phases
python -m src.cli.commands ideas --article articles/article.md
python -m src.cli.commands briefs --ideas-json output/slug/phase1_ideas.json
```

## CLI Commands

### `prompts` - Manage Prompts

Registers and updates prompts from `prompts/` directory in the database.

```bash
# Register all prompts
python -m src.cli.commands prompts

# Update metadata of existing prompts
python -m src.cli.commands prompts --update-metadata

# Specify custom directory
python -m src.cli.commands prompts --prompts-dir /path/to/prompts
```

**Features:**
- ✅ Automatic versioning (v1, v2, v3...)
- ✅ Duplicate prevention
- ✅ Automatic metrics calculation (size, complexity, tokens)
- ✅ Complete metadata storage

### `full` - Complete Pipeline

Executes complete pipeline: Article → Ideas → Briefs.

```bash
python -m src.cli.commands full \
  --article articles/article.md \
  --min-ideas 5 \
  --max-ideas 8 \
  --max-posts 3
```

### `ideas` - Phase 1: Idea Generation

Generates post ideas from an article.

```bash
python -m src.cli.commands ideas \
  --article articles/article.md \
  --min-ideas 3 \
  --max-ideas 6
```

### `briefs` - Phases 2 and 3: Coherence Briefs

Generates coherence briefs from selected ideas.

```bash
python -m src.cli.commands briefs \
  --ideas-json output/slug/phase1_ideas.json \
  --strategy diverse \
  --max-posts 3
```

## Configuration

### Environment Variables

```bash
# LLM API key (required)
export LLM_API_KEY="your-key-here"

# Custom path for SQLite database (optional)
export LLM_LOGS_DB_PATH="/path/to/llm_logs.db"

# To use PostgreSQL instead of SQLite (optional)
export DB_URL="postgresql://user:password@localhost/dbname"
```

## Project Structure

```
botique/
├── src/
│   ├── cli/              # Command-line interface
│   ├── core/             # Core modules (logging, prompts, etc.)
│   ├── coherence/        # Coherence system
│   ├── ideas/            # Idea generation
│   ├── templates/        # Template system with semantic selection
│   └── phases/           # Pipeline phases
├── prompts/              # Prompt templates (.md)
├── articles/             # Input articles
├── output/               # Pipeline results
├── scripts/              # Utility scripts
└── docs/                 # Documentation
```

## Prompt Versioning System

The system offers automatic prompt versioning:

- **Automatic**: Versions created automatically (v1, v2, v3...)
- **No duplicates**: Identical templates return existing version
- **Metrics**: Calculates size, complexity, estimated tokens
- **Traceable**: Each LLM event linked to specific prompt version

```bash
# Register prompts (first time)
python -m src.cli.commands prompts

# Update metadata (after modifying prompts)
python -m src.cli.commands prompts --update-metadata
```

## Documentation

- [CLI Commands](./docs/cli_commands.md) - Complete command guide
- [Event Logging](./docs/event_logging.md) - Event logging system
- [Prompt Versioning](./docs/prompt_versioning_automatic.md) - Versioning system
- [Pipeline Architecture](./docs/pipeline_architecture.md) - System overview
- [Semantic Template Selection](./docs/SEMANTIC_TEMPLATE_SELECTION.md) - Embeddings-based template matching
- [Template System](./docs/template_based_narrative_system.md) - Template hierarchy and selection

## Development

```bash
# Run tests
python scripts/test_prompt_versioning.py

# Test semantic selector
python scripts/test_semantic_selector.py

# Register prompts for development
python -m src.cli.commands prompts --update-metadata
```

## License

[Add license information here]
