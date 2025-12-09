from dataclasses import dataclass, asdict, field
from pathlib import Path
import json
from typing import Dict, List

@dataclass
class IdeationConfig:
    num_insights_min: int = 5
    num_insights_max: int = 8
    num_keywords_min: int = 5
    num_keywords_max: int = 10
    num_ideas_min: int = 3
    num_ideas_max: int = 6
    platforms: List[str] = field(default_factory=lambda: ["linkedin", "instagram"])
    platforms_examples: str = "LinkedIn for professional networking, Instagram for visual storytelling"
    formats: List[str] = field(default_factory=lambda: ["carousel", "single_image"])
    tones_word_limit: str = "1-2"
    tones_examples_list: List[str] = field(default_factory=lambda: ["professional", "empowering", "urgent"])
    insights_per_idea_min: int = 2
    insights_per_idea_max: int = 5
    estimated_slides_min: int = 5
    estimated_slides_max: int = 12
    explanation_sentences_min: int = 2
    explanation_sentences_max: int = 4
    risks_min: int = 0
    risks_max: int = 2
    max_json_chars: int = 2500
    vocabulary_levels_list: List[str] = field(default_factory=lambda: ["simple", "moderate", "sophisticated"])
    formality_levels_list: List[str] = field(default_factory=lambda: ["casual", "neutral", "formal"])
    insight_types_list: List[str] = field(default_factory=lambda: ["statistic", "quote", "advice", "story", "data_point"])
    personality_traits_examples_list: List[str] = field(default_factory=lambda: ["authoritative", "empathetic"])
    allowed_objectives: List[str] = field(default_factory=lambda: ["engagement", "awareness", "conversion"])
    hook_max_chars: int = 100

    def to_prompt_dict(self) -> Dict[str, any]:
        d = asdict(self)
        d["platforms"] = ", ".join(f"'{p}'" for p in self.platforms)
        d["formats"] = ", ".join(f"'{f}'" for f in self.formats)
        d["tones_examples"] = ", ".join(f"'{t}'" for t in self.tones_examples_list)
        d["vocabulary_levels"] = "/".join(f"'{v}'" for v in self.vocabulary_levels_list)
        d["formality_levels"] = "/".join(f"'{f}'" for f in self.formality_levels_list)
        d["insight_types"] = " | ".join(f"'{t}'" for t in self.insight_types_list)
        d["personality_traits_examples"] = ", ".join(f"'{p}'" for p in self.personality_traits_examples_list)
        d["objectives"] = " | ".join(f"'{o}'" for o in self.allowed_objectives)
        d["hook_max_chars"] = str(self.hook_max_chars)
        d["num_ideas_aim"] = self.num_ideas_aim
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

# -------------------------------------------------------------------
# Template loading & prompt building
# -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"
ARTICLES = ROOT / "articles"
POST_IDEATOR_TEMPLATE = PROMPTS / "post_ideator.md"
COHERENCE_BRIEF_TEMPLATE = PROMPTS / "coherence_brief.md"

def build_post_ideator_prompt(
    article_text: str,
    ideation_config: IdeationConfig,
) -> str:
    template = POST_IDEATOR_TEMPLATE.read_text(encoding="utf-8")
    prompt = template.replace("{article}", article_text)
    prompt = prompt.format(**ideation_config.to_prompt_dict())
    return prompt

if __name__ == "__main__":
    # Example usage
    config = IdeationConfig()

    # Load a sample article for testing (replace with actual file if needed)
    sample_article_path = ARTICLES / "why-tradicional-learning-fails.md"  # Assume this file exists or create a placeholder
    if sample_article_path.exists():
        article_text = sample_article_path.read_text(encoding="utf-8")
    else:
        # Placeholder article text for testing
        article_text = """
# Sample Article Title

This is a sample article about AI advancements. Key points include:
- AI is transforming industries.
- 80% of companies are adopting AI.
"""

    prompt = build_post_ideator_prompt(article_text, config)
    print(prompt)