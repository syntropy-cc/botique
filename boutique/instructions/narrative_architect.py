"""
Narrative Architect Instruction

Instrução para geração de estruturas narrativas detalhadas slide por slide.
"""

import json
from pathlib import Path
from typing import Any, Dict

from framework.core.instruction import Instruction


class NarrativeArchitectInstruction(Instruction):
    """Instrução para arquitetura narrativa"""
    
    def __init__(self):
        template_path = Path(__file__).parent / "templates" / "narrative_architect.md"
        template = template_path.read_text(encoding="utf-8")
        
        super().__init__(
            prompt_key="narrative_architect",
            prompt_template=template,
            model="deepseek-chat",
            temperature=0.2,
            max_tokens=8048,
            preprocess=self._preprocess_brief,
            postprocess=self._postprocess_structure,
        )
    
    def _preprocess_brief(self, input_data: Dict[str, Any]) -> str:
        """φ_in: Transforma brief em formato para prompt"""
        brief = input_data.get("brief")
        article_text = input_data.get("article_text", "")
        
        if not brief:
            raise ValueError("brief is required")
        
        # Constrói contexto do brief
        prompt_dict = {}
        
        # Voice
        prompt_dict["tone"] = brief.tone
        prompt_dict["personality_traits"] = ", ".join(brief.personality_traits)
        prompt_dict["vocabulary_level"] = brief.vocabulary_level
        prompt_dict["formality"] = brief.formality
        
        # Visual
        prompt_dict["visual_style"] = brief.visual_style
        prompt_dict["visual_mood"] = brief.visual_mood
        
        # Emotions
        prompt_dict["primary_emotion"] = brief.primary_emotion
        prompt_dict["secondary_emotions"] = ", ".join(brief.secondary_emotions)
        prompt_dict["avoid_emotions"] = ", ".join(brief.avoid_emotions)
        
        # Content
        prompt_dict["keywords"] = ", ".join(brief.keywords_to_emphasize)
        prompt_dict["themes"] = ", ".join(brief.themes)
        prompt_dict["main_message"] = brief.main_message
        prompt_dict["angle"] = brief.angle
        prompt_dict["hook"] = brief.hook
        
        # Audience
        prompt_dict["persona"] = brief.persona
        prompt_dict["pain_points"] = ", ".join(brief.pain_points)
        prompt_dict["desires"] = ", ".join(brief.desires)
        
        # Structure
        prompt_dict["objective"] = brief.objective
        prompt_dict["narrative_arc"] = brief.narrative_arc
        prompt_dict["estimated_slides"] = str(brief.estimated_slides)
        
        # Insights
        if hasattr(brief, 'key_insights_content') and brief.key_insights_content:
            insights_block = self._build_insights_block(brief)
            prompt_dict["insights_block"] = insights_block
        else:
            prompt_dict["insights_block"] = "- (no insights provided)"
        
        prompt_dict["article_text"] = article_text
        
        # Substitui variáveis no template
        prompt = self.prompt_template
        for key, value in prompt_dict.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))
        
        return prompt
    
    def _build_insights_block(self, brief) -> str:
        """Constrói bloco de insights formatado"""
        lines = []
        for insight in brief.key_insights_content:
            insight_id = insight.get("id", "unknown")
            content = insight.get("content", "")
            insight_type = insight.get("type", "unknown")
            strength = insight.get("strength", "N/A")
            source_quote = insight.get("source_quote", "")
            
            lines.append(
                f"- ID: {insight_id}\n"
                f"  Content: {content}\n"
                f"  Type: {insight_type}\n"
                f"  Strength: {strength} (1-10 scale)\n"
                f"  Source Quote: {source_quote}"
            )
        
        return "\n".join(lines) if lines else "- (no insights provided)"
    
    def _postprocess_structure(self, response: str) -> Dict[str, Any]:
        """φ_out: Transforma resposta em estrutura narrativa"""
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
            return {"pacing": "moderate", "transition_style": "smooth", "slides": []}
