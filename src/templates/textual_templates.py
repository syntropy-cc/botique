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
    detailed_description: str = ""  # Comprehensive description explaining what the template fundamentally achieves, its narrative purpose, when to use it, and how it serves the content strategy. Written specifically for LLM copywriter understanding.
    usage_examples: List[str] = None  # Multiple examples of creative template usage (3-5 variations)
    creative_guidance: str = ""    # Detailed guidance on how to use the template creatively
    interpretation_notes: str = ""  # Notes on how to interpret placeholders and structure conceptually
    what_to_avoid: str = ""        # What to avoid when using the template (e.g., don't use literal words from structure)
    
    def __post_init__(self):
        """Initialize default values for optional fields"""
        if self.usage_examples is None:
            self.usage_examples = []


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
        detailed_description="This template connects immediately with your audience's frustrations and pain points. It's designed to create instant recognition and empathy by acknowledging a common struggle they face. Use this when you want to establish that you understand their challenges before presenting a solution. The template works best when the pain is specific, relatable, and something your audience experiences regularly. It's particularly effective for audiences who feel misunderstood or who are actively seeking solutions to persistent problems.",
        usage_examples=[
            "Endless meetings leading nowhere?",
            "Still drowning in manual processes?",
            "How many hours did you lose to repetitive tasks this week?",
            "Frustrated with processes that waste your time?",
            "Another day lost to tasks that should be automated?"
        ],
        creative_guidance="Express fatigue or frustration implicitly through varied question structures. You don't need to always start with 'Tired of' - use rhetorical questions, statements that evoke the pain, or questions that quantify the frustration. The goal is to make the audience nod in recognition, not to literally ask if they're tired.",
        interpretation_notes="The [problem] placeholder represents the specific pain point your audience experiences. Frame it as a question, statement, or quantified frustration. Think about how your audience experiences this problem - is it time-consuming, emotionally draining, financially costly? Tap into the real impact.",
        what_to_avoid="Avoid always starting with 'Tired of' or 'Fed up with' - use varied pain triggers. Don't be generic with the problem. Make it specific and relatable. The structure shows the concept of pain activation, not a literal question format.",
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
        detailed_description="This template immediately promises a specific, measurable benefit within a clear timeframe. It's designed to grab attention by showing immediate value and setting expectations. Use this when you have a concrete deliverable or transformation that happens quickly. The template works best for audiences who value efficiency and want to see quick wins. It's particularly effective when the time-to-value is genuinely impressive and the benefit is clearly understood.",
        usage_examples=[
            "5 minutes to automate your first workflow",
            "From manual chaos to automated clarity in under 10 minutes",
            "Your first AI assistant ready in the time it takes to read this",
            "Transform your workflow in 60 seconds",
            "See results in minutes, not months"
        ],
        creative_guidance="Focus on the transformation speed or ease rather than always using 'Get...in...' formula. Emphasize what changes, how fast, and the impact. You can state the benefit first, then the time, or create a narrative of transformation. The key is making the speed impressive and the benefit tangible.",
        interpretation_notes="The [benefit] placeholder should be concrete and valuable - something your audience can visualize achieving. The [time] placeholder creates urgency and sets expectations. Think about what makes your solution fast or easy, and frame it in a way that feels impressive but achievable.",
        what_to_avoid="Avoid always using 'Get...in...' formula - express time and value creatively. Don't promise unrealistic timeframes. Don't be vague about the benefit. The structure shows the concept of speed-to-value, not a literal formula.",
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
        detailed_description="This template opens with a question that invites your audience to imagine a better, ideal scenario. It's designed to spark curiosity and make readers want to learn more. Use this when you want to paint a picture of possibility before revealing how to achieve it. The template works best when the ideal scenario is compelling, specific, and feels achievable with your solution. It's particularly effective for audiences who are open to new possibilities and enjoy envisioning better futures.",
        usage_examples=[
            "What if your team worked only 4h/day?",
            "Imagine cutting meeting time in half. What would you do with those hours?",
            "Ever wonder how top performers stay ahead? Here's their secret.",
            "What if every task that drains you could run automatically?",
            "Picture this: you finish your workday with energy to spare."
        ],
        creative_guidance="Questions can be direct, implied, or combined with statements. Focus on sparking imagination and curiosity. You don't always need to start with 'What if' - use 'Imagine', 'Ever wonder', 'Picture this', or lead with the scenario then ask a follow-up question. The goal is to make the reader want to know more.",
        interpretation_notes="The [ideal scenario] placeholder should be specific and desirable - something that would genuinely improve your audience's situation. Think about what your audience dreams of achieving, and frame it as a question that makes them want to explore the answer. Make it concrete enough to visualize but compelling enough to spark curiosity.",
        what_to_avoid="Avoid always starting with 'What if' - vary question structures. Don't make the scenario too vague or unrealistic. Don't ask questions that have obvious negative answers. The structure shows the concept of curiosity-driven hooks, not a literal question format.",
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
        detailed_description="This template leads with a compelling statistic or number that immediately establishes the scale or importance of a trend, problem, or opportunity. It's designed to grab attention through data-driven impact. Use this when you have credible statistics that support your message or reveal something surprising about your topic. The template works best when the number is genuinely surprising, relevant, and from a credible source. It's particularly effective for audiences who value data and facts, or when you're establishing authority through research.",
        usage_examples=[
            "80% of startups fail to scale",
            "Nine out of ten AI projects stall. Here's why the tenth succeeds.",
            "Only 23% of teams actually use automation. The rest? Still doing it manually.",
            "73% of professionals struggle with this. You're not alone.",
            "The number that should shock you: 60% of work time is wasted on repetitive tasks."
        ],
        creative_guidance="Numbers can be percentages, ratios, absolute counts, or fractions. Frame them dramatically and make them meaningful. You don't always need '[X]% of [group]' - try 'Nine out of ten', 'Only [X]%', or lead with why the number matters. Make the statistic feel personal and relevant to your audience.",
        interpretation_notes="The [X] and [action] placeholders represent the statistic and its context. The number should be credible, relevant, and meaningful. Think about what statistic would make your audience pause - is it surprising? Concerning? Impressive? Make the number do the work of creating interest.",
        what_to_avoid="Avoid always using '[X]% of [group]' format - vary number presentation. Don't use statistics that aren't credible or verifiable. Don't make the number so specific it feels fabricated. The structure shows the concept of data-driven hooks, not a literal percentage format.",
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
        detailed_description="This template creates a stark contrast between two states, situations, or approaches - typically showing the problem state versus the ideal state. It's designed to immediately clarify the transformation or choice at hand. Use this when you want to make the difference between approaches or states crystal clear. The template works best when the contrast is meaningful and the 'after' state is clearly superior. It's particularly effective for audiences who appreciate clear choices and binary thinking, or when you're positioning your solution as an obvious improvement.",
        usage_examples=[
            "Manual processes → automated workflows",
            "From chaos to clarity in one step",
            "Yesterday: drowning in emails. Today: zero inbox stress.",
            "Rework vs. maximum productivity",
            "Chaos vs. control. Which side are you on?"
        ],
        creative_guidance="Contrasts can use 'vs.', arrows (→), 'from...to', parallel structures, or narrative progression showing change over time. The contrast should be clear and meaningful. You can make it binary, show a transformation, or present it as a choice. The key is making the difference obvious and compelling.",
        interpretation_notes="The [Before] and [After] placeholders represent two opposing states. The 'before' should represent a problem, inefficiency, or undesirable state your audience recognizes. The 'after' should represent the ideal state your solution enables. Make the contrast vivid and relatable.",
        what_to_avoid="Avoid always using 'X vs. Y' format - explore varied contrast expressions. Don't make the contrast too subtle - it should be immediately clear. Don't use vague terms that don't create a meaningful distinction. The structure shows the concept of clear contrast, not a literal 'vs.' format.",
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
        detailed_description="This template immediately connects a recognized pain point with its solution, showing the direct path from problem to resolution. It's designed to reassure your audience that their problem has a clear fix. Use this when you want to show that you understand their challenge AND have the solution ready. The template works best when the pain is specific and the solution is directly related. It's particularly effective for audiences who are actively seeking solutions and appreciate straightforward problem-solving approaches.",
        usage_examples=[
            "Slow processes meet AI automation",
            "Your biggest bottleneck? Solved in three clicks.",
            "The problem: endless spreadsheets. The fix: one automated dashboard.",
            "Slow processes → AI Automation",
            "Manual chaos becomes automated clarity"
        ],
        creative_guidance="The connection between pain and solution can be explicit (using arrows), implicit (narrative flow), or shown through questions that reveal the solution. You can state the pain as a question and answer it, or show them side-by-side. The key is making the solution feel like a natural, obvious response to the pain.",
        interpretation_notes="The [Pain] placeholder should be a specific, relatable problem your audience faces. The [Solution] placeholder should directly address that pain in a clear, actionable way. Think about how your solution transforms the pain - is it elimination, improvement, or replacement? Make the connection obvious.",
        what_to_avoid="Avoid always using '[Pain] → [Solution]' format - vary connection methods. Don't make the pain too generic or the solution too vague. Don't create a disconnect between the problem and solution. The structure shows the concept of problem-solution pairing, not a literal arrow format.",
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
        detailed_description="This template makes a bold, provocative statement that challenges the reader's assumptions or behaviors. It's designed to stop scroll, create tension, and make the reader either agree or want to understand why you'd say this. Use this when you want to shake your audience out of complacency and get them to question their current approach. The template works best when the statement is true enough to be uncomfortable but specific enough to be actionable. It's particularly effective for audiences who appreciate direct communication and aren't easily offended by challenging statements.",
        usage_examples=[
            "You're wasting your talent on tasks that should be automated",
            "Still doing it the hard way? Here's a better path.",
            "The biggest productivity killer? It's not what you think.",
            "You're working harder, not smarter. Here's why.",
            "That thing you're proud of? It's holding you back."
        ],
        creative_guidance="Provocation can be a direct accusation, an implied question that challenges assumptions, or a revealed truth that makes the reader uncomfortable. You don't always need to say 'You are' - use questions, statements that reveal uncomfortable truths, or observations that challenge behavior. The goal is to create enough tension to make them want to read more.",
        interpretation_notes="The [common mistake] placeholder represents a behavior, belief, or pattern your audience engages in that's holding them back. It should be specific enough to be recognizable but general enough that many in your audience will identify with it. Think about what your audience is doing 'wrong' that your solution addresses.",
        what_to_avoid="Avoid always starting with 'You are' - vary confrontation styles. Don't be so provocative that you alienate your audience. Don't make accusations that aren't true or relatable. The structure shows the concept of provocative confrontation, not a literal 'You are' format.",
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
        detailed_description="This template leads with a quote from a recognized authority, expert, or thought leader that supports your message. It's designed to borrow credibility and establish your topic as important through association. Use this when you have a compelling quote from someone your audience respects that aligns with your message. The template works best when the source is genuinely authoritative and the quote is memorable or insightful. It's particularly effective for audiences who value expert opinions and research-backed insights.",
        usage_examples=[
            '"Automation is the future." – Gartner',
            "As McKinsey puts it: 'AI adoption is accelerating faster than expected.'",
            "Gartner research confirms: automation isn't optional anymore",
            "According to industry leaders: 'The companies that automate will define the next decade.'",
            "'The future belongs to those who automate intelligently.' – Industry expert"
        ],
        creative_guidance="Quotes can be presented directly with attribution, integrated into a sentence, paraphrased, or referenced as supporting evidence. You can lead with the quote, embed it naturally, or use it to support a statement. The key is making the authority's voice work for your message while keeping it natural.",
        interpretation_notes="The [Quote] placeholder should be a memorable, relevant statement from a credible source. The [Source] placeholder adds credibility. Think about what authority would support your message - industry research firms, well-known experts, respected publications. Make sure the quote genuinely adds value and isn't just name-dropping.",
        what_to_avoid="Avoid always using '[Quote] – [Source]' format - vary attribution styles. Don't use quotes from sources your audience won't recognize as authoritative. Don't misquote or take quotes out of context. The structure shows the concept of authority-backed hooks, not a literal quote format.",
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
        detailed_description="This template creates urgency by alerting your audience to a risk, danger, or common mistake they should avoid. It's designed to stop scroll and create immediate concern or curiosity about the threat. Use this when you want to warn your audience about a common pitfall or risk that your content helps them avoid. The template works best when the risk is real, relatable, and something your audience genuinely wants to prevent. It's particularly effective for audiences who are cautious, risk-aware, or learning from others' mistakes.",
        usage_examples=[
            "Professional burnout: here's how to prevent it",
            "This common mistake kills productivity. Here's how to dodge it.",
            "Warning: 73% of professionals make this error. Don't be one of them.",
            "Avoid this trap that derails 80% of projects",
            "The mistake that costs teams weeks of productivity? Here's how to sidestep it."
        ],
        creative_guidance="Alerts can use colons, warnings, statistics that reveal the risk, or dramatic statements that make the danger clear. You don't always need '[Risk]: Avoid this' - use questions, statistics, or narrative that shows the consequences. The key is making the risk feel urgent and the solution feel necessary.",
        interpretation_notes="The [Risk] placeholder should represent a genuine threat, mistake, or negative outcome your audience wants to avoid. It should be specific enough to be concerning but general enough that many will relate. Think about what common error or risk your content helps prevent.",
        what_to_avoid="Avoid always using '[Risk]: Avoid this' formula - vary alert structures. Don't create false urgency or exaggerate risks. Don't make the alert so generic it loses impact. The structure shows the concept of risk-awareness hooks, not a literal alert format.",
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
        detailed_description="This template establishes your brand's or organization's core principle, belief, or philosophical position on a topic. It's designed to position you as having a clear point of view and values. Use this when you want to establish thought leadership by taking a clear stand on an important topic. The template works best when the principle is meaningful, differentiated, and resonates with your audience's values. It's particularly effective for audiences who value authenticity, transparency, and brands that stand for something.",
        usage_examples=[
            "Here, we believe that AI is a tool, not a substitute",
            "Our philosophy: automation amplifies human potential",
            "We stand by this: technology serves strategy, not the other way around",
            "Our core belief? Efficiency without purpose is wasted effort.",
            "This is where we draw the line: automation should empower, not replace."
        ],
        creative_guidance="Principles can be stated directly as beliefs, framed as philosophy, positioned as values, or presented as boundaries. You don't always need to say 'Here, we believe' - use 'Our philosophy', 'We stand by', 'Our core belief', or present it as a manifesto statement. The key is making your position clear and meaningful.",
        interpretation_notes="The [statement] placeholder should represent a core belief, value, or principle that guides your approach. It should be substantive enough to matter but clear enough to be understood. Think about what principle your brand or content stands for that differentiates you and resonates with your audience.",
        what_to_avoid="Avoid always starting with 'Here, we believe' - vary principle statements. Don't state principles that are generic or don't differentiate you. Don't take positions that don't align with your actions. The structure shows the concept of values-driven hooks, not a literal belief statement format.",
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
        detailed_description="This template challenges your audience's assumptions or beliefs by questioning something they might take for granted. It's designed to create constructive tension that makes readers reconsider their position. Use this when you want to break through common misconceptions or assumptions that are holding your audience back. The template works best when the challenged belief is common, limiting, and something your content can help reframe. It's particularly effective for audiences who are open to having their assumptions questioned and appreciate thought-provoking content.",
        usage_examples=[
            "Do you really believe that AI is only for big techs?",
            "Still think automation is expensive? Think again.",
            "Believe it or not: small teams outpace enterprises in AI adoption.",
            "Think you need a big team to automate? Here's what the data shows.",
            "You might believe this is complex. The reality? It's simpler than you think."
        ],
        creative_guidance="Challenges can be direct questions that question beliefs, statements that reveal contradictions, or observations that challenge assumptions. You don't always need 'Do you really believe' - use 'Still think', 'Believe it or not', or reveal the truth that contradicts common belief. The goal is creating enough tension to make them want to understand why you're challenging them.",
        interpretation_notes="The [statement] placeholder should represent a common assumption, belief, or misconception your audience holds that your content challenges. It should be specific enough to be recognizable but general enough that many will identify with it. Think about what limiting belief your content helps break.",
        what_to_avoid="Avoid always using 'Do you really believe' - vary challenge formats. Don't challenge beliefs in a condescending way. Don't challenge positions that aren't actually common or limiting. The structure shows the concept of assumption-challenging hooks, not a literal question format.",
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
        detailed_description="This template empowers and encourages your audience by affirming they already have what they need to take action. It's designed to reduce friction and build confidence by removing barriers of perception. Use this when you want to motivate action by showing your audience they're more capable than they think. The template works best when the affirmation is true and actionable. It's particularly effective for audiences who need encouragement or struggle with imposter syndrome, or when you're removing perceived barriers to getting started.",
        usage_examples=[
            "You have everything to start",
            "Everything you need is already at your fingertips",
            "You're one decision away from transforming your workflow",
            "The tools you need? You already have them.",
            "You're closer than you think to [desired outcome]"
        ],
        creative_guidance="Affirmations can be direct statements of capability, implied empowerment, or statements that frame action as accessible. You don't always need 'You have everything' - use 'Everything you need', 'You're one decision away', or frame it as proximity to success. The key is making action feel achievable and within reach.",
        interpretation_notes="The [action] placeholder should represent something your audience wants to do but might feel is beyond their reach. It should be specific and achievable. Think about what action your content enables and how you can frame it as something your audience is already capable of doing.",
        what_to_avoid="Avoid always using 'You have everything' - vary encouragement methods. Don't make affirmations that aren't true or actionable. Don't be patronizing. The structure shows the concept of empowerment hooks, not a literal affirmation format.",
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
        detailed_description="This template promises to reveal something hidden, secret, or not commonly known about your topic. It's designed to create intrigue and curiosity by suggesting insider knowledge or overlooked information. Use this when you have genuinely surprising insights, hidden benefits, or commonly overlooked aspects of your topic. The template works best when there's actually something surprising or less-known to reveal. It's particularly effective for audiences who value insider knowledge and enjoy discovering unexpected insights.",
        usage_examples=[
            "What they didn't tell you about automation",
            "The automation secret no one talks about",
            "Here's what the experts won't tell you: automation is easier than you think",
            "The hidden cost of not automating? It's not what you'd expect.",
            "There's a reason successful teams automate differently. Here's why."
        ],
        creative_guidance="Mystery can use 'secrets', 'hidden', 'nobody tells you', 'what they don't tell you', or implied revelations. You don't always need 'What they didn't tell you' - use 'The secret', 'Here's what won't tell you', or frame it as hidden information being revealed. The goal is creating enough intrigue to make them want to discover what's being kept from them.",
        interpretation_notes="The [topic] placeholder should represent your main subject, and the hook promises to reveal something about it that's surprising, hidden, or not commonly known. Think about what surprising truth, hidden benefit, or overlooked aspect of your topic you can reveal. Make sure there's actually something interesting to reveal.",
        what_to_avoid="Avoid always using 'What they didn't tell you' - vary mystery expressions. Don't promise revelations that aren't actually surprising. Don't create false mystery. The structure shows the concept of curiosity-driven hooks, not a literal secret-revelation format.",
    ),
]

