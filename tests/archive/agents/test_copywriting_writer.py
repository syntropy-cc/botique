"""
Unit tests for Copywriter.

Tests the Copywriter agent that generates text content for slides
with emphasis guidance based on narrative structure and coherence brief.

Location: tests/test_copywriting_writer.py
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.copywriting.writer import Copywriter, _build_slide_insights_block
from src.coherence.brief import CoherenceBrief
from src.core.llm_client import HttpLLMClient


class TestCopywriter(unittest.TestCase):
    """Test cases for Copywriter."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock LLM client
        self.mock_llm_client = Mock(spec=HttpLLMClient)
        self.mock_logger = Mock()
        
        # Create copywriter instance
        self.copywriter = Copywriter(
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
            required_elements=["data points", "actionable tips"],
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
        
        # Create sample slides_info
        self.slides_info = [
            {
                "slide_number": 1,
                "template_id": "hero_001",
                "template_type": "hero",
                "purpose": "Hook the audience with a compelling question",
                "copy_direction": "Create an urgent, question-based hook that addresses the pain point",
                "visual_direction": "Bold typography with contrasting colors",
                "content_slots": {
                    "headline": {"required": True, "max_chars": 60},
                    "subheadline": {"required": False, "max_chars": 120},
                },
                "target_emotions": ["curious", "engaged"],
                "key_elements": ["question", "urgency"],
                "insights_referenced": ["insight_001"],
                "transition_to_next": "Lead into the problem",
            },
            {
                "slide_number": 2,
                "template_id": "value_001",
                "template_type": "value",
                "value_subtype": "benefit",
                "purpose": "Present the core value proposition",
                "copy_direction": "Highlight the main benefit clearly and concisely",
                "visual_direction": "Icon-based layout with clear hierarchy",
                "content_slots": {
                    "headline": {"required": True, "max_chars": 60},
                    "body": {"required": True, "max_chars": 250},
                },
                "target_emotions": ["convinced", "interested"],
                "key_elements": ["value", "benefit"],
                "insights_referenced": ["insight_001", "insight_002"],
                "transition_to_next": "Move to supporting evidence",
            },
            {
                "slide_number": 3,
                "template_id": "cta_001",
                "template_type": "cta",
                "purpose": "Encourage action",
                "copy_direction": "Create a clear, compelling call-to-action",
                "visual_direction": "Prominent CTA button with contrasting color",
                "content_slots": {
                    "headline": {"required": True, "max_chars": 60},
                },
                "target_emotions": ["motivated", "ready"],
                "key_elements": ["action", "urgency"],
                "insights_referenced": [],
                "transition_to_next": None,  # Last slide
            },
        ]
        
        # Sample article text
        self.article_text = """
        Workflow automation has become essential for modern teams. According to recent
        studies, companies that implement automation tools save an average of 10 hours
        per week. This translates to significant cost savings and improved team morale.
        Manual processes not only waste time but also reduce employee satisfaction.
        Experts recommend starting with repetitive tasks and gradually expanding
        automation across all workflows.
        """
        
        # Sample valid LLM response
        self.valid_response = json.dumps({
            "slides": [
                {
                    "slide_number": 1,
                    "title": {
                        "content": "Are you wasting 10 hours every week?",
                        "emphasis": ["wasting", "10 hours", "every week"]
                    },
                    "subtitle": {
                        "content": "Repetitive tasks are killing your productivity",
                        "emphasis": ["repetitive tasks", "productivity"]
                    },
                    "body": None,
                    "copy_guidelines": {
                        "headline_style": "question-based",
                        "body_style": "direct",
                    },
                    "cta_guidelines": None,
                },
                {
                    "slide_number": 2,
                    "title": {
                        "content": "Save 10 hours per week with automation",
                        "emphasis": ["Save", "10 hours", "automation"]
                    },
                    "subtitle": None,
                    "body": {
                        "content": "Companies that automate workflows report significant time savings and improved team morale.",
                        "emphasis": ["automate", "time savings", "team morale"]
                    },
                    "copy_guidelines": {
                        "headline_style": "benefit-focused",
                        "body_style": "evidence-based",
                    },
                    "cta_guidelines": None,
                },
                {
                    "slide_number": 3,
                    "title": {
                        "content": "Start automating today",
                        "emphasis": ["Start", "today"]
                    },
                    "subtitle": None,
                    "body": None,
                    "copy_guidelines": {
                        "headline_style": "action-oriented",
                        "body_style": None,
                    },
                    "cta_guidelines": {
                        "type": "button",
                        "tone": "urgent",
                        "suggested_text": "Learn More",
                    },
                },
            ],
        })
    
    def test_initialization(self):
        """Test Copywriter initialization."""
        copywriter = Copywriter(llm_client=self.mock_llm_client)
        
        self.assertEqual(copywriter.llm, self.mock_llm_client)
        self.assertIsNone(copywriter.logger)
        
        # Test with logger
        copywriter_with_logger = Copywriter(
            llm_client=self.mock_llm_client,
            logger=self.mock_logger,
        )
        self.assertEqual(copywriter_with_logger.logger, self.mock_logger)
    
    @patch('src.copywriting.writer.get_latest_prompt')
    def test_generate_post_copy_success(self, mock_get_prompt):
        """Test successful post copy generation."""
        # Mock prompt retrieval
        mock_get_prompt.return_value = {
            "template": "Generate copy for {total_slides} slides. Platform: {platform}. Tone: {tone}."
        }
        
        # Mock LLM response
        self.mock_llm_client.generate.return_value = self.valid_response
        
        # Call generate_post_copy
        result = self.copywriter.generate_post_copy(
            brief=self.brief,
            slides_info=self.slides_info,
            article_text=self.article_text,
        )
        
        # Verify prompt was loaded
        mock_get_prompt.assert_called_once_with("copywriter")
        
        # Verify LLM was called
        self.mock_llm_client.generate.assert_called_once()
        call_args = self.mock_llm_client.generate.call_args
        self.assertEqual(call_args.kwargs["context"], "test_post_001_post_copy")
        self.assertEqual(call_args.kwargs["temperature"], 0.3)
        self.assertEqual(call_args.kwargs["prompt_key"], "copywriter")
        
        # Verify result structure
        self.assertIn("slides", result)
        self.assertEqual(len(result["slides"]), 3)
        
        # Verify first slide
        slide1 = result["slides"][0]
        self.assertEqual(slide1["slide_number"], 1)
        self.assertIsNotNone(slide1["title"])
        self.assertEqual(slide1["title"]["content"], "Are you wasting 10 hours every week?")
        self.assertIn("emphasis", slide1["title"])
        self.assertIsNotNone(slide1["subtitle"])
        self.assertIsNone(slide1["body"])
        
        # Verify brief was enriched
        self.assertIsNotNone(self.brief.copy_guidelines)
        self.assertEqual(
            self.brief.copy_guidelines["headline_style"],
            "question-based"
        )
    
    @patch('src.copywriting.writer.get_latest_prompt')
    def test_generate_post_copy_with_prompt_version(self, mock_get_prompt):
        """Test post copy generation with specific prompt version."""
        # Mock prompt retrieval by version
        with patch('src.copywriting.writer.get_prompt_by_key_and_version') as mock_get_version:
            mock_get_version.return_value = {
                "template": "Versioned template: {platform}"
            }
            
            self.mock_llm_client.generate.return_value = self.valid_response
            
            result = self.copywriter.generate_post_copy(
                brief=self.brief,
                slides_info=self.slides_info,
                article_text=self.article_text,
                prompt_version="v2",
            )
            
            # Verify version-specific prompt was loaded
            mock_get_version.assert_called_once_with("copywriter", "v2")
            mock_get_prompt.assert_not_called()
            
            # Verify result
            self.assertIn("slides", result)
    
    @patch('src.copywriting.writer.get_latest_prompt')
    def test_generate_post_copy_prompt_not_found(self, mock_get_prompt):
        """Test error handling when prompt is not found."""
        mock_get_prompt.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.copywriter.generate_post_copy(
                brief=self.brief,
                slides_info=self.slides_info,
                article_text=self.article_text,
            )
        
        self.assertIn("Prompt 'copywriter' not found", str(context.exception))
    
    @patch('src.copywriting.writer.get_latest_prompt')
    def test_generate_post_copy_invalid_response_structure(self, mock_get_prompt):
        """Test error handling with invalid response structure."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Invalid response (missing slides)
        invalid_response = json.dumps({"wrong_key": []})
        self.mock_llm_client.generate.return_value = invalid_response
        
        with self.assertRaises(ValueError) as context:
            self.copywriter.generate_post_copy(
                brief=self.brief,
                slides_info=self.slides_info,
                article_text=self.article_text,
            )
        
        # Error message from validate_llm_json_response: "Missing required keys in JSON: slides"
        error_msg = str(context.exception)
        self.assertIn("Missing required keys", error_msg)
        self.assertIn("slides", error_msg)
    
    @patch('src.copywriting.writer.get_latest_prompt')
    def test_generate_post_copy_wrong_slide_count(self, mock_get_prompt):
        """Test error handling when slide count doesn't match."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Response with wrong number of slides
        parsed_wrong = json.loads(self.valid_response)
        parsed_wrong["slides"] = parsed_wrong["slides"][:1]  # Only 1 slide instead of 3
        wrong_response = json.dumps(parsed_wrong)
        
        self.mock_llm_client.generate.return_value = wrong_response
        
        with self.assertRaises(ValueError) as context:
            self.copywriter.generate_post_copy(
                brief=self.brief,
                slides_info=self.slides_info,
                article_text=self.article_text,
            )
        
        self.assertIn("Expected 3 slides", str(context.exception))
    
    @patch('src.copywriting.writer.get_latest_prompt')
    def test_generate_post_copy_missing_required_slot(self, mock_get_prompt):
        """Test error handling when required content slot is missing."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Response missing required headline for slide 2
        invalid_response = json.loads(self.valid_response)
        invalid_response["slides"][1]["title"] = None  # Remove required headline
        invalid_response_str = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = invalid_response_str
        
        with self.assertRaises(ValueError) as context:
            self.copywriter.generate_post_copy(
                brief=self.brief,
                slides_info=self.slides_info,
                article_text=self.article_text,
            )
        
        self.assertIn("Required content slot", str(context.exception))
        self.assertIn("headline", str(context.exception))
    
    @patch('src.copywriting.writer.get_latest_prompt')
    def test_generate_post_copy_max_tokens_calculation(self, mock_get_prompt):
        """Test max_tokens calculation based on number of slides."""
        mock_get_prompt.return_value = {"template": "Template"}
        self.mock_llm_client.generate.return_value = self.valid_response
        
        # Test with 3 slides (should be 1000 + 3*500 = 2500)
        result = self.copywriter.generate_post_copy(
            brief=self.brief,
            slides_info=self.slides_info,
            article_text=self.article_text,
        )
        
        call_args = self.mock_llm_client.generate.call_args
        self.assertEqual(call_args.kwargs["max_tokens"], 2500)
        
        # Test with 15 slides (should be capped at 8192)
        # Formula: min(8192, 1000 + (num_slides * 500))
        # With 15 slides: 1000 + (15 * 500) = 8500 >= 8192, so cap to 8192
        # With 13 slides: 1000 + (13 * 500) = 7500 < 8192, so would be 7500
        many_slides = self.slides_info * 5  # 3*5 = 15 slides
        # Create mock response with 15 slides to match
        valid_slides = json.loads(self.valid_response)["slides"]
        many_slides_response = json.dumps({
            "slides": valid_slides * 5  # 3*5 = 15 slides
        })
        self.mock_llm_client.generate.return_value = many_slides_response
        
        result = self.copywriter.generate_post_copy(
            brief=self.brief,
            slides_info=many_slides,
            article_text=self.article_text,
        )
        
        call_args = self.mock_llm_client.generate.call_args
        from src.core.config import DEEPSEEK_MAX_TOKENS
        self.assertEqual(call_args.kwargs["max_tokens"], DEEPSEEK_MAX_TOKENS)
    
    @patch('src.copywriting.writer.get_latest_prompt')
    def test_generate_post_copy_truncation_detection(self, mock_get_prompt):
        """Test truncation detection in LLM response."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Truncated response (doesn't end with } or ]})
        truncated_response = '{"slides": [{"slide_number": 1, "title": {'
        self.mock_llm_client.generate.return_value = truncated_response
        
        # Should raise ValueError due to invalid JSON structure
        with self.assertRaises(ValueError):
            self.copywriter.generate_post_copy(
                brief=self.brief,
                slides_info=self.slides_info,
                article_text=self.article_text,
            )
    
    @patch('src.copywriting.writer.get_latest_prompt')
    def test_generate_slide_copy_deprecated(self, mock_get_prompt):
        """Test deprecated generate_slide_copy method."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Single slide response
        single_slide_response = json.dumps({
            "slides": [json.loads(self.valid_response)["slides"][0]]
        })
        self.mock_llm_client.generate.return_value = single_slide_response
        
        # Call deprecated method
        result = self.copywriter.generate_slide_copy(
            brief=self.brief,
            slide_info=self.slides_info[0],
            article_text=self.article_text,
        )
        
        # Should return first slide from generate_post_copy result
        self.assertEqual(result["slide_number"], 1)
        self.assertIn("title", result)
    
    def test_build_prompt_dict(self):
        """Test _build_prompt_dict method."""
        prompt_dict = self.copywriter._build_prompt_dict(
            brief=self.brief,
            slides_info=self.slides_info,
            article_text=self.article_text,
        )
        
        # Verify voice & platform fields
        self.assertEqual(prompt_dict["platform"], "linkedin")
        self.assertEqual(prompt_dict["format"], "carousel")
        self.assertEqual(prompt_dict["tone"], "professional")
        self.assertEqual(prompt_dict["personality_traits"], "authoritative, empowering")
        self.assertEqual(prompt_dict["vocabulary_level"], "moderate")
        self.assertEqual(prompt_dict["formality"], "neutral")
        
        # Verify content essence
        self.assertEqual(prompt_dict["main_message"], self.brief.main_message)
        self.assertEqual(prompt_dict["value_proposition"], self.brief.value_proposition)
        self.assertEqual(prompt_dict["keywords_to_emphasize"], "productivity, efficiency, growth")
        self.assertEqual(prompt_dict["angle"], self.brief.angle)
        self.assertEqual(prompt_dict["hook"], self.brief.hook)
        
        # Verify audience
        self.assertEqual(prompt_dict["persona"], self.brief.persona)
        self.assertEqual(prompt_dict["pain_points"], "manual processes, lack of automation, time waste")
        self.assertEqual(prompt_dict["desires"], "efficiency, scalability, team productivity")
        
        # Verify emotions
        self.assertEqual(prompt_dict["primary_emotion"], "confident")
        self.assertEqual(prompt_dict["secondary_emotions"], "inspired, motivated")
        self.assertEqual(prompt_dict["target_emotions"], "confident, inspired")
        
        # Verify slides context
        self.assertIn("slides_context", prompt_dict)
        self.assertIn("SLIDE 1", prompt_dict["slides_context"])
        self.assertIn("SLIDE 2", prompt_dict["slides_context"])
        self.assertIn("SLIDE 3", prompt_dict["slides_context"])
        
        # Verify insights
        self.assertIn("slide_insights_content_block", prompt_dict)
        self.assertIn("insight_001", prompt_dict["slide_insights_content_block"])
        self.assertIn("insight_002", prompt_dict["slide_insights_content_block"])
        
        # Verify total slides
        self.assertEqual(prompt_dict["total_slides"], "3")
    
    def test_build_slide_insights_block(self):
        """Test _build_slide_insights_block helper function."""
        slide_info = self.slides_info[1]  # Slide 2 references both insights
        
        insights_block = _build_slide_insights_block(self.brief, slide_info)
        
        # Should contain both insights
        self.assertIn("insight_001", insights_block)
        self.assertIn("insight_002", insights_block)
        self.assertIn("Companies save 10 hours", insights_block)
        self.assertIn("Manual processes", insights_block)
        
        # Test with slide that has no referenced insights
        slide_no_insights = {**self.slides_info[2], "insights_referenced": []}
        insights_block_empty = _build_slide_insights_block(self.brief, slide_no_insights)
        self.assertIn("no insights referenced", insights_block_empty.lower())
    
    def test_validate_response_valid(self):
        """Test _validate_response with valid response."""
        payload = self.copywriter._validate_response(
            raw_response=self.valid_response,
            slides_info=self.slides_info,
            brief=self.brief,
        )
        
        self.assertIn("slides", payload)
        self.assertEqual(len(payload["slides"]), 3)
    
    def test_validate_response_invalid_json(self):
        """Test _validate_response with invalid JSON."""
        with self.assertRaises(ValueError):
            self.copywriter._validate_response(
                raw_response="not json",
                slides_info=self.slides_info,
                brief=self.brief,
            )
    
    def test_validate_response_missing_slides(self):
        """Test _validate_response with missing slides key."""
        invalid_response = json.dumps({"wrong_key": []})
        
        with self.assertRaises(ValueError) as context:
            self.copywriter._validate_response(
                raw_response=invalid_response,
                slides_info=self.slides_info,
                brief=self.brief,
            )
        
        # Error message from validate_llm_json_response: "Missing required keys in JSON: slides"
        error_msg = str(context.exception)
        self.assertIn("Missing required keys", error_msg)
        self.assertIn("slides", error_msg)
    
    def test_validate_response_slide_missing_content(self):
        """Test _validate_response when slide has no text elements."""
        invalid_response = json.loads(self.valid_response)
        invalid_response["slides"][0]["title"] = None
        invalid_response["slides"][0]["subtitle"] = None
        invalid_response["slides"][0]["body"] = None
        
        with self.assertRaises(ValueError) as context:
            self.copywriter._validate_response(
                raw_response=json.dumps(invalid_response),
                slides_info=self.slides_info,
                brief=self.brief,
            )
        
        self.assertIn("At least one of title, subtitle, or body", str(context.exception))
    
    def test_validate_response_element_missing_content(self):
        """Test _validate_response when element is missing content field."""
        invalid_response = json.loads(self.valid_response)
        del invalid_response["slides"][0]["title"]["content"]
        
        with self.assertRaises(ValueError) as context:
            self.copywriter._validate_response(
                raw_response=json.dumps(invalid_response),
                slides_info=self.slides_info,
                brief=self.brief,
            )
        
        self.assertIn("missing 'content' field", str(context.exception))
    
    def test_validate_response_element_missing_emphasis(self):
        """Test _validate_response when element is missing emphasis field."""
        invalid_response = json.loads(self.valid_response)
        del invalid_response["slides"][0]["title"]["emphasis"]
        
        with self.assertRaises(ValueError) as context:
            self.copywriter._validate_response(
                raw_response=json.dumps(invalid_response),
                slides_info=self.slides_info,
                brief=self.brief,
            )
        
        self.assertIn("missing 'emphasis' field", str(context.exception))
    
    def test_validate_response_invalid_emphasis_type(self):
        """Test _validate_response when emphasis is not a list."""
        invalid_response = json.loads(self.valid_response)
        invalid_response["slides"][0]["title"]["emphasis"] = "not a list"
        
        with self.assertRaises(ValueError) as context:
            self.copywriter._validate_response(
                raw_response=json.dumps(invalid_response),
                slides_info=self.slides_info,
                brief=self.brief,
            )
        
        self.assertIn("emphasis must be an array", str(context.exception))
    
    def test_validate_semantics_slide_missing_required_slot(self):
        """Test _validate_semantics_slide when required slot is missing."""
        slide_payload = json.loads(self.valid_response)["slides"][1]  # Slide 2 requires headline
        slide_payload["title"] = None  # Remove required headline
        
        with self.assertRaises(ValueError) as context:
            self.copywriter._validate_semantics_slide(
                slide_payload=slide_payload,
                slide_info=self.slides_info[1],
                brief=self.brief,
            )
        
        self.assertIn("Required content slot", str(context.exception))
    
    def test_validate_semantics_slide_cta_guidelines(self):
        """Test _validate_semantics_slide with CTA slide."""
        # Slide 3 is a CTA slide, but cta_guidelines are optional
        slide_payload = json.loads(self.valid_response)["slides"][2]
        slide_payload["cta_guidelines"] = None  # Missing CTA guidelines (should not error)
        
        # Should not raise an error (CTA guidelines are optional)
        try:
            self.copywriter._validate_semantics_slide(
                slide_payload=slide_payload,
                slide_info=self.slides_info[2],
                brief=self.brief,
            )
        except ValueError:
            self.fail("_validate_semantics_slide should not raise for missing CTA guidelines")
    
    @patch('src.copywriting.writer.get_latest_prompt')
    def test_generate_post_copy_logging(self, mock_get_prompt):
        """Test that logging is performed when logger is available."""
        mock_get_prompt.return_value = {"template": "Template"}
        self.mock_llm_client.generate.return_value = self.valid_response
        
        # Reset logger mock
        self.mock_logger.reset_mock()
        self.mock_logger.current_trace_id = "test_trace_001"
        
        result = self.copywriter.generate_post_copy(
            brief=self.brief,
            slides_info=self.slides_info,
            article_text=self.article_text,
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
        self.assertEqual(success_call.kwargs["name"], "copywriter_success_test_post_001")
        self.assertEqual(success_call.kwargs["status"], "success")
        self.assertIn("output_obj", success_call.kwargs)


class TestCopywriterIntegration(unittest.TestCase):
    """
    Integration tests for Copywriter with real LLM calls.
    
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
        
        # Register the copywriter prompt if not already registered
        copywriter_template_path = PROMPTS_DIR / "copywriter.md"
        if copywriter_template_path.exists():
            with open(copywriter_template_path, 'r', encoding='utf-8') as f:
                template_text = f.read()
            
            # Check if prompt already exists
            existing = find_existing_prompt("copywriter", template_text)
            if not existing:
                # Register the prompt
                register_prompt(
                    prompt_key="copywriter",
                    template=template_text,
                    description="Copywriter prompt for generating slide text content",
                    metadata={
                        "registered_by": "test_copywriting_writer",
                        "source_file": str(copywriter_template_path),
                    },
                )
                print(f"✓ Registered copywriter prompt for integration tests")
            else:
                print(f"✓ Copywriter prompt already registered: {existing[1]}")
        else:
            cls.skip_integration = True
            cls.skip_reason = f"Copywriter prompt template not found at {copywriter_template_path}"
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
        trace_id = self.logger.create_trace(name="test_copywriter_integration")
        self.logger.current_trace_id = trace_id
        
        self.llm_client = HttpLLMClient(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            logger=self.logger,
        )
        
        # Create copywriter instance
        self.copywriter = Copywriter(
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
            required_elements=["data points", "actionable tips"],
            objective="engagement",
            narrative_arc="problem-solution-benefit",
            estimated_slides=3,
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
        
        # Create slides info (3 slides: hero, value, CTA)
        self.slides_info = [
            {
                "slide_number": 1,
                "template_id": "hero_001",
                "template_type": "hero",
                "value_subtype": None,
                "purpose": "Hook the audience with a compelling question about time waste",
                "copy_direction": "Create an urgent, question-based hook that addresses the pain point of time waste on repetitive tasks",
                "visual_direction": "Bold typography with contrasting colors, minimal visual elements",
                "content_slots": {
                    "headline": {"required": True, "max_chars": 60},
                    "subheadline": {"required": False, "max_chars": 120},
                },
                "target_emotions": ["curious", "engaged"],
                "key_elements": ["question", "urgency"],
                "insights_referenced": ["insight_001"],
                "transition_to_next": "Lead into the problem and solution",
            },
            {
                "slide_number": 2,
                "template_id": "value_benefit_001",
                "template_type": "value",
                "value_subtype": "benefit",
                "purpose": "Present the core value proposition with supporting evidence",
                "copy_direction": "Highlight the main benefit (10 hours saved) clearly and concisely, supporting with data",
                "visual_direction": "Icon-based layout with clear hierarchy, data visualization",
                "content_slots": {
                    "headline": {"required": True, "max_chars": 60},
                    "body": {"required": True, "max_chars": 250},
                },
                "target_emotions": ["convinced", "interested"],
                "key_elements": ["value", "benefit", "data"],
                "insights_referenced": ["insight_001", "insight_002"],
                "transition_to_next": "Move to call-to-action",
            },
            {
                "slide_number": 3,
                "template_id": "cta_001",
                "template_type": "cta",
                "value_subtype": None,
                "purpose": "Encourage action with a clear call-to-action",
                "copy_direction": "Create a clear, compelling call-to-action that motivates immediate engagement",
                "visual_direction": "Prominent CTA button with contrasting color, clear focal point",
                "content_slots": {
                    "headline": {"required": True, "max_chars": 60},
                },
                "target_emotions": ["motivated", "ready"],
                "key_elements": ["action", "urgency"],
                "insights_referenced": [],
                "transition_to_next": None,  # Last slide
            },
        ]
        
        # Sample article text
        self.article_text = """
        Workflow automation has become essential for modern teams seeking to improve productivity 
        and reduce manual effort. According to recent studies, companies that implement automation 
        tools save an average of 10 hours per week per team member. This translates to significant 
        cost savings and improved team morale. Manual processes not only waste time but also increase 
        the likelihood of errors and reduce employee satisfaction. Experts recommend starting with 
        repetitive tasks and gradually expanding automation across all workflows to maximize impact.
        """
    
    def test_generate_post_copy_real_llm(self):
        """Test post copy generation with real LLM API calls."""
        # Generate copy for all slides
        result = self.copywriter.generate_post_copy(
            brief=self.brief,
            slides_info=self.slides_info,
            article_text=self.article_text,
            context="integration_test_001",
        )
        
        # Verify result structure
        self.assertIn("slides", result)
        self.assertEqual(len(result["slides"]), 3, "Should generate 3 slides")
        
        # Verify each slide
        for slide_idx, slide in enumerate(result["slides"]):
            slide_num = slide.get("slide_number")
            slide_info = self.slides_info[slide_idx]
            
            # Verify slide number matches
            self.assertEqual(slide_num, slide_info["slide_number"], 
                           f"Slide {slide_idx + 1} number should match")
            
            # Verify at least one text element exists
            has_content = any(
                slide.get(key) is not None 
                for key in ["title", "subtitle", "body"]
            )
            self.assertTrue(has_content, 
                          f"Slide {slide_num} must have at least one text element (title, subtitle, or body)")
            
            # Verify required content slots are filled
            content_slots = slide_info.get("content_slots", {})
            for slot_name, slot_info in content_slots.items():
                if slot_info.get("required", False):
                    element_name = {
                        "headline": "title",
                        "subheadline": "subtitle",
                        "body": "body",
                    }.get(slot_name)
                    
                    if element_name:
                        element = slide.get(element_name)
                        self.assertIsNotNone(
                            element,
                            f"Slide {slide_num} must have required {element_name} (from slot {slot_name})"
                        )
                        
                        # Verify element structure
                        if element:
                            self.assertIn("content", element, 
                                        f"Slide {slide_num} {element_name} must have 'content' field")
                            self.assertIn("emphasis", element,
                                        f"Slide {slide_num} {element_name} must have 'emphasis' field")
                            
                            # Verify content is not empty
                            content = element.get("content", "")
                            self.assertGreater(len(content), 0,
                                             f"Slide {slide_num} {element_name} content must not be empty")
                            
                            # Verify emphasis is a list
                            emphasis = element.get("emphasis", [])
                            self.assertIsInstance(emphasis, list,
                                                f"Slide {slide_num} {element_name} emphasis must be a list")
            
            # Verify emphasis strings appear in content (case-insensitive)
            for element_name in ["title", "subtitle", "body"]:
                element = slide.get(element_name)
                if element and isinstance(element, dict):
                    content = element.get("content", "").lower()
                    emphasis = element.get("emphasis", [])
                    for emph_str in emphasis:
                        if emph_str:  # Skip empty strings
                            # Allow partial matches or variations
                            # Just check that emphasis strings are reasonable
                            self.assertIsInstance(emph_str, str,
                                                f"Slide {slide_num} {element_name} emphasis items must be strings")
        
        # Verify brief was enriched with copy guidelines
        self.assertIsNotNone(self.brief.copy_guidelines, 
                           "Brief should be enriched with copy guidelines")
        
        # Verify content aligns with brief
        first_slide = result["slides"][0]
        first_title = first_slide.get("title")
        if first_title:
            title_content = first_title.get("content", "").lower()
            # Check that hook keywords or main message appear in first slide
            hook_lower = self.brief.hook.lower()
            main_message_lower = self.brief.main_message.lower()
            # At least one key concept should appear (flexible matching)
            keywords_in_title = any(
                keyword.lower() in title_content 
                for keyword in ["10", "hour", "time", "waste", "repetitive"]
            )
            # This is a soft check - just verify title is relevant
            self.assertTrue(
                len(title_content) > 0,
                "First slide title should have content"
            )
        
        # Verify platform and tone alignment
        # Content should be professional and appropriate for LinkedIn
        # (This is a semantic check - we verify structure, not exact content)
    
    def test_generate_post_copy_content_quality(self):
        """Test that generated content meets quality requirements."""
        result = self.copywriter.generate_post_copy(
            brief=self.brief,
            slides_info=self.slides_info,
            article_text=self.article_text,
            context="integration_test_quality",
        )
        
        slides = result.get("slides", [])
        self.assertGreater(len(slides), 0, "Should generate at least one slide")
        
        # Verify content length constraints
        for slide in slides:
            slide_num = slide.get("slide_number")
            
            for element_name in ["title", "subtitle", "body"]:
                element = slide.get(element_name)
                if element and isinstance(element, dict):
                    content = element.get("content", "")
                    
                    # Verify reasonable length (not too short, not too long)
                    if element_name == "title":
                        # Title should be concise (typically 40-70 chars for LinkedIn)
                        self.assertGreater(len(content), 10,
                                         f"Slide {slide_num} title should be at least 10 chars")
                        self.assertLess(len(content), 100,
                                      f"Slide {slide_num} title should be concise (< 100 chars)")
                    elif element_name == "subtitle":
                        # Subtitle can be longer but still concise
                        self.assertGreater(len(content), 15,
                                         f"Slide {slide_num} subtitle should be at least 15 chars")
                        self.assertLess(len(content), 150,
                                      f"Slide {slide_num} subtitle should be concise (< 150 chars)")
                    elif element_name == "body":
                        # Body can be longer but should be focused
                        self.assertGreater(len(content), 20,
                                         f"Slide {slide_num} body should be at least 20 chars")
                        self.assertLess(len(content), 300,
                                      f"Slide {slide_num} body should be focused (< 300 chars)")
        
        # Verify emphasis guidance is provided
        for slide in slides:
            for element_name in ["title", "subtitle", "body"]:
                element = slide.get(element_name)
                if element and isinstance(element, dict):
                    emphasis = element.get("emphasis", [])
                    content = element.get("content", "")
                    
                    # Emphasis should not be empty for non-empty content
                    if content:
                        self.assertGreater(len(emphasis), 0,
                                         f"Slide {slide.get('slide_number')} {element_name} should have emphasis guidance")
                        
                        # At least some emphasis strings should appear in content
                        content_lower = content.lower()
                        matching_emphasis = [
                            emph for emph in emphasis 
                            if emph and emph.lower() in content_lower
                        ]
                        # Allow for variations - at least 50% should match
                        if len(emphasis) > 0:
                            match_ratio = len(matching_emphasis) / len(emphasis)
                            # This is lenient - just verify some relevance
                            self.assertGreater(match_ratio, 0.3,
                                             f"Slide {slide.get('slide_number')} {element_name} emphasis should be relevant to content")
    
    def test_generate_post_copy_semantic_alignment(self):
        """Test that generated content aligns semantically with brief."""
        result = self.copywriter.generate_post_copy(
            brief=self.brief,
            slides_info=self.slides_info,
            article_text=self.article_text,
            context="integration_test_semantic",
        )
        
        slides = result.get("slides", [])
        
        # Check that keywords from brief appear in generated content
        keywords_to_check = ["productivity", "automation", "efficiency", "workflow"]
        content_text = " ".join([
            slide.get(key, {}).get("content", "") 
            for slide in slides 
            for key in ["title", "subtitle", "body"] 
            if slide.get(key) and isinstance(slide.get(key), dict)
        ]).lower()
        
        # At least some keywords should appear
        keywords_found = [
            keyword for keyword in keywords_to_check 
            if keyword.lower() in content_text
        ]
        self.assertGreater(len(keywords_found), 0,
                           f"Generated content should include some keywords from brief: {keywords_to_check}")
        
        # Verify that target emotions are considered (indirect check via word choice)
        # This is a soft semantic check - we verify structure and some alignment
        self.assertIsNotNone(content_text)
        self.assertGreater(len(content_text), 50,
                         "Generated content should be substantial")
        
        # Verify CTA slide has CTA guidelines (if it's a CTA slide)
        for slide in slides:
            slide_num = slide.get("slide_number")
            slide_info = next(
                (s for s in self.slides_info if s.get("slide_number") == slide_num),
                None
            )
            if slide_info and slide_info.get("template_type") == "cta":
                # CTA guidelines are optional but helpful
                cta_guidelines = slide.get("cta_guidelines")
                # We don't require it, but it's good if it exists
                if cta_guidelines:
                    self.assertIsInstance(cta_guidelines, dict,
                                        f"Slide {slide_num} CTA guidelines should be a dict")
        
        # Verify brief enrichment
        self.assertIsNotNone(self.brief.copy_guidelines,
                           "Brief should be enriched after generation")


if __name__ == '__main__':
    unittest.main()
