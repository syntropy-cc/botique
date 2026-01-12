"""
Validators Tool

Tool para validação de qualidade de outputs.
"""

from typing import Any, Dict, List

from framework.core.tool import Tool


class QualityValidatorTool(Tool):
    """Tool para validação de qualidade"""
    
    def __init__(self):
        super().__init__(
            sig=("output_data", "validation_rules"),
            f=self._validate_quality,
            effects=set(),  # Não modifica estado
            name="quality_validator",
            description="Validates quality of generated outputs",
        )
    
    def _validate_quality(
        self,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Valida qualidade de outputs.
        
        Args:
            input_data: Deve conter "output_data" e opcionalmente "validation_rules"
            
        Returns:
            Dict com score e breakdown
        """
        output_data = input_data.get("output_data", {})
        validation_rules = input_data.get("validation_rules", {})
        
        scores = {}
        total_score = 0.0
        weight_sum = 0.0
        
        # Validação de coerência
        coherence_score = self._validate_coherence(output_data)
        coherence_weight = validation_rules.get("coherence_weight", 0.4)
        scores["coherence"] = coherence_score
        total_score += coherence_score * coherence_weight
        weight_sum += coherence_weight
        
        # Validação visual
        visual_score = self._validate_visual(output_data)
        visual_weight = validation_rules.get("visual_weight", 0.3)
        scores["visual"] = visual_score
        total_score += visual_score * visual_weight
        weight_sum += visual_weight
        
        # Validação de conteúdo
        content_score = self._validate_content(output_data)
        content_weight = validation_rules.get("content_weight", 0.3)
        scores["content"] = content_score
        total_score += content_score * content_weight
        weight_sum += content_weight
        
        # Normaliza score
        final_score = total_score / weight_sum if weight_sum > 0 else 0.0
        
        return {
            "score": final_score,
            "breakdown": scores,
            "passed": final_score >= validation_rules.get("threshold", 0.7),
        }
    
    def _validate_coherence(self, output_data: Dict[str, Any]) -> float:
        """Valida coerência (voice, visual consistency)"""
        # Verifica se brief está presente e completo
        brief = output_data.get("brief")
        if not brief:
            return 0.5
        
        # Verifica campos essenciais
        essential_fields = ["tone", "platform", "main_message"]
        present_fields = sum(1 for field in essential_fields if hasattr(brief, field) and getattr(brief, field))
        
        return present_fields / len(essential_fields)
    
    def _validate_visual(self, output_data: Dict[str, Any]) -> float:
        """Valida aspectos visuais"""
        # Verifica se palette e typography estão presentes
        brief = output_data.get("brief")
        if not brief:
            return 0.5
        
        score = 0.0
        if hasattr(brief, 'palette') and brief.palette:
            score += 0.5
        if hasattr(brief, 'typography') and brief.typography:
            score += 0.5
        
        return score
    
    def _validate_content(self, output_data: Dict[str, Any]) -> float:
        """Valida conteúdo (completude, qualidade)"""
        # Verifica se há conteúdo gerado
        slides = output_data.get("slides", [])
        if not slides:
            return 0.0
        
        # Verifica se slides têm conteúdo
        valid_slides = 0
        for slide in slides:
            if isinstance(slide, dict):
                texts = slide.get("texts", {})
                if texts:
                    valid_slides += 1
        
        return valid_slides / len(slides) if slides else 0.0
