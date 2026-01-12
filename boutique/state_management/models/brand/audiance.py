"""
Brand audience profiles module

Detailed audience profiles based on Plano de Branding 360º.

Contains:
- C-Level profile (PMEs R$10-100Mi)
- Founder profile (Seed-Series B startups)
- Developer profile (Independent devs)

Location: src/brand/audience.py
"""

from typing import Dict, Any, Optional, List


# =============================================================================
# AUDIENCE PROFILES
# =============================================================================

AUDIENCE_PROFILES = {
    "c_level": {
        "name": "Decisor C-Level",
        "description": "C-Level executives from SMEs (R$10-100Mi revenue)",
        
        # Where to find them (from brand strategy)
        "platforms": ["linkedin", "email", "workshops"],
        "formats": ["carousel", "single_image", "video_short", "pdf", "newsletter"],
        
        # Content focus
        "content_focus": [
            "roi_rapido",              # ROI Rápido
            "eficiencia",              # Eficiência
            "mitigacao_risco",         # Mitigação de Risco
            "lideranca_mercado"        # Liderança no Mercado
        ],
        
        # Communication style
        "tone": "professional",
        "formality": "formal",
        "vocabulary": "sophisticated",
        "personality_traits": [
            "authoritative",
            "strategic",
            "data_driven",
            "results_oriented",
            "pragmatic"
        ],
        
        # Pain points (from brand strategy)
        "pain_points": [
            "compressed_margins",          # Margens Comprimidas
            "operational_inefficiency",    # Ineficiência Operacional
            "competitive_pressure",        # Pressão Competitiva
            "technology_adoption_risk",    # Risco de Adoção de Tecnologia
            "wasted_budgets",             # Orçamentos Desperdiçados
            "lack_of_visibility"          # Falta de Visibilidade
        ],
        
        # Desires/goals
        "desires": [
            "fast_roi",                   # ROI Rápido
            "opex_reduction",             # Redução de OPEX
            "competitive_advantage",      # Vantagem Competitiva
            "proven_solutions",           # Soluções Comprovadas
            "market_leadership",          # Liderança de Mercado
            "efficiency_gains"            # Ganhos de Eficiência
        ],
        
        # Brand values alignment
        "brand_values": ["go_deep_or_go_home", "open_source"],
        
        # KPIs (from brand strategy)
        "success_metrics": {
            "linkedin_followers": 2000,
            "ssi_score": 70,
            "engagement_rate": 0.03,
            "lead_quality": "high"
        }
    },
    
    "founder": {
        "name": "Fundador Visionário",
        "description": "Visionary founders from Seed to Series B startups",
        
        # Where to find them
        "platforms": [
            "linkedin",
            "instagram",
            "twitter",
            "product_hunt",
            "discord"
        ],
        "formats": [
            "carousel",
            "threads",
            "reels",
            "playbook_pdf",
            "podcast"
        ],
        
        # Content focus
        "content_focus": [
            "crescimento_exponencial",    # Crescimento Exponencial
            "pioneirismo",                # Pioneirismo
            "cultura_builder"             # Cultura Builder
        ],
        
        # Communication style
        "tone": "empowering",
        "formality": "casual",
        "vocabulary": "moderate",
        "personality_traits": [
            "visionary",
            "bold",
            "innovative",
            "resilient",
            "community_oriented"
        ],
        
        # Pain points
        "pain_points": [
            "scaling_without_resources",   # Escalar sem Recursos
            "building_without_funding",    # Construir sem Funding
            "finding_technical_edge",      # Encontrar Edge Técnico
            "team_building",               # Construção de Equipe
            "market_validation",           # Validação de Mercado
            "competitive_differentiation"  # Diferenciação Competitiva
        ],
        
        # Desires/goals
        "desires": [
            "exponential_growth",          # Crescimento Exponencial
            "competitive_edge",            # Edge Competitivo
            "community_support",           # Suporte da Comunidade
            "equity_partnerships",         # Equity & Parcerias
            "pioneering_innovation",       # Inovação Pioneira
            "builder_culture"              # Cultura de Construção
        ],
        
        # Brand values alignment
        "brand_values": [
            "go_deep_or_go_home",
            "open_source",
            "community_collaboration",
            "pioneer_new_world"
        ],
        
        # KPIs
        "success_metrics": {
            "instagram_followers": 1000,
            "twitter_followers": 1000,
            "engagement_rate": 0.05,
            "community_size": 300
        }
    },
    
    "developer": {
        "name": "DEV Forjador",
        "description": "Independent developers and OSS contributors",
        
        # Where to find them
        "platforms": [
            "github",
            "discord",
            "youtube",
            "twitch",
            "blog"
        ],
        "formats": [
            "repo_readme",
            "video_tutorial",
            "live_coding",
            "technical_blog",
            "gist"
        ],
        
        # Content focus
        "content_focus": [
            "mao_na_massa",              # Mão na Massa
            "code_deep_dive",            # Code Deep Dive
            "contribuicoes_comunidade"   # Contribuições para Comunidade
        ],
        
        # Communication style
        "tone": "technical",
        "formality": "casual",
        "vocabulary": "technical",
        "personality_traits": [
            "pragmatic",
            "detail_oriented",
            "community_focused",
            "hands_on",
            "analytical"
        ],
        
        # Pain points
        "pain_points": [
            "working_in_isolation",        # Trabalhar Isolado
            "lack_of_resources",           # Falta de Recursos
            "keeping_up_with_tech",        # Acompanhar Tecnologia
            "finding_projects",            # Encontrar Projetos
            "monetization_challenges",     # Desafios de Monetização
            "documentation_burden"         # Carga de Documentação
        ],
        
        # Desires/goals
        "desires": [
            "hands_on_experience",         # Experiência Hands-On
            "community_recognition",       # Reconhecimento da Comunidade
            "open_source_contributions",   # Contribuições Open Source
            "technical_mastery",           # Maestria Técnica
            "collaborative_projects",      # Projetos Colaborativos
            "learning_opportunities"       # Oportunidades de Aprendizado
        ],
        
        # Brand values alignment
        "brand_values": [
            "go_deep_or_go_home",
            "open_source",
            "community_collaboration"
        ],
        
        # KPIs
        "success_metrics": {
            "github_stars": 50,
            "forks": 20,
            "prs_accepted": 10,
            "community_engagement": "high"
        }
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_audience_profile(persona: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed audience profile for persona.
    
    Args:
        persona: Persona string (can be partial match)
    
    Returns:
        Audience profile dict or None if not found
    """
    persona_lower = persona.lower()
    
    # Match keywords to audience types
    if any(x in persona_lower for x in [
        "c-level", "executive", "decisor", "ceo", "cto", "cfo"
    ]):
        return AUDIENCE_PROFILES["c_level"]
    
    elif any(x in persona_lower for x in [
        "founder", "fundador", "visionário", "startup", "empreendedor"
    ]):
        return AUDIENCE_PROFILES["founder"]
    
    elif any(x in persona_lower for x in [
        "developer", "dev", "desenvolvedor", "forjador", "engineer"
    ]):
        return AUDIENCE_PROFILES["developer"]
    
    return None


def enrich_idea_with_audience(
    idea: Dict[str, Any],
    profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Enrich an idea with audience profile data.
    
    Merges LLM-generated idea attributes with brand audience profile,
    ensuring brand consistency.
    
    Args:
        idea: Idea dict from LLM
        profile: Audience profile dict
    
    Returns:
        Enriched idea dict
    """
    enriched = idea.copy()
    
    # Merge personality traits (keep unique)
    existing_traits = set(idea.get("personality_traits", []))
    profile_traits = set(profile.get("personality_traits", []))
    enriched["personality_traits"] = list(existing_traits | profile_traits)[:5]
    
    # Merge pain points (keep unique)
    existing_pains = set(idea.get("pain_points", []))
    profile_pains = set(profile.get("pain_points", []))
    enriched["pain_points"] = list(existing_pains | profile_pains)[:5]
    
    # Merge desires (keep unique)
    existing_desires = set(idea.get("desires", []))
    profile_desires = set(profile.get("desires", []))
    enriched["desires"] = list(existing_desires | profile_desires)[:5]
    
    # Override vocabulary/formality with profile defaults if not specified
    if not idea.get("vocabulary_level"):
        enriched["vocabulary_level"] = profile.get("vocabulary", "moderate")
    
    if not idea.get("formality"):
        enriched["formality"] = profile.get("formality", "neutral")
    
    # Add brand values
    enriched["brand_values"] = profile.get("brand_values", [])
    
    return enriched


def get_audience_from_platform(platform: str) -> str:
    """
    Infer primary audience type from platform.
    
    Based on brand strategy platform mapping.
    
    Args:
        platform: Social media platform
    
    Returns:
        Audience type string ("c_level", "founder", or "developer")
    """
    platform_lower = platform.lower()
    
    platform_mapping = {
        "linkedin": "c_level",        # Authority & B2B Leads
        "instagram": "founder",        # Community & Awareness
        "twitter": "founder",          # Viral Reach
        "github": "developer",         # OSS Credibility
        "discord": "developer",        # Deep Interaction
        "youtube": "founder",          # Deep Education (mixed, default to founder)
    }
    
    return platform_mapping.get(platform_lower, "founder")


def get_content_focus_keywords(audience_type: str) -> List[str]:
    """
    Get content focus keywords for audience type.
    
    Args:
        audience_type: "c_level", "founder", or "developer"
    
    Returns:
        List of content focus keywords
    """
    profile = AUDIENCE_PROFILES.get(audience_type)
    if not profile:
        return []
    
    return profile.get("content_focus", [])


def get_recommended_platforms(audience_type: str) -> List[str]:
    """
    Get recommended platforms for audience type.
    
    Args:
        audience_type: "c_level", "founder", or "developer"
    
    Returns:
        List of platform names
    """
    profile = AUDIENCE_PROFILES.get(audience_type)
    if not profile:
        return ["linkedin", "instagram"]
    
    return profile.get("platforms", [])