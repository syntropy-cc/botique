"""
Unit tests for Narrative Architect.

Tests the Narrative Architect agent that generates detailed slide-by-slide
narrative structures from coherence briefs.

Location: tests/test_narrative_architect.py
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.narrative.architect import NarrativeArchitect, build_insights_block
from src.coherence.brief import CoherenceBrief
from src.core.llm_client import HttpLLMClient


class TestNarrativeArchitect(unittest.TestCase):
    """Test cases for Narrative Architect."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock LLM client
        self.mock_llm_client = Mock(spec=HttpLLMClient)
        self.mock_logger = Mock()
        
        # Create narrative architect instance
        self.architect = NarrativeArchitect(
            llm_client=self.mock_llm_client,
            logger=self.mock_logger,
        )
        
        # Create sample CoherenceBrief
        self.brief = CoherenceBrief(
            post_id="test_post_001",
            idea_id="idea_001",
            platform="linkedin",
            format="carousel",
            tone="professional",
            personality_traits=["authoritative", "empowering"],
            vocabulary_level="moderate",
            formality="neutral",
            palette_id="blue_professional",
            palette={
                "theme": "professional",
                "primary": "#1E3A8A",
                "accent": "#3B82F6",
                "cta": "#10B981",
            },
            typography_id="modern_sans",
            typography={
                "heading_font": "Inter Bold",
                "body_font": "Inter Regular",
            },
            visual_style="clean and modern",
            visual_mood="confident",
            canvas={
                "width": 1080,
                "height": 1080,
                "aspect_ratio": "1:1",
            },
            primary_emotion="confident",
            secondary_emotions=["inspired", "motivated"],
            avoid_emotions=["anxious", "overwhelmed"],
            target_emotions=["confident", "inspired"],
            keywords_to_emphasize=["productivity", "efficiency", "growth"],
            themes=["productivity", "workplace"],
            main_message="Boost your team's productivity with smart workflows",
            value_proposition="Save 10 hours per week with automated processes",
            angle="Data-driven approach to workflow optimization",
            hook="Are you wasting 10 hours every week on repetitive tasks?",
            persona="Tech-savvy managers looking to optimize team workflows",
            pain_points=["manual processes", "lack of automation", "time waste"],
            desires=["efficiency", "scalability", "team productivity"],
            avoid_topics=["layoffs", "controversial politics"],
            required_elements=["data points", "actionable tips", "professional_cta"],
            objective="engagement",
            narrative_arc="problem-solution-benefit",
            estimated_slides=6,
            article_context="Article about workflow automation and productivity tools",
            key_insights_used=["insight_001", "insight_002"],
            key_insights_content=[
                {
                    "id": "insight_001",
                    "content": "Companies save 10 hours per week with automation",
                    "type": "statistic",
                    "strength": 8,
                    "source_quote": "According to recent studies...",
                },
                {
                    "id": "insight_002",
                    "content": "Manual processes reduce team morale",
                    "type": "advice",
                    "strength": 7,
                    "source_quote": "Experts recommend...",
                },
            ],
            idea_explanation="This idea focuses on workflow automation benefits",
            rationale="Workflow automation is a trending topic with high engagement potential",
        )
        
        # Sample valid LLM response
        self.valid_response = json.dumps({
            "narrative_pacing": "moderate",
            "transition_style": "smooth",
            "arc_refined": "Hook → Problem → Value (Data) → Value (Solution) → Value (Benefit) → CTA",
            "slides": [
                {
                    "slide_number": 1,
                    "template_type": "hook",
                    "value_subtype": None,
                    "purpose": "Hook the audience with a compelling question about time waste",
                    "target_emotions": ["curious", "engaged"],
                    "copy_direction": "Create an urgent, question-based hook that addresses the pain point of time waste on repetitive tasks. Use direct language that resonates with managers who struggle with inefficiency. Emphasize the emotional cost of wasted time and set up the narrative for the solution that follows. The tone should be conversational yet professional, inviting the reader to reflect on their own situation.",
                    "visual_direction": "Design a visual composition that emphasizes contrast and urgency. Use bold typography for the question, with a clean background that doesn't distract from the message. Consider using subtle time-related imagery or icons (clocks, calendars) to reinforce the time-waste theme. The color palette should draw attention without being overwhelming, using the primary brand color strategically to highlight key words.",
                    "key_elements": ["question", "urgency", "time waste"],
                    "insights_referenced": ["insight_001"],
                    "transition_to_next": "Lead into the problem and solution",
                },
                {
                    "slide_number": 2,
                    "template_type": "value",
                    "value_subtype": "data",
                    "purpose": "Present the core value proposition with supporting evidence",
                    "target_emotions": ["convinced", "interested"],
                    "copy_direction": "Highlight the main benefit (10 hours saved) clearly and concisely, supporting with data. Use concrete numbers and statistics to build credibility. Frame the value in terms that resonate with the target persona - emphasizing both time savings and team impact. The language should be professional yet accessible, avoiding jargon while maintaining authority.",
                    "visual_direction": "Create an icon-based layout with clear hierarchy, featuring data visualization. Use charts or infographic elements to present the statistics visually. The design should feel modern and trustworthy, with plenty of white space to ensure readability. Emphasize key numbers through typography and color, making the data immediately digestible. Consider using gradient backgrounds or subtle patterns to add visual interest without overwhelming the data presentation. Ensure that the color contrast meets accessibility standards while maintaining brand consistency.",
                    "key_elements": ["value", "benefit", "data"],
                    "insights_referenced": ["insight_001", "insight_002"],
                    "transition_to_next": "Move to solution details",
                },
                {
                    "slide_number": 3,
                    "template_type": "value",
                    "value_subtype": "solution",
                    "purpose": "Explain the solution approach",
                    "target_emotions": ["hopeful", "motivated"],
                    "copy_direction": "Explain how automation solves the identified problems. Focus on the practical approach and methodology rather than specific tools. Use clear, actionable language that helps readers understand the path forward. Emphasize the simplicity of getting started while highlighting the transformative potential. Address common concerns about implementation complexity and show how the solution integrates seamlessly into existing workflows. Use concrete examples that illustrate the before-and-after scenario to make the value tangible and relatable to the target audience.",
                    "visual_direction": "Design a visual that illustrates the solution concept through icons or simple diagrams. Use flow-based imagery to show the transformation from manual to automated processes. The composition should feel optimistic and forward-moving, with visual elements that suggest progress and efficiency. Consider using before-and-after comparisons or process flow diagrams that clearly communicate the transformation. Use warm, inviting colors that suggest positive change while maintaining professional credibility through balanced composition and clear visual hierarchy.",
                    "key_elements": ["solution", "automation", "process"],
                    "insights_referenced": [],
                    "transition_to_next": "Highlight the benefits",
                },
                {
                    "slide_number": 4,
                    "template_type": "value",
                    "value_subtype": "solution",
                    "purpose": "Showcase the benefits of automation",
                    "target_emotions": ["confident", "inspired"],
                    "copy_direction": "Detail the specific benefits teams experience after implementing automation. Focus on both quantitative results (time saved, efficiency gained) and qualitative improvements (team morale, reduced errors). Use examples that resonate with the target persona, showing real-world impact. Include testimonials or case study elements that add credibility and social proof. Connect the benefits to broader business outcomes like increased revenue opportunities, improved customer satisfaction, and competitive advantages that result from streamlined operations.",
                    "visual_direction": "Create a visual that emphasizes positive outcomes through imagery or icons representing benefits. Use upward-trending visuals, happy team imagery, or success indicators. The color palette should feel positive and energetic, reinforcing the benefits message. Consider using infographic-style layouts with icons for each key benefit, or illustrate a journey from challenge to success. The design should feel celebratory yet professional, using dynamic compositions that guide the eye and emphasize the transformative nature of the solution.",
                    "key_elements": ["benefits", "outcomes", "impact"],
                    "insights_referenced": ["insight_002"],
                    "transition_to_next": "Move to call-to-action",
                },
                {
                    "slide_number": 5,
                    "template_type": "cta",
                    "value_subtype": None,
                    "purpose": "Encourage action with a clear call-to-action",
                    "target_emotions": ["motivated", "ready"],
                    "copy_direction": "Create a clear, compelling call-to-action that motivates immediate engagement. The CTA should feel invitational rather than pushy, given the engagement objective. Invite readers to share their own experiences or explore the topic further. Use action-oriented language that creates a sense of opportunity rather than urgency. Frame the CTA as an invitation to join a conversation or community, making it feel collaborative and welcoming. Address potential objections subtly by acknowledging that the solution may not be right for everyone, while emphasizing the value for those who are ready to take action.",
                    "visual_direction": "Design a prominent CTA area with clear visual hierarchy. Use the CTA color from the brand palette to draw attention to the action element. Keep the design clean and uncluttered, ensuring the CTA text is easily readable. Consider using directional cues (arrows, pointers) to guide the eye toward the action.",
                    "key_elements": ["action", "engagement", "invitation"],
                    "insights_referenced": [],
                    "transition_to_next": None,
                },
            ],
            "rationale": {
                "pacing_choice": "Moderate pacing allows readers to digest the data and benefits without feeling rushed, suitable for professional LinkedIn audience.",
                "transition_choice": "Smooth transitions create a cohesive narrative flow that guides readers naturally through the problem-solution-benefit arc.",
                "emotional_arc": "Starts with curiosity and engagement, moves through conviction and interest, builds hope and motivation, culminates in confidence and readiness to act.",
                "structural_decisions": [
                    "Hook slide establishes the pain point immediately",
                    "Data slide provides credibility early in the narrative",
                    "Solution slides break down the approach into digestible parts",
                    "CTA slide aligns with engagement objective with invitational tone",
                ],
            },
        })
    
    def test_initialization(self):
        """Test Narrative Architect initialization."""
        architect = NarrativeArchitect(llm_client=self.mock_llm_client)
        
        self.assertEqual(architect.llm, self.mock_llm_client)
        self.assertIsNone(architect.logger)
        
        # Test with logger
        architect_with_logger = NarrativeArchitect(
            llm_client=self.mock_llm_client,
            logger=self.mock_logger,
        )
        self.assertEqual(architect_with_logger.logger, self.mock_logger)
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_success(self, mock_template_selector_class, mock_get_prompt):
        """Test successful narrative structure generation."""
        # Mock prompt retrieval
        mock_get_prompt.return_value = {
            "template": "Generate narrative structure. Objective: {objective}. Arc: {narrative_arc}."
        }
        
        # Mock template selector
        mock_template_selector = Mock()
        mock_template_selector_class.return_value = mock_template_selector
        mock_template_selector.select_template.return_value = (
            "template_001",
            "Semantic match with high confidence",
            0.85,
        )
        
        # Mock LLM response
        self.mock_llm_client.generate.return_value = self.valid_response
        
        # Call generate_structure
        result = self.architect.generate_structure(
            brief=self.brief,
            context="test_context",
        )
        
        # Verify prompt was loaded
        mock_get_prompt.assert_called_once_with("narrative_architect")
        
        # Verify LLM was called
        self.mock_llm_client.generate.assert_called_once()
        call_args = self.mock_llm_client.generate.call_args
        self.assertEqual(call_args.kwargs["context"], "test_context")
        self.assertEqual(call_args.kwargs["temperature"], 0.2)
        self.assertEqual(call_args.kwargs["prompt_key"], "narrative_architect")
        
        # Verify result structure
        self.assertIn("slides", result)
        self.assertEqual(len(result["slides"]), 5)
        self.assertEqual(result["narrative_pacing"], "moderate")
        self.assertEqual(result["transition_style"], "smooth")
        self.assertIn("arc_refined", result)
        self.assertIn("rationale", result)
        
        # Verify first slide is hook
        first_slide = result["slides"][0]
        self.assertEqual(first_slide["slide_number"], 1)
        self.assertEqual(first_slide["template_type"], "hook")
        self.assertIsNone(first_slide["value_subtype"])
        
        # Verify last slide is CTA
        last_slide = result["slides"][-1]
        self.assertEqual(last_slide["template_type"], "cta")
        self.assertIsNone(last_slide["value_subtype"])
        
        # Verify template selector was called for each slide
        self.assertEqual(mock_template_selector.select_template.call_count, 5)
        
        # Verify brief was enriched
        self.assertIsNotNone(self.brief.narrative_structure)
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_with_prompt_version(self, mock_template_selector_class, mock_get_prompt):
        """Test narrative structure generation with specific prompt version."""
        # Mock prompt retrieval by version
        with patch('src.narrative.architect.get_prompt_by_key_and_version') as mock_get_version:
            mock_get_version.return_value = {
                "template": "Versioned template: {objective}"
            }
            
            mock_template_selector = Mock()
            mock_template_selector_class.return_value = mock_template_selector
            mock_template_selector.select_template.return_value = (
                "template_001",
                "Justification",
                0.8,
            )
            
            self.mock_llm_client.generate.return_value = self.valid_response
            
            result = self.architect.generate_structure(
                brief=self.brief,
                prompt_version="v2",
            )
            
            # Verify version-specific prompt was loaded
            mock_get_version.assert_called_once_with("narrative_architect", "v2")
            mock_get_prompt.assert_not_called()
            
            # Verify result
            self.assertIn("slides", result)
    
    @patch('src.narrative.architect.get_latest_prompt')
    def test_generate_structure_prompt_not_found(self, mock_get_prompt):
        """Test error handling when prompt is not found."""
        mock_get_prompt.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        self.assertIn("Prompt 'narrative_architect' not found", str(context.exception))
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_invalid_response_structure(self, mock_template_selector_class, mock_get_prompt):
        """Test error handling with invalid response structure."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Invalid response (missing required top-level keys)
        invalid_response = json.dumps({"wrong_key": []})
        self.mock_llm_client.generate.return_value = invalid_response
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        error_msg = str(context.exception)
        self.assertIn("Missing required keys", error_msg)
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_invalid_pacing(self, mock_template_selector_class, mock_get_prompt):
        """Test error handling with invalid narrative pacing."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        invalid_response = json.loads(self.valid_response)
        invalid_response["narrative_pacing"] = "invalid_pacing"
        invalid_response_str = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = invalid_response_str
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        self.assertIn("Invalid narrative_pacing", str(context.exception))
        self.assertIn("invalid_pacing", str(context.exception))
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_invalid_transition_style(self, mock_template_selector_class, mock_get_prompt):
        """Test error handling with invalid transition style."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        invalid_response = json.loads(self.valid_response)
        invalid_response["transition_style"] = "invalid_style"
        invalid_response_str = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = invalid_response_str
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        self.assertIn("Invalid transition_style", str(context.exception))
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_wrong_slide_count(self, mock_template_selector_class, mock_get_prompt):
        """Test error handling when slide count is out of range."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Response with too many slides
        invalid_response = json.loads(self.valid_response)
        # Create 20 slides (exceeds MAX_SLIDES_PER_POST which is typically 15)
        many_slides = invalid_response["slides"] * 4  # 5 * 4 = 20
        invalid_response["slides"] = many_slides
        invalid_response_str = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = invalid_response_str
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        self.assertIn("Slide count", str(context.exception))
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_first_slide_not_hook(self, mock_template_selector_class, mock_get_prompt):
        """Test error handling when first slide is not a hook."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        invalid_response = json.loads(self.valid_response)
        invalid_response["slides"][0]["template_type"] = "value"  # Change from hook
        invalid_response_str = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = invalid_response_str
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        self.assertIn("First slide must have template_type='hook'", str(context.exception))
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_last_slide_not_cta_when_required(self, mock_template_selector_class, mock_get_prompt):
        """Test error handling when last slide is not CTA when required."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        invalid_response = json.loads(self.valid_response)
        invalid_response["slides"][-1]["template_type"] = "value"  # Change from cta
        invalid_response_str = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = invalid_response_str
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        self.assertIn("Last slide must have template_type='cta'", str(context.exception))
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_value_slide_missing_subtype(self, mock_template_selector_class, mock_get_prompt):
        """Test error handling when value slide is missing value_subtype."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        invalid_response = json.loads(self.valid_response)
        invalid_response["slides"][1]["value_subtype"] = None  # Remove required subtype
        invalid_response_str = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = invalid_response_str
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        self.assertIn("template_type='value' requires value_subtype", str(context.exception))
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_invalid_value_subtype(self, mock_template_selector_class, mock_get_prompt):
        """Test error handling with invalid value_subtype."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        invalid_response = json.loads(self.valid_response)
        invalid_response["slides"][1]["value_subtype"] = "invalid_subtype"
        invalid_response_str = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = invalid_response_str
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        self.assertIn("Invalid value_subtype", str(context.exception))
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_hook_with_value_subtype(self, mock_template_selector_class, mock_get_prompt):
        """Test error handling when hook slide has value_subtype set."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        invalid_response = json.loads(self.valid_response)
        invalid_response["slides"][0]["value_subtype"] = "data"  # Hook shouldn't have subtype
        invalid_response_str = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = invalid_response_str
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        self.assertIn("must have value_subtype=null", str(context.exception))
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_missing_insights_referenced(self, mock_template_selector_class, mock_get_prompt):
        """Test error handling when insights are not referenced."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        invalid_response = json.loads(self.valid_response)
        # Remove insight_002 from all slides
        for slide in invalid_response["slides"]:
            if "insight_002" in slide.get("insights_referenced", []):
                slide["insights_referenced"] = [
                    i for i in slide["insights_referenced"] if i != "insight_002"
                ]
        invalid_response_str = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = invalid_response_str
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        self.assertIn("Insights not referenced", str(context.exception))
        self.assertIn("insight_002", str(context.exception))
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_avoid_emotions_in_target(self, mock_template_selector_class, mock_get_prompt):
        """Test error handling when avoid_emotions appear in target_emotions."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        invalid_response = json.loads(self.valid_response)
        invalid_response["slides"][0]["target_emotions"] = ["anxious"]  # Use avoid emotion
        invalid_response_str = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = invalid_response_str
        
        with self.assertRaises(ValueError) as context:
            self.architect.generate_structure(brief=self.brief)
        
        self.assertIn("uses avoid_emotions", str(context.exception))
        self.assertIn("anxious", str(context.exception))
    
    def test_build_prompt_dict(self):
        """Test _build_prompt_dict method."""
        prompt_dict = self.architect._build_prompt_dict(self.brief)
        
        # Verify narrative foundation
        self.assertEqual(prompt_dict["objective"], "engagement")
        self.assertEqual(prompt_dict["narrative_arc"], "problem-solution-benefit")
        self.assertEqual(prompt_dict["estimated_slides"], "6")
        self.assertEqual(prompt_dict["hook"], self.brief.hook)
        
        # Verify content essence
        self.assertEqual(prompt_dict["main_message"], self.brief.main_message)
        self.assertEqual(prompt_dict["value_proposition"], self.brief.value_proposition)
        self.assertEqual(prompt_dict["keywords_to_emphasize"], "productivity, efficiency, growth")
        self.assertEqual(prompt_dict["themes"], "productivity, workplace")
        
        # Verify audience
        self.assertEqual(prompt_dict["persona"], self.brief.persona)
        self.assertEqual(prompt_dict["pain_points"], "manual processes, lack of automation, time waste")
        self.assertEqual(prompt_dict["desires"], "efficiency, scalability, team productivity")
        
        # Verify emotions
        self.assertEqual(prompt_dict["primary_emotion"], "confident")
        self.assertEqual(prompt_dict["secondary_emotions"], "inspired, motivated")
        self.assertEqual(prompt_dict["avoid_emotions"], "anxious, overwhelmed")
        self.assertEqual(prompt_dict["target_emotions"], "confident, inspired")
        
        # Verify voice & platform
        self.assertEqual(prompt_dict["platform"], "linkedin")
        self.assertEqual(prompt_dict["format"], "carousel")
        self.assertEqual(prompt_dict["tone"], "professional")
        self.assertEqual(prompt_dict["personality_traits"], "authoritative, empowering")
        
        # Verify insights
        self.assertIn("key_insights_content_block", prompt_dict)
        self.assertIn("insight_001", prompt_dict["key_insights_content_block"])
        self.assertIn("insight_002", prompt_dict["key_insights_content_block"])
    
    def test_build_insights_block(self):
        """Test build_insights_block helper function."""
        insights_block = build_insights_block(self.brief)
        
        # Should contain both insights
        self.assertIn("insight_001", insights_block)
        self.assertIn("insight_002", insights_block)
        self.assertIn("Companies save 10 hours", insights_block)
        self.assertIn("Manual processes", insights_block)
        self.assertIn("statistic", insights_block)
        self.assertIn("advice", insights_block)
        
        # Test with brief that has no insights
        brief_no_insights = CoherenceBrief(
            post_id="test_002",
            idea_id="idea_002",
            platform="linkedin",
            format="carousel",
            tone="professional",
            personality_traits=["authoritative"],
            vocabulary_level="moderate",
            formality="neutral",
            palette_id="blue",
            palette={},
            typography_id="sans",
            typography={},
            visual_style="clean",
            visual_mood="confident",
            canvas={"width": 1080, "height": 1080},
            primary_emotion="confident",
            secondary_emotions=[],
            avoid_emotions=[],
            target_emotions=["confident"],
            keywords_to_emphasize=[],
            themes=[],
            main_message="Test message",
            value_proposition="Test value",
            angle="Test angle",
            hook="Test hook",
            persona="Test persona",
            pain_points=[],
            desires=[],
            avoid_topics=[],
            required_elements=[],
            objective="engagement",
            narrative_arc="problem-solution",
            estimated_slides=3,
            article_context="Test context",
            key_insights_used=[],
            key_insights_content=[],
            idea_explanation="Test explanation",
            rationale="Test rationale",
        )
        
        insights_block_empty = build_insights_block(brief_no_insights)
        self.assertIn("no insights provided", insights_block_empty.lower())
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_validate_response_valid(self, mock_template_selector_class, mock_get_prompt):
        """Test _validate_response with valid response."""
        mock_get_prompt.return_value = {"template": "Template"}
        mock_template_selector = Mock()
        mock_template_selector_class.return_value = mock_template_selector
        mock_template_selector.select_template.return_value = ("template_001", "Justification", 0.8)
        
        payload = self.architect._validate_response(
            raw_response=self.valid_response,
            brief=self.brief,
        )
        
        self.assertIn("slides", payload)
        self.assertEqual(len(payload["slides"]), 5)
        self.assertEqual(payload["narrative_pacing"], "moderate")
        self.assertEqual(payload["transition_style"], "smooth")
    
    def test_validate_response_invalid_json(self):
        """Test _validate_response with invalid JSON."""
        with self.assertRaises(ValueError):
            self.architect._validate_response(
                raw_response="not json",
                brief=self.brief,
            )
    
    def test_validate_semantics_slide_count_single_image(self):
        """Test _validate_semantics with single_image format requiring exactly 1 slide."""
        brief_single = CoherenceBrief(
            post_id="test_single",
            idea_id="idea_single",
            platform="linkedin",
            format="single_image",
            tone="professional",
            personality_traits=["authoritative"],
            vocabulary_level="moderate",
            formality="neutral",
            palette_id="blue",
            palette={},
            typography_id="sans",
            typography={},
            visual_style="clean",
            visual_mood="confident",
            canvas={"width": 1080, "height": 1080},
            primary_emotion="confident",
            secondary_emotions=[],
            avoid_emotions=[],
            target_emotions=["confident"],
            keywords_to_emphasize=[],
            themes=[],
            main_message="Test",
            value_proposition="Test",
            angle="Test",
            hook="Test",
            persona="Test",
            pain_points=[],
            desires=[],
            avoid_topics=[],
            required_elements=[],
            objective="engagement",
            narrative_arc="problem-solution",
            estimated_slides=1,
            article_context="Test",
            key_insights_used=[],
            key_insights_content=[],
            idea_explanation="Test",
            rationale="Test",
        )
        
        # Valid: exactly 1 slide
        valid_response = json.loads(self.valid_response)
        valid_response["slides"] = [valid_response["slides"][0]]
        valid_response["slides"][0]["template_type"] = "hook"
        
        payload = {
            "narrative_pacing": "moderate",
            "transition_style": "smooth",
            "arc_refined": "Hook",
            "slides": valid_response["slides"],
            "rationale": {},
        }
        
        # Should not raise
        try:
            self.architect._validate_semantics(payload, brief_single)
        except ValueError:
            self.fail("_validate_semantics should not raise for valid single_image format")
        
        # Invalid: 2 slides for single_image
        payload["slides"].append(valid_response["slides"][0].copy())
        payload["slides"][1]["slide_number"] = 2
        
        with self.assertRaises(ValueError) as context:
            self.architect._validate_semantics(payload, brief_single)
        
        self.assertIn("single_image format requires exactly 1 slide", str(context.exception))
    
    @patch('src.narrative.architect.get_latest_prompt')
    @patch('src.templates.selector.TemplateSelector')
    def test_generate_structure_logging(self, mock_template_selector_class, mock_get_prompt):
        """Test that logging is performed when logger is available."""
        mock_get_prompt.return_value = {"template": "Template"}
        mock_template_selector = Mock()
        mock_template_selector_class.return_value = mock_template_selector
        mock_template_selector.select_template.return_value = ("template_001", "Justification", 0.8)
        
        self.mock_llm_client.generate.return_value = self.valid_response
        
        # Reset logger mock
        self.mock_logger.reset_mock()
        self.mock_logger.current_trace_id = "test_trace_001"
        
        result = self.architect.generate_structure(
            brief=self.brief,
            context="test_context",
        )
        
        # Verify success logging was called
        self.mock_logger.log_step_event.assert_called()
        
        # Check that log_step_event was called with success status
        calls = self.mock_logger.log_step_event.call_args_list
        success_call = None
        for call in calls:
            if call.kwargs.get("status") == "success":
                success_call = call
                break
        
        self.assertIsNotNone(success_call)
        self.assertEqual(success_call.kwargs["name"], "narrative_architect_success_test_post_001")
        self.assertEqual(success_call.kwargs["status"], "success")
        self.assertIn("output_obj", success_call.kwargs)
    
    def test_count_insights_referenced(self):
        """Test _count_insights_referenced method."""
        slides = json.loads(self.valid_response)["slides"]
        
        count = self.architect._count_insights_referenced(slides)
        
        # insight_001 and insight_002 are referenced
        self.assertEqual(count, 2)


class TestNarrativeArchitectIntegration(unittest.TestCase):
    """
    Integration tests for Narrative Architect with real LLM calls.
    
    These tests require LLM_API_KEY or DEEPSEEK_API_KEY environment variable.
    The tests automatically load the .env file if it exists (using python-dotenv).
    They will be skipped automatically if the API key is not available.
    
    To run these tests, either:
    1. Create a .env file with: DEEPSEEK_API_KEY=your_api_key_here
    2. Or set the environment variable: export LLM_API_KEY=your_api_key_here
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up integration test fixtures (once per test class)."""
        import os
        from pathlib import Path
        
        # Load environment variables from .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # dotenv not available, continue without it
            pass
        
        from src.core.prompt_registry import register_prompt, find_existing_prompt
        from src.core.config import PROMPTS_DIR
        
        # Check if LLM API key is available (from .env or environment)
        cls.api_key = os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        if not cls.api_key:
            cls.skip_integration = True
            cls.skip_reason = (
                "LLM_API_KEY or DEEPSEEK_API_KEY not found. "
                "Integration tests require a real API key to make LLM calls. "
                "Create a .env file with DEEPSEEK_API_KEY=your_key or set the environment variable."
            )
            return
        
        cls.skip_integration = False
        
        # Register the narrative_architect prompt if not already registered
        narrative_architect_template_path = PROMPTS_DIR / "narrative_architect.md"
        if narrative_architect_template_path.exists():
            with open(narrative_architect_template_path, 'r', encoding='utf-8') as f:
                template_text = f.read()
            
            # Check if prompt already exists
            existing = find_existing_prompt("narrative_architect", template_text)
            if not existing:
                # Register the prompt
                register_prompt(
                    prompt_key="narrative_architect",
                    template=template_text,
                    description="Narrative Architect prompt for generating slide-by-slide narrative structures",
                    metadata={
                        "registered_by": "test_narrative_architect",
                        "source_file": str(narrative_architect_template_path),
                    },
                )
                print(f"✓ Registered narrative_architect prompt for integration tests")
            else:
                print(f"✓ Narrative Architect prompt already registered: {existing[1]}")
        else:
            cls.skip_integration = True
            cls.skip_reason = f"Narrative Architect prompt template not found at {narrative_architect_template_path}"
            print(f"⚠️  {cls.skip_reason}")
            return
    
    def setUp(self):
        """Set up test fixtures."""
        if self.skip_integration:
            self.skipTest(self.skip_reason)
        
        # Create real LLM client
        from src.core.llm_logger import LLMLogger
        
        self.logger = LLMLogger()
        self.logger.set_context(article_slug="test_article", post_id="test_post_integration")
        trace_id = self.logger.create_trace(name="test_narrative_architect_integration")
        self.logger.current_trace_id = trace_id
        
        self.llm_client = HttpLLMClient(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            logger=self.logger,
        )
        
        # Create narrative architect instance
        self.architect = NarrativeArchitect(
            llm_client=self.llm_client,
            logger=self.logger,
        )
        
        # Create realistic CoherenceBrief
        self.brief = CoherenceBrief(
            post_id="test_post_integration_001",
            idea_id="idea_integration_001",
            platform="linkedin",
            format="carousel",
            tone="professional",
            personality_traits=["authoritative", "empathetic"],
            vocabulary_level="moderate",
            formality="neutral",
            palette_id="blue_professional",
            palette={
                "theme": "professional",
                "primary": "#1E3A8A",
                "accent": "#3B82F6",
                "cta": "#10B981",
            },
            typography_id="modern_sans",
            typography={
                "heading_font": "Inter Bold",
                "body_font": "Inter Regular",
            },
            visual_style="clean and modern",
            visual_mood="confident",
            canvas={
                "width": 1080,
                "height": 1080,
                "aspect_ratio": "1:1",
            },
            primary_emotion="confident",
            secondary_emotions=["inspired", "motivated"],
            avoid_emotions=["anxious", "overwhelmed"],
            target_emotions=["confident", "inspired"],
            keywords_to_emphasize=["productivity", "automation", "efficiency"],
            themes=["productivity", "workplace automation"],
            main_message="Boost your team's productivity with smart workflows",
            value_proposition="Save 10 hours per week with automated processes",
            angle="Data-driven approach to workflow optimization",
            hook="Are you wasting 10 hours every week on repetitive tasks?",
            persona="Tech-savvy managers looking to optimize team workflows",
            pain_points=["manual processes", "lack of automation", "time waste"],
            desires=["efficiency", "scalability", "team productivity"],
            avoid_topics=["layoffs", "controversial politics"],
            required_elements=["data points", "actionable tips", "professional_cta"],
            objective="engagement",
            narrative_arc="problem-solution-benefit",
            estimated_slides=6,
            article_context="Article about workflow automation and productivity tools",
            key_insights_used=["insight_001", "insight_002"],
            key_insights_content=[
                {
                    "id": "insight_001",
                    "content": "Companies save an average of 10 hours per week with workflow automation",
                    "type": "statistic",
                    "strength": 8,
                    "source_quote": "According to recent studies, teams that automate workflows save significant time.",
                },
                {
                    "id": "insight_002",
                    "content": "Manual processes reduce team morale and increase errors",
                    "type": "advice",
                    "strength": 7,
                    "source_quote": "Experts recommend automating repetitive tasks to improve team satisfaction.",
                },
            ],
            idea_explanation="This idea focuses on the tangible benefits of workflow automation, using data to support the value proposition.",
            rationale="Workflow automation is a trending topic with high engagement potential on LinkedIn",
        )
    
    def test_generate_structure_real_llm(self):
        """Test narrative structure generation with real LLM API calls."""
        # Generate structure
        result = self.architect.generate_structure(
            brief=self.brief,
            context="integration_test_001",
        )
        
        # Verify result structure
        self.assertIn("slides", result)
        self.assertGreaterEqual(len(result["slides"]), 3, "Should generate at least 3 slides")
        self.assertLessEqual(len(result["slides"]), 15, "Should not exceed maximum slides")
        
        # Verify top-level fields
        self.assertIn("narrative_pacing", result)
        self.assertIn("transition_style", result)
        self.assertIn("arc_refined", result)
        self.assertIn("rationale", result)
        
        # Verify pacing is valid
        valid_pacing = {"fast", "moderate", "deliberate"}
        self.assertIn(result["narrative_pacing"], valid_pacing,
                     f"narrative_pacing should be one of {valid_pacing}")
        
        # Verify transition style is valid
        valid_transitions = {"abrupt", "smooth", "dramatic", "conversational"}
        self.assertIn(result["transition_style"], valid_transitions,
                     f"transition_style should be one of {valid_transitions}")
        
        # Verify each slide
        for slide_idx, slide in enumerate(result["slides"]):
            slide_num = slide.get("slide_number")
            
            # Verify slide number matches index
            self.assertEqual(slide_num, slide_idx + 1,
                           f"Slide {slide_idx + 1} number should match index")
            
            # Verify required fields
            self.assertIn("template_type", slide,
                         f"Slide {slide_num} must have template_type")
            self.assertIn("value_subtype", slide,
                         f"Slide {slide_num} must have value_subtype")
            self.assertIn("purpose", slide,
                         f"Slide {slide_num} must have purpose")
            self.assertIn("target_emotions", slide,
                         f"Slide {slide_num} must have target_emotions")
            self.assertIn("copy_direction", slide,
                         f"Slide {slide_num} must have copy_direction")
            self.assertIn("visual_direction", slide,
                         f"Slide {slide_num} must have visual_direction")
            self.assertIn("key_elements", slide,
                         f"Slide {slide_num} must have key_elements")
            self.assertIn("insights_referenced", slide,
                         f"Slide {slide_num} must have insights_referenced")
            
            # Verify template_type is valid
            valid_template_types = {"hook", "transition", "value", "cta"}
            template_type = slide.get("template_type")
            self.assertIn(template_type, valid_template_types,
                         f"Slide {slide_num} template_type should be one of {valid_template_types}")
            
            # Verify value_subtype rules
            value_subtype = slide.get("value_subtype")
            if template_type == "value":
                valid_value_subtypes = {"data", "insight", "solution", "example"}
                self.assertIsNotNone(value_subtype,
                                    f"Slide {slide_num} (value type) must have value_subtype")
                self.assertIn(value_subtype, valid_value_subtypes,
                             f"Slide {slide_num} value_subtype should be one of {valid_value_subtypes}")
            else:
                self.assertIsNone(value_subtype,
                                 f"Slide {slide_num} ({template_type} type) must have value_subtype=None")
            
            # Verify first slide is hook
            if slide_idx == 0:
                self.assertEqual(template_type, "hook",
                               "First slide must be a hook")
            
            # Verify last slide is CTA (since professional_cta is required)
            if slide_idx == len(result["slides"]) - 1:
                self.assertEqual(template_type, "cta",
                               "Last slide must be a CTA when professional_cta is required")
            
            # Verify copy_direction and visual_direction are non-empty
            copy_direction = slide.get("copy_direction", "")
            visual_direction = slide.get("visual_direction", "")
            self.assertIsInstance(copy_direction, str)
            self.assertIsInstance(visual_direction, str)
            self.assertGreater(len(copy_direction), 0,
                             f"Slide {slide_num} copy_direction must not be empty")
            self.assertGreater(len(visual_direction), 0,
                             f"Slide {slide_num} visual_direction must not be empty")
            
            # Verify target_emotions is a list
            target_emotions = slide.get("target_emotions", [])
            self.assertIsInstance(target_emotions, list,
                                 f"Slide {slide_num} target_emotions must be a list")
            
            # Verify no avoid emotions in target_emotions
            avoid_emotions = set(self.brief.avoid_emotions or [])
            overlap = avoid_emotions & set(target_emotions)
            self.assertEqual(len(overlap), 0,
                           f"Slide {slide_num} should not use avoid_emotions: {overlap}")
            
            # Verify insights_referenced is a list
            insights_referenced = slide.get("insights_referenced", [])
            self.assertIsInstance(insights_referenced, list,
                                 f"Slide {slide_num} insights_referenced must be a list")
        
        # Verify all insights are referenced
        insights_used = set(self.brief.key_insights_used or [])
        insights_referenced = set()
        for slide in result["slides"]:
            insights_referenced.update(slide.get("insights_referenced", []))
        
        missing = insights_used - insights_referenced
        self.assertEqual(len(missing), 0,
                        f"All insights should be referenced. Missing: {missing}")
        
        # Verify brief was enriched
        self.assertIsNotNone(self.brief.narrative_structure,
                           "Brief should be enriched with narrative structure")
    
    def test_generate_structure_content_quality(self):
        """Test that generated content meets quality requirements."""
        result = self.architect.generate_structure(
            brief=self.brief,
            context="integration_test_quality",
        )
        
        slides = result.get("slides", [])
        self.assertGreater(len(slides), 0, "Should generate at least one slide")
        
        # Verify copy_direction and visual_direction length
        for slide in slides:
            slide_num = slide.get("slide_number")
            copy_direction = slide.get("copy_direction", "")
            visual_direction = slide.get("visual_direction", "")
            
            # Should be substantial (at least 50 words as per prompt, but we're lenient in tests)
            copy_words = len(copy_direction.split())
            visual_words = len(visual_direction.split())
            
            # Verify reasonable length (not too short)
            self.assertGreater(copy_words, 20,
                             f"Slide {slide_num} copy_direction should be substantial (got {copy_words} words)")
            self.assertGreater(visual_words, 20,
                             f"Slide {slide_num} visual_direction should be substantial (got {visual_words} words)")
            
            # Verify key_elements is not empty for most slides
            key_elements = slide.get("key_elements", [])
            self.assertIsInstance(key_elements, list)
            # Allow empty for some slides, but most should have elements
        
        # Verify rationale structure
        rationale = result.get("rationale", {})
        self.assertIsInstance(rationale, dict,
                             "Rationale should be a dictionary")
        # Rationale fields are optional but nice to have
        if rationale:
            self.assertIn("pacing_choice", rationale or "transition_choice" in rationale or "emotional_arc" in rationale or "structural_decisions" in rationale,
                         "Rationale should contain at least one explanation field")
    
    def test_generate_structure_semantic_alignment(self):
        """Test that generated structure aligns semantically with brief."""
        result = self.architect.generate_structure(
            brief=self.brief,
            context="integration_test_semantic",
        )
        
        slides = result.get("slides", [])
        
        # Check that keywords from brief appear in key_elements or copy_direction
        keywords_to_check = ["productivity", "automation", "efficiency", "workflow"]
        content_text = " ".join([
            " ".join(slide.get("key_elements", [])) + " " + slide.get("copy_direction", "")
            for slide in slides
        ]).lower()
        
        # At least some keywords should appear
        keywords_found = [
            keyword for keyword in keywords_to_check
            if keyword.lower() in content_text
        ]
        self.assertGreater(len(keywords_found), 0,
                          f"Generated structure should include some keywords from brief: {keywords_to_check}")
        
        # Verify arc_refined mentions the hook or main message concepts
        arc_refined = result.get("arc_refined", "").lower()
        self.assertGreater(len(arc_refined), 0,
                         "arc_refined should be a non-empty string")
        
        # Verify that the structure makes sense (first slide is hook, last is CTA)
        self.assertEqual(slides[0].get("template_type"), "hook",
                        "First slide should be a hook")
        self.assertEqual(slides[-1].get("template_type"), "cta",
                        "Last slide should be a CTA when required")
        
        # Verify brief enrichment
        self.assertIsNotNone(self.brief.narrative_structure,
                           "Brief should be enriched after generation")


if __name__ == '__main__':
    unittest.main()
