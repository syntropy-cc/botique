"""
Copywriter Instruction

Instrução para geração de texto para slides.
"""

import json
from pathlib import Path
from typing import Any, Dict

from framework.core.instruction import Instruction


class CopywriterInstruction(Instruction):
    """Instrução para copywriting"""
    
    def __init__(self):
        template_path = Path(__file__).parent / "templates" / "copywriter.md"
        template = template_path.read_text(encoding="utf-8")
        
        super().__init__(
            prompt_key="copywriter",
            prompt_template=template,
            model="deepseek-chat",
            temperature=0.2,
            max_tokens=2048,
            preprocess=self._preprocess_slide,
            postprocess=self._postprocess_copy,
        )
    
    def _preprocess_slide(self, input_data: Dict[str, Any]) -> str:
        """φ_in: Transforma brief e slide_info em prompt"""
        brief = input_data.get("brief")
        slide_info = input_data.get("slide_info", {})
        article_text = input_data.get("article_text", "")
        
        if not brief:
            raise ValueError("brief is required")
        
        prompt_dict = {}
        
        # Voice do brief
        prompt_dict["tone"] = brief.tone
        prompt_dict["personality_traits"] = ", ".join(brief.personality_traits)
        prompt_dict["vocabulary_level"] = brief.vocabulary_level
        prompt_dict["formality"] = brief.formality
        
        # Content
        prompt_dict["keywords"] = ", ".join(brief.keywords_to_emphasize)
        prompt_dict["themes"] = ", ".join(brief.themes)
        prompt_dict["main_message"] = brief.main_message
        
        # Audience
        prompt_dict["persona"] = brief.persona
        prompt_dict["pain_points"] = ", ".join(brief.pain_points)
        prompt_dict["desires"] = ", ".join(brief.desires)
        
        # Slide info
        prompt_dict["slide_number"] = str(slide_info.get("number", 1))
        prompt_dict["module"] = slide_info.get("module", "")
        prompt_dict["purpose"] = slide_info.get("purpose", "")
        prompt_dict["emotions"] = ", ".join(slide_info.get("emotions", []))
        
        # Content slots do layout
        if "content_slots" in slide_info:
            slots_desc = []
            for slot_name, slot_config in slide_info["content_slots"].items():
                max_chars = slot_config.get("max_chars", "")
                slots_desc.append(f"{slot_name} (max {max_chars} chars)" if max_chars else slot_name)
            prompt_dict["content_slots"] = ", ".join(slots_desc)
        else:
            prompt_dict["content_slots"] = "headline, subheadline, body"
        
        prompt_dict["article_text"] = article_text
        
        # Substitui variáveis
        prompt = self.prompt_template
        for key, value in prompt_dict.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))
        
        return prompt
    
    def _postprocess_copy(self, response: str) -> Dict[str, Any]:
        """φ_out: Transforma resposta em conteúdo de slide"""
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
            return {"texts": {}}
