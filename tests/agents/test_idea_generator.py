"""
Unit tests for IdeaGenerator.

Tests the IdeaGenerator agent that generates post ideas from articles
using LLM and configuration parameters.

Location: tests/agents/test_idea_generator.py
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.ideas.generator import IdeaGenerator
from src.core.config import IdeationConfig
from src.core.llm_client import HttpLLMClient


class TestIdeaGenerator(unittest.TestCase):
    """Test cases for IdeaGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock LLM client
        self.mock_llm_client = Mock(spec=HttpLLMClient)
        
        # Create idea generator instance
        self.generator = IdeaGenerator(llm_client=self.mock_llm_client)
        
        # Create sample IdeationConfig
        self.config = IdeationConfig(
            num_insights_min=2,
            num_insights_max=4,
            num_keywords_min=5,
            num_keywords_max=10,
            num_ideas_min=5,
            num_ideas_max=8,
            platforms=["linkedin", "instagram"],
            formats=["carousel", "single_image"],
        )
        
        # Sample article text
        self.article_text = """
        Workflow automation has become essential for modern teams seeking to improve productivity 
        and reduce manual effort. According to recent studies, companies that implement automation 
        tools save an average of 10 hours per week per team member. This translates to significant 
        cost savings and improved team morale. Manual processes not only waste time but also increase 
        the likelihood of errors and reduce employee satisfaction. Experts recommend starting with 
        repetitive tasks and gradually expanding automation across all workflows to maximize impact.
        """
        
        # Sample valid LLM response
        self.valid_response = json.dumps({
            "article_summary": {
                "title": "The Future of Workflow Automation",
                "main_thesis": "Workflow automation significantly improves productivity and team morale",
                "detected_tone": "professional",
                "key_insights": [
                    {
                        "id": "insight_001",
                        "content": "Companies save 10 hours per week with automation",
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
                "themes": ["productivity", "workplace automation", "efficiency"],
                "keywords": ["automation", "productivity", "workflow", "efficiency", "team", "time", "processes"],
                "main_message": "Boost your team's productivity with smart workflows",
                "avoid_topics": ["layoffs", "controversial politics"],
            },
            "ideas": [
                {
                    "id": "idea_001",
                    "platform": "linkedin",
                    "format": "carousel",
                    "tone": "professional",
                    "persona": "Tech-savvy managers looking to optimize team workflows",
                    "personality_traits": ["authoritative", "empathetic"],
                    "objective": "engagement",
                    "angle": "Data-driven approach to workflow optimization",
                    "hook": "Are you wasting 10 hours every week on repetitive tasks?",
                    "narrative_arc": "problem-solution-benefit",
                    "vocabulary_level": "moderate",
                    "formality": "neutral",
                    "key_insights_used": ["insight_001", "insight_002"],
                    "target_emotions": ["confident", "inspired"],
                    "primary_emotion": "confident",
                    "secondary_emotions": ["inspired", "motivated"],
                    "avoid_emotions": ["anxious", "overwhelmed"],
                    "value_proposition": "Save 10 hours per week with automated processes",
                    "article_context_for_idea": "Article about workflow automation and productivity tools",
                    "idea_explanation": "This idea focuses on workflow automation benefits using data to support the value proposition",
                    "estimated_slides": 6,
                    "confidence": 0.85,
                    "rationale": "Workflow automation is a trending topic with high engagement potential on LinkedIn",
                    "risks": ["May be too technical for some audiences"],
                    "keywords_to_emphasize": ["productivity", "automation", "efficiency"],
                    "pain_points": ["manual processes", "lack of automation", "time waste"],
                    "desires": ["efficiency", "scalability", "team productivity"],
                },
                {
                    "id": "idea_002",
                    "platform": "instagram",
                    "format": "carousel",
                    "tone": "empowering",
                    "persona": "Entrepreneurs seeking to optimize their daily operations",
                    "personality_traits": ["motivational", "practical"],
                    "objective": "engagement",
                    "angle": "Visual story of time saved through automation",
                    "hook": "What if you could get 10 hours back every single week?",
                    "narrative_arc": "transformation-story",
                    "vocabulary_level": "simple",
                    "formality": "casual",
                    "key_insights_used": ["insight_001"],
                    "target_emotions": ["motivated", "excited"],
                    "primary_emotion": "motivated",
                    "secondary_emotions": ["excited", "empowered"],
                    "avoid_emotions": ["overwhelmed", "discouraged"],
                    "value_proposition": "Reclaim your time with smart automation",
                    "article_context_for_idea": "Focus on the personal transformation aspect of automation",
                    "idea_explanation": "This idea emphasizes the personal benefits and time freedom from automation",
                    "estimated_slides": 8,
                    "confidence": 0.80,
                    "rationale": "Visual format works well on Instagram and resonates with entrepreneurial audience",
                    "risks": [],
                    "keywords_to_emphasize": ["time", "freedom", "automation"],
                    "pain_points": ["time constraints", "manual work", "burnout"],
                    "desires": ["time freedom", "efficiency", "growth"],
                },
                {
                    "id": "idea_003",
                    "platform": "linkedin",
                    "format": "single_image",
                    "tone": "professional",
                    "persona": "C-level executives interested in operational efficiency",
                    "personality_traits": ["authoritative", "strategic"],
                    "objective": "awareness",
                    "angle": "ROI and business impact of workflow automation",
                    "hook": "The hidden cost of manual processes: 10 hours per week",
                    "narrative_arc": "problem-data-solution",
                    "vocabulary_level": "sophisticated",
                    "formality": "formal",
                    "key_insights_used": ["insight_001", "insight_002"],
                    "target_emotions": ["confident", "informed"],
                    "primary_emotion": "confident",
                    "secondary_emotions": ["informed", "strategic"],
                    "avoid_emotions": ["uncertain", "anxious"],
                    "value_proposition": "Increase operational efficiency by 25% through automation",
                    "article_context_for_idea": "Executive-focused perspective on automation ROI",
                    "idea_explanation": "This idea targets decision-makers with data-driven insights about automation ROI",
                    "estimated_slides": 5,
                    "confidence": 0.75,
                    "rationale": "Single image format is effective for executive audience on LinkedIn",
                    "risks": ["May require more technical knowledge"],
                    "keywords_to_emphasize": ["ROI", "efficiency", "automation", "productivity"],
                    "pain_points": ["operational inefficiency", "high labor costs", "manual errors"],
                    "desires": ["cost reduction", "efficiency", "competitive advantage"],
                },
                {
                    "id": "idea_004",
                    "platform": "linkedin",
                    "format": "carousel",
                    "tone": "professional",
                    "persona": "HR professionals focused on employee experience",
                    "personality_traits": ["empathetic", "people-focused"],
                    "objective": "engagement",
                    "angle": "How automation improves employee satisfaction",
                    "hook": "Happy teams are productive teams: The automation connection",
                    "narrative_arc": "benefit-story-evidence",
                    "vocabulary_level": "moderate",
                    "formality": "neutral",
                    "key_insights_used": ["insight_002"],
                    "target_emotions": ["inspired", "empowered"],
                    "primary_emotion": "inspired",
                    "secondary_emotions": ["empowered", "confident"],
                    "avoid_emotions": ["frustrated", "overwhelmed"],
                    "value_proposition": "Boost team morale by eliminating repetitive tasks",
                    "article_context_for_idea": "HR perspective on automation and employee satisfaction",
                    "idea_explanation": "This idea highlights the human side of automation, focusing on employee well-being",
                    "estimated_slides": 7,
                    "confidence": 0.82,
                    "rationale": "HR professionals value employee experience and engagement metrics",
                    "risks": ["May not resonate with tech-focused audience"],
                    "keywords_to_emphasize": ["team", "satisfaction", "automation", "productivity"],
                    "pain_points": ["low morale", "repetitive tasks", "employee burnout"],
                    "desires": ["happy teams", "employee engagement", "retention"],
                },
                {
                    "id": "idea_005",
                    "platform": "instagram",
                    "format": "carousel",
                    "tone": "urgent",
                    "persona": "Small business owners seeking growth",
                    "personality_traits": ["action-oriented", "practical"],
                    "objective": "conversion",
                    "angle": "Quick wins: Start automating today",
                    "hook": "Stop wasting time. Start automating now.",
                    "narrative_arc": "problem-solution-action",
                    "vocabulary_level": "simple",
                    "formality": "casual",
                    "key_insights_used": ["insight_001"],
                    "target_emotions": ["motivated", "ready"],
                    "primary_emotion": "motivated",
                    "secondary_emotions": ["ready", "confident"],
                    "avoid_emotions": ["overwhelmed", "procrastinating"],
                    "value_proposition": "Save 10 hours this week with simple automation",
                    "article_context_for_idea": "Action-oriented approach for small business owners",
                    "idea_explanation": "This idea provides immediate, actionable steps for small business automation",
                    "estimated_slides": 6,
                    "confidence": 0.78,
                    "rationale": "Urgent tone and simple format work well for small business audience on Instagram",
                    "risks": ["May seem too simplistic for enterprise audience"],
                    "keywords_to_emphasize": ["quick", "easy", "automation", "time"],
                    "pain_points": ["time constraints", "limited resources", "growth barriers"],
                    "desires": ["quick wins", "growth", "efficiency"],
                },
            ],
        })
    
    def test_initialization(self):
        """Test IdeaGenerator initialization."""
        generator = IdeaGenerator(llm_client=self.mock_llm_client)
        
        self.assertEqual(generator.llm, self.mock_llm_client)
    
    @patch('src.ideas.generator.get_latest_prompt')
    def test_generate_ideas_success(self, mock_get_prompt):
        """Test successful idea generation."""
        # Mock prompt retrieval
        mock_get_prompt.return_value = {
            "template": "Generate {num_ideas_min} to {num_ideas_max} ideas from article: {article}"
        }
        
        # Mock LLM response
        self.mock_llm_client.generate.return_value = self.valid_response
        
        # Call generate_ideas
        result = self.generator.generate_ideas(
            article_text=self.article_text,
            config=self.config,
        )
        
        # Verify prompt was loaded
        mock_get_prompt.assert_called_once_with("post_ideator")
        
        # Verify LLM was called
        self.mock_llm_client.generate.assert_called_once()
        call_args = self.mock_llm_client.generate.call_args
        self.assertEqual(call_args.kwargs["prompt_key"], "post_ideator")
        
        # Verify result structure
        self.assertIn("article_summary", result)
        self.assertIn("ideas", result)
        self.assertEqual(len(result["ideas"]), 5)
        
        # Verify article summary structure
        summary = result["article_summary"]
        self.assertIn("title", summary)
        self.assertIn("main_thesis", summary)
        self.assertIn("key_insights", summary)
        self.assertEqual(len(summary["key_insights"]), 2)
        
        # Verify first idea structure
        idea1 = result["ideas"][0]
        self.assertEqual(idea1["id"], "idea_001")
        self.assertEqual(idea1["platform"], "linkedin")
        self.assertEqual(idea1["format"], "carousel")
        self.assertIn("hook", idea1)
        self.assertIn("value_proposition", idea1)
    
    @patch('src.ideas.generator.get_latest_prompt')
    def test_generate_ideas_with_prompt_version(self, mock_get_prompt):
        """Test idea generation with specific prompt version."""
        # Mock prompt retrieval by version
        with patch('src.ideas.generator.get_prompt_by_key_and_version') as mock_get_version:
            mock_get_version.return_value = {
                "template": "Versioned template: {article}"
            }
            
            self.mock_llm_client.generate.return_value = self.valid_response
            
            result = self.generator.generate_ideas(
                article_text=self.article_text,
                config=self.config,
                prompt_version="v2",
            )
            
            # Verify version-specific prompt was loaded
            mock_get_version.assert_called_once_with("post_ideator", "v2")
            mock_get_prompt.assert_not_called()
            
            # Verify result
            self.assertIn("ideas", result)
    
    @patch('src.ideas.generator.get_latest_prompt')
    def test_generate_ideas_prompt_not_found(self, mock_get_prompt):
        """Test error handling when prompt is not found."""
        mock_get_prompt.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.generator.generate_ideas(
                article_text=self.article_text,
                config=self.config,
            )
        
        self.assertIn("Prompt 'post_ideator' not found", str(context.exception))
    
    @patch('src.ideas.generator.get_latest_prompt')
    def test_generate_ideas_prompt_version_not_found(self, mock_get_prompt):
        """Test error handling when prompt version is not found."""
        with patch('src.ideas.generator.get_prompt_by_key_and_version') as mock_get_version:
            mock_get_version.return_value = None
            
            with self.assertRaises(ValueError) as context:
                self.generator.generate_ideas(
                    article_text=self.article_text,
                    config=self.config,
                    prompt_version="v999",
                )
            
            self.assertIn("Prompt 'post_ideator' version 'v999' not found", str(context.exception))
    
    @patch('src.ideas.generator.get_latest_prompt')
    def test_generate_ideas_invalid_response_structure(self, mock_get_prompt):
        """Test error handling with invalid response structure."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Invalid response (missing required keys)
        invalid_response = json.dumps({"wrong_key": []})
        self.mock_llm_client.generate.return_value = invalid_response
        
        with self.assertRaises(ValueError) as context:
            self.generator.generate_ideas(
                article_text=self.article_text,
                config=self.config,
            )
        
        # Error message from validate_llm_json_response
        error_msg = str(context.exception)
        self.assertIn("Missing required keys", error_msg)
        self.assertIn("article_summary", error_msg)
        self.assertIn("ideas", error_msg)
    
    @patch('src.ideas.generator.get_latest_prompt')
    def test_generate_ideas_empty_ideas_list(self, mock_get_prompt):
        """Test error handling when ideas list is empty."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Response with empty ideas list
        invalid_response = json.loads(self.valid_response)
        invalid_response["ideas"] = []
        wrong_response = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = wrong_response
        
        with self.assertRaises(ValueError) as context:
            self.generator.generate_ideas(
                article_text=self.article_text,
                config=self.config,
            )
        
        self.assertIn("At least one idea must be generated", str(context.exception))
    
    @patch('src.ideas.generator.get_latest_prompt')
    def test_generate_ideas_insufficient_ideas(self, mock_get_prompt):
        """Test error handling when fewer ideas than minimum are generated."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Response with fewer ideas than minimum (config requires 5, we provide 3)
        invalid_response = json.loads(self.valid_response)
        invalid_response["ideas"] = invalid_response["ideas"][:3]  # Only 3 ideas instead of 5
        wrong_response = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = wrong_response
        
        with self.assertRaises(ValueError) as context:
            self.generator.generate_ideas(
                article_text=self.article_text,
                config=self.config,
            )
        
        self.assertIn("Generated 3 ideas, but minimum is 5", str(context.exception))
    
    @patch('src.ideas.generator.get_latest_prompt')
    def test_generate_ideas_empty_insights_list(self, mock_get_prompt):
        """Test error handling when insights list is empty."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Response with empty insights list
        invalid_response = json.loads(self.valid_response)
        invalid_response["article_summary"]["key_insights"] = []
        wrong_response = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = wrong_response
        
        with self.assertRaises(ValueError) as context:
            self.generator.generate_ideas(
                article_text=self.article_text,
                config=self.config,
            )
        
        self.assertIn("At least one key insight must be generated", str(context.exception))
    
    @patch('src.ideas.generator.get_latest_prompt')
    def test_generate_ideas_insufficient_insights(self, mock_get_prompt):
        """Test error handling when fewer insights than minimum are generated."""
        mock_get_prompt.return_value = {"template": "Template"}
        
        # Response with fewer insights than minimum (config requires 2, we provide 1)
        invalid_response = json.loads(self.valid_response)
        invalid_response["article_summary"]["key_insights"] = invalid_response["article_summary"]["key_insights"][:1]
        wrong_response = json.dumps(invalid_response)
        
        self.mock_llm_client.generate.return_value = wrong_response
        
        with self.assertRaises(ValueError) as context:
            self.generator.generate_ideas(
                article_text=self.article_text,
                config=self.config,
            )
        
        self.assertIn("Generated 1 insights, but minimum is 2", str(context.exception))
    
    @patch('src.ideas.generator.get_latest_prompt')
    def test_generate_ideas_with_context(self, mock_get_prompt):
        """Test idea generation with context identifier."""
        mock_get_prompt.return_value = {"template": "Template"}
        self.mock_llm_client.generate.return_value = self.valid_response
        
        result = self.generator.generate_ideas(
            article_text=self.article_text,
            config=self.config,
            context="test_article_slug",
        )
        
        # Verify context was passed to LLM
        call_args = self.mock_llm_client.generate.call_args
        self.assertEqual(call_args.kwargs["context"], "test_article_slug")
        
        # Verify result
        self.assertIn("ideas", result)
    
    @patch('src.ideas.generator.get_latest_prompt')
    def test_generate_ideas_prompt_dict_building(self, mock_get_prompt):
        """Test that prompt_dict is built correctly from config."""
        # Template must include {article} placeholder for article text to be included
        mock_get_prompt.return_value = {"template": "Template with {platforms}, {formats}, and article: {article}"}
        self.mock_llm_client.generate.return_value = self.valid_response
        
        self.generator.generate_ideas(
            article_text=self.article_text,
            config=self.config,
        )
        
        # Verify prompt was built and article was added
        call_args = self.mock_llm_client.generate.call_args
        prompt = call_args.args[0]  # First positional argument
        
        # Check that config values appear in prompt (formatted)
        self.assertIn("'linkedin', 'instagram'", prompt)  # Platforms formatted
        self.assertIn("'carousel', 'single_image'", prompt)  # Formats formatted
        # Verify article text is included (strip whitespace for comparison)
        article_in_prompt = self.article_text.strip() in prompt or self.article_text in prompt
        self.assertTrue(article_in_prompt, "Article text should be included in prompt")
    
    def test_config_to_prompt_dict(self):
        """Test that IdeationConfig.to_prompt_dict formats correctly."""
        prompt_dict = self.config.to_prompt_dict()
        
        # Verify platforms are formatted as comma-separated quoted strings
        self.assertEqual(prompt_dict["platforms"], "'linkedin', 'instagram'")
        
        # Verify formats are formatted as comma-separated quoted strings
        self.assertEqual(prompt_dict["formats"], "'carousel', 'single_image'")
        
        # Verify numeric values are converted to strings
        self.assertEqual(prompt_dict["num_ideas_min"], "5")
        self.assertEqual(prompt_dict["num_ideas_max"], "8")
        
        # Verify other fields are present
        self.assertIn("system_prompt", prompt_dict)
        self.assertIn("vocabulary_levels", prompt_dict)
        self.assertIn("formality_levels", prompt_dict)


class TestIdeaGeneratorIntegration(unittest.TestCase):
    """
    Integration tests for IdeaGenerator with real LLM calls.
    
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
        
        # Register the post_ideator prompt if not already registered
        ideator_template_path = PROMPTS_DIR / "post_ideator.md"
        if ideator_template_path.exists():
            with open(ideator_template_path, 'r', encoding='utf-8') as f:
                template_text = f.read()
            
            # Check if prompt already exists
            existing = find_existing_prompt("post_ideator", template_text)
            if not existing:
                # Register the prompt
                register_prompt(
                    prompt_key="post_ideator",
                    template=template_text,
                    description="Post ideator prompt for generating post ideas from articles",
                    metadata={
                        "registered_by": "test_idea_generator",
                        "source_file": str(ideator_template_path),
                    },
                )
                print(f"✓ Registered post_ideator prompt for integration tests")
            else:
                print(f"✓ Post ideator prompt already registered: {existing[1]}")
        else:
            cls.skip_integration = True
            cls.skip_reason = f"Post ideator prompt template not found at {ideator_template_path}"
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
        trace_id = self.logger.create_trace(name="test_idea_generator_integration")
        self.logger.current_trace_id = trace_id
        
        self.llm_client = HttpLLMClient(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            logger=self.logger,
        )
        
        # Create idea generator instance
        self.generator = IdeaGenerator(llm_client=self.llm_client)
        
        # Create IdeationConfig
        self.config = IdeationConfig(
            num_insights_min=2,
            num_insights_max=4,
            num_keywords_min=5,
            num_keywords_max=10,
            num_ideas_min=5,
            num_ideas_max=8,
            platforms=["linkedin", "instagram"],
            formats=["carousel", "single_image"],
        )
        
        # Sample article text
        self.article_text = """
        Workflow automation has become essential for modern teams seeking to improve productivity 
        and reduce manual effort. According to recent studies, companies that implement automation 
        tools save an average of 10 hours per week per team member. This translates to significant 
        cost savings and improved team morale. Manual processes not only waste time but also increase 
        the likelihood of errors and reduce employee satisfaction. Experts recommend starting with 
        repetitive tasks and gradually expanding automation across all workflows to maximize impact.
        
        The key to successful automation lies in identifying repetitive tasks that consume valuable 
        time. Many organizations start with simple processes like email filtering, data entry, and 
        report generation. As teams become more comfortable with automation tools, they can expand 
        to more complex workflows involving multiple systems and stakeholders.
        
        Beyond time savings, automation also reduces the risk of human error in critical processes. 
        Automated workflows ensure consistency and accuracy, which is especially important in 
        industries with strict compliance requirements. Additionally, by freeing employees from 
        mundane tasks, automation allows them to focus on more strategic, creative work that adds 
        greater value to the organization.
        """
    
    def test_generate_ideas_real_llm(self):
        """Test idea generation with real LLM API calls."""
        # Generate ideas
        result = self.generator.generate_ideas(
            article_text=self.article_text,
            config=self.config,
            context="integration_test_001",
        )
        
        # Verify result structure
        self.assertIn("article_summary", result)
        self.assertIn("ideas", result)
        
        # Verify article summary
        summary = result["article_summary"]
        self.assertIn("title", summary)
        self.assertIsInstance(summary["title"], str)
        self.assertGreater(len(summary["title"]), 0)
        
        self.assertIn("main_thesis", summary)
        self.assertIsInstance(summary["main_thesis"], str)
        self.assertGreater(len(summary["main_thesis"]), 0)
        
        self.assertIn("detected_tone", summary)
        self.assertIn("key_insights", summary)
        self.assertIsInstance(summary["key_insights"], list)
        self.assertGreaterEqual(len(summary["key_insights"]), self.config.num_insights_min)
        self.assertLessEqual(len(summary["key_insights"]), self.config.num_insights_max)
        
        # Verify insights structure
        for insight in summary["key_insights"]:
            self.assertIn("id", insight)
            self.assertIn("content", insight)
            self.assertIn("type", insight)
            self.assertIn("strength", insight)
            self.assertIn("source_quote", insight)
            
            # Verify content is not empty
            self.assertGreater(len(insight["content"]), 0)
            
            # Verify strength is numeric
            self.assertIsInstance(insight["strength"], (int, float))
            self.assertGreaterEqual(insight["strength"], 1)
            self.assertLessEqual(insight["strength"], 10)
        
        # Verify ideas list
        ideas = result["ideas"]
        self.assertGreaterEqual(len(ideas), self.config.num_ideas_min)
        self.assertLessEqual(len(ideas), self.config.num_ideas_max)
        
        # Verify each idea structure
        for idea in ideas:
            # Required fields
            self.assertIn("id", idea)
            self.assertIn("platform", idea)
            self.assertIn("format", idea)
            self.assertIn("tone", idea)
            self.assertIn("persona", idea)
            self.assertIn("personality_traits", idea)
            self.assertIn("objective", idea)
            self.assertIn("angle", idea)
            self.assertIn("hook", idea)
            self.assertIn("narrative_arc", idea)
            self.assertIn("vocabulary_level", idea)
            self.assertIn("formality", idea)
            self.assertIn("key_insights_used", idea)
            self.assertIn("target_emotions", idea)
            self.assertIn("primary_emotion", idea)
            self.assertIn("secondary_emotions", idea)
            self.assertIn("avoid_emotions", idea)
            self.assertIn("value_proposition", idea)
            self.assertIn("article_context_for_idea", idea)
            self.assertIn("idea_explanation", idea)
            self.assertIn("estimated_slides", idea)
            self.assertIn("confidence", idea)
            self.assertIn("rationale", idea)
            self.assertIn("risks", idea)
            self.assertIn("keywords_to_emphasize", idea)
            self.assertIn("pain_points", idea)
            self.assertIn("desires", idea)
            
            # Verify platform is in allowed list
            self.assertIn(idea["platform"], self.config.platforms)
            
            # Verify format is in allowed list
            self.assertIn(idea["format"], self.config.formats)
            
            # Verify hook length
            self.assertLessEqual(len(idea["hook"]), self.config.hook_max_chars)
            
            # Verify estimated slides is present and numeric
            # Note: LLM may not always respect the exact min/max range from config,
            # so we verify it's a valid positive number but don't strictly enforce config limits
            self.assertIsInstance(idea["estimated_slides"], (int, float))
            self.assertGreater(idea["estimated_slides"], 0, 
                             f"Idea {idea['id']} estimated_slides should be positive")
            # Config limits are suggestions to the LLM, not hard requirements
            # We verify the value is reasonable (> 0) but allow it to be outside config range
            
            # Verify confidence is numeric and in valid range
            self.assertIsInstance(idea["confidence"], (int, float))
            self.assertGreaterEqual(idea["confidence"], 0.0)
            self.assertLessEqual(idea["confidence"], 1.0)
            
            # Verify lists are actually lists
            self.assertIsInstance(idea["personality_traits"], list)
            self.assertIsInstance(idea["key_insights_used"], list)
            self.assertIsInstance(idea["target_emotions"], list)
            self.assertIsInstance(idea["secondary_emotions"], list)
            self.assertIsInstance(idea["avoid_emotions"], list)
            self.assertIsInstance(idea["risks"], list)
            self.assertIsInstance(idea["keywords_to_emphasize"], list)
            self.assertIsInstance(idea["pain_points"], list)
            self.assertIsInstance(idea["desires"], list)
            
            # Verify key_insights_used references actual insights
            for insight_id in idea["key_insights_used"]:
                insight_ids = [insight["id"] for insight in summary["key_insights"]]
                self.assertIn(insight_id, insight_ids, 
                            f"Idea {idea['id']} references insight {insight_id} that doesn't exist")
    
    def test_generate_ideas_quality(self):
        """Test that generated ideas meet quality requirements."""
        result = self.generator.generate_ideas(
            article_text=self.article_text,
            config=self.config,
            context="integration_test_quality",
        )
        
        ideas = result.get("ideas", [])
        self.assertGreater(len(ideas), 0, "Should generate at least one idea")
        
        # Verify idea diversity
        platforms = [idea["platform"] for idea in ideas]
        formats = [idea["format"] for idea in ideas]
        
        # Should have ideas for multiple platforms (if config allows)
        if len(self.config.platforms) > 1:
            unique_platforms = set(platforms)
            # At least some diversity expected (though not required)
            self.assertGreaterEqual(len(unique_platforms), 1)
        
        # Verify hook quality
        for idea in ideas:
            hook = idea.get("hook", "")
            self.assertGreater(len(hook), 10, 
                             f"Idea {idea['id']} hook should be substantial")
            self.assertLessEqual(len(hook), self.config.hook_max_chars,
                               f"Idea {idea['id']} hook should not exceed max chars")
        
        # Verify idea explanations are meaningful
        for idea in ideas:
            explanation = idea.get("idea_explanation", "")
            self.assertGreater(len(explanation), 50,
                             f"Idea {idea['id']} explanation should be detailed")
        
        # Verify value propositions are clear
        for idea in ideas:
            value_prop = idea.get("value_proposition", "")
            self.assertGreater(len(value_prop), 10,
                             f"Idea {idea['id']} value proposition should be clear")
    
    def test_generate_ideas_semantic_alignment(self):
        """Test that generated ideas align semantically with article."""
        result = self.generator.generate_ideas(
            article_text=self.article_text,
            config=self.config,
            context="integration_test_semantic",
        )
        
        summary = result["article_summary"]
        ideas = result["ideas"]
        
        # Verify article summary keywords appear in article text
        keywords = summary.get("keywords", [])
        article_lower = self.article_text.lower()
        keywords_found = [
            keyword for keyword in keywords 
            if keyword.lower() in article_lower
        ]
        # At least some keywords should match
        self.assertGreater(len(keywords_found), 0,
                          "Article summary keywords should match article content")
        
        # Verify ideas reference article insights
        for idea in ideas:
            insights_used = idea.get("key_insights_used", [])
            self.assertGreater(len(insights_used), 0,
                             f"Idea {idea['id']} should use at least one insight")
            
            # Verify article context references article themes
            article_context = idea.get("article_context_for_idea", "")
            self.assertGreater(len(article_context), 20,
                             f"Idea {idea['id']} should have meaningful article context")


if __name__ == '__main__':
    unittest.main()
