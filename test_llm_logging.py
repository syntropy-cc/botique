#!/usr/bin/env python3
"""
Script de teste para o sistema de log LLM.

Faz uma chamada real ao LLM e verifica se os logs são criados corretamente.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

from src.core.llm_client import HttpLLMClient
from src.core.llm_logger import LLMLogger
from src.core.config import OUTPUT_DIR

# Carregar variáveis de ambiente do .env
load_dotenv()

def main():
    print("=" * 70)
    print("TESTE DO SISTEMA DE LOG LLM")
    print("=" * 70)
    
    # Verificar se a API key está disponível (tenta ambas as variáveis)
    api_key = os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ ERRO: LLM_API_KEY ou DEEPSEEK_API_KEY não encontrada no arquivo .env")
        return 1
    
    print(f"✓ API Key encontrada: {api_key[:10]}...")
    
    # Criar diretório de teste
    test_output_dir = OUTPUT_DIR / "test_logs"
    test_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Criar logger
    print("\n1. Criando logger...")
    logger = LLMLogger(output_dir=test_output_dir)
    logger.set_context(article_slug="test_article", post_id="test_post_001")
    print(f"   ✓ Logger criado: session_id={logger.get_session_id()[:8]}...")
    
    # Criar cliente LLM com logger
    print("\n2. Criando cliente LLM...")
    client = HttpLLMClient(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        model="deepseek-chat",
        logger=logger,
    )
    print(f"   ✓ Cliente criado: model={client.model}")
    
    # Fazer chamada real ao LLM
    print("\n3. Fazendo chamada ao LLM...")
    test_prompt = "Responda em português em uma frase: O que é inteligência artificial?"
    
    try:
        response = client.generate(
            prompt=test_prompt,
            max_tokens=100,
            temperature=0.2,
        )
        print(f"   ✓ Resposta recebida: {response[:100]}...")
    except Exception as e:
        print(f"   ❌ Erro na chamada: {e}")
        return 1
    
    # Verificar logs criados
    print("\n4. Verificando logs...")
    print(f"   Total de chamadas logadas: {len(logger.calls)}")
    
    if logger.calls:
        call = logger.calls[0]
        print(f"   ✓ Call ID: {call['call_id'][:8]}...")
        print(f"   ✓ Status: {call['status']}")
        print(f"   ✓ Fase: {call['phase']}")
        print(f"   ✓ Função: {call['function']}")
        print(f"   ✓ Duração: {call['metrics']['duration_ms']} ms")
        if call['metrics']['tokens_total']:
            print(f"   ✓ Tokens: {call['metrics']['tokens_total']} (in: {call['metrics']['tokens_input']}, out: {call['metrics']['tokens_output']})")
        if call['metrics']['cost_estimate']:
            print(f"   ✓ Custo estimado: ${call['metrics']['cost_estimate']:.6f}")
    
    # Salvar logs
    print("\n5. Salvando logs...")
    log_paths = logger.save_logs(article_slug="test_article")
    
    if log_paths.get('local'):
        local_path = Path(log_paths['local'])
        print(f"   ✓ Log local salvo: {local_path}")
        
        # Verificar estrutura do arquivo
        log_data = json.loads(local_path.read_text())
        print(f"   ✓ Estrutura válida:")
        print(f"     - Session ID: {log_data['session_id'][:8]}...")
        print(f"     - Total de chamadas: {log_data['total_calls']}")
        print(f"     - Total de tokens: {log_data.get('total_tokens', 'N/A')}")
        print(f"     - Custo total: ${log_data.get('total_cost_estimate', 0):.6f}")
    
    if log_paths.get('central'):
        central_path = Path(log_paths['central'])
        print(f"   ✓ Log centralizado salvo: {central_path}")
    
    # Mostrar conteúdo do log (primeira chamada)
    print("\n6. Conteúdo do log (primeira chamada):")
    if logger.calls:
        call = logger.calls[0]
        print(f"   Input length: {call['input']['prompt_length']} chars")
        print(f"   Output length: {call['output']['content_length']} chars")
        print(f"   Context: article_slug={call['context']['article_slug']}, post_id={call['context']['post_id']}")
    
    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    
    if log_paths.get('local'):
        print(f"\n📄 Log completo disponível em: {log_paths['local']}")
    
    return 0

if __name__ == "__main__":
    exit(main())

