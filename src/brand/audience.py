"""
Brand audience profiles module

Detailed audience profiles based on Plano de Branding 360º.

Contains comprehensive information about three personas:
- C-Level profile (PMEs R$10-100Mi)
- Founder profile (Seed-Series B startups)
- Developer profile (Independent devs)

Location: src/brand/audience.py
"""

from typing import Any, Dict, Optional, List


# =============================================================================
# AUDIENCE PROFILES - DETAILED PERSONA INFORMATION
# =============================================================================

AUDIENCE_PROFILES = {
    "c_level": {
        # =====================================================================
        # BASIC INFORMATION
        # =====================================================================
        "name": "Decisor C-Level",
        "description": "C-Level executives from SMEs with revenue between R$10-100Mi",
        "persona_type": "c_level",
        
        # =====================================================================
        # PROFESSIONAL BACKGROUND
        # =====================================================================
        "professional_background": {
            "company_size": "R$10-100Mi revenue (SME)",
            "role_types": ["CEO", "CTO", "CFO", "COO", "CMO"],
            "experience_level": "15-30 years professional experience",
            "decision_making_authority": "Strategic and budget decisions",
            "reporting_to": "Board of directors or owner",
            "team_size_managed": "50-500 employees",
            "industry_sectors": [
                "Technology services",
                "Manufacturing",
                "Retail and e-commerce",
                "Financial services",
                "Professional services",
                "Healthcare",
                "Logistics and distribution"
            ],
            "geographic_focus": "Primarily Brazil, expanding to Latin America",
            "digital_maturity": "Growing, seeking to modernize operations"
        },
        
        # =====================================================================
        # MARKET CONTEXT
        # =====================================================================
        "market_context": {
            "competitive_landscape": "High competition, pressure to differentiate",
            "economic_challenges": [
                "Compressed profit margins",
                "Currency volatility",
                "Regulatory complexity",
                "Labor costs",
                "Technology adoption costs"
            ],
            "growth_drivers": [
                "Digital transformation",
                "Operational efficiency",
                "Market expansion",
                "Customer experience improvement"
            ],
            "technology_adoption": "Cautious but necessary - requires proven ROI"
        },
        
        # =====================================================================
        # COMMUNICATION STYLE
        # =====================================================================
        "communication_style": {
            "tone": "professional",
            "formality": "formal",
            "vocabulary": "sophisticated",
            "language_preferences": {
                "preferred_terms": [
                    "ROI", "KPI", "Eficiência", "Vantagem competitiva",
                    "Estratégia", "Escalabilidade", "Mitigação de risco",
                    "Otimização", "Transformação digital", "Liderança de mercado"
                ],
                "avoid_terms": [
                    "Disrupt", "Game-changer", "Revolutionary",
                    "Hype", "Buzzwords técnicos sem contexto"
                ],
                "metric_focus": "Quantifiable results, percentages, timeframes",
                "proof_requirement": "Case studies, benchmarks, industry data"
            },
            "communication_channels": {
                "primary": ["LinkedIn", "Email", "Industry workshops"],
                "secondary": ["Webinars", "Industry publications", "Networking events"],
                "content_consumption": "B2B publications, industry reports, LinkedIn articles"
            }
        },
        
        # =====================================================================
        # PERSONALITY TRAITS
        # =====================================================================
        "personality_traits": [
            "authoritative",
            "strategic",
            "data_driven",
            "results_oriented",
            "pragmatic",
            "risk_aware",
            "time_constrained",
            "decisive",
            "accountable"
        ],
        
        # =====================================================================
        # PAIN POINTS - DETAILED
        # =====================================================================
        "pain_points": {
            "operational": [
                "compressed_margins",           # Margens comprimidas reduzindo lucratividade
                "operational_inefficiency",     # Processos manuais e ineficientes
                "lack_of_visibility",           # Falta de visibilidade em operações
                "resource_optimization"         # Dificuldade em otimizar recursos
            ],
            "strategic": [
                "competitive_pressure",         # Pressão competitiva crescente
                "technology_adoption_risk",     # Risco de adotar tecnologia nova
                "digital_transformation_pace",  # Ritmo lento de transformação digital
                "talent_acquisition"            # Dificuldade em atrair talentos
            ],
            "financial": [
                "wasted_budgets",               # Orçamentos desperdiçados em projetos
                "roi_uncertainty",              # Incerteza sobre retorno de investimento
                "cost_control",                 # Controle rigoroso de custos
                "budget_justification"          # Necessidade de justificar investimentos
            ],
            "emotional": [
                "decision_fatigue",             # Fadiga de decisão constante
                "pressure_to_innovate",         # Pressão para inovar vs estabilidade
                "balancing_risk_opportunity"    # Equilibrar risco e oportunidade
            ]
        },
        
        # =====================================================================
        # DESIRES AND GOALS - DETAILED
        # =====================================================================
        "desires": {
            "immediate": [
                "fast_roi",                     # ROI rápido e mensurável
                "efficiency_gains",             # Ganhos imediatos de eficiência
                "cost_reduction",               # Redução de custos operacionais
                "risk_mitigation"               # Mitigação de riscos
            ],
            "strategic": [
                "competitive_advantage",        # Vantagem competitiva sustentável
                "market_leadership",            # Liderança de mercado
                "proven_solutions",             # Soluções comprovadas e testadas
                "scalable_growth"               # Crescimento escalável
            ],
            "long_term": [
                "digital_maturity",             # Maturidade digital organizacional
                "innovation_culture",           # Cultura de inovação
                "sustainable_operations",       # Operações sustentáveis
                "market_expansion"              # Expansão de mercado
            ]
        },
        
        # =====================================================================
        # CUSTOMER JOURNEY
        # =====================================================================
        "customer_journey": {
            "awareness_stage": {
                "triggers": [
                    "Industry report highlighting inefficiency",
                    "Competitor moves in market",
                    "Board pressure for digital transformation",
                    "Operational pain becomes critical"
                ],
                "information_sources": [
                    "LinkedIn industry posts",
                    "B2B publications",
                    "Peer recommendations",
                    "Industry conferences"
                ],
                "search_behavior": "Research-driven, seeks benchmarks and case studies"
            },
            "consideration_stage": {
                "evaluation_criteria": [
                    "ROI projections",
                    "Implementation timeline",
                    "Risk assessment",
                    "Vendor credibility",
                    "Total cost of ownership"
                ],
                "decision_factors": [
                    "Proven track record",
                    "Industry references",
                    "Scalability",
                    "Integration capabilities",
                    "Support and training"
                ],
                "decision_timeframe": "3-6 months typically"
            },
            "decision_stage": {
                "approval_process": "Multi-stakeholder, requires business case",
                "risk_considerations": "Comprehensive risk analysis required",
                "success_metrics": "Clear KPIs and success criteria defined upfront"
            },
            "adoption_stage": {
                "success_factors": [
                    "Clear implementation roadmap",
                    "Change management support",
                    "Measurable progress milestones",
                    "Ongoing support and optimization"
                ]
            }
        },
        
        # =====================================================================
        # CONTENT PREFERENCES
        # =====================================================================
        "content_preferences": {
            "formats": ["carousel", "single_image", "video_short", "pdf", "newsletter"],
            "content_focus": [
                "roi_rapido",              # ROI Rápido
                "eficiencia",              # Eficiência
                "mitigacao_risco",         # Mitigação de Risco
                "lideranca_mercado",       # Liderança no Mercado
                "case_studies",            # Casos de sucesso
                "industry_benchmarks",     # Benchmarks da indústria
                "best_practices",          # Melhores práticas
                "strategic_insights"       # Insights estratégicos
            ],
            "content_structure_preferences": {
                "hook_type": "Problem statement or industry insight",
                "value_delivery": "Data-driven, evidence-based",
                "proof_elements": "Statistics, case studies, testimonials",
                "cta_style": "Professional, low-pressure, informative"
            },
            "engagement_triggers": [
                "Industry-specific data",
                "Peer success stories",
                "Actionable insights",
                "Strategic frameworks",
                "Risk mitigation strategies"
            ]
        },
        
        # =====================================================================
        # PLATFORMS AND FORMATS
        # =====================================================================
        "platforms": ["linkedin", "email", "workshops"],
        "formats": ["carousel", "single_image", "video_short", "pdf", "newsletter"],
        
        # =====================================================================
        # EMOTIONAL TRIGGERS
        # =====================================================================
        "emotional_triggers": {
            "positive": [
                "confidence",      # Confiança em decisões
                "relief",          # Alívio ao encontrar solução
                "excitement",      # Excitação por oportunidade estratégica
                "trust"            # Confiança em fornecedor/produto
            ],
            "negative_to_avoid": [
                "fear",            # Evitar medo baseado em FOMO
                "urgency_artificial",  # Urgência artificial
                "desperation",     # Desespero
                "overwhelm"        # Sobrecarga de informações
            ],
            "emotional_journey": "From concern → curiosity → confidence → action"
        },
        
        # =====================================================================
        # BRAND VALUES ALIGNMENT
        # =====================================================================
        "brand_values": ["go_deep_or_go_home", "open_source"],
        
        # =====================================================================
        # SUCCESS METRICS
        # =====================================================================
        "success_metrics": {
            "linkedin_followers": 2000,
            "ssi_score": 70,
            "engagement_rate": 0.03,
            "lead_quality": "high",
            "conversion_timeline": "3-6 months",
            "decision_influence": "Strategic and budget authority"
        },
        
        # =====================================================================
        # LANGUAGE EXAMPLES
        # =====================================================================
        "language_examples": {
            "phrases_that_resonate": [
                "Como reduzir custos operacionais em 30%",
                "Estratégia comprovada para aumento de margem",
                "Transformação digital sem riscos",
                "ROI mensurável em 90 dias",
                "Liderança de mercado através de eficiência"
            ],
            "writing_style_notes": [
                "Use dados e estatísticas para credibilidade",
                "Evite jargões técnicos sem explicação",
                "Foque em resultados mensuráveis",
                "Apresente soluções práticas e comprovadas",
                "Seja direto e objetivo"
            ]
        }
    },
    
    "founder": {
        # =====================================================================
        # BASIC INFORMATION
        # =====================================================================
        "name": "Fundador Visionário",
        "description": "Visionary founders from Seed to Series B startups",
        "persona_type": "founder",
        
        # =====================================================================
        # PROFESSIONAL BACKGROUND
        # =====================================================================
        "professional_background": {
            "company_stage": "Seed to Series B (US$500K - $20M raised)",
            "role_types": ["CEO/Founder", "CTO/Founder", "CPO/Founder", "Co-founder"],
            "experience_level": "5-15 years, mix of technical and business",
            "decision_making_authority": "Full autonomy, fast decisions",
            "funding_status": "Bootstrapped, Seed, or Series A/B",
            "team_size": "5-100 employees",
            "industry_sectors": [
                "SaaS and B2B software",
                "Fintech",
                "Healthtech",
                "E-commerce and marketplace",
                "Developer tools",
                "AI/ML startups",
                "PropTech",
                "EdTech"
            ],
            "geographic_focus": "Global-first mindset, targeting US/LATAM markets",
            "growth_phase": "Product-market fit achieved, scaling operations"
        },
        
        # =====================================================================
        # MARKET CONTEXT
        # =====================================================================
        "market_context": {
            "competitive_landscape": "Hyper-competitive, moving fast",
            "challenges": [
                "Funding winter constraints",
                "Resource scarcity",
                "Talent acquisition",
                "Market saturation",
                "Unit economics pressure",
                "Burn rate management"
            ],
            "opportunities": [
                "Open source advantage",
                "Community-driven growth",
                "Developer-first products",
                "Emerging tech adoption",
                "Distribution innovation"
            ],
            "mindset": "Build fast, iterate, ship early, community-first"
        },
        
        # =====================================================================
        # COMMUNICATION STYLE
        # =====================================================================
        "communication_style": {
            "tone": "empowering",
            "formality": "casual",
            "vocabulary": "moderate",
            "language_preferences": {
                "preferred_terms": [
                    "Growth", "Scale", "Build", "Ship", "Iterate",
                    "Community", "Open source", "Developer-first",
                    "Edge", "Advantage", "Innovation", "Exponential",
                    "Builder culture", "Pioneer", "Disrupt"
                ],
                "avoid_terms": [
                    "Enterprise-grade",  # without context
                    "Robust",  # overused
                    "Legacy thinking",
                    "Bureaucracy"
                ],
                "metric_focus": "Growth metrics, engagement, community size",
                "proof_requirement": "Use cases, traction, community validation"
            },
            "communication_channels": {
                "primary": ["LinkedIn", "Instagram", "Twitter", "Product Hunt", "Discord"],
                "secondary": ["Indie Hackers", "Dev.to", "Hacker News", "Reddit"],
                "content_consumption": "Twitter threads, LinkedIn posts, indie maker blogs, podcasts"
            }
        },
        
        # =====================================================================
        # PERSONALITY TRAITS
        # =====================================================================
        "personality_traits": [
            "visionary",
            "bold",
            "innovative",
            "resilient",
            "community_oriented",
            "action_oriented",
            "risk_taking",
            "experimental",
            "fast_moving"
        ],
        
        # =====================================================================
        # PAIN POINTS - DETAILED
        # =====================================================================
        "pain_points": {
            "growth": [
                "scaling_without_resources",    # Escalar sem recursos suficientes
                "hiring_talent",                # Contratar talento em mercado competitivo
                "burn_rate_management",         # Gerenciar burn rate com recursos limitados
                "unit_economics"                # Fazer unit economics funcionarem
            ],
            "technical": [
                "building_without_funding",     # Construir sem funding suficiente
                "finding_technical_edge",       # Encontrar edge técnico competitivo
                "technical_debt",               # Balancear velocidade vs dívida técnica
                "infrastructure_costs"          # Custos de infraestrutura escalando
            ],
            "strategic": [
                "market_validation",            # Validar mercado rapidamente
                "competitive_differentiation",  # Diferenciação competitiva
                "product_market_fit",           # Atingir/sustentar product-market fit
                "distribution_channels"         # Encontrar canais de distribuição eficientes
            ],
            "emotional": [
                "founder_loneliness",           # Solidão do fundador
                "decision_overload",            # Sobrecarga de decisões
                "uncertainty_management",       # Gerenciar incerteza constante
                "pressure_to_perform"           # Pressão para performar e crescer
            ]
        },
        
        # =====================================================================
        # DESIRES AND GOALS - DETAILED
        # =====================================================================
        "desires": {
            "immediate": [
                "traction",                     # Tração mensurável (usuários, receita)
                "community_growth",             # Crescimento da comunidade
                "product_improvement",          # Melhorias rápidas no produto
                "developer_adoption"            # Adoção por desenvolvedores
            ],
            "strategic": [
                "exponential_growth",           # Crescimento exponencial
                "competitive_edge",             # Edge competitivo sustentável
                "community_support",            # Suporte ativo da comunidade
                "equity_partnerships",          # Parcerias estratégicas
                "market_leadership"             # Liderança de mercado
            ],
            "long_term": [
                "pioneering_innovation",        # Inovação pioneira
                "builder_culture",              # Cultura de construção
                "sustainable_business",         # Negócio sustentável e escalável
                "impact_at_scale",              # Impacto em escala
                "legacy_building"               # Construir legado
            ]
        },
        
        # =====================================================================
        # CUSTOMER JOURNEY
        # =====================================================================
        "customer_journey": {
            "awareness_stage": {
                "triggers": [
                    "Peer sharing on Twitter/LinkedIn",
                    "Product Hunt launch",
                    "Open source discovery",
                    "Community discussion",
                    "Problem-solution fit moment"
                ],
                "information_sources": [
                    "Twitter threads",
                    "Indie Hackers",
                    "Dev.to",
                    "Product Hunt",
                    "Discord communities",
                    "Maker blogs"
                ],
                "search_behavior": "Social-driven, community-validated, quick decisions"
            },
            "consideration_stage": {
                "evaluation_criteria": [
                    "Developer experience",
                    "Community size and engagement",
                    "Open source availability",
                    "Ease of integration",
                    "Documentation quality",
                    "Cost-effectiveness"
                ],
                "decision_factors": [
                    "Community validation",
                    "Time to value",
                    "Flexibility and customization",
                    "Vendor philosophy alignment",
                    "Growth trajectory"
                ],
                "decision_timeframe": "Days to weeks (fast decision cycle)"
            },
            "decision_stage": {
                "approval_process": "Founder autonomy, quick trial",
                "risk_considerations": "Low switching cost, open source provides safety",
                "success_metrics": "Adoption speed, community engagement, traction"
            },
            "adoption_stage": {
                "success_factors": [
                    "Quick onboarding",
                    "Active community support",
                    "Regular product updates",
                    "Transparent roadmap",
                    "Founder accessibility"
                ]
            }
        },
        
        # =====================================================================
        # CONTENT PREFERENCES
        # =====================================================================
        "content_preferences": {
            "formats": ["carousel", "threads", "reels", "playbook_pdf", "podcast"],
            "content_focus": [
                "crescimento_exponencial",    # Crescimento Exponencial
                "pioneirismo",                # Pioneirismo
                "cultura_builder",            # Cultura Builder
                "growth_hacks",               # Growth hacks e táticas
                "founder_stories",            # Histórias de fundadores
                "community_building",         # Construção de comunidade
                "open_source",                # Open source e colaboração
                "product_market_fit"          # Product-market fit insights
            ],
            "content_structure_preferences": {
                "hook_type": "Bold statement, contrarian insight, or personal story",
                "value_delivery": "Actionable, relatable, community-validated",
                "proof_elements": "Traction metrics, community testimonials, live examples",
                "cta_style": "Invitation to try, join community, or collaborate"
            },
            "engagement_triggers": [
                "Founder authenticity",
                "Growth tactics",
                "Community stories",
                "Open source philosophy",
                "Pioneer mindset",
                "Builder culture"
            ]
        },
        
        # =====================================================================
        # PLATFORMS AND FORMATS
        # =====================================================================
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
        
        # =====================================================================
        # EMOTIONAL TRIGGERS
        # =====================================================================
        "emotional_triggers": {
            "positive": [
                "inspiration",      # Inspiração para construir
                "empowerment",      # Empoderamento para crescer
                "belonging",        # Pertencimento à comunidade
                "excitement",       # Excitação por inovação
                "determination"     # Determinação para seguir em frente
            ],
            "negative_to_avoid": [
                "despair",          # Desesperança
                "overwhelm",        # Sobrecarga (já têm o suficiente)
                "doubt",            # Dúvida sobre capacidade
                "isolation"         # Isolamento
            ],
            "emotional_journey": "From curiosity → inspiration → determination → action"
        },
        
        # =====================================================================
        # BRAND VALUES ALIGNMENT
        # =====================================================================
        "brand_values": [
            "go_deep_or_go_home",
            "open_source",
            "community_collaboration",
            "pioneer_new_world"
        ],
        
        # =====================================================================
        # SUCCESS METRICS
        # =====================================================================
        "success_metrics": {
            "instagram_followers": 1000,
            "twitter_followers": 1000,
            "engagement_rate": 0.05,
            "community_size": 300,
            "conversion_timeline": "Days to weeks",
            "decision_influence": "Full autonomy, fast decisions"
        },
        
        # =====================================================================
        # LANGUAGE EXAMPLES
        # =====================================================================
        "language_examples": {
            "phrases_that_resonate": [
                "Como construímos X sem funding",
                "Growth hack que multiplicou nossa comunidade",
                "Por que abrimos o código fonte",
                "A jornada de 0 a 1000 usuários",
                "Builder culture vs corporate culture"
            ],
            "writing_style_notes": [
                "Seja autêntico e pessoal",
                "Compartilhe aprendizados reais",
                "Use histórias e exemplos concretos",
                "Fale com igualdade, não de cima para baixo",
                "Inspire ação e experimentação"
            ]
        }
    },
    
    "developer": {
        # =====================================================================
        # BASIC INFORMATION
        # =====================================================================
        "name": "DEV Forjador",
        "description": "Independent developers and OSS contributors",
        "persona_type": "developer",
        
        # =====================================================================
        # PROFESSIONAL BACKGROUND
        # =====================================================================
        "professional_background": {
            "work_mode": "Independent, freelancer, or side-project builder",
            "role_types": [
                "Full-stack developer",
                "Open source contributor",
                "Indie maker",
                "Freelance developer",
                "Part-time startup founder"
            ],
            "experience_level": "2-10 years, mix of self-taught and formal education",
            "decision_making_authority": "Full autonomy on tech choices",
            "income_sources": [
                "Freelance projects",
                "Side projects",
                "Open source contributions",
                "Part-time employment",
                "Product sales"
            ],
            "project_types": [
                "Open source tools",
                "Personal projects",
                "Client work",
                "Side businesses",
                "Community contributions"
            ],
            "technology_stack": "Modern stack preferred (React, Node, Python, etc.)",
            "community_involvement": "Active in GitHub, Discord, Reddit, Dev.to"
        },
        
        # =====================================================================
        # MARKET CONTEXT
        # =====================================================================
        "market_context": {
            "challenges": [
                "Working in isolation",
                "Limited resources",
                "Keeping up with tech",
                "Finding meaningful projects",
                "Monetization challenges",
                "Documentation burden"
            ],
            "opportunities": [
                "Open source collaboration",
                "Community recognition",
                "Skill development",
                "Portfolio building",
                "Network expansion"
            ],
            "mindset": "Hands-on, collaborative, learning-focused, community-driven"
        },
        
        # =====================================================================
        # COMMUNICATION STYLE
        # =====================================================================
        "communication_style": {
            "tone": "technical",
            "formality": "casual",
            "vocabulary": "technical",
            "language_preferences": {
                "preferred_terms": [
                    "Code", "API", "Library", "Framework", "Tool",
                    "Open source", "Community", "Contribution",
                    "Deep dive", "Hands-on", "Practical", "Technical",
                    "Documentation", "Example", "Tutorial"
                ],
                "avoid_terms": [
                    "Enterprise buzzwords",
                    "Marketing speak",
                    "Vague promises",
                    "Non-technical fluff"
                ],
                "metric_focus": "Code quality, performance, developer experience",
                "proof_requirement": "Working code, benchmarks, GitHub stats"
            },
            "communication_channels": {
                "primary": ["GitHub", "Discord", "YouTube", "Twitch", "Blog"],
                "secondary": ["Reddit", "Dev.to", "Stack Overflow", "Twitter"],
                "content_consumption": "GitHub READMEs, technical blogs, video tutorials, live coding"
            }
        },
        
        # =====================================================================
        # PERSONALITY TRAITS
        # =====================================================================
        "personality_traits": [
            "pragmatic",
            "detail_oriented",
            "community_focused",
            "hands_on",
            "analytical",
            "curious",
            "problem_solver",
            "collaborative",
            "learning_oriented"
        ],
        
        # =====================================================================
        # PAIN POINTS - DETAILED
        # =====================================================================
        "pain_points": {
            "professional": [
                "working_in_isolation",        # Trabalhar isolado sem comunidade
                "finding_projects",            # Encontrar projetos interessantes
                "monetization_challenges",     # Desafios de monetização
                "client_acquisition"           # Aquisição de clientes
            ],
            "technical": [
                "keeping_up_with_tech",        # Acompanhar evolução tecnológica
                "technical_debt",              # Dívida técnica em projetos
                "documentation_burden",        # Carga de documentação
                "tool_complexity"              # Complexidade de ferramentas
            ],
            "resource": [
                "lack_of_resources",           # Falta de recursos (servidores, ferramentas)
                "time_management",             # Gerenciamento de tempo
                "cost_of_tools",               # Custo de ferramentas e infraestrutura
                "learning_curves"              # Curvas de aprendizado íngremes
            ],
            "emotional": [
                "imposter_syndrome",           # Síndrome do impostor
                "burnout",                     # Burnout de projetos
                "loneliness",                  # Solidão do desenvolvedor independente
                "uncertainty_about_path"       # Incerteza sobre caminho profissional
            ]
        },
        
        # =====================================================================
        # DESIRES AND GOALS - DETAILED
        # =====================================================================
        "desires": {
            "immediate": [
                "hands_on_experience",         # Experiência prática e hands-on
                "skill_improvement",           # Melhoria de habilidades
                "project_ideas",               # Ideias de projetos
                "community_connection"         # Conexão com comunidade
            ],
            "professional": [
                "community_recognition",       # Reconhecimento da comunidade
                "open_source_contributions",   # Contribuições open source relevantes
                "portfolio_building",          # Construção de portfólio
                "collaborative_projects"       # Projetos colaborativos
            ],
            "long_term": [
                "technical_mastery",           # Maestria técnica
                "learning_opportunities",      # Oportunidades de aprendizado contínuo
                "community_leadership",        # Liderança na comunidade
                "sustainable_career"           # Carreira sustentável
            ]
        },
        
        # =====================================================================
        # CUSTOMER JOURNEY
        # =====================================================================
        "customer_journey": {
            "awareness_stage": {
                "triggers": [
                    "GitHub trending repository",
                    "Community recommendation",
                    "Technical blog post",
                    "YouTube tutorial",
                    "Discord community discussion",
                    "Reddit post"
                ],
                "information_sources": [
                    "GitHub",
                    "Discord servers",
                    "YouTube channels",
                    "Dev.to",
                    "Reddit (r/programming, etc.)",
                    "Technical blogs"
                ],
                "search_behavior": "Code-first, documentation-driven, community-validated"
            },
            "consideration_stage": {
                "evaluation_criteria": [
                    "Code quality",
                    "Documentation completeness",
                    "Community activity",
                    "Ease of use",
                    "Performance",
                    "License compatibility"
                ],
                "decision_factors": [
                    "GitHub stars and activity",
                    "Documentation quality",
                    "Community support",
                    "Code examples",
                    "Active maintenance",
                    "Open source license"
                ],
                "decision_timeframe": "Hours to days (quick evaluation)"
            },
            "decision_stage": {
                "approval_process": "Personal decision, often starts with code review",
                "risk_considerations": "Low risk - can switch easily, open source provides safety",
                "success_metrics": "Working implementation, performance, developer experience"
            },
            "adoption_stage": {
                "success_factors": [
                    "Clear documentation",
                    "Working examples",
                    "Active community support",
                    "Regular updates",
                    "Responsive maintainers"
                ]
            }
        },
        
        # =====================================================================
        # CONTENT PREFERENCES
        # =====================================================================
        "content_preferences": {
            "formats": ["repo_readme", "video_tutorial", "live_coding", "technical_blog", "gist"],
            "content_focus": [
                "mao_na_massa",              # Mão na Massa
                "code_deep_dive",            # Code Deep Dive
                "contribuicoes_comunidade",  # Contribuições para Comunidade
                "technical_tutorials",       # Tutoriais técnicos
                "code_examples",             # Exemplos de código
                "best_practices",            # Melhores práticas
                "problem_solving",           # Resolução de problemas
                "tool_comparisons"           # Comparações de ferramentas
            ],
            "content_structure_preferences": {
                "hook_type": "Problem statement or code challenge",
                "value_delivery": "Practical, code-heavy, immediately applicable",
                "proof_elements": "Working code, benchmarks, GitHub links",
                "cta_style": "Invitation to try, contribute, or discuss"
            },
            "engagement_triggers": [
                "Practical code examples",
                "Technical deep dives",
                "Problem-solving approaches",
                "Open source contributions",
                "Community collaboration",
                "Learning opportunities"
            ]
        },
        
        # =====================================================================
        # PLATFORMS AND FORMATS
        # =====================================================================
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
        
        # =====================================================================
        # EMOTIONAL TRIGGERS
        # =====================================================================
        "emotional_triggers": {
            "positive": [
                "curiosity",       # Curiosidade por aprender
                "satisfaction",    # Satisfação ao resolver problema
                "belonging",       # Pertencimento à comunidade
                "pride",           # Orgulho em contribuições
                "growth"           # Sensação de crescimento
            ],
            "negative_to_avoid": [
                "overwhelm",       # Sobrecarga técnica
                "intimidation",    # Intimidação por complexidade
                "isolation",       # Isolamento
                "inadequacy"       # Sensação de inadequação
            ],
            "emotional_journey": "From curiosity → understanding → mastery → contribution"
        },
        
        # =====================================================================
        # BRAND VALUES ALIGNMENT
        # =====================================================================
        "brand_values": [
            "go_deep_or_go_home",
            "open_source",
            "community_collaboration"
        ],
        
        # =====================================================================
        # SUCCESS METRICS
        # =====================================================================
        "success_metrics": {
            "github_stars": 50,
            "forks": 20,
            "prs_accepted": 10,
            "community_engagement": "high",
            "conversion_timeline": "Hours to days",
            "decision_influence": "Personal autonomy, technical merit"
        },
        
        # =====================================================================
        # LANGUAGE EXAMPLES
        # =====================================================================
        "language_examples": {
            "phrases_that_resonate": [
                "Como implementar X com código",
                "Deep dive em [tecnologia]",
                "Contribuindo para open source",
                "Resolvendo [problema técnico]",
                "Best practices para [categoria]"
            ],
            "writing_style_notes": [
                "Inclua código real e funcional",
                "Seja técnico mas acessível",
                "Forneça exemplos práticos",
                "Explique o 'por quê' além do 'como'",
                "Conecte com a comunidade"
            ]
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
        "c-level", "executive", "decisor", "ceo", "cto", "cfo", "coo", "cmo"
    ]):
        return AUDIENCE_PROFILES["c_level"]
    
    elif any(x in persona_lower for x in [
        "founder", "fundador", "visionário", "startup", "empreendedor", "co-founder"
    ]):
        return AUDIENCE_PROFILES["founder"]
    
    elif any(x in persona_lower for x in [
        "developer", "dev", "desenvolvedor", "forjador", "engineer", "programmer"
    ]):
        return AUDIENCE_PROFILES["developer"]
    
    return None


def enrich_idea_with_audience(
    idea: Dict[str, Any],
    audience_profile: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Enrich idea dict with audience profile data.
    
    Merges LLM-generated idea attributes with brand audience profile,
    ensuring brand consistency. Maintains backward compatibility by
    extracting top-level attributes from detailed profile structure.
    
    Args:
        idea: Idea dict from LLM
        audience_profile: Audience profile dict
    
    Returns:
        Enriched idea dict
    """
    enriched = idea.copy()
    
    # Extract personality traits (flatten if nested)
    profile_traits = audience_profile.get("personality_traits", [])
    if isinstance(profile_traits, dict):
        # Handle nested structure if exists
        profile_traits = profile_traits.get("primary", [])
    
    # Merge personality traits (keep unique)
    existing_traits = set(idea.get("personality_traits", []))
    profile_traits_set = set(profile_traits)
    enriched["personality_traits"] = list(existing_traits | profile_traits_set)[:5]
    
    # Extract pain points (flatten if nested)
    profile_pains = audience_profile.get("pain_points", [])
    if isinstance(profile_pains, dict):
        # Flatten nested pain points structure
        all_pains = []
        for category, pains in profile_pains.items():
            if isinstance(pains, list):
                all_pains.extend(pains)
        profile_pains = all_pains
    elif not isinstance(profile_pains, list):
        profile_pains = []
    
    # Merge pain points (keep unique)
    existing_pains = set(idea.get("pain_points", []))
    profile_pains_set = set(profile_pains)
    enriched["pain_points"] = list(existing_pains | profile_pains_set)[:5]
    
    # Extract desires (flatten if nested)
    profile_desires = audience_profile.get("desires", [])
    if isinstance(profile_desires, dict):
        # Flatten nested desires structure
        all_desires = []
        for category, desires in profile_desires.items():
            if isinstance(desires, list):
                all_desires.extend(desires)
        profile_desires = all_desires
    elif not isinstance(profile_desires, list):
        profile_desires = []
    
    # Merge desires (keep unique)
    existing_desires = set(idea.get("desires", []))
    profile_desires_set = set(profile_desires)
    enriched["desires"] = list(existing_desires | profile_desires_set)[:5]
    
    # Override vocabulary/formality with profile defaults if not specified
    communication_style = audience_profile.get("communication_style", {})
    if not idea.get("vocabulary_level"):
        enriched["vocabulary_level"] = communication_style.get("vocabulary", "moderate")
    
    if not idea.get("formality"):
        enriched["formality"] = communication_style.get("formality", "neutral")
    
    # Add brand values
    enriched["brand_values"] = audience_profile.get("brand_values", [])
    
    # Add full profile context for agents (preserve for detailed context)
    enriched["audience_profile_full"] = audience_profile
    
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
    
    content_prefs = profile.get("content_preferences", {})
    return content_prefs.get("content_focus", [])


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
