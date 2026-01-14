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
    
    id: str                        # Template ID (ex: "H_PERGUNTA", "VS_123")
    module_type: str               # Module type ("hook", "insight", "solution", "example", "cta")
    function: str                  # Description of function
    structure: str                 # Text structure (ex: "E se [cenário ideal]?")
    length_range: Tuple[int, int]  # (min, max) characters
    tone: str                      # Recommended tone
    example: str                   # Example usage
    keywords: List[str]            # Keywords for matching (ex: ["pergunta", "curiosidade"])
    semantic_description: str      # Description for semantic matching


# =============================================================================
# HOOK TEMPLATES
# =============================================================================

HOOK_TEMPLATES = [
    TextualTemplate(
        id="H_DOR",
        module_type="hook",
        function="Ativa dor específica",
        structure="Cansado de [problema]?",
        length_range=(50, 80),
        tone="provocativo e empático",
        example="Cansado de reuniões infinitas que não levam a lugar nenhum?",
        keywords=["cansado", "dor", "problema", "frustração"],
        semantic_description="Ativa dor específica do público com pergunta provocativa e empática",
    ),
    TextualTemplate(
        id="H_PROMESSA",
        module_type="hook",
        function="Promete resultado",
        structure="Obtenha [benefício] em [tempo]",
        length_range=(60, 90),
        tone="direto e profissional",
        example="Automatize tarefas em 5 minutos.",
        keywords=["obtenha", "benefício", "resultado", "tempo", "rapidez"],
        semantic_description="Promete resultado tangível em tempo específico, tom direto e profissional",
    ),
    TextualTemplate(
        id="H_PERGUNTA",
        module_type="hook",
        function="Gera curiosidade",
        structure="E se [cenário ideal]?",
        length_range=(60, 90),
        tone="curioso ou inspirador",
        example="E se sua equipe trabalhasse só 4h/dia?",
        keywords=["e se", "pergunta", "curiosidade", "cenário", "possibilidade"],
        semantic_description="Gera curiosidade com pergunta sobre cenário ideal, tom curioso ou inspirador",
    ),
    TextualTemplate(
        id="H_NUMERO",
        module_type="hook",
        function="Número impactante",
        structure="[X]% das empresas [ação]",
        length_range=(60, 90),
        tone="objetivo e factual",
        example="80% das startups falham em escalar.",
        keywords=["porcentagem", "número", "estatística", "empresas", "fato"],
        semantic_description="Número impactante como gancho, tom objetivo e factual",
    ),
    TextualTemplate(
        id="H_CONTRASTE",
        module_type="hook",
        function="Contraste claro",
        structure="[Antes] vs. [Depois]",
        length_range=(50, 80),
        tone="binário e claro",
        example="Retrabalho vs. produtividade máxima.",
        keywords=["vs", "contraste", "antes", "depois", "transformação"],
        semantic_description="Contraste claro entre antes e depois, tom binário e direto",
    ),
    TextualTemplate(
        id="H_COMBO",
        module_type="hook",
        function="Dor + solução",
        structure="[Dor] → [Solução]",
        length_range=(60, 90),
        tone="direto e prático",
        example="Processos lentos → Automação em IA.",
        keywords=["dor", "solução", "seta", "transformação", "prático"],
        semantic_description="Combina dor real com solução clara, tom direto e prático",
    ),
    TextualTemplate(
        id="H_DECLARACAO",
        module_type="hook",
        function="Afirmação provocativa",
        structure="Você está [erro comum].",
        length_range=(60, 90),
        tone="ousado",
        example="Você está desperdiçando seu talento.",
        keywords=["você está", "erro", "provocação", "confronto", "verdade"],
        semantic_description="Afirmação provocativa que confronta erro comum do leitor, tom ousado",
    ),
    TextualTemplate(
        id="H_CITACAO",
        module_type="hook",
        function="Frase de autoridade",
        structure='"[Frase]" – [Fonte]"',
        length_range=(60, 100),
        tone="inspirador ou técnico",
        example='"Automação é o futuro." – Gartner',
        keywords=["citação", "autoridade", "fonte", "famous", "expert"],
        semantic_description="Frase de autoridade com citação, tom inspirador ou técnico",
    ),
    TextualTemplate(
        id="H_ALERTA",
        module_type="hook",
        function="Alerta chamativo",
        structure="[Risco]: Evite isso.",
        length_range=(50, 80),
        tone="urgente e assertivo",
        example="Burnout profissional: evite isso.",
        keywords=["alerta", "risco", "evite", "perigo", "urgente"],
        semantic_description="Alerta chamativo sobre risco a evitar, tom urgente e assertivo",
    ),
    TextualTemplate(
        id="H_ESTATUTO",
        module_type="hook",
        function="Posição de princípio",
        structure="Por aqui, acreditamos que [declaração]",
        length_range=(60, 100),
        tone="institucional",
        example="Por aqui, acreditamos que IA é ferramenta, não substituto.",
        keywords=["acreditamos", "princípio", "valores", "institucional", "posicionamento"],
        semantic_description="Posição de princípio institucional, tom manifesto ou valor de marca",
    ),
    TextualTemplate(
        id="H_PROVOCACAO",
        module_type="hook",
        function="Desafia o leitor",
        structure="Você realmente acredita que [afirmação]?",
        length_range=(60, 100),
        tone="questionador",
        example="Você realmente acredita que IA é só para big techs?",
        keywords=["realmente", "acredita", "desafio", "questionamento", "tensão"],
        semantic_description="Desafia crenças do leitor com pergunta, tom questionador criando tensão construtiva",
    ),
    TextualTemplate(
        id="H_AFIRMACAO",
        module_type="hook",
        function="Afirmação direta sem provocação",
        structure="Você tem tudo para [ação]",
        length_range=(50, 80),
        tone="encorajador",
        example="Você tem tudo para começar.",
        keywords=["você tem", "tudo", "capacidade", "encorajador", "positivo"],
        semantic_description="Afirmação direta encorajadora sem provocação, tom positivo e motivador",
    ),
    TextualTemplate(
        id="H_MISTÉRIO",
        module_type="hook",
        function="Cria curiosidade sem pergunta",
        structure="O que eles não te contaram sobre [tema]",
        length_range=(60, 90),
        tone="intrigante",
        example="O que eles não te contaram sobre automação.",
        keywords=["não te contaram", "segredo", "mistério", "revelação", "curiosidade"],
        semantic_description="Cria curiosidade com mistério ou segredo, tom intrigante sem pergunta direta",
    ),
]

