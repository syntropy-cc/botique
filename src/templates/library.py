"""
Template library manager

Manages textual/narrative templates and provides access methods.

Location: src/templates/library.py
"""

from typing import Dict, List, Optional

from .textual_templates import (
    TextualTemplate,
    HOOK_TEMPLATES,
    VALUE_DATA_TEMPLATES,
    VALUE_INSIGHT_TEMPLATES,
    VALUE_SOLUTION_TEMPLATES,
    VALUE_EXAMPLE_TEMPLATES,
    CTA_TEMPLATES,
)


class TemplateLibrary:
    """Manages textual/narrative template library"""
    
    def __init__(self):
        """Initialize template library"""
        self.templates: Dict[str, TextualTemplate] = {}
        self._load_all_templates()
    
    def _load_all_templates(self) -> None:
        """Load all templates into dictionary by ID"""
        all_templates = (
            HOOK_TEMPLATES +
            VALUE_DATA_TEMPLATES +
            VALUE_INSIGHT_TEMPLATES +
            VALUE_SOLUTION_TEMPLATES +
            VALUE_EXAMPLE_TEMPLATES +
            CTA_TEMPLATES
        )
        self.templates = {t.id: t for t in all_templates}
    
    def get_template(self, template_id: str) -> Optional[TextualTemplate]:
        """
        Get template by ID.
        
        Args:
            template_id: Template ID (ex: "H_QUESTION")
            
        Returns:
            TextualTemplate if found, None otherwise
        """
        return self.templates.get(template_id)
    
    def get_templates_by_module_type(self, module_type: str) -> List[TextualTemplate]:
        """
        Get all templates of a specific module type.
        
        Args:
            module_type: Module type ("hook", "insight", "solution", "example", "cta")
            
        Returns:
            List of templates matching the module type
        """
        return [t for t in self.templates.values() if t.module_type == module_type]
    
    def get_templates_for_ids(self, template_ids: List[str]) -> List[TextualTemplate]:
        """
        Get templates for specified IDs.
        
        Args:
            template_ids: List of template IDs
            
        Returns:
            List of templates found (in order of IDs)
        """
        return [self.templates[tid] for tid in template_ids if tid in self.templates]
    
    def to_detailed_reference(self, template_ids: List[str]) -> str:
        """
        Generate detailed reference for specified templates.
        
        For use in Copywriter prompts - includes structure, examples, etc.
        
        Args:
            template_ids: List of template IDs to include
            
        Returns:
            Formatted markdown string with detailed template information
        """
        templates = self.get_templates_for_ids(template_ids)
        if not templates:
            return "- (no templates selected)"
        
        lines = []
        lines.append("## SELECTED TEXTUAL TEMPLATES\n")
        
        # Group by module type for better organization
        by_type: Dict[str, List[TextualTemplate]] = {}
        for template in templates:
            if template.module_type not in by_type:
                by_type[template.module_type] = []
            by_type[template.module_type].append(template)
        
        # Output templates grouped by type
        type_names = {
            "hook": "HOOK",
            "insight": "VALUE: Insight/Data",
            "solution": "VALUE: Solution",
            "example": "VALUE: Example",
            "cta": "CTA",
        }
        
        for module_type in ["hook", "insight", "solution", "example", "cta"]:
            if module_type not in by_type:
                continue
            
            type_name = type_names.get(module_type, module_type.upper())
            lines.append(f"### {type_name} Templates\n")
            
            for template in by_type[module_type]:
                lines.append(f"- **{template.id}**: {template.function}")
                
                # Detailed description (comprehensive explanation)
                if template.detailed_description:
                    lines.append(f"  - Detailed Description: {template.detailed_description}")
                
                # Structure (conceptual guide, not literal)
                lines.append(f"  - Structure: `{template.structure}` (conceptual guide, not literal text)")
                
                # Length range
                lines.append(f"  - Length: {template.length_range[0]}-{template.length_range[1]} characters")
                
                # Tone
                lines.append(f"  - Tone: {template.tone}")
                
                # Creative guidance (prominently displayed)
                if template.creative_guidance:
                    lines.append(f"  - Creative Guidance: {template.creative_guidance}")
                
                # Interpretation notes
                if template.interpretation_notes:
                    lines.append(f"  - Interpretation Notes: {template.interpretation_notes}")
                
                # Usage examples (numbered list)
                if template.usage_examples:
                    lines.append("  - Usage Examples:")
                    for idx, example in enumerate(template.usage_examples, 1):
                        lines.append(f"    {idx}. \"{example}\"")
                
                # What to avoid (warning/note)
                if template.what_to_avoid:
                    lines.append(f"  - Avoid: {template.what_to_avoid}")
                
                # Basic example (legacy)
                if template.example:
                    lines.append(f"  - Basic Example: \"{template.example}\"")
                
                lines.append("")
        
        return "\n".join(lines)
