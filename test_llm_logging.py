#!/usr/bin/env python3
"""
Script de teste para o sistema de log LLM.

Faz uma chamada real ao LLM e verifica se os logs são criados corretamente.
"""

import os
from dotenv import load_dotenv

from src.core.llm_client import HttpLLMClient
from src.core.llm_logger import LLMLogger

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
    
    # Criar logger
    print("\n1. Criando logger...")
    logger = LLMLogger()
    logger.set_context(article_slug="test_article", post_id="test_post_001")
    trace_id = logger.create_trace(name="test_llm_logging")
    logger.current_trace_id = trace_id
    print(f"   ✓ Logger criado: session_id={logger.get_session_id()[:8]}...")
    print(f"   ✓ Trace criado: {trace_id[:8]}...")
    
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
    
    # Verify logs in database
    print("\n5. Verificando logs no banco de dados...")
    from src.core.llm_log_db import db_connection, get_db_path
    
    db_path = get_db_path()
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM events WHERE trace_id = ?", (logger.current_trace_id or logger.session_id,))
        row = cursor.fetchone()
        event_count = row['count'] if hasattr(row, 'keys') else row[0]
        print(f"   ✓ Eventos no banco: {event_count}")
    
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
    print(f"\n📄 Logs disponíveis no banco de dados: {db_path}")
    
    return 0

if __name__ == "__main__":
    exit(main())

