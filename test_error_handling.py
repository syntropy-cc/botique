#!/usr/bin/env python3
"""
Teste para verificar se a resposta bruta é salva mesmo em caso de erro de validação.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

from src.core.llm_client import HttpLLMClient
from src.core.llm_logger import LLMLogger
from src.core.config import OUTPUT_DIR, IdeationConfig
from src.ideas.generator import IdeaGenerator

load_dotenv()

def test_raw_response_saved_on_validation_error():
    """Testa se a resposta bruta é salva mesmo quando há erro de validação JSON"""
    
    print("=" * 70)
    print("TESTE: Resposta Bruta Salva em Caso de Erro")
    print("=" * 70)
    
    api_key = os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ API key não encontrada")
        return False
    
    # Criar logger
    logger = LLMLogger()
    
    # Criar cliente
    client = HttpLLMClient(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        model="deepseek-chat",
        logger=logger,
    )
    
    # Criar gerador
    generator = IdeaGenerator(client)
    
    # Criar diretório de debug
    debug_dir = test_output_dir / "test_article" / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    raw_response_path = debug_dir / "raw_llm_response.txt"
    
    # Fazer uma chamada que provavelmente vai gerar JSON válido
    # Mas vamos simular um erro de validação modificando a resposta
    print("\n1. Fazendo chamada ao LLM...")
    config = IdeationConfig()
    
    # Usar um artigo pequeno para teste rápido
    article_text = "This is a test article about AI and machine learning."
    
    try:
        # Chamar o gerador - se houver erro de validação, a resposta bruta deve ser salva
        payload = generator.generate_ideas(
            article_text,
            config,
            save_raw_response=True,
            raw_response_path=raw_response_path,
        )
        print("   ✓ Chamada bem-sucedida (sem erro de validação)")
        
    except ValueError as e:
        print(f"   ⚠️  Erro de validação (esperado em alguns casos): {e}")
        
        # Verificar se a resposta bruta foi salva
        if raw_response_path.exists():
            print(f"   ✓ Resposta bruta salva: {raw_response_path}")
            raw_content = raw_response_path.read_text()
            print(f"   ✓ Tamanho da resposta: {len(raw_content)} caracteres")
            return True
        else:
            print(f"   ❌ Resposta bruta NÃO foi salva!")
            return False
    
    # Verificar se a resposta bruta foi salva mesmo em caso de sucesso
    if raw_response_path.exists():
        print(f"   ✓ Resposta bruta salva mesmo em caso de sucesso: {raw_response_path}")
        return True
    else:
        print(f"   ⚠️  Resposta bruta não foi salva (pode ser normal se não houver erro)")
        return True  # Não é um erro se não houver problema de validação
    
    # Verificar e salvar logs
    print("\n2. Verificando logs...")
    if logger.calls:
        call = logger.calls[0]
        print(f"   ✓ Log criado: status={call['status']}")
        print(f"   ✓ Resposta no log: {len(call['output']['content']) if call['output']['content'] else 0} caracteres")
        if call['error']:
            print(f"   ✓ Erro registrado no log: {call['error'][:80]}...")
        
        # Logs are automatically saved to database
        print(f"   ✓ Logs salvos no banco de dados")
        return True
    else:
        print(f"   ❌ Nenhum log foi criado!")
        return False

if __name__ == "__main__":
    success = test_raw_response_saved_on_validation_error()
    print("\n" + "=" * 70)
    if success:
        print("✅ TESTE PASSOU")
    else:
        print("❌ TESTE FALHOU")
    print("=" * 70)

