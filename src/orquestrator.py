"""
Orchestrator for the Social Media Post Generation Pipeline

Concept:
- A prompt = template (.md) + attributes.
- Templates contain placeholders like {article}, {ideation_config_json}, etc.
- The orchestrator fills these placeholders and calls the LLM via HTTP.

Phases implemented:
  1) ideas : Article -> Ideas (post_ideator)
  2) brief : Article Summary + Selected Ideas -> Coherence Brief

Dependencies:
    pip install requests

Environment:
    export LLM_API_KEY="your_api_key_here"
    (or override via CLI if you prefer)
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# -------------------------------------------------------------------
# Paths & constants
# -------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT_DIR / "articles"
PROMPTS_DIR = ROOT_DIR / "prompts"
OUTPUT_DIR = ROOT_DIR / "output"

POST_IDEATOR_TEMPLATE_PATH = PROMPTS_DIR / "post_ideator.md"
COHERENCE_BRIEF_TEMPLATE_PATH = PROMPTS_DIR / "coherence_brief.md"

DEFAULT_BASE_URL = "https://api.deepseek.com/v1"  # OpenAI-compatible
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_API_ENV_VAR = "LLM_API_KEY"  # you can point this to DEEPSEEK_API_KEY if you want

# -------------------------------------------------------------------
# LLM client (HTTP, OpenAI-compatible chat API)
# -------------------------------------------------------------------

class HttpLLMClient:
    """
    Minimal chat-completions client for OpenAI-compatible APIs (DeepSeek, OpenAI, etc.).

    It:
      - Sends one user message with the full prompt (already built from template).
      - Returns the assistant's content as a raw string (expected to be pure JSON).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout: int = 60,
    ) -> None:
        api_key = api_key or os.getenv(DEFAULT_API_ENV_VAR)
        if not api_key:
            raise RuntimeError(
                f"API key not found. Set environment variable {DEFAULT_API_ENV_VAR} "
                "or pass --api-key on the CLI."
            )

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    @property
    def chat_url(self) -> str:
        return f"{self.base_url}/chat/completions"

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> str:
        """
        Sends the prompt to the chat completions endpoint and returns the
        assistant message content as a string.

        The prompt MUST already instruct the model to output ONLY JSON.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        response = requests.post(
            self.chat_url,
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"LLM API error {response.status_code}: {response.text}"
            )

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                f"Unexpected LLM response format: {json.dumps(data, indent=2)}"
            ) from exc

        if not isinstance(content, str):
            raise RuntimeError(
                f"Expected text content from LLM, got: {type(content)}"
            )

        return content.strip()


# -------------------------------------------------------------------
# Ideation configuration – attributes for post_ideator template
# -------------------------------------------------------------------

@dataclass
class IdeationConfig:
    """
    Attributes for the post_ideator template.

    These attributes are injected into {ideation_config_json} in post_ideator.md.
    The template is responsible for explaining how to use them.
    """

    min_ideas: int = 3
    max_ideas: int = 5
    allowed_platforms: List[str] | None = None
    allowed_formats: List[str] | None = None
    allowed_objectives: List[str] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_ideas": self.min_ideas,
            "max_ideas": self.max_ideas,
            "allowed_platforms": self.allowed_platforms or ["linkedin", "instagram"],
            "allowed_formats": self.allowed_formats or ["carousel", "single_image"],
            "allowed_objectives": self.allowed_objectives or [
                "awareness",
                "engagement",
                "conversion",
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


# -------------------------------------------------------------------
# Template rendering helper
# -------------------------------------------------------------------

def render_template(template_path: Path, context: Dict[str, str]) -> str:
    """
    Very simple placeholder replacement:
    - For each key in context, replace occurrences of `{key}` in the template.

    This avoids issues with str.format and braces inside the article text.
    Responsibility:
    - The template must use placeholders that match the keys in `context`.
    """
    text = template_path.read_text(encoding="utf-8")
    for key, value in context.items():
        placeholder = "{" + key + "}"
        text = text.replace(placeholder, value)
    return text


# -------------------------------------------------------------------
# JSON helper (strip fences if needed)
# -------------------------------------------------------------------

def parse_json_safely(raw: str) -> Dict[str, Any]:
    """
    Parse a JSON string, stripping ``` fences if the model accidentally adds them.
    """
    cleaned = raw.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Model output is not valid JSON. Check the template or raw response."
        ) from exc


# -------------------------------------------------------------------
# Orchestrator – phases wired to templates
# -------------------------------------------------------------------

class Orchestrator:
    """
    Orchestrates:
      - Phase 1: Idea generation (Article -> Ideas)
      - Phase 2: Coherence brief generation (Article Summary + Selected Ideas -> Brief)

    It only knows about templates and attributes. Selection / editing happens
    outside or via CLI helpers.
    """

    def __init__(
        self,
        llm_client: HttpLLMClient,
        articles_dir: Path = ARTICLES_DIR,
        prompts_dir: Path = PROMPTS_DIR,
        output_dir: Path = OUTPUT_DIR,
    ) -> None:
        self.llm = llm_client
        self.articles_dir = articles_dir
        self.prompts_dir = prompts_dir
        self.output_dir = output_dir

    # ----------------------------
    # Phase 1 – Ideas (post_ideator)
    # ----------------------------

    def run_ideas_phase(
        self,
        article_path: Path,
        ideation_config: IdeationConfig,
    ) -> Dict[str, Any]:
        """
        - Reads article text.
        - Builds prompt from post_ideator.md + ideation_config + article.
        - Calls LLM.
        - Returns parsed JSON: {"article_summary": ..., "ideas": [...]}.
        - Saves JSON to output/{slug}/phase1_ideas.json
        """
        article_text = article_path.read_text(encoding="utf-8")

        context = {
            "ideation_config_json": ideation_config.to_json(),
            "article": article_text,
        }

        prompt = render_template(POST_IDEATOR_TEMPLATE_PATH, context)
        raw_response = self.llm.generate(prompt)
        payload = parse_json_safely(raw_response)

        # Basic validation
        if "article_summary" not in payload or "ideas" not in payload:
            raise ValueError(
                "post_ideator output must contain 'article_summary' and 'ideas'."
            )

        slug = article_path.stem
        out_dir = self.output_dir / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "phase1_ideas.json"
        out_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"[Phase 1] Ideas saved to: {out_path}")

        return payload

    # ----------------------------
    # Phase 2 – Coherence Brief
    # ----------------------------

    def run_coherence_phase(
        self,
        article_summary: Dict[str, Any],
        selected_ideas: List[Dict[str, Any]],
        article_slug: str,
    ) -> Dict[str, Any]:
        """
        - Builds prompt from coherence_brief.md + article_summary + selected_ideas.
        - Calls LLM.
        - Returns parsed JSON: {"coherence_brief": {...}}.
        - Saves JSON to output/{slug}/phase2_coherence_brief.json
        """
        article_summary_json = json.dumps(
            article_summary, indent=2, ensure_ascii=False
        )
        selected_ideas_json = json.dumps(
            selected_ideas, indent=2, ensure_ascii=False
        )

        context = {
            "article_summary_json": article_summary_json,
            "selected_ideas_json": selected_ideas_json,
        }

        prompt = render_template(COHERENCE_BRIEF_TEMPLATE_PATH, context)
        raw_response = self.llm.generate(prompt)
        payload = parse_json_safely(raw_response)

        if "coherence_brief" not in payload:
            raise ValueError(
                "coherence_brief output must contain a 'coherence_brief' key."
            )

        out_dir = self.output_dir / article_slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "phase2_coherence_brief.json"
        out_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"[Phase 2] Coherence brief saved to: {out_path}")

        return payload


# -------------------------------------------------------------------
# CLI helpers – selection & config via arguments
# -------------------------------------------------------------------

def parse_list_arg(value: Optional[str]) -> Optional[List[str]]:
    if not value:
        return None
    return [v.strip() for v in value.split(",") if v.strip()]


def auto_select_ideas(
    ideas: List[Dict[str, Any]],
    selected_ids: Optional[List[str]],
    max_selected: int,
) -> List[Dict[str, Any]]:
    """
    Selection strategy:
    - If selected_ids provided: filter by those ids (in that order if you want).
    - Else: select top `max_selected` by confidence (descending).
    """
    if selected_ids:
        id_set = set(selected_ids)
        selected = [i for i in ideas if i.get("id") in id_set]
        if not selected:
            raise ValueError(
                f"No ideas matched the selected ids: {selected_ids}"
            )
        return selected

    # fallback: sort by confidence
    sorted_ideas = sorted(
        ideas,
        key=lambda i: i.get("confidence", 0.0),
        reverse=True,
    )
    if not sorted_ideas:
        raise ValueError("No ideas available to select from.")
    return sorted_ideas[:max_selected]


# -------------------------------------------------------------------
# CLI entrypoint
# -------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Orchestrator for Article -> Ideas -> Coherence Brief pipeline",
    )

    parser.add_argument(
        "--api-key",
        default=None,
        help=f"LLM API key (overrides {DEFAULT_API_ENV_VAR} env var).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"LLM model name (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"LLM base URL (default: {DEFAULT_BASE_URL}).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Phase 1: ideas
    p_ideas = subparsers.add_parser(
        "ideas",
        help="Generate ideas from an article using post_ideator.md",
    )
    p_ideas.add_argument(
        "--article",
        "-a",
        required=True,
        help="Article file (relative to articles/ or absolute).",
    )
    p_ideas.add_argument(
        "--min-ideas",
        type=int,
        default=3,
        help="Minimum number of ideas to generate.",
    )
    p_ideas.add_argument(
        "--max-ideas",
        type=int,
        default=5,
        help="Maximum number of ideas to generate.",
    )
    p_ideas.add_argument(
        "--platforms",
        type=str,
        default=None,
        help="Comma-separated allowed platforms (e.g. 'linkedin,instagram').",
    )
    p_ideas.add_argument(
        "--formats",
        type=str,
        default=None,
        help="Comma-separated allowed formats (e.g. 'carousel,single_image').",
    )
    p_ideas.add_argument(
        "--objectives",
        type=str,
        default=None,
        help="Comma-separated allowed objectives (e.g. 'awareness,engagement').",
    )

    # Phase 2: coherence brief
    p_brief = subparsers.add_parser(
        "brief",
        help="Generate coherence brief from an ideas JSON and selected ideas.",
    )
    p_brief.add_argument(
        "--ideas-json",
        required=True,
        help="Path to phase1_ideas.json (relative or absolute).",
    )
    p_brief.add_argument(
        "--selected-ids",
        default=None,
        help="Comma-separated idea ids to select (e.g. 'idea_1,idea_3'). "
             "If omitted, top N by confidence are selected.",
    )
    p_brief.add_argument(
        "--max-selected",
        type=int,
        default=1,
        help="Max number of ideas to select when --selected-ids is not provided.",
    )

    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    llm = HttpLLMClient(
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model,
    )
    orchestrator = Orchestrator(llm)

    if args.command == "ideas":
        # Resolve article path
        article_path = Path(args.article)
        if not article_path.is_absolute():
            article_path = (ARTICLES_DIR / article_path).resolve()
        if not article_path.exists():
            raise FileNotFoundError(f"Article not found: {article_path}")

        ideation_config = IdeationConfig(
            min_ideas=args.min_ideas,
            max_ideas=args.max_ideas,
            allowed_platforms=parse_list_arg(args.platforms),
            allowed_formats=parse_list_arg(args.formats),
            allowed_objectives=parse_list_arg(args.objectives),
        )

        orchestrator.run_ideas_phase(
            article_path=article_path,
            ideation_config=ideation_config,
        )

    elif args.command == "brief":
        ideas_path = Path(args.ideas_json)
        if not ideas_path.is_absolute():
            ideas_path = ideas_path.resolve()
        if not ideas_path.exists():
            raise FileNotFoundError(f"Ideas JSON not found: {ideas_path}")

        ideas_payload = json.loads(ideas_path.read_text(encoding="utf-8"))
        article_summary = ideas_payload["article_summary"]
        ideas = ideas_payload["ideas"]

        selected_ids = parse_list_arg(args.selected_ids)
        selected_ideas = auto_select_ideas(
            ideas=ideas,
            selected_ids=selected_ids,
            max_selected=args.max_selected,
        )

        # At this point you can modify selected_ideas programmatically if desired
        # (e.g. change platform, tone, persona, etc.) before building the brief.
        # This is where "attributes defined by the LLM can be changed" lives.

        slug = ideas_path.parent.name  # assumes output/{slug}/phase1_ideas.json
        orchestrator.run_coherence_phase(
            article_summary=article_summary,
            selected_ideas=selected_ideas,
            article_slug=slug,
        )

    else:
        parser.error("Unknown command")


if __name__ == "__main__":
    main()