# =============================================================================
# VALOR: DADO TEMPLATES
# =============================================================================

VALOR_DADO_TEMPLATES = [
    TextualTemplate(
        id="VD_DADO%",
        module_type="insight",  # Data templates map to insight module type
        function="Porcentagem direta",
        structure="[X]% das [grupo] [ação]",
        length_range=(100, 200),
        tone="técnico e objetivo",
        example="67% das PMEs ignoram automação básica – McKinsey 2024",
        keywords=["porcentagem", "%", "dado", "estatística", "grupo"],
        semantic_description="Apresenta porcentagem direta com contexto, tom técnico e objetivo",
    ),
    TextualTemplate(
        id="VD_NUMERO",
        module_type="insight",  # Data templates map to insight module type
        function="Número absoluto",
        structure="[X] [entidade] por [tempo]",
        length_range=(100, 180),
        tone="analítico",
        example="3 horas perdidas por dia por funcionário.",
        keywords=["número", "entidade", "tempo", "quantidade", "escala"],
        semantic_description="Mostra impacto em escala com número absoluto, tom analítico",
    ),
    TextualTemplate(
        id="VD_COMPARA",
        module_type="insight",  # Data templates map to insight module type
        function="Comparação numérica",
        structure="[X] vezes mais que [Y]",
        length_range=(100, 180),
        tone="comparativo claro",
        example="IA gera resultados 5x mais rápidos.",
        keywords=["vezes", "comparação", "mais", "relativo", "benefício"],
        semantic_description="Realça benefício relativo com comparação numérica, linguagem clara",
    ),
    TextualTemplate(
        id="VD_TEMPO",
        module_type="insight",  # Data templates map to insight module type
        function="Economia de tempo",
        structure="Reduza [tempo] com [ação]",
        length_range=(100, 180),
        tone="prático e orientado a ganho",
        example="Reduza 20h/mês em relatórios.",
        keywords=["reduza", "tempo", "economia", "ganho", "horas"],
        semantic_description="Enfatiza economia de tempo, tom prático e orientado a ganho real",
    ),
    TextualTemplate(
        id="VD_CUSTO",
        module_type="insight",  # Data templates map to insight module type
        function="Economia financeira",
        structure="Economize até R$[valor]",
        length_range=(100, 180),
        tone="econômico",
        example="Economize até R$10k/mês automatizando.",
        keywords=["economize", "custo", "dinheiro", "financeiro", "roi"],
        semantic_description="Quantifica impacto financeiro, tom econômico focado em ROI",
    ),
    TextualTemplate(
        id="VD_FONTE",
        module_type="insight",  # Data templates map to insight module type
        function="Dado com referência",
        structure="[Dado] – [Fonte]",
        length_range=(120, 200),
        tone="técnico e sério",
        example="Automação gera 30% mais ROI – McKinsey",
        keywords=["fonte", "referência", "autoridade", "validação", "credibilidade"],
        semantic_description="Apresenta dado com atribuição a fonte confiável, tom técnico e sério",
    ),
    TextualTemplate(
        id="VD_GRAFICO",
        module_type="insight",  # Data templates map to insight module type
        function="Dados visuais",
        structure="Veja no gráfico: [tendência ou relação]",
        length_range=(100, 200),
        tone="visual e direto",
        example="Veja no gráfico como a adoção de IA cresce 5x mais rápido em startups B2B.",
        keywords=["gráfico", "visual", "tendência", "relação", "dados"],
        semantic_description="Referencia dados visuais para tendências temporais ou comparações, tom visual e direto",
    ),
]

