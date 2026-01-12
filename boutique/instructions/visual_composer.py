"""
Visual Composer Instruction

Instrução para geração de especificações visuais para slides.
"""

import json
from pathlib import Path
from typing import Any, Dict

from framework.core.instruction import Instruction


class VisualComposerInstruction(Instruction):
    """Instrução para composição visual"""
    
    def __init__(self):
        template_path = Path(__file__).parent / "templates" / "visual_composer.md"
        template = template_path.read_text(encoding="utf-8")
        
        super().__init__(
            prompt_key="visual_composer",
            prompt_template=template,
            model="deepseek-chat",
            temperature=0.2,
            max_tokens=2048,
            preprocess=self._preprocess_visual,
            postprocess=self._postprocess_visual,
        )
    
    def _preprocess_visual(self, input_data: Dict[str, Any]) -> str:
        """φ_in: Transforma brief e layout em prompt visual"""
        brief = input_data.get("brief")
        slide_info = input_data.get("slide_info", {})
        layout = input_data.get("layout", {})
        
        if not brief:
            raise ValueError("brief is required")
        
        prompt_dict = {}
        
        # Visual do brief
        prompt_dict["palette_id"] = brief.palette_id
        prompt_dict["palette"] = json.dumps(brief.palette, indent=2)
        prompt_dict["typography_id"] = brief.typography_id
        prompt_dict["visual_style"] = brief.visual_style
        prompt_dict["visual_mood"] = brief.visual_mood
        
        # Emotions
        prompt_dict["primary_emotion"] = brief.primary_emotion
        prompt_dict["secondary_emotions"] = ", ".join(brief.secondary_emotions)
        prompt_dict["avoid_emotions"] = ", ".join(brief.avoid_emotions)
        
        # Slide info
        prompt_dict["slide_number"] = str(slide_info.get("number", 1))
        prompt_dict["module"] = slide_info.get("module", "")
        prompt_dict["purpose"] = slide_info.get("purpose", "")
        prompt_dict["visual_mood_slide"] = slide_info.get("visual_mood", brief.visual_mood)
        
        # Layout
        if layout:
            prompt_dict["layout"] = json.dumps(layout, indent=2)
        else:
            prompt_dict["layout"] = "{}"
        
        # Substitui variáveis
        prompt = self.prompt_template
        for key, value in prompt_dict.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))
        
        return prompt
    
    def _postprocess_visual(self, response: str) -> Dict[str, Any]:
        """φ_out: Transforma resposta em especificações visuais"""
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
            return {"background": {}, "elements": []}
