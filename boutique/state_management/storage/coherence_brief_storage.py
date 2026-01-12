"""
Coherence Brief Storage

Storage específico para CoherenceBrief usando JSON backend.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from framework.storage.adapters.json_adapter import JSONStorageBackend


class CoherenceBriefStorage(JSONStorageBackend):
    """
    Storage específico para CoherenceBrief.
    
    Serializa/deserializa CoherenceBrief para/do JSON.
    """
    
    def __init__(self, base_path: Path):
        """
        Inicializa storage para briefs.
        
        Args:
            base_path: Diretório base para armazenar briefs JSON
        """
        super().__init__(base_path / "briefs")
        self.base_path = base_path / "briefs"
    
    def store_brief(self, brief: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Armazena CoherenceBrief.
        
        Args:
            brief: CoherenceBrief object
            metadata: Metadados opcionais
            
        Returns:
            Chave (post_id) do brief armazenado
        """
        if not hasattr(brief, 'post_id'):
            raise ValueError("Brief must have post_id attribute")
        
        # Serializa brief para dict
        if hasattr(brief, 'to_dict'):
            brief_dict = brief.to_dict()
        else:
            # Fallback: usa dataclass asdict
            from dataclasses import asdict
            brief_dict = asdict(brief)
        
        return self.store(brief.post_id, brief_dict, metadata)
    
    def retrieve_brief(self, post_id: str) -> Optional[Any]:
        """
        Recupera CoherenceBrief.
        
        Args:
            post_id: Identificador do post
            
        Returns:
            CoherenceBrief object ou None
        """
        brief_dict = self.retrieve(post_id)
        if brief_dict is None:
            return None
        
        # Deserializa dict para CoherenceBrief
        from ..models.coherence_brief import CoherenceBrief
        
        # Converte estrutura aninhada de dict para CoherenceBrief
        return self._dict_to_brief(brief_dict)
    
    def _dict_to_brief(self, data: Dict[str, Any]) -> Any:
        """Converte dict aninhado para CoherenceBrief"""
        from ..models.coherence_brief import CoherenceBrief
        
        # Extrai campos do formato aninhado
        metadata = data.get("metadata", {})
        voice = data.get("voice", {})
        visual = data.get("visual", {})
        emotions = data.get("emotions", {})
        content = data.get("content", {})
        audience = data.get("audience", {})
        constraints = data.get("constraints", {})
        structure = data.get("structure", {})
        context = data.get("context", {})
        brand = data.get("brand", {})
        evolution = data.get("evolution", {})
        
        return CoherenceBrief(
            post_id=metadata.get("post_id", ""),
            idea_id=metadata.get("idea_id", ""),
            platform=metadata.get("platform", ""),
            format=metadata.get("format", ""),
            tone=voice.get("tone", ""),
            personality_traits=voice.get("personality_traits", []),
            vocabulary_level=voice.get("vocabulary_level", "moderate"),
            formality=voice.get("formality", "neutral"),
            palette_id=visual.get("palette_id", ""),
            palette=visual.get("palette", {}),
            typography_id=visual.get("typography_id", ""),
            typography=visual.get("typography", {}),
            visual_style=visual.get("style", ""),
            visual_mood=visual.get("mood", ""),
            canvas=visual.get("canvas", {}),
            primary_emotion=emotions.get("primary", ""),
            secondary_emotions=emotions.get("secondary", []),
            avoid_emotions=emotions.get("avoid", []),
            target_emotions=emotions.get("target", []),
            keywords_to_emphasize=content.get("keywords_to_emphasize", []),
            themes=content.get("themes", []),
            main_message=content.get("main_message", ""),
            value_proposition=content.get("value_proposition", ""),
            angle=content.get("angle", ""),
            hook=content.get("hook", ""),
            persona=audience.get("persona", ""),
            pain_points=audience.get("pain_points", []),
            desires=audience.get("desires", []),
            avoid_topics=constraints.get("avoid_topics", []),
            required_elements=constraints.get("required_elements", []),
            objective=structure.get("objective", ""),
            narrative_arc=structure.get("narrative_arc", ""),
            estimated_slides=structure.get("estimated_slides", 0),
            article_context=context.get("article_context", ""),
            key_insights_used=context.get("key_insights_used", []),
            key_insights_content=context.get("key_insights_content", []),
            idea_explanation=context.get("idea_explanation"),
            rationale=context.get("rationale"),
            brand_values=brand.get("values", []),
            brand_assets=brand.get("assets", {}),
            narrative_structure=evolution.get("narrative_structure"),
            narrative_pacing=evolution.get("narrative_pacing"),
            transition_style=evolution.get("transition_style"),
            arc_refined=evolution.get("arc_refined"),
            narrative_rationale=evolution.get("narrative_rationale"),
            copy_guidelines=evolution.get("copy_guidelines"),
            cta_guidelines=evolution.get("cta_guidelines"),
            visual_preferences=evolution.get("visual_preferences"),
            platform_constraints=evolution.get("platform_constraints"),
        )
