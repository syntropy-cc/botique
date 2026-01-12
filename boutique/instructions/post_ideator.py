"""
Post Ideator Instruction

Instrução para geração de ideias de posts a partir de artigos.
"""

import json
from pathlib import Path
from typing import Any, Dict

from framework.core.instruction import Instruction


class PostIdeatorInstruction(Instruction):
    """Instrução para geração de ideias de posts"""
    
    def __init__(self):
        template_path = Path(__file__).parent / "templates" / "post_ideator.md"
        template = template_path.read_text(encoding="utf-8")
        
        super().__init__(
            prompt_key="post_ideator",
            prompt_template=template,
            model="deepseek-chat",
            temperature=0.2,
            max_tokens=2048,
            preprocess=self._preprocess_article,
            postprocess=self._postprocess_ideas,
        )
    
    def _preprocess_article(self, input_data: Dict[str, Any]) -> str:
        """
        φ_in: Transforma artigo e configuração em formato para prompt.
        
        Args:
            input_data: Deve conter "article" e "config" (IdeationConfig)
            
        Returns:
            Prompt formatado com variáveis substituídas
        """
        article = input_data.get("article", "")
        config = input_data.get("config")
        
        # Se config tem método to_prompt_dict, usa ele
        if config and hasattr(config, "to_prompt_dict"):
            prompt_dict = config.to_prompt_dict()
        else:
            prompt_dict = {}
        
        prompt_dict["article"] = article
        
        # Substitui variáveis no template
        prompt = self.prompt_template
        for key, value in prompt_dict.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))
        
        return prompt
    
    def _postprocess_ideas(self, response: str) -> Dict[str, Any]:
        """
        φ_out: Transforma resposta LLM em JSON estruturado.
        
        Args:
            response: Resposta do LLM
            
        Returns:
            Dict com "article_summary" e "ideas"
        """
        # Tenta extrair JSON se estiver em code blocks
        response = response.strip()
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end != -1:
                response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end != -1:
                response = response[start:end].strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: retorna estrutura básica
            return {
                "article_summary": {"main_thesis": "", "key_insights": [], "themes": []},
                "ideas": []
            }