# =============================================================================
# VALOR: INSIGHT TEMPLATES
# =============================================================================

VALOR_INSIGHT_TEMPLATES = [
    TextualTemplate(
        id="VI_PRINCIPIO",
        module_type="insight",
        function="Princípio universal",
        structure="[Ação] é sobre [princípio]",
        length_range=(150, 250),
        tone="inspirador ou técnico",
        example="Automação é sobre estratégia, não só eficiência.",
        keywords=["princípio", "sobre", "essência", "estratégia", "universal"],
        semantic_description="Vai além do óbvio destacando valor estratégico, tom inspirador ou técnico",
    ),
    TextualTemplate(
        id="VI_CONSEQUENCIA",
        module_type="insight",
        function="Consequência direta",
        structure="[Problema] gera [consequência]",
        length_range=(150, 250),
        tone="explicativo",
        example="Decisões lentas geram perda de mercado.",
        keywords=["consequência", "gera", "causa", "efeito", "relação"],
        semantic_description="Relaciona causas e efeitos, tom explicativo mostrando relação direta",
    ),
    TextualTemplate(
        id="VI_PARADOXO",
        module_type="insight",
        function="Insight inesperado",
        structure="Você não precisa [ação esperada] para [resultado]",
        length_range=(150, 250),
        tone="reflexivo",
        example="Você não precisa ser grande para escalar rápido.",
        keywords=["não precisa", "paradoxo", "inesperado", "quebra", "expectativa"],
        semantic_description="Quebra expectativas com insight inesperado, tom reflexivo e surpreendente",
    ),
    TextualTemplate(
        id="VI_MITO",
        module_type="insight",
        function="Quebra de mito",
        structure="Mito: [falso] Realidade: [verdade]",
        length_range=(150, 250),
        tone="educativo",
        example="Mito: IA substitui pessoas. Realidade: Amplia capacidades.",
        keywords=["mito", "realidade", "falso", "verdade", "quebra"],
        semantic_description="Confronta suposições comuns, tom educativo quebra mitos",
    ),
    TextualTemplate(
        id="VI_CITACAO",
        module_type="insight",
        function="Insight por citação",
        structure='"[Insight forte]" – [Fonte]"',
        length_range=(120, 200),
        tone="inspirador ou técnico",
        example='"Não automatizar é como correr sem tênis." – Seth Godin',
        keywords=["citação", "insight", "fonte", "autoridade", "sabedoria"],
        semantic_description="Insight forte através de citação, fonte confiável com impacto real",
    ),
    TextualTemplate(
        id="VI_ESCADA",
        module_type="insight",
        function="Insight evolutivo",
        structure="Você começa com [ação], depois [aprendizado]",
        length_range=(150, 250),
        tone="construtivo",
        example="Você começa automatizando tarefas. Depois, aprende a escalar decisões.",
        keywords=["começa", "depois", "evolução", "progressão", "aprendizado"],
        semantic_description="Mostra evolução lógica de aprendizado, tom construtivo progressivo",
    ),
    TextualTemplate(
        id="VI_DECLARACAO",
        module_type="insight",
        function="Posição clara",
        structure="[Declaração sobre o mercado ou o tema]",
        length_range=(150, 250),
        tone="institucional",
        example="IA não é diferencial competitivo. É pré-requisito para sobreviver.",
        keywords=["declaração", "posicionamento", "mercado", "tema", "opinião"],
        semantic_description="Posicionamento forte com clareza sobre cenário, tom institucional",
    ),
]

