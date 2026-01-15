"""
Textual templates definitions

Contains all textual/narrative templates organized by module type.

Templates guide text structure and content for slides.
Design templates (for visual composition) are separate and not included here.

Location: src/templates/textual_templates.py
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class TextualTemplate:
    """Textual template for narrative/content structure"""
    
    id: str                        # Template ID (ex: "H_QUESTION", "VS_123")
    module_type: str               # Module type ("hook", "insight", "solution", "example", "cta")
    function: str                  # Description of function
    structure: str                 # Text structure (ex: "What if [ideal scenario]?")
    length_range: Tuple[int, int]  # (min, max) characters
    tone: str                      # Recommended tone
    example: str                   # Example usage
    keywords: List[str]            # Keywords for matching (ex: ["question", "curiosity"])
    semantic_description: str      # Description for semantic matching


# =============================================================================
# HOOK TEMPLATES
# =============================================================================

HOOK_TEMPLATES = [
    TextualTemplate(
        id="H_PAIN",
        module_type="hook",
        function="Activates specific pain",
        structure="Tired of [problem]?",
        length_range=(50, 80),
        tone="provocative and empathetic",
        example="Tired of endless meetings that lead nowhere?",
        keywords=["tired", "pain", "problem", "frustration"],
        semantic_description="Activates specific audience pain with provocative and empathetic question",
    ),
    TextualTemplate(
        id="H_PROMISE",
        module_type="hook",
        function="Promises result",
        structure="Get [benefit] in [time]",
        length_range=(60, 90),
        tone="direct and professional",
        example="Automate tasks in 5 minutes.",
        keywords=["get", "benefit", "result", "time", "speed"],
        semantic_description="Promises tangible result in specific time, direct and professional tone",
    ),
    TextualTemplate(
        id="H_QUESTION",
        module_type="hook",
        function="Generates curiosity",
        structure="What if [ideal scenario]?",
        length_range=(60, 90),
        tone="curious or inspiring",
        example="What if your team worked only 4h/day?",
        keywords=["what if", "question", "curiosity", "scenario", "possibility"],
        semantic_description="Generates curiosity with question about ideal scenario, curious or inspiring tone",
    ),
    TextualTemplate(
        id="H_NUMBER",
        module_type="hook",
        function="Impactful number",
        structure="[X]% of companies [action]",
        length_range=(60, 90),
        tone="objective and factual",
        example="80% of startups fail to scale.",
        keywords=["percentage", "number", "statistic", "companies", "fact"],
        semantic_description="Impactful number as hook, objective and factual tone",
    ),
    TextualTemplate(
        id="H_CONTRAST",
        module_type="hook",
        function="Clear contrast",
        structure="[Before] vs. [After]",
        length_range=(50, 80),
        tone="binary and clear",
        example="Rework vs. maximum productivity.",
        keywords=["vs", "contrast", "before", "after", "transformation"],
        semantic_description="Clear contrast between before and after, binary and direct tone",
    ),
    TextualTemplate(
        id="H_COMBO",
        module_type="hook",
        function="Pain + solution",
        structure="[Pain] → [Solution]",
        length_range=(60, 90),
        tone="direct and practical",
        example="Slow processes → AI Automation.",
        keywords=["pain", "solution", "arrow", "transformation", "practical"],
        semantic_description="Combines real pain with clear solution, direct and practical tone",
    ),
    TextualTemplate(
        id="H_STATEMENT",
        module_type="hook",
        function="Provocative statement",
        structure="You are [common mistake].",
        length_range=(60, 90),
        tone="bold",
        example="You are wasting your talent.",
        keywords=["you are", "mistake", "provocation", "confrontation", "truth"],
        semantic_description="Provocative statement that confronts reader's common mistake, bold tone",
    ),
    TextualTemplate(
        id="H_QUOTE",
        module_type="hook",
        function="Authority quote",
        structure='"[Quote]" – [Source]"',
        length_range=(60, 100),
        tone="inspiring or technical",
        example='"Automation is the future." – Gartner',
        keywords=["quote", "authority", "source", "famous", "expert"],
        semantic_description="Authority quote with citation, inspiring or technical tone",
    ),
    TextualTemplate(
        id="H_ALERT",
        module_type="hook",
        function="Attention-grabbing alert",
        structure="[Risk]: Avoid this.",
        length_range=(50, 80),
        tone="urgent and assertive",
        example="Professional burnout: avoid this.",
        keywords=["alert", "risk", "avoid", "danger", "urgent"],
        semantic_description="Attention-grabbing alert about risk to avoid, urgent and assertive tone",
    ),
    TextualTemplate(
        id="H_PRINCIPLE",
        module_type="hook",
        function="Principle position",
        structure="Here, we believe that [statement]",
        length_range=(60, 100),
        tone="institutional",
        example="Here, we believe that AI is a tool, not a substitute.",
        keywords=["we believe", "principle", "values", "institutional", "positioning"],
        semantic_description="Institutional principle position, manifesto tone or brand value",
    ),
    TextualTemplate(
        id="H_CHALLENGE",
        module_type="hook",
        function="Challenges the reader",
        structure="Do you really believe that [statement]?",
        length_range=(60, 100),
        tone="questioning",
        example="Do you really believe that AI is only for big techs?",
        keywords=["really", "believe", "challenge", "questioning", "tension"],
        semantic_description="Challenges reader's beliefs with question, questioning tone creating constructive tension",
    ),
    TextualTemplate(
        id="H_AFFIRMATION",
        module_type="hook",
        function="Direct statement without provocation",
        structure="You have everything to [action]",
        length_range=(50, 80),
        tone="encouraging",
        example="You have everything to start.",
        keywords=["you have", "everything", "capacity", "encouraging", "positive"],
        semantic_description="Encouraging direct statement without provocation, positive and motivating tone",
    ),
    TextualTemplate(
        id="H_MYSTERY",
        module_type="hook",
        function="Creates curiosity without question",
        structure="What they didn't tell you about [topic]",
        length_range=(60, 90),
        tone="intriguing",
        example="What they didn't tell you about automation.",
        keywords=["didn't tell you", "secret", "mystery", "revelation", "curiosity"],
        semantic_description="Creates curiosity with mystery or secret, intriguing tone without direct question",
    ),
]

# =============================================================================
# VALUE: DATA TEMPLATES
# =============================================================================

VALOR_DADO_TEMPLATES = [
    TextualTemplate(
        id="VD_DATA%",
        module_type="insight",  # Data templates map to insight module type
        function="Direct percentage",
        structure="[X]% of [group] [action]",
        length_range=(100, 200),
        tone="technical and objective",
        example="67% of SMEs ignore basic automation – McKinsey 2024",
        keywords=["percentage", "%", "data", "statistic", "group"],
        semantic_description="Presents direct percentage with context, technical and objective tone",
    ),
    TextualTemplate(
        id="VD_NUMBER",
        module_type="insight",  # Data templates map to insight module type
        function="Absolute number",
        structure="[X] [entity] per [time]",
        length_range=(100, 180),
        tone="analytical",
        example="3 hours lost per day per employee.",
        keywords=["number", "entity", "time", "quantity", "scale"],
        semantic_description="Shows impact at scale with absolute number, analytical tone",
    ),
    TextualTemplate(
        id="VD_COMPARE",
        module_type="insight",  # Data templates map to insight module type
        function="Numerical comparison",
        structure="[X] times more than [Y]",
        length_range=(100, 180),
        tone="clear comparative",
        example="AI generates results 5x faster.",
        keywords=["times", "comparison", "more", "relative", "benefit"],
        semantic_description="Highlights relative benefit with numerical comparison, clear language",
    ),
    TextualTemplate(
        id="VD_TIME",
        module_type="insight",  # Data templates map to insight module type
        function="Time savings",
        structure="Reduce [time] with [action]",
        length_range=(100, 180),
        tone="practical and gain-oriented",
        example="Reduce 20h/month in reports.",
        keywords=["reduce", "time", "savings", "gain", "hours"],
        semantic_description="Emphasizes time savings, practical and gain-oriented tone",
    ),
    TextualTemplate(
        id="VD_COST",
        module_type="insight",  # Data templates map to insight module type
        function="Financial savings",
        structure="Save up to $[amount]",
        length_range=(100, 180),
        tone="economic",
        example="Save up to $10k/month by automating.",
        keywords=["save", "cost", "money", "financial", "roi"],
        semantic_description="Quantifies financial impact, economic tone focused on ROI",
    ),
    TextualTemplate(
        id="VD_SOURCE",
        module_type="insight",  # Data templates map to insight module type
        function="Data with reference",
        structure="[Data] – [Source]",
        length_range=(120, 200),
        tone="technical and serious",
        example="Automation generates 30% more ROI – McKinsey",
        keywords=["source", "reference", "authority", "validation", "credibility"],
        semantic_description="Presents data with attribution to reliable source, technical and serious tone",
    ),
    TextualTemplate(
        id="VD_CHART",
        module_type="insight",  # Data templates map to insight module type
        function="Visual data",
        structure="See in the chart: [trend or relationship]",
        length_range=(100, 200),
        tone="visual and direct",
        example="See in the chart how AI adoption grows 5x faster in B2B startups.",
        keywords=["chart", "visual", "trend", "relationship", "data"],
        semantic_description="References visual data for temporal trends or comparisons, visual and direct tone",
    ),
]

# =============================================================================
# VALUE: INSIGHT TEMPLATES
# =============================================================================

VALOR_INSIGHT_TEMPLATES = [
    TextualTemplate(
        id="VI_PRINCIPLE",
        module_type="insight",
        function="Universal principle",
        structure="[Action] is about [principle]",
        length_range=(150, 250),
        tone="inspiring or technical",
        example="Automation is about strategy, not just efficiency.",
        keywords=["principle", "about", "essence", "strategy", "universal"],
        semantic_description="Goes beyond the obvious highlighting strategic value, inspiring or technical tone",
    ),
    TextualTemplate(
        id="VI_CONSEQUENCE",
        module_type="insight",
        function="Direct consequence",
        structure="[Problem] generates [consequence]",
        length_range=(150, 250),
        tone="explanatory",
        example="Slow decisions generate market loss.",
        keywords=["consequence", "generates", "cause", "effect", "relationship"],
        semantic_description="Relates causes and effects, explanatory tone showing direct relationship",
    ),
    TextualTemplate(
        id="VI_PARADOX",
        module_type="insight",
        function="Unexpected insight",
        structure="You don't need [expected action] to [result]",
        length_range=(150, 250),
        tone="reflective",
        example="You don't need to be big to scale fast.",
        keywords=["don't need", "paradox", "unexpected", "break", "expectation"],
        semantic_description="Breaks expectations with unexpected insight, reflective and surprising tone",
    ),
    TextualTemplate(
        id="VI_MYTH",
        module_type="insight",
        function="Myth breaking",
        structure="Myth: [false] Reality: [truth]",
        length_range=(150, 250),
        tone="educational",
        example="Myth: AI replaces people. Reality: Amplifies capabilities.",
        keywords=["myth", "reality", "false", "truth", "breaking"],
        semantic_description="Confronts common assumptions, educational tone breaks myths",
    ),
    TextualTemplate(
        id="VI_QUOTE",
        module_type="insight",
        function="Insight through quote",
        structure='"[Strong insight]" – [Source]"',
        length_range=(120, 200),
        tone="inspiring or technical",
        example='"Not automating is like running without shoes." – Seth Godin',
        keywords=["quote", "insight", "source", "authority", "wisdom"],
        semantic_description="Strong insight through quote, reliable source with real impact",
    ),
    TextualTemplate(
        id="VI_LADDER",
        module_type="insight",
        function="Evolutionary insight",
        structure="You start with [action], then [learning]",
        length_range=(150, 250),
        tone="constructive",
        example="You start by automating tasks. Then, learn to scale decisions.",
        keywords=["start", "then", "evolution", "progression", "learning"],
        semantic_description="Shows logical learning evolution, progressive constructive tone",
    ),
    TextualTemplate(
        id="VI_STATEMENT",
        module_type="insight",
        function="Clear position",
        structure="[Statement about the market or topic]",
        length_range=(150, 250),
        tone="institutional",
        example="AI is not a competitive advantage. It's a prerequisite to survive.",
        keywords=["statement", "positioning", "market", "topic", "opinion"],
        semantic_description="Strong positioning with clarity about scenario, institutional tone",
    ),
]

# =============================================================================
# VALUE: SOLUTION TEMPLATES
# =============================================================================

VALOR_SOLUCAO_TEMPLATES = [
    TextualTemplate(
        id="VS_123",
        module_type="solution",
        function="Sequential steps",
        structure="1. [Step] 2. [Step] 3. [Step]",
        length_range=(200, 350),
        tone="tutorial",
        example="1. List manual processes. 2. Use AI. 3. Measure results.",
        keywords=["steps", "sequential", "1.", "2.", "3.", "process"],
        semantic_description="Clear and progressive explanation with sequential steps, tutorial tone",
    ),
    TextualTemplate(
        id="VS_LIST",
        module_type="solution",
        function="Practical list",
        structure="- [Short action] - [Short action]",
        length_range=(150, 250),
        tone="practical",
        example="- Delegate repetitive tasks - Apply AI - Evaluate results",
        keywords=["list", "action", "-", "practical", "quick"],
        semantic_description="Objective list with short actions, light and direct format",
    ),
    TextualTemplate(
        id="VS_FORMULA",
        module_type="solution",
        function="Simple formula",
        structure="[Result] = [Factor] + [Factor]",
        length_range=(100, 200),
        tone="analytical",
        example="Productivity = Automation + Clear leadership",
        keywords=["formula", "=", "factor", "equation", "simple"],
        semantic_description="Synthetic but didactic, analytical tone with replicable formula",
    ),
    TextualTemplate(
        id="VS_FRAMEWORK",
        module_type="solution",
        function="Short framework",
        structure="[Acronym]: [Definition 1], [Definition 2], [Definition 3]",
        length_range=(150, 250),
        tone="systematic",
        example="PAR: Process, Automation, Results",
        keywords=["framework", "acronym", "model", "systematic", "structure"],
        semantic_description="Teaches applicable model with acronym and definitions, systematic tone",
    ),
    TextualTemplate(
        id="VS_CHECKLIST",
        module_type="solution",
        function="Visual checklist",
        structure="☑️ [Action] ☑️ [Action] ☑️ [Action]",
        length_range=(150, 200),
        tone="direct and visual",
        example="☑️ Map tasks ☑️ Choose tool ☑️ Implement",
        keywords=["checklist", "☑️", "action", "visual", "sequential"],
        semantic_description="Objective and sequential checklist, direct and visual tone",
    ),
    TextualTemplate(
        id="VS_OBSTACLE",
        module_type="solution",
        function="Overcomes common blocker",
        structure="If [problem], then [practical solution]",
        length_range=(150, 250),
        tone="empathetic and technical",
        example="If you don't have a tech team, use AI with pre-ready agents.",
        keywords=["if", "then", "problem", "solution", "blocker"],
        semantic_description="Helps reader overcome common blockers, empathetic and technical tone",
    ),
    TextualTemplate(
        id="VS_DECISION",
        module_type="solution",
        function="Choice criteria",
        structure="Choose [X] if seeking [Y]",
        length_range=(120, 200),
        tone="objective and strategic",
        example="Choose local AI if seeking data control. Cloud, if seeking scale.",
        keywords=["choose", "if", "criteria", "decision", "option"],
        semantic_description="Helps make decisions with criteria, objective and strategic tone",
    ),
]

# =============================================================================
# VALUE: EXAMPLE TEMPLATES
# =============================================================================

VALOR_EXEMPLO_TEMPLATES = [
    TextualTemplate(
        id="VE_MINICASE",
        module_type="example",
        function="Quantified result",
        structure="[Company] had [result] with [applied action]",
        length_range=(200, 300),
        tone="institutional",
        example="Shopify increased checkout speed 40% through AI optimization.",
        keywords=["company", "result", "case", "quantified", "proof"],
        semantic_description="Clear case with strong number and direct impact, institutional tone",
    ),
    TextualTemplate(
        id="VE_SIMULATION",
        module_type="example",
        function="Hypothetical scenario",
        structure="Imagine that you [ideal action / positive context]",
        length_range=(150, 250),
        tone="imaginative and engaging",
        example="Imagine reducing meetings by half with AI.",
        keywords=["imagine", "scenario", "hypothetical", "ideal", "reflection"],
        semantic_description="Leads to reflection with positive hypothetical scenario, imaginative and engaging tone",
    ),
    TextualTemplate(
        id="VE_ANECDOTE",
        module_type="example",
        function="Informal example",
        structure="[Person] used [solution] and [observed result]",
        length_range=(150, 250),
        tone="accessible and humanized",
        example="Sarah automated her weekly reports and eliminated all deadline stress.",
        keywords=["person", "used", "anecdote", "storytelling", "human"],
        semantic_description="Light storytelling style, accessible and humanized tone",
    ),
    TextualTemplate(
        id="VE_COMPARATIVE",
        module_type="example",
        function="Contrasting example",
        structure="[Company A] did [X], [Company B] didn't. Result? [Y]",
        length_range=(200, 300),
        tone="factual and instructive",
        example="Amazon invested in warehouse AI early, competitors didn't. Result: 50% faster fulfillment.",
        keywords=["comparison", "company", "contrast", "decision", "result"],
        semantic_description="Direct contrast of decision and impact, factual and instructive tone",
    ),
    TextualTemplate(
        id="VE_MICROCAUSE",
        module_type="example",
        function="Detail with impact",
        structure="[Team/person] changed [action] and [symbolic result]",
        length_range=(150, 250),
        tone="light and revealing",
        example="Finance team automated one report and saved 9h/week.",
        keywords=["team", "person", "change", "detail", "impact"],
        semantic_description="Shows granular transformation with small detail, light and revealing tone",
    ),
]

# =============================================================================
# CTA TEMPLATES
# =============================================================================

CTA_TEMPLATES = [
    TextualTemplate(
        id="CTA_FOLLOW",
        module_type="cta",
        function="Build audience",
        structure="Follow for [value promise]",
        length_range=(50, 100),
        tone="invitation",
        example="Follow for weekly insights on AI implementation.",
        keywords=["follow", "audience", "promise", "content"],
        semantic_description="Invites to follow to receive continuous value, invitation tone",
    ),
    TextualTemplate(
        id="CTA_COMMENT",
        module_type="cta",
        function="Generate engagement",
        structure="[Question or invite to share]",
        length_range=(50, 150),
        tone="engaging",
        example="Which of these mistakes have you made? Comment below 👇",
        keywords=["comment", "question", "engagement", "share", "interaction"],
        semantic_description="Invites to comment with question or invite, engaging tone",
    ),
    TextualTemplate(
        id="CTA_SAVE",
        module_type="cta",
        function="Increase reach through saves",
        structure="Save this for [future use case]",
        length_range=(50, 100),
        tone="practical",
        example="Save this before your next AI project.",
        keywords=["save", "future", "reference"],
        semantic_description="Invites to save for future use, practical and useful tone",
    ),
    TextualTemplate(
        id="CTA_SHARE",
        module_type="cta",
        function="Viral spread",
        structure="Tag someone who [needs this]",
        length_range=(60, 120),
        tone="social",
        example="Tag a founder who is drowning in manual work.",
        keywords=["tag", "share", "someone", "viral"],
        semantic_description="Invites to tag/share, social tone for viral spread",
    ),
    TextualTemplate(
        id="CTA_DM",
        module_type="cta",
        function="Personal connection",
        structure="[Personal invite]",
        length_range=(50, 120),
        tone="personal and inviting",
        example="DM me 'framework' and I'll send the complete guide.",
        keywords=["dm", "inbox", "message", "personal", "connection"],
        semantic_description="Personal invite for DM, intimate and inviting tone",
    ),
    TextualTemplate(
        id="CTA_LINK",
        module_type="cta",
        function="Generate traffic",
        structure="Access [resource] at [destination]",
        length_range=(50, 100),
        tone="direct",
        example="Download the complete checklist (link in bio).",
        keywords=["access", "link", "download", "resource", "traffic"],
        semantic_description="Invites to access external resource, direct tone to generate traffic",
    ),
    TextualTemplate(
        id="CTA_DOUBLE_ACTION",
        module_type="cta",
        function="Multiple engagement paths",
        structure="[Action 1] + [Action 2]",
        length_range=(60, 120),
        tone="flexible",
        example="Save this post + share with your team.",
        keywords=["action", "double", "+", "multiple", "flexible"],
        semantic_description="Offers multiple engagement paths, flexible tone",
    ),
]
