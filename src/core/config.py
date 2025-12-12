"""
Core configuration module

Paths, constants, and configuration dataclasses for the pipeline.

Location: src/core/config.py
"""

from dataclasses import dataclass, field
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

class IdeationConfig:
    """
    Configuration for the ideation phase (Phase 1).
    
    Controls the parameters for idea generation from articles.
    Follows the structure from orquestrator.py to match the post_ideator.md template.
    """
    
    # System prompt
    system_prompt: str = "You are an expert content ideator. Output only valid JSON as specified, without any additional text."
    
    # Number of insights and keywords
    num_insights_min: int = 2
    num_insights_max: int = 4
    num_keywords_min: int = 5
    num_keywords_max: int = 10
    
    # Number of ideas (also accessible via min_ideas/max_ideas for compatibility)
    num_ideas_min: int = 5
    num_ideas_max: int = 8
    
    # Platforms
    platforms: List[str] = field(default_factory=lambda: ["linkedin", "instagram"])
    platforms_examples: str = "LinkedIn for professional networking, Instagram for visual storytelling"
    
    # Formats
    formats: List[str] = field(default_factory=lambda: ["carousel", "single_image"])
    
    # Tones
    tones_word_limit: str = "1-2"
    tones_examples_list: List[str] = field(default_factory=lambda: ["professional", "empowering", "urgent"])
    
    # Insights per idea
    insights_per_idea_min: int = 2
    insights_per_idea_max: int = 5
    
    # Estimated slides
    estimated_slides_min: int = 5
    estimated_slides_max: int = 12
    
    # Explanation sentences
    explanation_sentences_min: int = 2
    explanation_sentences_max: int = 4
    
    # Risks
    risks_min: int = 0
    risks_max: int = 2
    
    # JSON limits
    max_json_chars: int = 2500
    
    # Vocabulary and formality levels
    vocabulary_levels_list: List[str] = field(default_factory=lambda: ["simple", "moderate", "sophisticated"])
    formality_levels_list: List[str] = field(default_factory=lambda: ["casual", "neutral", "formal"])
    
    # Insight types
    insight_types_list: List[str] = field(default_factory=lambda: ["statistic", "quote", "advice", "story", "data_point"])
    
    # Personality traits
    personality_traits_examples_list: List[str] = field(default_factory=lambda: ["authoritative", "empathetic"])
    
    # Objectives
    allowed_objectives: List[str] = field(default_factory=lambda: ["engagement", "awareness", "conversion"])
    
    # Hook limits
    hook_max_chars: int = 100
    
    def __init__(
        self,
        min_ideas: Optional[int] = None,
        max_ideas: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize IdeationConfig.
        
        Accepts min_ideas/max_ideas for compatibility, which map to num_ideas_min/max.
        All other fields can be passed as keyword arguments.
        """
        # Set defaults for all fields
        self.system_prompt = kwargs.get("system_prompt", "You are an expert content ideator. Output only valid JSON as specified, without any additional text.")
        self.num_insights_min = kwargs.get("num_insights_min", 2)
        self.num_insights_max = kwargs.get("num_insights_max", 4)
        self.num_keywords_min = kwargs.get("num_keywords_min", 5)
        self.num_keywords_max = kwargs.get("num_keywords_max", 10)
        self.num_ideas_min = kwargs.get("num_ideas_min", 5)
        self.num_ideas_max = kwargs.get("num_ideas_max", 8)
        self.platforms = kwargs.get("platforms", ["linkedin", "instagram"])
        self.platforms_examples = kwargs.get("platforms_examples", "LinkedIn for professional networking, Instagram for visual storytelling")
        self.formats = kwargs.get("formats", ["carousel", "single_image"])
        self.tones_word_limit = kwargs.get("tones_word_limit", "1-2")
        self.tones_examples_list = kwargs.get("tones_examples_list", ["professional", "empowering", "urgent"])
        self.insights_per_idea_min = kwargs.get("insights_per_idea_min", 2)
        self.insights_per_idea_max = kwargs.get("insights_per_idea_max", 5)
        self.estimated_slides_min = kwargs.get("estimated_slides_min", 5)
        self.estimated_slides_max = kwargs.get("estimated_slides_max", 12)
        self.explanation_sentences_min = kwargs.get("explanation_sentences_min", 2)
        self.explanation_sentences_max = kwargs.get("explanation_sentences_max", 4)
        self.risks_min = kwargs.get("risks_min", 0)
        self.risks_max = kwargs.get("risks_max", 2)
        self.max_json_chars = kwargs.get("max_json_chars", 2500)
        self.vocabulary_levels_list = kwargs.get("vocabulary_levels_list", ["simple", "moderate", "sophisticated"])
        self.formality_levels_list = kwargs.get("formality_levels_list", ["casual", "neutral", "formal"])
        self.insight_types_list = kwargs.get("insight_types_list", ["statistic", "quote", "advice", "story", "data_point"])
        self.personality_traits_examples_list = kwargs.get("personality_traits_examples_list", ["authoritative", "empathetic"])
        self.allowed_objectives = kwargs.get("allowed_objectives", ["engagement", "awareness", "conversion"])
        self.hook_max_chars = kwargs.get("hook_max_chars", 100)
        
        # Map compatibility fields
        if min_ideas is not None:
            self.num_ideas_min = min_ideas
        if max_ideas is not None:
            self.num_ideas_max = max_ideas
    
    # Compatibility properties for min_ideas/max_ideas
    @property
    def min_ideas(self) -> int:
        """Compatibility property: maps to num_ideas_min"""
        return self.num_ideas_min
    
    @min_ideas.setter
    def min_ideas(self, value: int) -> None:
        """Compatibility setter: maps to num_ideas_min"""
        self.num_ideas_min = value
    
    @property
    def max_ideas(self) -> int:
        """Compatibility property: maps to num_ideas_max"""
        return self.num_ideas_max
    
    @max_ideas.setter
    def max_ideas(self, value: int) -> None:
        """Compatibility setter: maps to num_ideas_max"""
        self.num_ideas_max = value
    
    def to_prompt_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for prompt template replacement.
        
        Formats fields according to the post_ideator.md template requirements.
        """
        d = {
            "system_prompt": self.system_prompt,
            "num_insights_min": self.num_insights_min,
            "num_insights_max": self.num_insights_max,
            "num_keywords_min": self.num_keywords_min,
            "num_keywords_max": self.num_keywords_max,
            "num_ideas_min": self.num_ideas_min,
            "num_ideas_max": self.num_ideas_max,
            "platforms": self.platforms,
            "platforms_examples": self.platforms_examples,
            "formats": self.formats,
            "tones_word_limit": self.tones_word_limit,
            "tones_examples_list": self.tones_examples_list,
            "insights_per_idea_min": self.insights_per_idea_min,
            "insights_per_idea_max": self.insights_per_idea_max,
            "estimated_slides_min": self.estimated_slides_min,
            "estimated_slides_max": self.estimated_slides_max,
            "explanation_sentences_min": self.explanation_sentences_min,
            "explanation_sentences_max": self.explanation_sentences_max,
            "risks_min": self.risks_min,
            "risks_max": self.risks_max,
            "max_json_chars": self.max_json_chars,
            "vocabulary_levels_list": self.vocabulary_levels_list,
            "formality_levels_list": self.formality_levels_list,
            "insight_types_list": self.insight_types_list,
            "personality_traits_examples_list": self.personality_traits_examples_list,
            "allowed_objectives": self.allowed_objectives,
            "hook_max_chars": self.hook_max_chars,
        }
        # Format fields for template
        d["system_prompt"] = self.system_prompt
        d["platforms"] = ", ".join(f"'{p}'" for p in self.platforms)
        d["formats"] = ", ".join(f"'{f}'" for f in self.formats)
        d["tones_examples"] = ", ".join(f"'{t}'" for t in self.tones_examples_list)
        d["vocabulary_levels"] = "/".join(f"'{v}'" for v in self.vocabulary_levels_list)
        d["formality_levels"] = "/".join(f"'{f}'" for f in self.formality_levels_list)
        d["insight_types"] = " | ".join(f"'{t}'" for t in self.insight_types_list)
        d["personality_traits_examples"] = ", ".join(f"'{p}'" for p in self.personality_traits_examples_list)
        d["objectives"] = " | ".join(f"'{o}'" for o in self.allowed_objectives)
        d["hook_max_chars"] = str(self.hook_max_chars)
        d["tones_word_limit"] = self.tones_word_limit
        d["platforms_examples"] = self.platforms_examples
        d["max_json_chars"] = str(self.max_json_chars)
        d["estimated_slides_min"] = str(self.estimated_slides_min)
        d["estimated_slides_max"] = str(self.estimated_slides_max)
        d["risks_min"] = str(self.risks_min)
        d["risks_max"] = str(self.risks_max)
        d["explanation_sentences_min"] = str(self.explanation_sentences_min)
        d["explanation_sentences_max"] = str(self.explanation_sentences_max)
        d["insights_per_idea_min"] = str(self.insights_per_idea_min)
        d["insights_per_idea_max"] = str(self.insights_per_idea_max)
        d["num_insights_min"] = str(self.num_insights_min)
        d["num_insights_max"] = str(self.num_insights_max)
        d["num_keywords_min"] = str(self.num_keywords_min)
        d["num_keywords_max"] = str(self.num_keywords_max)
        d["num_ideas_min"] = str(self.num_ideas_min)
        d["num_ideas_max"] = str(self.num_ideas_max)
        return d
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "min_ideas": self.min_ideas,
            "max_ideas": self.max_ideas,
            "allowed_platforms": self.platforms,
            "allowed_formats": self.formats,
            "allowed_objectives": self.allowed_objectives,
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