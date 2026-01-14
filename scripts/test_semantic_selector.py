"""
Test script for Template Selector with semantic analysis

Demonstrates the selector's functionality using embeddings and compares
with the fallback method to show the differences.

Usage:
    python scripts/test_semantic_selector.py
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.templates.selector import TemplateSelector, EMBEDDINGS_AVAILABLE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)


def print_section(title: str):
    """Print formatted section"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_selector(test_cases):
    """
    Test selector with multiple cases
    
    Args:
        test_cases: List of test cases
    """
    print_section("INITIALIZING TEMPLATE SELECTOR")
    
    if EMBEDDINGS_AVAILABLE:
        print("✅ sentence-transformers available - Using semantic analysis with embeddings")
    else:
        print("⚠️  sentence-transformers NOT available - Using fallback method")
        print("   To enable embeddings: pip install sentence-transformers\n")
    
    selector = TemplateSelector()
    
    print_section("RUNNING TEST CASES")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"Test Case #{i}: {test_case['name']}")
        print(f"{'─'*80}\n")
        
        print(f"📋 Template Type: {test_case['template_type']}")
        if test_case.get('value_subtype'):
            print(f"📋 Value Subtype: {test_case['value_subtype']}")
        print(f"🎯 Purpose: {test_case['purpose']}")
        print(f"📝 Copy Direction: {test_case['copy_direction'][:100]}...")
        print(f"🔑 Key Elements: {', '.join(test_case['key_elements'])}")
        
        # Execute selection
        template_id, justification, confidence = selector.select_template(
            template_type=test_case['template_type'],
            value_subtype=test_case.get('value_subtype'),
            purpose=test_case['purpose'],
            copy_direction=test_case['copy_direction'],
            key_elements=test_case['key_elements'],
            persona=test_case.get('persona', 'Professional'),
            tone=test_case.get('tone', 'conversational'),
            platform=test_case.get('platform', 'linkedin'),
        )
        
        # Display result
        print(f"\n{'─'*40}")
        print("RESULT")
        print(f"{'─'*40}")
        print(f"✨ Template ID: {template_id}")
        print(f"📊 Confidence: {confidence:.2f}")
        
        # Quality indicator
        if confidence >= 0.7:
            quality = "✅ EXCELLENT"
        elif confidence >= 0.5:
            quality = "⚠️  MODERATE"
        else:
            quality = "❌ WEAK"
        print(f"🎖️  Quality: {quality}")
        
        print(f"💡 Justification:\n   {justification}")
        
        # Get complete template
        template = selector.library.get_template(template_id)
        if template:
            print(f"\n📐 Structure: {template.structure}")
            print(f"📏 Length: {template.length_range[0]}-{template.length_range[1]} characters")
            print(f"🎨 Tone: {template.tone}")
            print(f"💬 Example: \"{template.example}\"")


def main():
    """Main function"""
    print_section("TEMPLATE SELECTOR SEMANTIC ANALYSIS TEST")
    
    # Diverse test cases
    test_cases = [
        {
            'name': 'Hook with contrast',
            'template_type': 'hook',
            'purpose': 'Create recognition about certificates vs skills',
            'copy_direction': 'Open with contrast highlighting gap between static collection and dynamic use. Professional conversational tone.',
            'key_elements': ['certificates', 'skills', 'contrast'],
            'persona': 'Professional',
            'tone': 'conversational',
        },
        {
            'name': 'Hook with provocative question',
            'template_type': 'hook',
            'purpose': 'Challenge common belief about AI',
            'copy_direction': 'Ask question that challenges the assumption that AI is only for big companies. Create constructive tension.',
            'key_elements': ['AI', 'big tech', 'challenge', 'question'],
            'persona': 'Professional',
            'tone': 'questioning',
        },
        {
            'name': 'Value/Data with credible source',
            'template_type': 'value',
            'value_subtype': 'data',
            'purpose': 'Present quantified evidence of problem',
            'copy_direction': 'Show statistics quantifying the Certificate Graveyard phenomenon. Use percentage or absolute numbers. Include credible source like McKinsey or Gartner.',
            'key_elements': ['statistics', 'unused knowledge', 'scale', 'source'],
            'persona': 'Professional',
            'tone': 'technical and authoritative',
        },
        {
            'name': 'Value/Insight breaking myth',
            'template_type': 'value',
            'value_subtype': 'insight',
            'purpose': 'Challenge common assumption',
            'copy_direction': 'Break myth that AI completely replaces people, showing reality that it amplifies human capabilities.',
            'key_elements': ['myth', 'AI', 'people', 'reality'],
            'persona': 'Educator',
            'tone': 'educational and clear',
        },
        {
            'name': 'Value/Solution with framework',
            'template_type': 'value',
            'value_subtype': 'solution',
            'purpose': 'Teach replicable method',
            'copy_direction': 'Present framework with memorable acronym and three clear components. Should be applicable and systematic.',
            'key_elements': ['framework', 'process', 'method', 'systematic'],
            'persona': 'Consultant',
            'tone': 'systematic and didactic',
        },
        {
            'name': 'Value/Example with real case',
            'template_type': 'value',
            'value_subtype': 'example',
            'purpose': 'Demonstrate practical application',
            'copy_direction': 'Show case of known company that achieved quantified result through specific action. Institutional and credible tone.',
            'key_elements': ['company', 'result', 'case', 'proof'],
            'persona': 'Analyst',
            'tone': 'institutional and factual',
        },
        {
            'name': 'CTA for engagement',
            'template_type': 'cta',
            'purpose': 'Generate comments and discussion',
            'copy_direction': 'Invite audience to share experiences in comments. Engaging and social tone.',
            'key_elements': ['comment', 'share', 'experience'],
            'persona': 'Influencer',
            'tone': 'engaging and friendly',
        },
    ]
    
    # Run tests
    test_selector(test_cases)
    
    # Final summary
    print_section("SUMMARY")
    
    if EMBEDDINGS_AVAILABLE:
        print("✅ Test executed with semantic analysis using embeddings")
        print("   - Selection based on real text meaning")
        print("   - Captures synonyms and semantic context")
        print("   - Higher precision in complex matches")
    else:
        print("⚠️  Test executed with fallback method")
        print("   - Selection based on keywords and overlap")
        print("   - Functional but less precise than embeddings")
        print("   - To enable embeddings:")
        print("     pip install sentence-transformers")
    
    print("\n" + "="*80)
    print("  Test completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
