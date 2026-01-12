"""
Caption Writer Instruction

Instrução para geração de captions para posts.
"""

import json
from pathlib import Path
from typing import Any, Dict

from framework.core.instruction import Instruction


class CaptionWriterInstruction(Instruction):
    """Instrução para escrita de caption"""
    
    def __init__(self):
        template_path = Path(__file__).parent / "templates" / "caption_writer.md"
        template = template_path.read_text(encoding="utf-8")
        
        super().__init__(
            prompt_key="caption_writer",
            prompt_template=template,
            model="deepseek-chat",
            temperature=0.2,
            max_tokens=2048,
            preprocess=self._preprocess_caption,
            postprocess=self._postprocess_caption,
        )
    
    def _preprocess_caption(self, input_data: Dict[str, Any]) -> str:
        """φ_in: Transforma brief e slides em prompt para caption"""
        brief = input_data.get("brief")
        all_slide_contents = input_data.get("all_slide_contents", [])
        
        if not brief:
            raise ValueError("brief is required")
        
        prompt_dict = {}
        
        # Voice
        prompt_dict["tone"] = brief.tone
        prompt_dict["personality_traits"] = ", ".join(brief.personality_traits)
        prompt_dict["formality"] = brief.formality
        
        # Platform
        prompt_dict["platform"] = brief.platform
        
        # Content
        prompt_dict["main_message"] = brief.main_message
        prompt_dict["hook"] = brief.hook
        
        # CTA guidelines se disponível
        if brief.cta_guidelines:
            prompt_dict["cta_guidelines"] = json.dumps(brief.cta_guidelines, indent=2)
        else:
            prompt_dict["cta_guidelines"] = "{}"
        
        # Slides summary
        slides_summary = []
        for slide_content in all_slide_contents:
            if isinstance(slide_content, dict):
                texts = slide_content.get("texts", {})
                headline = texts.get("headline", {}).get("content", "")
                if headline:
                    slides_summary.append(f"- {headline}")
        
        prompt_dict["slides_summary"] = "\n".join(slides_summary) if slides_summary else "- (no slides)"
        
        # Substitui variáveis
        prompt = self.prompt_template
        for key, value in prompt_dict.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))
        
        return prompt
    
    def _postprocess_caption(self, response: str) -> Dict[str, Any]:
        """φ_out: Transforma resposta em caption"""
        response = response.strip()
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end != -1:
                response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end != -1:
                response = response[start:end].strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"full_caption": response, "hashtags": []}
