"""
Template selector with semantic analysis using embeddings

Selects appropriate templates using embedding-based semantic similarity.
Uses sentence-transformers to generate high-quality embeddings that capture
the real meaning of text, not just keywords.

Location: src/templates/selector.py
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
import numpy as np

from .library import TemplateLibrary
from .textual_templates import TextualTemplate

# Configure logging
logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logger.warning(
        "sentence-transformers not available. "
        "Using keyword-based fallback method. "
        "For real semantic analysis, install: pip install sentence-transformers"
    )


class TemplateSelector:
    """Selects textual template based on semantic similarity using embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize template selector.
        
        Args:
            model_name: Name of the embeddings model.
                       Default uses fast English-optimized model.
                       Alternatives:
                       - "paraphrase-multilingual-MiniLM-L12-v2" (multilingual support)
                       - "all-mpnet-base-v2" (higher quality, slower)
                       - "all-MiniLM-L6-v2" (faster, English-only)
        """
        self.library = TemplateLibrary()
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.template_embeddings_cache: Dict[str, np.ndarray] = {}
        
        # Initialize embeddings model if available
        if EMBEDDINGS_AVAILABLE:
            try:
                logger.info(f"Loading embeddings model: {model_name}")
                self.model = SentenceTransformer(model_name)
                self._precompute_template_embeddings()
                logger.info(f"Model loaded successfully. {len(self.template_embeddings_cache)} templates indexed.")
            except Exception as e:
                logger.error(f"Error loading embeddings model: {e}")
                self.model = None
        else:
            logger.info("Using fallback method without embeddings")
    
    def _precompute_template_embeddings(self) -> None:
        """
        Pre-compute embeddings for all templates to optimize performance.
        
        Calculates embeddings once and stores in cache. This avoids recalculating
        on each selection and makes the process much faster.
        """
        if not self.model:
            return
        
        logger.info("Pre-computing template embeddings...")
        
        for template_id, template in self.library.templates.items():
            # Combine template information for rich embedding
            template_text = self._build_template_description(template)
            
            # Generate embedding
            embedding = self.model.encode(template_text, convert_to_numpy=True)
            self.template_embeddings_cache[template_id] = embedding
        
        logger.info(f"Pre-computed embeddings for {len(self.template_embeddings_cache)} templates")
    
    def _build_template_description(self, template: TextualTemplate) -> str:
        """
        Build rich template description for embedding.
        
        Combines multiple template fields to create a complete semantic
        representation that will be converted to embedding.
        
        Args:
            template: Template to describe
            
        Returns:
            Combined text describing the template
        """
        parts = [
            template.semantic_description or "",
            template.function or "",
            template.structure or "",
            " ".join(template.keywords or []),
        ]
        return " ".join([p for p in parts if p])
    
    def select_template(
        self,
        template_type: str,
        value_subtype: str = None,
        purpose: str = "",
        copy_direction: str = "",
        key_elements: List[str] = None,
        persona: str = "",
        tone: str = "",
        platform: str = "",
    ) -> Tuple[str, str, float]:
        """
        Select appropriate template based on semantic similarity.
        
        Uses embeddings to find the template most semantically similar
        to the slide description created by the Narrative Architect.
        
        Args:
            template_type: High-level template type (hook, transition, value, cta)
            value_subtype: Value subtype (data, insight, solution, example) - required if template_type is 'value'
            purpose: Slide purpose from Narrative Architect
            copy_direction: Narrative guidance from Narrative Architect
            key_elements: Key slide elements
            persona: Brief persona
            tone: Brief tone
            platform: Brief platform
        
        Returns:
            Tuple of (template_id, justification, confidence)
        """
        key_elements = key_elements or []
        
        # Map template type to specific module types
        template_module_types = self._map_template_type_to_module_types(template_type, value_subtype)
        
        # Get candidate templates from all relevant types
        candidates = []
        for template_module_type in template_module_types:
            candidates.extend(self.library.get_templates_by_module_type(template_module_type))
        
        if not candidates:
            raise ValueError(f"No template found for template_type: {template_type}, value_subtype: {value_subtype}")
        
        # Build slide description for semantic analysis
        slide_description = self._build_slide_description(
            purpose=purpose,
            copy_direction=copy_direction,
            key_elements=key_elements,
        )
        
        # Select best template using embeddings or fallback
        if self.model and EMBEDDINGS_AVAILABLE:
            best_template_id, best_score = self._select_with_embeddings(
                candidates=candidates,
                slide_description=slide_description,
                tone=tone,
            )
        else:
            best_template_id, best_score = self._select_with_fallback(
                candidates=candidates,
                slide_description=slide_description,
                persona=persona,
                tone=tone,
            )
        
        # Generate justification
        justification = self._generate_justification(
            template_id=best_template_id,
            score=best_score,
            persona=persona,
            tone=tone,
            method="embeddings" if self.model else "fallback",
        )
        
        return (best_template_id, justification, best_score)
    
    def _select_with_embeddings(
        self,
        candidates: List[TextualTemplate],
        slide_description: str,
        tone: str,
    ) -> Tuple[str, float]:
        """
        Select template using embedding similarity (primary method).
        
        Uses cosine similarity between slide description embedding
        and pre-computed template embeddings.
        
        Args:
            candidates: List of candidate templates
            slide_description: Combined slide description
            tone: Brief tone
            
        Returns:
            Tuple of (template_id, score)
        """
        # Generate embedding for slide description
        slide_embedding = self.model.encode(slide_description, convert_to_numpy=True)
        
        # Calculate cosine similarity with each candidate
        scores = []
        for template in candidates:
            template_embedding = self.template_embeddings_cache.get(template.id)
            
            if template_embedding is None:
                # If for some reason we don't have the embedding cached, calculate now
                template_text = self._build_template_description(template)
                template_embedding = self.model.encode(template_text, convert_to_numpy=True)
                self.template_embeddings_cache[template.id] = template_embedding
            
            # Cosine similarity
            similarity = self._cosine_similarity(slide_embedding, template_embedding)
            
            # Boost based on tone (small fine-tuning)
            tone_boost = self._calculate_tone_boost(template, tone)
            final_score = similarity * 0.9 + tone_boost * 0.1
            
            scores.append((template.id, final_score))
        
        # Select template with highest score
        scores.sort(key=lambda x: x[1], reverse=True)
        best_template_id, best_score = scores[0]
        
        logger.debug(f"Top 3 templates by embeddings: {scores[:3]}")
        
        return best_template_id, best_score
    
    def _select_with_fallback(
        self,
        candidates: List[TextualTemplate],
        slide_description: str,
        persona: str,
        tone: str,
    ) -> Tuple[str, float]:
        """
        Select template using fallback method (without embeddings).
        
        Uses keyword matching and text analysis when
        embeddings are not available.
        
        Args:
            candidates: List of candidate templates
            slide_description: Combined slide description
            persona: Brief persona
            tone: Brief tone
            
        Returns:
            Tuple of (template_id, score)
        """
        scores = []
        for template in candidates:
            score = self._calculate_semantic_similarity_fallback(
                template=template,
                slide_description=slide_description,
                persona=persona,
                tone=tone,
            )
            scores.append((template.id, score))
        
        # Select template with highest score
        scores.sort(key=lambda x: x[1], reverse=True)
        best_template_id, best_score = scores[0]
        
        logger.debug(f"Top 3 templates by fallback: {scores[:3]}")
        
        return best_template_id, best_score
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (0.0 to 1.0)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to 0-1 (cosine similarity can be -1 to 1)
        normalized = (similarity + 1) / 2
        
        return float(normalized)
    
    def _calculate_tone_boost(self, template: TextualTemplate, tone: str) -> float:
        """
        Calculate small boost based on tone matching.
        
        Fine-tuning to prefer templates with similar tone to specified.
        
        Args:
            template: Template to evaluate
            tone: Desired tone
            
        Returns:
            Boost score (0.0 to 1.0)
        """
        if not tone or not template.tone:
            return 0.5
        
        template_tone_normalized = self._normalize_text(template.tone)
        brief_tone_normalized = self._normalize_text(tone)
        
        # Check words in common
        template_words = set(template_tone_normalized.split())
        brief_words = set(brief_tone_normalized.split())
        
        if not template_words or not brief_words:
            return 0.5
        
        overlap = len(template_words.intersection(brief_words))
        max_words = max(len(template_words), len(brief_words))
        
        return overlap / max_words if max_words > 0 else 0.5
    
    def _build_slide_description(
        self,
        purpose: str,
        copy_direction: str,
        key_elements: List[str],
    ) -> str:
        """
        Build comprehensive slide description for semantic analysis.
        
        Combines purpose and copy_direction from Narrative Architect to create
        a rich description of what the slide should communicate.
        
        Args:
            purpose: Slide purpose
            copy_direction: Narrative guidance
            key_elements: Key elements
        
        Returns:
            Combined description string
        """
        description_parts = [purpose, copy_direction]
        if key_elements:
            description_parts.append(" ".join(key_elements))
        return " ".join(description_parts)
    
    def _map_template_type_to_module_types(self, template_type: str, value_subtype: str = None) -> List[str]:
        """
        Map high-level template type to specific module types.
        
        High-level template types: hook, transition, value, cta
        Value subtypes: data, insight, solution, example
        Template module types (in library): hook, insight, solution, example, cta
        
        Args:
            template_type: High-level template type
            value_subtype: Value subtype (only relevant if template_type is 'value')
        
        Returns:
            List of template module types to search
        """
        if template_type == "hook":
            return ["hook"]
        elif template_type == "transition":
            # Transitions use insight-style templates
            return ["insight"]
        elif template_type == "value":
            # Map value subtypes to template module types
            if value_subtype == "data":
                return ["insight"]  # Data templates are stored as insight module_type
            elif value_subtype == "insight":
                return ["insight"]  # Insight templates
            elif value_subtype == "solution":
                return ["solution"]  # Solution templates
            elif value_subtype == "example":
                return ["example"]  # Example templates
            else:
                # If no subtype specified, search all value-related templates
                return ["insight", "solution", "example"]
        elif template_type == "cta":
            return ["cta"]
        else:
            # Default to insight if unknown
            return ["insight"]
    
    def _calculate_semantic_similarity_fallback(
        self,
        template: TextualTemplate,
        slide_description: str,
        persona: str,
        tone: str,
    ) -> float:
        """
        Calculate semantic similarity score using fallback method (0.0-1.0).
        
        Uses multiple matching strategies when embeddings are not available:
        1. Semantic description matching (primary - 50%)
        2. Function matching (25%)
        3. Tone matching (15%)
        4. Keyword matching (10%)
        
        Args:
            template: Template to evaluate
            slide_description: Combined slide description from Narrative Architect
            persona: Brief persona
            tone: Brief tone
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        score = 0.0
        
        # Normalize text for comparison
        slide_text = self._normalize_text(slide_description)
        template_description = self._normalize_text(template.semantic_description or "")
        template_function = self._normalize_text(template.function or "")
        template_tone = self._normalize_text(template.tone or "")
        brief_tone = self._normalize_text(tone)
        
        # 1. Semantic description matching (50% weight)
        if template_description:
            description_score = self._text_similarity(slide_text, template_description)
            score += description_score * 0.5
        
        # 2. Function matching (25% weight)
        if template_function:
            function_score = self._text_similarity(slide_text, template_function)
            score += function_score * 0.25
        
        # 3. Tone matching (15% weight)
        if template_tone and brief_tone:
            tone_score = self._text_similarity(template_tone, brief_tone)
            score += tone_score * 0.15
        
        # 4. Keyword matching (10% weight)
        template_keywords = template.keywords or []
        if template_keywords:
            keyword_score = self._keyword_similarity(slide_text, template_keywords)
            score += keyword_score * 0.1
        
        # Ensure score is between 0.0 and 1.0
        return min(score, 1.0)
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Input text
        
        Returns:
            Normalized text (lowercase, punctuation removed, whitespace normalized)
        """
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation (keep alphanumeric and spaces)
        text = re.sub(r'[^\w\s]', ' ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate text similarity using word overlap and position.
        
        Uses Jaccard similarity (intersection over union) weighted by
        word frequency and position importance.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity (intersection over union)
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        base_similarity = intersection / union
        
        # Boost score if multiple matching words
        # (indicates stronger semantic match)
        if intersection > 1:
            boost = min(0.2, intersection * 0.05)
            base_similarity = min(1.0, base_similarity + boost)
        
        return base_similarity
    
    def _keyword_similarity(self, text: str, keywords: List[str]) -> float:
        """
        Calculate keyword matching score.
        
        Args:
            text: Text to search in
            keywords: List of keywords to match
        
        Returns:
            Score between 0.0 and 1.0 based on keyword matches
        """
        if not keywords:
            return 0.0
        
        normalized_text = self._normalize_text(text)
        normalized_keywords = [self._normalize_text(kw) for kw in keywords]
        
        matches = sum(1 for kw in normalized_keywords if kw in normalized_text)
        return matches / len(normalized_keywords)
    
    def _generate_justification(
        self,
        template_id: str,
        score: float,
        persona: str,
        tone: str,
        method: str = "embeddings",
    ) -> str:
        """
        Generate justification for template selection.
        
        Args:
            template_id: Selected template ID
            score: Similarity score
            persona: Brief persona
            tone: Brief tone
            method: Method used ("embeddings" or "fallback")
        
        Returns:
            Justification string
        """
        template = self.library.get_template(template_id)
        if not template:
            return f"Template {template_id} selected (score: {score:.2f})"
        
        structure_preview = template.structure[:50]
        if len(template.structure) > 50:
            structure_preview += "..."
        
        method_label = "📊 Semantic Analysis" if method == "embeddings" else "🔤 Fallback"
        
        return (
            f"{method_label} | {persona} in {tone} → {template.function} "
            f"({structure_preview}) - similarity: {score:.2f}"
        )