# =============================================================================
# VALUE: DATA TEMPLATES
# =============================================================================

VALUE_DATA_TEMPLATES = [
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
        detailed_description="This template presents a percentage statistic that quantifies a trend, behavior, or outcome within a specific group. It's designed to add credibility and concrete evidence to support your message. Use this when you have reliable statistics that illustrate a point about your audience or topic. The template works best when the percentage is surprising, relevant, and from a credible source. It's particularly effective for audiences who value data-driven insights and when you're establishing the scale or prevalence of a trend.",
        usage_examples=[
            "67% of SMEs ignore basic automation – McKinsey 2024",
            "Nearly seven in ten small businesses are missing out on automation",
            "McKinsey research: only 33% of SMEs leverage automation effectively",
            "The data is clear: 67% haven't automated. Here's what that means.",
            "Two-thirds of small businesses are leaving efficiency on the table"
        ],
        creative_guidance="Percentages can be presented directly, flipped to show what's missing, or reframed as ratios. You don't always need '[X]% of [group]' - try 'Nearly seven in ten', 'Only [X]%', or lead with the research source. Make the statistic feel relevant and actionable.",
        interpretation_notes="The [X] placeholder is the percentage number. The [group] placeholder identifies who the statistic applies to. The [action] placeholder describes what the statistic reveals. Think about what percentage would be most relevant and surprising to your audience.",
        what_to_avoid="Avoid always using '[X]% of [group]' format - vary data presentation. Don't use statistics that aren't credible or verifiable. Don't make percentages overly specific if they're estimates. The structure shows the concept of percentage-based data presentation, not a literal formula.",
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
        detailed_description="This template presents an absolute number that quantifies impact, scale, or quantity over time. It's designed to make abstract problems concrete by showing the real-world magnitude of an issue or opportunity. Use this when you want to illustrate scale and make impact tangible through specific numbers. The template works best when the numbers are significant and relatable. It's particularly effective for audiences who think in terms of measurable outcomes and when you're demonstrating the cumulative impact of actions or inactions.",
        usage_examples=[
            "3 hours lost per day per employee",
            "Every employee wastes 15 hours weekly on manual tasks",
            "That's 60 hours of lost productivity monthly, per person",
            "15 hours weekly. Multiplied across your team, that's real money.",
            "The math is simple: 3 hours daily × 20 employees = 60 hours wasted every single day"
        ],
        creative_guidance="Numbers can emphasize individual impact, scale across teams, or accumulation over time. You don't always need '[X] per [time]' - try showing accumulation, multiplication across groups, or reframing the number to show scale. Make the number feel significant and relatable.",
        interpretation_notes="The [X] placeholder is the absolute number. The [entity] placeholder identifies what is being counted. The [time] placeholder shows the timeframe. Think about how to make the number most impactful - individual impact, team scale, or cumulative effect.",
        what_to_avoid="Avoid always using '[X] per [time]' format - vary number framing. Don't use numbers that aren't significant or relatable. Don't make numbers overly precise if they're estimates. The structure shows the concept of absolute number presentation, not a literal formula.",
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
        detailed_description="This template presents a numerical comparison that highlights relative benefit, advantage, or difference between two approaches, methods, or states. It's designed to make superiority or improvement clear through quantifiable comparison. Use this when you want to show how one approach significantly outperforms another. The template works best when the multiplier is impressive and the comparison is meaningful. It's particularly effective for audiences who make decisions based on performance metrics and when you're positioning your solution as clearly superior.",
        usage_examples=[
            "AI generates results 5x faster",
            "Five times the output in half the time",
            "Compared to manual work? Automation delivers fivefold results",
            "5x faster. That's the automation advantage.",
            "The difference is stark: automation delivers 5x the productivity"
        ],
        creative_guidance="Comparisons can use 'x', 'times', multipliers expressed as words, or relative expressions. You don't always need 'X times more' - try 'Xx faster', 'Fivefold', or lead with the result then reveal the comparison. Make the advantage feel significant and meaningful.",
        interpretation_notes="The [X] placeholder is the multiplier number. The comparison shows how much better one approach is than another. Think about what comparison would be most compelling to your audience - speed, output, efficiency, cost savings? Frame it to highlight the biggest advantage.",
        what_to_avoid="Avoid always using 'X times more' - vary comparison language. Don't use multipliers that aren't impressive or credible. Don't make comparisons that aren't meaningful or relevant. The structure shows the concept of comparative advantage, not a literal comparison format.",
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
        detailed_description="This template emphasizes time savings by showing how much time can be reduced or freed up through a specific action. It's designed to make time benefits tangible and motivate action by quantifying the value of saved time. Use this when time savings is a key benefit of your solution. The template works best when the time saved is significant and the action is clear. It's particularly effective for audiences who value time and efficiency, or when you're demonstrating productivity improvements.",
        usage_examples=[
            "Reduce 20h/month in reports",
            "Cut reporting time by 20 hours monthly",
            "Turn 20 hours of report work into 20 minutes",
            "20 hours monthly reclaimed. That's a full workday freed up.",
            "What if those 20 monthly hours went to strategy instead of spreadsheets?"
        ],
        creative_guidance="Time savings can be stated as reduction, transformation (hours to minutes), or freedom gained. You don't always need 'Reduce [time]' - try 'Cut', 'Turn X into Y', or frame it as time reclaimed or repurposed. Make the time savings feel significant and relatable.",
        interpretation_notes="The [time] placeholder represents the amount of time saved. The [action] placeholder shows what achieves the savings. Think about how to make the time most meaningful - is it hours per week? Per month? Could it be reframed as time freed up for higher-value work?",
        what_to_avoid="Avoid always using 'Reduce [time]' - vary time savings expressions. Don't use time savings that aren't significant or believable. Don't be vague about what creates the savings. The structure shows the concept of time value, not a literal reduction formula.",
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
        detailed_description="This template quantifies financial benefits by showing specific dollar amounts that can be saved or earned. It's designed to make economic value tangible and create urgency around financial gains. Use this when financial benefits are a key selling point of your solution. The template works best when the amounts are significant and credible. It's particularly effective for audiences who make decisions based on ROI and financial impact, or when you're demonstrating clear economic advantage.",
        usage_examples=[
            "Save up to $10k/month by automating",
            "$10,000 monthly savings: that's what automation delivers",
            "Cut costs by $10k every month. Here's how.",
            "The math is simple: $10k monthly savings × 12 months = $120k annually",
            "Automation pays for itself. Then saves you $10k every month after."
        ],
        creative_guidance="Financial benefits can be expressed as savings, ROI, cost transformation, or annual accumulation. You don't always need 'Save up to $X' - try leading with the amount, showing annual value, or framing it as ROI. Make the financial impact feel significant and achievable.",
        interpretation_notes="The [amount] placeholder represents the financial value. Think about how to make it most impactful - monthly, annually, per project? Could it be reframed as ROI percentage or payback period? Make the number feel both impressive and believable.",
        what_to_avoid="Avoid always using 'Save up to $X' - vary financial expressions. Don't use amounts that aren't credible or relevant to your audience. Don't be vague about how the savings are achieved. The structure shows the concept of financial value, not a literal savings formula.",
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
        detailed_description="This template presents data or statistics with clear attribution to a credible source, adding authority and trustworthiness to your claims. It's designed to strengthen your message by associating it with respected research, experts, or institutions. Use this when you have data from credible sources that supports your point. The template works best when the source is recognized as authoritative by your audience. It's particularly effective for audiences who value research-backed insights and when you're establishing credibility through third-party validation.",
        usage_examples=[
            "Automation generates 30% more ROI – McKinsey",
            "According to McKinsey, automation boosts ROI by 30%",
            "McKinsey research confirms: 30% ROI increase through automation",
            "The data is in: McKinsey found that automation delivers 30% higher ROI",
            "McKinsey's latest research? 30% ROI boost from automation"
        ],
        creative_guidance="Attribution can come first (source leads), last (source follows), or be integrated naturally into the sentence. You don't always need '[Data] – [Source]' - try 'According to', 'Research confirms', or embed the source naturally. Make the attribution feel credible and relevant.",
        interpretation_notes="The [Data] placeholder contains the statistic or finding. The [Source] placeholder identifies the credible authority. Think about what source would be most respected by your audience - industry research firms, well-known experts, respected publications? Make sure the data and source are genuinely connected.",
        what_to_avoid="Avoid always using '[Data] – [Source]' format - vary attribution styles. Don't use sources your audience won't recognize as authoritative. Don't misattribute or take data out of context. The structure shows the concept of authoritative data presentation, not a literal attribution format.",
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
        detailed_description="This template references visual data (charts, graphs, visualizations) that illustrate trends, relationships, or patterns. It's designed to direct attention to visual elements that support your message. Use this when your slide includes visual data representations and you want to guide the audience to key insights in the visualization. The template works best when the visual data clearly shows a meaningful trend or relationship. It's particularly effective for audiences who respond well to visual information and when you're presenting complex data that benefits from visual representation.",
        usage_examples=[
            "See in the chart how AI adoption grows 5x faster in B2B startups",
            "The data shows: B2B startups adopt AI five times faster",
            "As the visualization reveals, AI adoption accelerates 5x in startups",
            "The chart tells a clear story: startup AI adoption outpaces enterprise by 5x",
            "Visual proof: the graph shows 5x faster AI adoption in B2B startups"
        ],
        creative_guidance="Visual references can be direct ('see chart'), implied ('the data shows'), or descriptive of what the visualization reveals. You don't always need 'See in the chart:' - try 'The data shows', 'As the visualization reveals', or describe what the chart demonstrates. Make the visual reference feel natural and purposeful.",
        interpretation_notes="The [trend or relationship] placeholder describes what the visual data shows. Think about the key insight the chart reveals - is it a growth trend, a comparison, a pattern? Guide the audience to the most important takeaway from the visualization.",
        what_to_avoid="Avoid always using 'See in the chart:' - vary visual reference methods. Don't reference visuals that don't clearly support your message. Don't make the reference feel forced or unnatural. The structure shows the concept of visual data guidance, not a literal chart reference format.",
    ),
]