# =============================================================================
# VALOR: SOLUÇÃO TEMPLATES
# =============================================================================

VALOR_SOLUCAO_TEMPLATES = [
    TextualTemplate(
        id="VS_123",
        module_type="solution",
        function="Passos sequenciais",
        structure="1. [Passo] 2. [Passo] 3. [Passo]",
        length_range=(200, 350),
        tone="tutorial",
        example="1. Liste processos manuais. 2. Use IA. 3. Meça resultados.",
        keywords=["passos", "sequencial", "1.", "2.", "3.", "processo"],
        semantic_description="Explicação clara e progressiva com passos sequenciais, tom tutorial",
    ),
    TextualTemplate(
        id="VS_LISTA",
        module_type="solution",
        function="Lista prática",
        structure="- [Ação curta] - [Ação curta]",
        length_range=(150, 250),
        tone="prático",
        example="- Delegue tarefas repetitivas - Aplique IA - Avalie resultados",
        keywords=["lista", "ação", "-", "prático", "rápido"],
        semantic_description="Lista objetiva com ações curtas, formato leve e direto",
    ),
    TextualTemplate(
        id="VS_FORMULA",
        module_type="solution",
        function="Fórmula simples",
        structure="[Resultado] = [Fator] + [Fator]",
        length_range=(100, 200),
        tone="analítico",
        example="Produtividade = Automação + Liderança clara",
        keywords=["fórmula", "=", "fator", "equação", "simples"],
        semantic_description="Sintético mas didático, tom analítico com fórmula replicável",
    ),
    TextualTemplate(
        id="VS_FRAMEWORK",
        module_type="solution",
        function="Framework curto",
        structure="[Sigla]: [Definição 1], [Definição 2], [Definição 3]",
        length_range=(150, 250),
        tone="sistemático",
        example="PAR: Processo, Automação, Resultados",
        keywords=["framework", "sigla", "modelo", "sistemático", "estrutura"],
        semantic_description="Ensina modelo aplicável com sigla e definições, tom sistemático",
    ),
    TextualTemplate(
        id="VS_CHECKLIST",
        module_type="solution",
        function="Checklist visual",
        structure="☑️ [Ação] ☑️ [Ação] ☑️ [Ação]",
        length_range=(150, 200),
        tone="direto e visual",
        example="☑️ Mapear tarefas ☑️ Escolher ferramenta ☑️ Implementar",
        keywords=["checklist", "☑️", "ação", "visual", "sequencial"],
        semantic_description="Checklist objetivo e sequencial, tom direto e visual",
    ),
    TextualTemplate(
        id="VS_OBSTACULO",
        module_type="solution",
        function="Supera bloqueio comum",
        structure="Se [problema], então [solução prática]",
        length_range=(150, 250),
        tone="empático e técnico",
        example="Se você não tem equipe de tech, use IA com agentes pré-prontos.",
        keywords=["se", "então", "problema", "solução", "bloqueio"],
        semantic_description="Ajuda leitor a superar travas comuns, tom empático e técnico",
    ),
    TextualTemplate(
        id="VS_DECISAO",
        module_type="solution",
        function="Critério de escolha",
        structure="Escolha [X] se busca [Y]",
        length_range=(120, 200),
        tone="objetivo e estratégico",
        example="Escolha IA local se busca controle de dados. Cloud, se busca escala.",
        keywords=["escolha", "se", "critério", "decisão", "opção"],
        semantic_description="Ajuda a tomar decisões com critério, tom objetivo e estratégico",
    ),
]

