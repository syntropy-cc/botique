"""
Core configuration module

Paths, constants, and configuration dataclasses for the pipeline.

Location: src/core/config.py
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# PATHS
# =============================================================================

# Determine root directory (assuming this file is at src/core/config.py)
ROOT_DIR = Path(__file__).resolve().parents[2]

ARTICLES_DIR = ROOT_DIR / "articles"
PROMPTS_DIR = ROOT_DIR / "prompts"
OUTPUT_DIR = ROOT_DIR / "output"
LIBRARIES_DIR = ROOT_DIR / "libraries"

# Prompt template paths
POST_IDEATOR_TEMPLATE = PROMPTS_DIR / "post_ideator.md"
NARRATIVE_ARCHITECT_TEMPLATE = PROMPTS_DIR / "narrative_architect.md"
COPYWRITER_TEMPLATE = PROMPTS_DIR / "copywriter.md"
VISUAL_COMPOSER_TEMPLATE = PROMPTS_DIR / "visual_composer.md"
CAPTION_WRITER_TEMPLATE = PROMPTS_DIR / "caption_writer.md"


# =============================================================================
# LLM CONFIGURATION
# =============================================================================

DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_API_ENV_VAR = "LLM_API_KEY"

DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TIMEOUT = 60


# =============================================================================
# PIPELINE CONFIGURATION
# =============================================================================

@dataclass
class IdeationConfig:
    """
    Configuration for the ideation phase (Phase 1).
    
    Controls the parameters for idea generation from articles.
    """
    
    min_ideas: int = 3
    max_ideas: int = 5
    allowed_platforms: Optional[List[str]] = None
    allowed_formats: Optional[List[str]] = None
    allowed_objectives: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "min_ideas": self.min_ideas,
            "max_ideas": self.max_ideas,
            "allowed_platforms": self.allowed_platforms or [
                "linkedin",
                "instagram",
                "twitter",
            ],
            "allowed_formats": self.allowed_formats or [
                "carousel",
                "single_image",
            ],
            "allowed_objectives": self.allowed_objectives or [
                "awareness",
                "engagement",
                "conversion",
            ],
        }
    
    def to_json(self) -> str:
        """Convert to JSON string for prompt injection"""
        import json
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


@dataclass
class SelectionConfig:
    """
    Configuration for the selection phase (Phase 2).
    
    Controls how ideas are filtered and selected.
    """
    
    min_confidence: float = 0.7
    max_selected: int = 3
    strategy: str = "diverse"  # "diverse" or "top"
    selected_ids: Optional[List[str]] = None
    
    def __post_init__(self):
        """Validate configuration"""
        if self.strategy not in ["diverse", "top"]:
            raise ValueError(f"Invalid strategy: {self.strategy}")
        
        if self.min_confidence < 0.0 or self.min_confidence > 1.0:
            raise ValueError(f"min_confidence must be between 0.0 and 1.0")
        
        if self.max_selected < 1:
            raise ValueError(f"max_selected must be at least 1")


@dataclass
class PipelineConfig:
    """
    Global pipeline configuration.
    
    Aggregates all phase configurations and global settings.
    """
    
    # Directories
    articles_dir: Path = ARTICLES_DIR
    prompts_dir: Path = PROMPTS_DIR
    output_dir: Path = OUTPUT_DIR
    libraries_dir: Path = LIBRARIES_DIR
    
    # LLM settings
    llm_base_url: str = DEFAULT_BASE_URL
    llm_model: str = DEFAULT_MODEL
    llm_temperature: float = DEFAULT_TEMPERATURE
    llm_max_tokens: int = DEFAULT_MAX_TOKENS
    llm_timeout: int = DEFAULT_TIMEOUT
    
    # Phase configurations
    ideation: IdeationConfig = None
    selection: SelectionConfig = None
    
    def __post_init__(self):
        """Initialize sub-configs if not provided"""
        if self.ideation is None:
            self.ideation = IdeationConfig()
        
        if self.selection is None:
            self.selection = SelectionConfig()
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_defaults(cls) -> "PipelineConfig":
        """Create configuration with all defaults"""
        return cls()


# =============================================================================
# VALIDATION CONSTANTS
# =============================================================================

# Minimum confidence threshold for ideas
MIN_CONFIDENCE_THRESHOLD = 0.5

# Maximum slides per post
MAX_SLIDES_PER_POST = 12
MIN_SLIDES_PER_POST = 5

# Character limits
MAX_HOOK_LENGTH = 100
MAX_HEADLINE_LENGTH = 60
MAX_SUBHEADLINE_LENGTH = 120
MAX_BODY_TEXT_LENGTH = 250

# LinkedIn caption limits
LINKEDIN_CAPTION_MAX = 3000
INSTAGRAM_CAPTION_MAX = 2200
TWITTER_CAPTION_MAX = 280


# =============================================================================
# SUPPORTED VALUES
# =============================================================================

SUPPORTED_PLATFORMS = [
    "linkedin",
    "instagram",
    "twitter",
    "github",
    "youtube",
    "discord",
]

SUPPORTED_FORMATS = [
    "carousel",
    "single_image",
    "story",
    "reel",
    "video_short",
    "thumbnail",
]

SUPPORTED_OBJECTIVES = [
    "awareness",
    "engagement",
    "conversion",
]

SUPPORTED_TONES = [
    "professional",
    "empowering",
    "urgent",
    "technical",
    "conversational",
    "inspiring",
]

SUPPORTED_AUDIENCES = [
    "c_level",
    "founder",
    "developer",
]