# =============================================================================
# VALUE: INSIGHT TEMPLATES
# =============================================================================

VALUE_INSIGHT_TEMPLATES = [
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
        detailed_description="This template reveals the deeper principle or essential truth underlying an action or concept. It's designed to elevate understanding from surface-level to strategic insight. Use this when you want to help your audience see beyond the obvious and understand the fundamental purpose or value of something. The template works best when the principle reveals something non-obvious or strategic. It's particularly effective for audiences who value strategic thinking and when you're positioning your solution as having deeper value beyond its immediate benefits.",
        usage_examples=[
            "Automation is about strategy, not just efficiency",
            "The real power of automation? Strategic transformation, not speed",
            "Automation transcends efficiency. It's fundamentally about strategic advantage.",
            "Beyond speed: automation is really about strategic positioning",
            "Here's what automation is truly about: strategic advantage, not just time savings"
        ],
        creative_guidance="Principles can reframe actions, reveal deeper meaning, or contrast surface vs. essence. You don't always need '[X] is about [Y]' - try questions, contrasts ('not X, but Y'), or statements that reveal the deeper truth. The goal is helping readers see the strategic or fundamental value, not just the surface benefit.",
        interpretation_notes="The [Action] placeholder represents the surface-level action or concept. The [principle] placeholder reveals the deeper purpose, strategic value, or fundamental truth. Think about what principle your solution or approach embodies that goes beyond the obvious benefit.",
        what_to_avoid="Avoid always using '[X] is about [Y]' - vary principle statements. Don't state principles that are too obvious or generic. Don't make the principle so abstract it loses meaning. The structure shows the concept of principle revelation, not a literal 'is about' format.",
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
        detailed_description="This template shows the direct cause-and-effect relationship between a problem and its consequences. It's designed to help your audience understand the real cost or impact of inaction or current approaches. Use this when you want to demonstrate why a problem matters by showing its concrete effects. The template works best when the consequence is significant and clearly connected to the problem. It's particularly effective for audiences who need to understand the 'why' behind taking action and when you're building urgency by showing real costs.",
        usage_examples=[
            "Slow decisions generate market loss",
            "When decisions lag, markets move without you",
            "Delayed decisions? They cost you market share every single day",
            "The cost of slow decisions: lost market opportunities",
            "Every day of delay in decision-making costs you competitive advantage"
        ],
        creative_guidance="Consequences can be direct (generates), implied (leads to), or shown through questions or statements that reveal the cost. You don't always need '[X] generates [Y]' - try 'When X happens, Y occurs', 'X costs you Y', or frame it as a question that reveals the consequence. Make the connection between cause and effect clear and meaningful.",
        interpretation_notes="The [Problem] placeholder represents the cause or current situation. The [consequence] placeholder shows the negative outcome or cost. Think about what consequence of the problem would be most relevant and concerning to your audience - is it financial, competitive, time-based, opportunity cost?",
        what_to_avoid="Avoid always using '[X] generates [Y]' - vary cause-effect expressions. Don't make connections that aren't clear or credible. Don't exaggerate consequences unrealistically. The structure shows the concept of cause-effect relationships, not a literal 'generates' format.",
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
        detailed_description="This template challenges conventional wisdom by revealing that a commonly expected prerequisite isn't actually necessary to achieve a desired result. It's designed to break through limiting assumptions and open up new possibilities. Use this when you want to challenge beliefs about what's required for success and show an unexpected path. The template works best when the paradox is genuinely surprising but true. It's particularly effective for audiences who feel constrained by conventional thinking and when you're positioning your solution as accessible despite perceived barriers.",
        usage_examples=[
            "You don't need to be big to scale fast",
            "Size isn't everything. Small teams outpace giants daily.",
            "Forget scale. Speed comes from focus, not size.",
            "The paradox? Small teams often scale faster than large ones.",
            "You might think you need X to achieve Y. The reality? You don't."
        ],
        creative_guidance="Paradoxes can be direct contradictions, reframed assumptions, or reversed expectations. You don't always need 'You don't need [X] to [Y]' - try statements that reverse expectations, contrasts that show the paradox, or questions that challenge assumptions. The goal is making the unexpected truth feel revelatory, not just contrarian.",
        interpretation_notes="The [expected action] placeholder represents what people assume is necessary. The [result] placeholder is what they want to achieve. Think about what assumption prevents your audience from seeing a simpler path, and how you can reveal that assumption is false.",
        what_to_avoid="Avoid always using 'You don't need [X] to [Y]' - vary paradox expressions. Don't create false paradoxes just to be contrarian. Make sure the insight is genuinely true and helpful. The structure shows the concept of expectation-breaking insights, not a literal negation format.",
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
        detailed_description="This template serves to confront and break common misconceptions or false beliefs that your audience may hold. It's designed for moments when you need to challenge assumptions and reveal deeper truths. Use this when your content aims to educate by correcting misunderstandings, especially when those misunderstandings are barriers to adopting your solution or perspective. The template creates a 'before/after' mental shift, moving readers from a false belief to an accurate understanding. This is particularly effective in thought leadership content where you're positioning your brand as an authority that clarifies industry misconceptions.",
        usage_examples=[
            "AI doesn't replace people. It amplifies their capabilities.",
            "Think automation eliminates jobs? It actually creates new roles.",
            "The common belief that AI is only for tech giants? Reality shows it's democratizing innovation.",
            "You might believe automation requires technical expertise. Truth? It's more accessible than ever.",
            "The myth that small teams can't automate? Here's why that's wrong."
        ],
        creative_guidance="Break myths without explicitly labeling them. Use direct contrast or implied questioning. The structure shows the concept of confronting false assumptions, but you don't need to use the words 'Myth:' and 'Reality:' literally. You can state the false belief implicitly through questions, then reveal the truth. Or confront the misconception directly with a statement that shows the actual reality.",
        interpretation_notes="The [false] and [truth] placeholders represent conceptual opposites - the misconception and the actual truth. You can express these through direct statements, questions that challenge beliefs, or narrative that reveals the contradiction. Think about what false belief your audience holds that prevents them from seeing the value of your solution, and how you can reveal the truth in a compelling way.",
        what_to_avoid="Avoid starting with 'Myth:' or 'Reality:' labels. Don't be formulaic. The structure is conceptual, not literal. Don't confront beliefs in a condescending way. Make sure there's actually a real misconception to address, not just stating your opinion as fact.",
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
        detailed_description="This template presents a powerful insight through a memorable quote from a respected authority. It's designed to add weight and memorability to your message by associating it with a recognized expert or thought leader. Use this when you have a compelling quote that encapsulates your insight in a memorable way. The template works best when the quote is genuinely insightful and the source is respected by your audience. It's particularly effective for audiences who value wisdom from recognized experts and when you want to add memorability to your insight.",
        usage_examples=[
            '"Not automating is like running without shoes." – Seth Godin',
            "As Seth Godin puts it: 'Not automating is like running without shoes.'",
            "Seth Godin's insight rings true: automation isn't optional anymore",
            "Seth Godin nailed it: 'Running without automation is like running without shoes.'",
            "A simple truth from Seth Godin: automation is no longer optional"
        ],
        creative_guidance="Quotes can be direct with attribution, integrated into a sentence, paraphrased, or referenced as supporting evidence. You don't always need '[Quote] – [Source]' - try leading with the source, embedding it naturally, or referencing it. The key is making the authority's voice work for your message while keeping it natural.",
        interpretation_notes="The [Strong insight] placeholder contains the memorable quote that captures your point. The [Source] placeholder identifies the respected authority. Think about what quote from a recognized expert would support your insight and resonate with your audience.",
        what_to_avoid="Avoid always using '[Quote] – [Source]' format - vary quote presentation. Don't use quotes from sources your audience won't recognize or respect. Don't misquote or take quotes out of context. The structure shows the concept of authority-backed insights, not a literal quote format.",
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
        detailed_description="This template shows the logical progression or evolution of learning, skill development, or implementation. It's designed to help your audience understand that mastery happens in stages, starting with foundational steps before advancing. Use this when you want to show a learning path or implementation sequence that builds logically. The template works best when the progression is clear and each stage builds on the previous one. It's particularly effective for audiences who are just getting started and need to understand the learning path, or when you're positioning your solution as part of a logical progression.",
        usage_examples=[
            "You start by automating tasks. Then, learn to scale decisions.",
            "First: automate the routine. Next: master the strategic.",
            "Begin with task automation. Evolve to decision automation.",
            "Step one: automate repetitive work. Step two: automate decision-making.",
            "The progression is clear: start with automation, then scale with intelligence"
        ],
        creative_guidance="Progressions can use 'start/then', 'first/next', numbered steps, or narrative flow showing evolution. You don't always need 'You start with X, then Y' - try 'First X, next Y', 'Begin with X, evolve to Y', or show it as a logical sequence. Make the progression feel natural and achievable.",
        interpretation_notes="The [action] placeholder represents the starting point or first step. The [learning] placeholder shows what comes next or what you evolve toward. Think about the logical sequence of learning or implementation - what comes first, what builds on it, and how you progress.",
        what_to_avoid="Avoid always using 'You start with X, then Y' - vary progression expressions. Don't create progressions that don't make logical sense. Don't skip important intermediate steps. The structure shows the concept of progressive learning, not a literal start-then format.",
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
        detailed_description="This template makes a bold, clear statement that positions your view on a market trend, industry reality, or important topic. It's designed to establish thought leadership by taking a definitive stand. Use this when you want to make a strong positioning statement that differentiates your perspective. The template works best when the statement is bold, clear, and substantiated by your content. It's particularly effective for audiences who value clear thinking and when you're establishing yourself as a thought leader with a distinct point of view.",
        usage_examples=[
            "AI is not a competitive advantage. It's a prerequisite to survive.",
            "Let's be clear: AI isn't optional anymore. It's survival.",
            "The harsh truth? AI transformed from advantage to necessity overnight.",
            "Here's the reality: AI went from nice-to-have to must-have",
            "The market has shifted. AI isn't an advantage - it's table stakes."
        ],
        creative_guidance="Statements can be direct, framed as truths, or presented as revelations. You don't always need a simple statement - try contrasts ('not X, but Y'), framing as truth ('Let's be clear'), or positioning as a revelation. Make the statement bold and clear, not wishy-washy.",
        interpretation_notes="The [Statement] placeholder should be a strong, clear position on your topic. Think about what bold statement would differentiate your perspective and resonate with your audience. It should be substantial enough to matter but clear enough to be understood immediately.",
        what_to_avoid="Avoid generic weak statements - make bold, clear positions. Don't make statements that are so obvious they're meaningless. Don't take positions that aren't substantiated by your content. The structure shows the concept of strong positioning, but the statement itself should be meaningful and differentiated.",
    ),
]