# =============================================================================
# VALOR: EXEMPLO TEMPLATES
# =============================================================================

VALOR_EXEMPLO_TEMPLATES = [
    TextualTemplate(
        id="VE_MINICASE",
        module_type="example",
        function="Resultado quantificado",
        structure="[Empresa] teve [resultado] com [ação aplicada]",
        length_range=(200, 300),
        tone="institucional",
        example="Shopify aumentou velocidade de checkout 40% através de otimização com IA.",
        keywords=["empresa", "resultado", "caso", "quantificado", "prova"],
        semantic_description="Case claro com número forte e impacto direto, tom institucional",
    ),
    TextualTemplate(
        id="VE_SIMULACAO",
        module_type="example",
        function="Cenário hipotético",
        structure="Imagine que você [ação ideal / contexto positivo]",
        length_range=(150, 250),
        tone="imaginativo e envolvente",
        example="Imagine reduzir reuniões pela metade com IA.",
        keywords=["imagine", "cenário", "hipotético", "ideal", "reflexão"],
        semantic_description="Leva à reflexão com cenário hipotético positivo, tom imaginativo e envolvente",
    ),
    TextualTemplate(
        id="VE_ANEDOTA",
        module_type="example",
        function="Exemplo informal",
        structure="[Pessoa] usou [solução] e [resultado observado]",
        length_range=(150, 250),
        tone="acessível e humanizado",
        example="Sarah automatizou seus relatórios semanais e eliminou todo o estresse de prazos.",
        keywords=["pessoa", "usou", "anedota", "storytelling", "humano"],
        semantic_description="Estilo storytelling leve, tom acessível e humanizado",
    ),
    TextualTemplate(
        id="VE_COMPARATIVO",
        module_type="example",
        function="Exemplo contrastante",
        structure="[Empresa A] fez [X], [Empresa B] não. Resultado? [Y]",
        length_range=(200, 300),
        tone="factual e instrutivo",
        example="Amazon investiu em IA de warehouse cedo, concorrentes não. Resultado: 50% mais rápido no fulfillment.",
        keywords=["comparação", "empresa", "contraste", "decisão", "resultado"],
        semantic_description="Contraste direto de decisão e impacto, tom factual e instrutivo",
    ),
    TextualTemplate(
        id="VE_MICROCAUSA",
        module_type="example",
        function="Detalhe com impacto",
        structure="[Time/pessoa] mudou [ação] e [resultado simbólico]",
        length_range=(150, 250),
        tone="leve e revelador",
        example="Time financeiro automatizou um relatório e economizou 9h/semana.",
        keywords=["time", "pessoa", "mudança", "detalhe", "impacto"],
        semantic_description="Mostra transformação granular com detalhe pequeno, tom leve e revelador",
    ),
]

