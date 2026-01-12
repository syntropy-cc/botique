"""
Boutique Orchestrator

Orquestrador específico do boutique que executa fases sequenciais.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from framework.core.orchestrator import Orchestrator
from framework.core.universal_state import UniversalState

from boutique.agents.caption_writer_agent import CaptionWriterAgent
from boutique.agents.copywriter_agent import CopywriterAgent
from boutique.agents.narrative_architect_agent import NarrativeArchitectAgent
from boutique.agents.post_ideator_agent import PostIdeatorAgent
from boutique.agents.visual_composer_agent import VisualComposerAgent
from boutique.state_management.boutique_state import BoutiqueState


class BoutiqueOrchestrator(Orchestrator):
    """
    Orquestrador específico do boutique.
    
    Executa pipeline sequencial simples:
    Phase 1 (Ideation) → Phase 2 (Selection) → Phase 3 (Coherence) → ...
    """
    
    def __init__(self):
        """Inicializa orquestrador do boutique."""
        super().__init__()
        self._register_boutique_agents()
    
    def _register_boutique_agents(self):
        """Registra agentes específicos do boutique."""
        self.register_agent(PostIdeatorAgent(), "Generates post ideas from articles")
        self.register_agent(NarrativeArchitectAgent(), "Creates narrative structures")
        self.register_agent(CopywriterAgent(), "Writes slide copy")
        self.register_agent(VisualComposerAgent(), "Composes visual designs")
        self.register_agent(CaptionWriterAgent(), "Writes post captions")
    
    def run_full_pipeline(
        self,
        article_path: Path,
        ideation_config: Optional[Any] = None,
        selection_config: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Executa pipeline completo de geração de posts.
        
        Args:
            article_path: Caminho para artigo
            ideation_config: Configuração de ideação
            selection_config: Configuração de seleção
            
        Returns:
            Resultado completo do pipeline
        """
        # Lê artigo
        article_text = article_path.read_text(encoding="utf-8")
        article_slug = article_path.stem
        
        # Cria estado do boutique
        state = BoutiqueState()
        state.article_slug = article_slug
        
        # Phase 1: Ideation
        ideation_result = self.orchestrate(
            query="ideation",
            initial_data={
                "article": article_text,
                "article_slug": article_slug,
                "config": ideation_config,
                "article_path": str(article_path),
            },
            state=state,
        )
        
        # Phase 2: Selection (se necessário)
        # Por enquanto, usa todas as ideias
        ideas = ideation_result.get("ideas", [])
        selected_ideas = ideas[:selection_config.max_posts if selection_config else 3]
        
        # Phase 3: Coherence (para cada idea selecionada)
        briefs = []
        for idea in selected_ideas:
            post_id = f"post_{article_slug}_{idea.get('id', 'unknown')}"
            
            # Cria brief usando CoherenceBriefBuilder
            from boutique.state_management.models.coherence_brief import CoherenceBrief
            from boutique.state_management.models.brand.library import BrandLibrary
            from boutique.state_management.models.brand.audience import get_audience_profile, enrich_idea_with_audience
            
            # Resolve parâmetros
            platform = idea.get("platform", "")
            tone = idea.get("tone", "")
            persona = idea.get("persona", "")
            format_type = idea.get("format", "carousel")
            
            palette = BrandLibrary.select_palette(platform, tone, persona)
            typography = BrandLibrary.select_typography(platform, persona)
            canvas = BrandLibrary.get_canvas_config(platform, format_type)
            
            # Enrich com audience
            audience_profile = get_audience_profile(persona)
            if audience_profile:
                idea = enrich_idea_with_audience(idea, audience_profile)
            
            # Cria brief básico (simplificado - pode usar CoherenceBriefBuilder completo)
            brief = CoherenceBrief(
                post_id=post_id,
                idea_id=idea.get("id", ""),
                platform=platform,
                format=format_type,
                tone=tone,
                personality_traits=idea.get("personality_traits", []),
                vocabulary_level=idea.get("vocabulary_level", "moderate"),
                formality=idea.get("formality", "neutral"),
                palette_id=palette.id if hasattr(palette, 'id') else "",
                palette=palette.__dict__ if hasattr(palette, '__dict__') else {},
                typography_id=typography.id if hasattr(typography, 'id') else "",
                typography=typography.__dict__ if hasattr(typography, '__dict__') else {},
                visual_style="",
                visual_mood="",
                canvas=canvas.__dict__ if hasattr(canvas, '__dict__') else {},
                primary_emotion=idea.get("primary_emotion", ""),
                secondary_emotions=idea.get("secondary_emotions", []),
                avoid_emotions=idea.get("avoid_emotions", []),
                target_emotions=idea.get("target_emotions", []),
                keywords_to_emphasize=idea.get("keywords", []),
                themes=ideation_result.get("article_summary", {}).get("themes", []),
                main_message=idea.get("main_message", ""),
                value_proposition=idea.get("value_proposition", ""),
                angle=idea.get("angle", ""),
                hook=idea.get("hook", ""),
                persona=persona,
                pain_points=idea.get("pain_points", []),
                desires=idea.get("desires", []),
                avoid_topics=[],
                required_elements=[],
                objective=idea.get("objective", ""),
                narrative_arc=idea.get("narrative_arc", ""),
                estimated_slides=idea.get("estimated_slides", 7),
                article_context=ideation_result.get("article_summary", {}).get("main_thesis", ""),
                key_insights_used=idea.get("key_insights_used", []),
                key_insights_content=ideation_result.get("article_summary", {}).get("key_insights", []),
            )
            
            state.store_brief(brief)
            briefs.append(brief)
        
        return {
            "article_slug": article_slug,
            "article_summary": ideation_result.get("article_summary", {}),
            "ideas": ideas,
            "selected_ideas": selected_ideas,
            "briefs": briefs,
        }