# =============================================================================
# VALUE: SOLUTION TEMPLATES
# =============================================================================

VALUE_SOLUTION_TEMPLATES = [
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
        detailed_description="This template presents a clear sequence of steps that leads to a desired outcome. It's designed to make complex processes feel manageable by breaking them into discrete, actionable steps. Use this when you want to provide a practical, step-by-step guide that your audience can follow. The template works best when the steps are clear, logical, and build on each other. It's particularly effective for audiences who learn by doing and when you're providing actionable frameworks that solve a specific problem.",
        usage_examples=[
            "1. List manual processes. 2. Use AI. 3. Measure results.",
            "Start by listing processes. Automate with AI. Track your results.",
            "First: identify what's manual. Second: introduce AI. Third: measure impact.",
            "Begin by mapping your processes. Then automate. Finally, optimize based on results.",
            "Step one: identify bottlenecks. Step two: apply automation. Step three: track improvements."
        ],
        creative_guidance="Steps can be numbered (1. 2. 3.), sequential words (First, Second, Third), or narrative flow showing progression. You don't always need '1. 2. 3.' - try 'Start by, Then, Finally', 'First, Next, Last', or show it as a natural progression. Make the sequence clear and actionable.",
        interpretation_notes="The [Step] placeholders represent discrete actions that build on each other. Think about the logical sequence - what comes first, what follows, what completes the process? Each step should be clear and actionable on its own while building toward the desired outcome.",
        what_to_avoid="Avoid always using '1. 2. 3.' format - vary sequential expressions. Don't create steps that don't follow logically. Don't make steps too vague to be actionable. The structure shows the concept of sequential guidance, not a literal numbered format.",
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
        detailed_description="This template presents a quick, practical list of actions without extensive explanation. It's designed to provide a simple, scannable framework that your audience can quickly grasp and remember. Use this when you want to give a concise action list that doesn't require detailed explanation. The template works best when the actions are clear and self-explanatory. It's particularly effective for audiences who prefer quick, actionable takeaways and when you're providing a simple framework or checklist.",
        usage_examples=[
            "- Delegate repetitive tasks - Apply AI - Evaluate results",
            "Delegate. Automate. Evaluate. That's the framework.",
            "Three moves: delegate repetition, apply automation, evaluate outcomes",
            "Quick wins: delegate, automate, optimize",
            "The framework? Simple: delegate, automate, measure"
        ],
        creative_guidance="Lists can use dashes, periods, colons, or parallel structure. You don't always need '- X - Y - Z' - try parallel statements with periods, numbered items, or framed as a simple framework. Make the list scannable and memorable.",
        interpretation_notes="Each [Short action] placeholder represents a concise, actionable step. Think about the essential actions your audience needs to take - what are the core moves that will achieve the outcome? Keep actions short, clear, and memorable.",
        what_to_avoid="Avoid always using '- X - Y - Z' format - vary list structures. Don't make actions too long or complex for a list. Don't create lists that don't form a coherent framework. The structure shows the concept of quick action lists, not a literal dash format.",
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
        detailed_description="This template presents a simple, memorable formula that shows how different factors combine to create a desired result. It's designed to make complex relationships feel simple and replicable. Use this when you want to show that success comes from combining specific elements. The template works best when the formula is simple, memorable, and captures an essential truth. It's particularly effective for audiences who appreciate analytical frameworks and when you're providing a memorable model they can apply.",
        usage_examples=[
            "Productivity = Automation + Clear leadership",
            "Productivity emerges from automation plus leadership clarity",
            "The equation: combine automation with leadership, get productivity",
            "Productivity comes from two factors: automation and clear direction",
            "Here's the formula: automation plus leadership equals productivity"
        ],
        creative_guidance="Formulas can use equals signs, words like 'plus' or 'and', or narrative equations. You don't always need '[X] = [Y] + [Z]' - try 'X comes from Y and Z', 'Combine Y and Z, get X', or frame it as the equation. Make the formula feel simple and memorable.",
        interpretation_notes="The [Result] placeholder is the desired outcome. The [Factor] placeholders are the essential ingredients. Think about what elements combine to create success - what are the key factors that, together, produce the result? Keep the formula simple and meaningful.",
        what_to_avoid="Avoid always using '[X] = [Y] + [Z]' format - vary formula expressions. Don't make formulas too complex. Don't create formulas with factors that don't clearly combine to create the result. The structure shows the concept of formulaic thinking, not a literal equation format.",
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
        detailed_description="This template presents a memorable framework with an acronym that makes the model easy to remember and apply. It's designed to teach a systematic approach that your audience can reference and use. Use this when you want to provide a structured model or framework that encapsulates your approach. The template works best when the acronym is memorable and the components clearly define the framework. It's particularly effective for audiences who learn through structured models and when you're providing a reusable framework they can apply to different situations.",
        usage_examples=[
            "PAR: Process, Automation, Results",
            "The PAR framework: Process first, Automation next, Results follow",
            "Process → Automation → Results. Remember it as PAR.",
            "PAR stands for Process, Automation, Results - your three-step path to efficiency",
            "The framework? PAR. Process. Automation. Results. That's the sequence."
        ],
        creative_guidance="Frameworks can be acronyms with definitions, spelled out as a sequence, or shown as flow with the acronym referenced. You don't always need '[ACRONYM]: X, Y, Z' - try showing the sequence then revealing the acronym, or spelling out the framework then identifying it. Make the framework memorable and applicable.",
        interpretation_notes="The [Acronym] placeholder should spell out to something memorable. The [Definition] placeholders are the components of the framework. Think about what systematic approach you're teaching - can it be encapsulated in a memorable acronym? What are the essential components?",
        what_to_avoid="Avoid always using '[ACRONYM]: X, Y, Z' format - vary framework presentation. Don't force acronyms that aren't memorable or meaningful. Don't create frameworks with components that don't form a coherent system. The structure shows the concept of systematic frameworks, not a literal acronym format.",
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
        detailed_description="This template presents a visual checklist that makes it easy to track progress through sequential actions. It's designed to provide a clear, visual guide that feels actionable and completable. Use this when you want to give your audience a checklist they can mentally or literally check off. The template works best when the actions are sequential and clear. It's particularly effective for audiences who respond well to visual organization and when you're providing a step-by-step process they can follow.",
        usage_examples=[
            "☑️ Map tasks ☑️ Choose tool ☑️ Implement",
            "Map your tasks. Choose your tool. Implement and iterate.",
            "Three checks: map tasks, choose tools, implement solutions",
            "Checklist: map, choose, implement, optimize",
            "Your action items: map tasks ✓ choose tool ✓ implement ✓"
        ],
        creative_guidance="Checklists can use visual markers (☑️), sequential structure, or narrative format. You don't always need checkmark emoji - try parallel statements, numbered checklist, or framed as action items. Though visual markers work well for actual visual slides. Make the checklist feel actionable and completable.",
        interpretation_notes="Each [Action] placeholder represents a task to be completed. Think about what sequential actions your audience needs to take - what can they check off as they progress? Keep actions clear and measurable.",
        what_to_avoid="Avoid always using checkmark emoji - vary checklist presentation (though emojis work for visual slides). Don't make checklists too long or complex. Don't create items that aren't clearly actionable. The structure shows the concept of sequential checklists, not a literal emoji format.",
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
        detailed_description="This template addresses a common obstacle or blocker that prevents your audience from moving forward, and provides a practical solution. It's designed to remove barriers and show that there's always a path forward. Use this when you want to help your audience overcome perceived barriers to adopting your solution. The template works best when the obstacle is real and common, and the solution is genuinely practical. It's particularly effective for audiences who feel stuck or face common constraints, and when you're positioning your solution as accessible despite obstacles.",
        usage_examples=[
            "If you don't have a tech team, use AI with pre-ready agents",
            "No tech team? Pre-built AI agents solve that.",
            "Tech team shortage? Here's your workaround: pre-ready AI agents",
            "Don't have technical resources? Pre-built solutions bridge that gap.",
            "The obstacle: no tech expertise. The solution: pre-ready automation tools."
        ],
        creative_guidance="Obstacles can be addressed with if/then, questions that reveal solutions, or problem/workaround framing. You don't always need 'If [X], then [Y]' - try questions that identify the problem then provide the solution, or frame it as obstacle/workaround. Make the solution feel accessible and practical.",
        interpretation_notes="The [problem] placeholder represents the common blocker your audience faces. The [practical solution] placeholder shows how to overcome it. Think about what obstacles prevent your audience from adopting your solution, and what practical workaround you can offer.",
        what_to_avoid="Avoid always using 'If [X], then [Y]' format - vary obstacle-resolution expressions. Don't address obstacles that aren't real or common. Don't offer solutions that aren't practical or accessible. The structure shows the concept of obstacle-solving, not a literal if-then format.",
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
        detailed_description="This template helps your audience make decisions by providing clear criteria for choosing between options. It's designed to guide decision-making by connecting choices to desired outcomes. Use this when you want to help your audience understand which option fits their specific situation or goals. The template works best when the criteria are clear and the options are distinct. It's particularly effective for audiences who are evaluating options and need guidance on decision-making, or when you're helping them choose the right approach for their context.",
        usage_examples=[
            "Choose local AI if seeking data control. Cloud, if seeking scale.",
            "Want data control? Go local. Need scale? Cloud is your answer.",
            "Local AI = control. Cloud AI = scale. Choose your priority.",
            "Data control matters? Choose local. Scale is key? Go cloud.",
            "The decision comes down to priorities: local for control, cloud for scale"
        ],
        creative_guidance="Decisions can be choice-based, question-answer pairs, or comparison-based. You don't always need 'Choose [X] if [Y]' - try questions that reveal the criteria, comparisons that show trade-offs, or priority-based guidance. Make the decision criteria clear and actionable.",
        interpretation_notes="The [X] placeholder is the option or choice. The [Y] placeholder is the criterion or goal. Think about what decision your audience is facing - what are the options, what criteria should guide the choice, and which option fits which situation?",
        what_to_avoid="Avoid always using 'Choose [X] if [Y]' format - vary decision guidance. Don't create false dichotomies. Don't make criteria that aren't clear or meaningful. The structure shows the concept of criteria-based decision-making, not a literal choice format.",
    ),
]