# =============================================================================
# CTA TEMPLATES
# =============================================================================

CTA_TEMPLATES = [
    TextualTemplate(
        id="CTA_SEGUIR",
        module_type="cta",
        function="Construir audiência",
        structure="Siga para [promessa de valor]",
        length_range=(50, 100),
        tone="convite",
        example="Siga para insights semanais sobre implementação de IA.",
        keywords=["siga", "seguir", "audiência", "promessa", "conteúdo"],
        semantic_description="Convida a seguir para receber valor contínuo, tom de convite",
    ),
    TextualTemplate(
        id="CTA_COMENTAR",
        module_type="cta",
        function="Gerar engajamento",
        structure="[Pergunta ou convite para compartilhar]",
        length_range=(50, 150),
        tone="engajador",
        example="Quais desses erros você já cometeu? Comente abaixo 👇",
        keywords=["comente", "pergunta", "engajamento", "compartilhar", "interação"],
        semantic_description="Convida a comentar com pergunta ou convite, tom engajador",
    ),
    TextualTemplate(
        id="CTA_SALVAR",
        module_type="cta",
        function="Aumentar alcance através de saves",
        structure="Salve isso para [caso de uso futuro]",
        length_range=(50, 100),
        tone="prático",
        example="Salve isso antes do seu próximo projeto de IA.",
        keywords=["salve", "salvar", "guardar", "futuro", "referência"],
        semantic_description="Convida a salvar para uso futuro, tom prático e útil",
    ),
    TextualTemplate(
        id="CTA_COMPARTILHAR",
        module_type="cta",
        function="Espalhamento viral",
        structure="Marque alguém que [precisa disso]",
        length_range=(60, 120),
        tone="social",
        example="Marque um founder que está se afogando em trabalho manual.",
        keywords=["marque", "compartilhar", "tag", "alguém", "viral"],
        semantic_description="Convida a marcar/compartilhar, tom social para espalhamento viral",
    ),
    TextualTemplate(
        id="CTA_DM",
        module_type="cta",
        function="Conexão pessoal",
        structure="[Convite pessoal]",
        length_range=(50, 120),
        tone="pessoal e convidativo",
        example="Me chama no inbox: 'framework' e eu envio o guia completo.",
        keywords=["dm", "inbox", "mensagem", "pessoal", "conexão"],
        semantic_description="Convite pessoal para DM, tom íntimo e convidativo",
    ),
    TextualTemplate(
        id="CTA_LINK",
        module_type="cta",
        function="Gerar tráfego",
        structure="Acesse [recurso] em [destino]",
        length_range=(50, 100),
        tone="direto",
        example="Baixe o checklist completo (link na bio).",
        keywords=["acesse", "link", "baixe", "recurso", "tráfego"],
        semantic_description="Convida a acessar recurso externo, tom direto para gerar tráfego",
    ),
    TextualTemplate(
        id="CTA_ACAO_DUPLA",
        module_type="cta",
        function="Múltiplos caminhos de engajamento",
        structure="[Ação 1] + [Ação 2]",
        length_range=(60, 120),
        tone="flexível",
        example="Salve este post + compartilhe com sua equipe.",
        keywords=["ação", "dupla", "+", "múltiplo", "flexível"],
        semantic_description="Oferece múltiplos caminhos de engajamento, tom flexível",
    ),
]