# =============================================================================
# VALUE: EXAMPLE TEMPLATES
# =============================================================================

VALUE_EXAMPLE_TEMPLATES = [
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
        detailed_description="This template presents a real-world case study with quantified results that demonstrate the impact of your solution. It's designed to provide social proof and concrete evidence through a recognizable company's success story. Use this when you have actual case studies or examples with measurable results that support your message. The template works best when the company is recognizable and the results are impressive. It's particularly effective for audiences who value proof through real examples and when you're establishing credibility through demonstrated success.",
        usage_examples=[
            "Shopify increased checkout speed 40% through AI optimization",
            "Shopify's AI move? 40% faster checkouts, same team.",
            "Here's what happened when Shopify optimized with AI: 40% speed boost",
            "Shopify saw checkout speed jump 40% after implementing AI automation",
            "The result when Shopify applied AI? 40% faster checkout, zero additional headcount."
        ],
        creative_guidance="Cases can be result-focused (lead with the number), transformation-focused (show the change), or narrative-focused (tell the story). You don't always need '[Company] had [result] with [action]' - try leading with the result, showing the transformation, or telling the story. Make the case feel real and relatable.",
        interpretation_notes="The [Company] placeholder should be a recognizable brand. The [result] placeholder should be a specific, measurable outcome. The [applied action] placeholder shows what they did. Think about what company story would be most relevant and impressive to your audience.",
        what_to_avoid="Avoid always using '[Company] had [result] with [action]' format - vary case presentation. Don't use companies that aren't recognizable or relevant. Don't use results that aren't credible or impressive. The structure shows the concept of proof through examples, not a literal case format.",
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
        detailed_description="This template invites your audience to imagine an ideal scenario or positive outcome that your solution enables. It's designed to create engagement by helping them visualize a better future. Use this when you want to help your audience see the possibilities and motivate them to take action by making the outcome tangible. The template works best when the scenario is specific, desirable, and feels achievable. It's particularly effective for audiences who respond to vision and possibility, or when you're helping them see what's possible.",
        usage_examples=[
            "Imagine reducing meetings by half with AI",
            "Picture this: meetings cut in half. What would you do with that time?",
            "What if your meeting load dropped 50%? AI makes it possible.",
            "Visualize this: half the meetings, double the output",
            "See yourself with 50% fewer meetings. That's the AI advantage."
        ],
        creative_guidance="Scenarios can use 'imagine', 'picture', 'what if', 'visualize', or direct visualization. You don't always need 'Imagine that you' - try 'Picture this', 'What if', 'Visualize', or lead with the scenario. Make the ideal outcome feel vivid and achievable.",
        interpretation_notes="The [ideal action / positive context] placeholder should represent a desirable, specific scenario your audience can visualize. Think about what ideal outcome your solution enables that would be most compelling - is it time saved, stress reduced, productivity increased? Make it concrete and desirable.",
        what_to_avoid="Avoid always using 'Imagine that you' - vary scenario introductions. Don't create scenarios that are too abstract or unrealistic. Don't make the outcome feel unattainable. The structure shows the concept of possibility visualization, not a literal imagination format.",
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
        detailed_description="This template tells a relatable story about a person who used your solution and achieved a specific result. It's designed to humanize your message and make it relatable through personal narrative. Use this when you want to make your solution feel accessible and relatable by showing how a real person benefited. The template works best when the person feels like someone your audience can relate to and the result is meaningful. It's particularly effective for audiences who respond to human stories and when you're making your solution feel accessible and personal.",
        usage_examples=[
            "Sarah automated her weekly reports and eliminated all deadline stress",
            "Sarah's automation move? Weekly reports handled, stress eliminated.",
            "Meet Sarah. She automated one weekly report. Result? Zero deadline stress.",
            "Sarah used to stress over reports. Now? Automation handles them. Stress? Gone.",
            "One report automation. Zero deadline panic. That's Sarah's story."
        ],
        creative_guidance="Anecdotes can be narrative (tell the story), result-focused (show the outcome), or story-driven (humanize the transformation). You don't always need '[Person] used X and Y' - try introducing the person, showing the transformation, or telling it as a before/after story. Make the story feel relatable and human.",
        interpretation_notes="The [Person] placeholder should be a relatable name or role. The [solution] placeholder shows what they used. The [observed result] placeholder shows the meaningful outcome. Think about what person your audience can relate to and what result would be most meaningful to them.",
        what_to_avoid="Avoid always using '[Person] used X and Y' format - vary storytelling. Don't use names that feel fake or generic. Don't make results that aren't meaningful or relatable. The structure shows the concept of human stories, not a literal anecdote format.",
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
        detailed_description="This template shows a clear contrast between two companies that made different decisions, highlighting the consequences of their choices. It's designed to demonstrate the value of taking action by showing what happens when companies do versus don't adopt your solution. Use this when you want to illustrate the opportunity cost of inaction through real-world comparison. The template works best when the companies are recognizable and the contrast is stark. It's particularly effective for audiences who need to see the consequences of decisions and when you're building urgency by showing competitive advantage.",
        usage_examples=[
            "Amazon invested in warehouse AI early, competitors didn't. Result: 50% faster fulfillment.",
            "Early AI adoption: Amazon's move. Competitors waited. Outcome? 50% faster delivery advantage.",
            "Amazon moved early on warehouse AI. Competitors hesitated. The gap? 50% faster fulfillment.",
            "While competitors debated, Amazon automated. The result? 50% fulfillment speed advantage.",
            "Amazon's early AI bet paid off: 50% faster than competitors who waited."
        ],
        creative_guidance="Comparisons can use did/didn't, action/inaction, or contrast with varied result presentation. You don't always need 'X did Y, Z didn't. Result?' - try showing the decision contrast, then revealing the outcome, or framing it as early vs. late adoption. Make the contrast and consequences clear.",
        interpretation_notes="The [Company A] placeholder is the one that took action. [Company B] is the one that didn't. The [X] placeholder is the action taken. The [Y] placeholder shows the result or competitive advantage. Think about what comparison would be most relevant and instructive to your audience.",
        what_to_avoid="Avoid always using 'X did Y, Z didn't. Result?' format - vary comparison structures. Don't use companies that aren't relevant or recognizable. Don't create false comparisons. The structure shows the concept of decision consequences, not a literal comparison format.",
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
        detailed_description="This template shows how a small, specific change created a meaningful impact. It's designed to demonstrate that significant results can come from simple actions, making transformation feel achievable. Use this when you want to show that big changes start small and motivate action by making it feel doable. The template works best when the action is simple and the impact is surprising. It's particularly effective for audiences who feel overwhelmed by big changes and when you're positioning your solution as something simple that delivers outsized results.",
        usage_examples=[
            "Finance team automated one report and saved 9h/week",
            "One report automation. 9 hours saved weekly. The finance team's win.",
            "Finance team's small move: automate one report. Big result: 9 hours weekly freed up.",
            "What changed? One report. What happened? 9 hours weekly reclaimed.",
            "Small action: automate one report. Big impact: 9 hours weekly back to the team."
        ],
        creative_guidance="Microcases can emphasize the small action, the big result, or the transformation. You don't always need '[Team] changed X and Y' - try leading with the small change, showing the impact, or framing it as small action/big result. Make the simplicity-to-impact ratio feel surprising and motivating.",
        interpretation_notes="The [Team/person] placeholder should be relatable. The [action] placeholder should be a small, simple change. The [symbolic result] placeholder shows the meaningful impact. Think about what small action would be most relatable and what impact would be most impressive - make the ratio surprising.",
        what_to_avoid="Avoid always using '[Team] changed X and Y' format - vary microcase presentation. Don't make actions that aren't actually simple or achievable. Don't make results that aren't meaningful or impressive. The structure shows the concept of simple actions with big results, not a literal change format.",
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
        detailed_description="This template invites your audience to follow you to receive ongoing value and content. It's designed to grow your audience by promising continuous value delivery. Use this when you want to build a long-term relationship with your audience and establish yourself as a consistent source of value. The template works best when you can clearly articulate what value they'll receive. It's particularly effective for audiences who are engaged with your content and want more, or when you're positioning yourself as an ongoing resource.",
        usage_examples=[
            "Follow for weekly insights on AI implementation",
            "Weekly AI insights? Hit follow.",
            "Want weekly implementation tips? Follow along.",
            "Get weekly AI insights delivered to your feed. Follow for more.",
            "Join 10k+ professionals getting weekly automation tips. Follow to stay updated."
        ],
        creative_guidance="Follow CTAs can be direct invitations, question-based prompts, or value-focused statements. You don't always need 'Follow for [X]' - try questions, value statements, or social proof that makes following feel valuable. Make the follow feel worthwhile and low-pressure.",
        interpretation_notes="The [value promise] placeholder should clearly communicate what they'll get by following. Think about what ongoing value you can deliver - weekly tips, insights, updates? Make the promise specific and valuable.",
        what_to_avoid="Avoid always using 'Follow for [X]' - vary follow invitations. Don't make promises you can't deliver. Don't be vague about what value they'll receive. The structure shows the concept of audience-building CTAs, not a literal follow format.",
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
        detailed_description="This template invites your audience to engage by commenting, sharing their experience, or responding to a question. It's designed to create conversation and community engagement around your content. Use this when you want to generate discussion and learn from your audience. The template works best when the question or invite is specific and easy to answer. It's particularly effective for audiences who want to participate and share, or when you're building community around your content.",
        usage_examples=[
            "Which of these mistakes have you made? Comment below 👇",
            "What's your automation story? Drop it in the comments.",
            "Been there? Done that? Share your experience below.",
            "Have you tried this approach? Tell us about your results in the comments.",
            "What's your take? Join the conversation below."
        ],
        creative_guidance="Comment CTAs can be questions that invite sharing, invitations to participate, or prompts that make commenting feel easy and valuable. You don't always need a generic question - try specific prompts, invitations to share experiences, or questions that relate directly to your content. Make commenting feel valuable and easy.",
        interpretation_notes="The [Question or invite to share] placeholder should be specific and engaging. Think about what question would get your audience to share their experience, opinion, or story. Make it easy to answer and valuable to participate in.",
        what_to_avoid="Avoid generic 'What do you think?' - make specific, engaging asks. Don't ask questions that are too difficult to answer. Don't make the CTA feel forced. The structure shows the concept of engagement CTAs, but the question itself should be compelling.",
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
        detailed_description="This template encourages your audience to save your content for future reference, increasing your reach through platform algorithms that favor saved content. It's designed to position your content as valuable reference material they'll want to return to. Use this when your content provides actionable information or frameworks that have lasting value. The template works best when you can point to a specific future use case. It's particularly effective for audiences who value practical resources and when you're providing content they'll want to reference later.",
        usage_examples=[
            "Save this before your next AI project",
            "Bookmark this for your next automation sprint",
            "You'll want this later. Save it now.",
            "Save this framework for when you're ready to automate",
            "Bookmark this guide. You'll thank yourself later."
        ],
        creative_guidance="Save CTAs can be direct instructions, future-focused statements, or benefit-oriented invitations. You don't always need 'Save this for [X]' - try 'Bookmark this', 'You'll want this later', or frame it as a valuable resource. Make saving feel practical and valuable.",
        interpretation_notes="The [future use case] placeholder should identify when they'll find your content useful. Think about what future moment your content will be valuable - before a project, when they're ready to implement, during a specific situation? Make the future value clear.",
        what_to_avoid="Avoid always using 'Save this for [X]' - vary save invitations. Don't make the future use case too vague. Don't overpromise on future value. The structure shows the concept of reference CTAs, not a literal save format.",
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
        detailed_description="This template encourages your audience to share your content by tagging someone who would benefit from it. It's designed to increase reach through social sharing and create a sense of helpfulness. Use this when your content would genuinely help specific people your audience knows. The template works best when you can identify who would benefit. It's particularly effective for audiences who want to help others and when you're creating shareable content that has clear beneficiaries.",
        usage_examples=[
            "Tag a founder who is drowning in manual work",
            "Know someone stuck in manual processes? Tag them.",
            "This one's for your overwhelmed teammate. Share it forward.",
            "Tag a colleague who needs this framework",
            "Know someone struggling with this? Pass it along. Tag them below."
        ],
        creative_guidance="Share CTAs can be direct tagging invitations, implied sharing prompts, or benefit-focused invitations to help others. You don't always need 'Tag someone who [X]' - try 'Know someone who', 'This one's for', or frame it as helping someone specific. Make sharing feel like helping, not just sharing.",
        interpretation_notes="The [needs this] placeholder should identify who would benefit. Think about what person or role would find your content most valuable - founders, teammates, colleagues, friends in a specific situation? Make it easy for your audience to think of someone to tag.",
        what_to_avoid="Avoid always using 'Tag someone who [X]' - vary share prompts. Don't make the beneficiary too vague. Don't create share CTAs for content that isn't actually shareable. The structure shows the concept of viral CTAs, not a literal tag format.",
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
        detailed_description="This template invites your audience to send you a direct message, creating a personal connection and potentially leading to deeper engagement or conversion. It's designed to make you accessible and create a one-on-one relationship opportunity. Use this when you want to offer something valuable through DMs or create personal connections with your audience. The template works best when you have something specific to offer or want to start a conversation. It's particularly effective for audiences who value personal connection and when you're building relationships that can lead to business opportunities.",
        usage_examples=[
            "DM me 'framework' and I'll send the complete guide",
            "Want the full guide? DM 'framework' and it's yours.",
            "Slide into my DMs with 'framework' for the complete toolkit.",
            "DM me for the full automation checklist",
            "Got questions? DM me. I respond to everyone."
        ],
        creative_guidance="DM CTAs can be direct instructions, question-answer formats, or conversational invitations. You don't always need a specific keyword - try offering value, inviting questions, or making yourself accessible. Make the DM feel valuable and the connection feel personal.",
        interpretation_notes="The [Personal invite] placeholder should feel personal and valuable. Think about what you can offer through DMs - a resource, personal help, answers to questions? Make the value clear and the invitation feel genuine.",
        what_to_avoid="Avoid generic 'DM me' - make specific, valuable offers. Don't promise something you can't deliver. Don't make the invitation feel transactional. The structure shows the concept of personal CTAs, but the offer should be genuine and valuable.",
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
        detailed_description="This template drives traffic to an external resource by inviting your audience to access something valuable. It's designed to move your audience from the platform to your website, landing page, or other resource. Use this when you want to drive traffic to a specific resource or capture leads. The template works best when the resource is clearly valuable. It's particularly effective for audiences who want more detailed information and when you're converting social engagement into website traffic or leads.",
        usage_examples=[
            "Download the complete checklist (link in bio)",
            "The full checklist? Link in bio.",
            "Complete checklist available. Check the link in bio.",
            "Get the full automation framework: link in bio",
            "Want the complete guide? Tap the link in bio."
        ],
        creative_guidance="Link CTAs can be direct instructions, implied invitations, or benefit-focused statements. You don't always need 'Access [X] at [Y]' - try 'Link in bio', 'Get the full [resource]', or frame it as accessing valuable content. Make the link feel worth clicking.",
        interpretation_notes="The [resource] placeholder should clearly communicate what they'll get. The [destination] placeholder can be 'link in bio', a specific URL, or platform-appropriate link reference. Think about what resource would be most valuable to your audience.",
        what_to_avoid="Avoid always using 'Access [X] at [Y]' - vary link invitations. Don't promise resources you don't deliver. Don't make the link destination unclear. The structure shows the concept of traffic-driving CTAs, not a literal access format.",
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
        detailed_description="This template offers two complementary actions your audience can take, increasing overall engagement by giving them options. It's designed to maximize engagement by combining actions that work well together. Use this when you want to encourage multiple types of engagement and give your audience flexibility in how they participate. The template works best when the actions complement each other. It's particularly effective for audiences who want options and when you're trying to maximize various engagement metrics.",
        usage_examples=[
            "Save this post + share with your team",
            "Save it. Share it. Your team will thank you.",
            "Two clicks: save for later, share for your team.",
            "Save this framework and share it with someone who needs it",
            "Do both: save for reference and tag a colleague who'd benefit"
        ],
        creative_guidance="Double actions can use '+', sequential structure, or parallel action framing. You don't always need '[X] + [Y]' - try sequential statements, 'Do both', or frame them as complementary actions. Make both actions feel valuable and easy.",
        interpretation_notes="The [Action 1] and [Action 2] placeholders should be complementary actions that increase engagement. Think about what actions work well together - save and share? Comment and tag? Follow and DM? Make the combination feel natural and valuable.",
        what_to_avoid="Avoid always using '[X] + [Y]' format - vary multiple action prompts. Don't combine actions that don't make sense together. Don't make the CTA feel overwhelming with too many actions. The structure shows the concept of multiple engagement paths, not a literal plus format.",
    ),
]
