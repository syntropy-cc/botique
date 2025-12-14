#!/usr/bin/env python3
"""
Test script for prompt versioning system.

Demonstrates:
- Creating two versions of the same prompt
- Executing both in LLM calls
- Logging events with prompt_id
- Comparing metrics between versions

Location: scripts/test_prompt_versioning.py
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.llm_log_db import init_database, get_db_path, db_connection
from core.llm_logger import LLMLogger
from core.prompt_registry import register_prompt, list_prompt_versions, get_prompt
from core.llm_log_queries import (
    get_prompt_versions_with_usage,
    compare_prompt_versions,
    get_prompt_quality_stats,
)


def test_prompt_versioning():
    """Test prompt versioning system end-to-end."""
    
    print("=" * 80)
    print("TESTE DO SISTEMA DE VERSIONAMENTO DE PROMPTS")
    print("=" * 80)
    print()
    
    # Initialize database
    db_path = get_db_path()
    print(f"📊 Inicializando banco de dados: {db_path}")
    init_database(db_path)
    print("✅ Banco de dados inicializado\n")
    
    # Create logger
    logger = LLMLogger(db_path=db_path, use_json=False)
    trace_id = logger.create_trace(name="test_prompt_versioning")
    print(f"📝 Trace criado: {trace_id}\n")
    
    # Register prompts - versioning is automatic with duplicate prevention
    print("📋 Registrando prompts (versionamento automático + prevenção de duplicatas)...")
    
    prompt_key = "test_summarize"
    
    # First registration: will create v1
    template_v1 = "Summarize the following text in one sentence:\n\n{text}"
    prompt_id_v1, version_v1 = register_prompt(
        prompt_key=prompt_key,
        template=template_v1,
        description="Initial simple version",
        metadata={"author": "test", "experiment": "baseline"},
        db_path=db_path,
    )
    print(f"  ✅ {version_v1} registrada: {prompt_id_v1}")
    
    # Second registration with identical template: should return v1 (no duplicate)
    prompt_id_v1_duplicate, version_v1_duplicate = register_prompt(
        prompt_key=prompt_key,
        template=template_v1,  # Identical to first
        description="Initial simple version",
        db_path=db_path,
    )
    assert prompt_id_v1_duplicate == prompt_id_v1, "Should return same prompt_id for identical template"
    assert version_v1_duplicate == version_v1, "Should return same version for identical template"
    print(f"  ✅ Template idêntico retorna {version_v1_duplicate} existente (sem duplicata)")
    
    # Third registration with different template: will create v2
    template_v2 = """You are an expert summarizer. 
Summarize the following text in one clear, concise sentence.
Focus on the main idea and key points.

Text:
{text}"""
    prompt_id_v2, version_v2 = register_prompt(
        prompt_key=prompt_key,
        template=template_v2,
        description="Enhanced version with instructions",
        metadata={"author": "test", "experiment": "enhanced"},
        db_path=db_path,
    )
    print(f"  ✅ {version_v2} registrada: {prompt_id_v2}")
    
    # Fourth registration with identical template to v2: should return v2 (no duplicate)
    prompt_id_v2_duplicate, version_v2_duplicate = register_prompt(
        prompt_key=prompt_key,
        template=template_v2,  # Identical to v2
        description="Enhanced version with instructions",
        db_path=db_path,
    )
    assert prompt_id_v2_duplicate == prompt_id_v2, "Should return same prompt_id for identical template"
    assert version_v2_duplicate == version_v2, "Should return same version for identical template"
    print(f"  ✅ Template idêntico retorna {version_v2_duplicate} existente (sem duplicata)\n")
    
    # Verify no duplicates were created
    versions = list_prompt_versions(prompt_key, db_path=db_path)
    assert len(versions) == 2, f"Should have exactly 2 versions, got {len(versions)}"
    print(f"  ✅ Verificação: {len(versions)} versões na tabela (sem duplicatas)\n")
    
    # Verify both versions exist
    versions = list_prompt_versions(prompt_key, db_path=db_path)
    print(f"📚 Versões registradas para '{prompt_key}': {len(versions)}")
    for v in versions:
        print(f"  - {v['version']}: {v['description']}")
    print()
    
    # Simulate LLM calls with both versions
    print("🤖 Simulando chamadas LLM com ambas as versões...")
    
    test_text = "Artificial intelligence is transforming industries worldwide. Companies are adopting AI to improve efficiency and create new products."
    
    # Call with version 1
    prompt_v1 = template_v1.format(text=test_text)
    print(f"  📤 Chamada com v1...")
    time.sleep(0.1)  # Simulate API call
    event_id_v1 = logger.log_llm_event(
        trace_id=trace_id,
        name="test_summarize_v1",
        model="deepseek-chat",
        input_text=prompt_v1,
        input_obj={"prompt": prompt_v1, "temperature": 0.2},
        output_text="AI is transforming industries by improving efficiency and enabling new products.",
        output_obj={"content": "AI is transforming industries by improving efficiency and enabling new products."},
        duration_ms=150.5,
        tokens_input=25,
        tokens_output=15,
        tokens_total=40,
        prompt_id=prompt_id_v1,
        metadata={"test": True, "version": "v1"},
    )
    print(f"    ✅ Evento registrado: {event_id_v1}")
    
    # Call with version 2
    prompt_v2 = template_v2.format(text=test_text)
    print(f"  📤 Chamada com v2...")
    time.sleep(0.1)  # Simulate API call
    event_id_v2 = logger.log_llm_event(
        trace_id=trace_id,
        name="test_summarize_v2",
        model="deepseek-chat",
        input_text=prompt_v2,
        input_obj={"prompt": prompt_v2, "temperature": 0.2},
        output_text="Artificial intelligence is revolutionizing global industries, enabling companies to enhance operational efficiency and develop innovative products.",
        output_obj={"content": "Artificial intelligence is revolutionizing global industries, enabling companies to enhance operational efficiency and develop innovative products."},
        duration_ms=180.2,
        tokens_input=45,
        tokens_output=20,
        tokens_total=65,
        prompt_id=prompt_id_v2,
        metadata={"test": True, "version": "v2"},
    )
    print(f"    ✅ Evento registrado: {event_id_v2}\n")
    
    # Verify events are linked to prompts
    print("🔍 Verificando ligação entre eventos e prompts...")
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT prompt_id FROM events WHERE id = ?", (event_id_v1,))
        row_v1 = cursor.fetchone()
        assert row_v1["prompt_id"] == prompt_id_v1, "Event v1 should reference prompt_id_v1"
        print(f"  ✅ Evento v1 ligado ao prompt: {row_v1['prompt_id']}")
        
        cursor.execute("SELECT prompt_id FROM events WHERE id = ?", (event_id_v2,))
        row_v2 = cursor.fetchone()
        assert row_v2["prompt_id"] == prompt_id_v2, "Event v2 should reference prompt_id_v2"
        print(f"  ✅ Evento v2 ligado ao prompt: {row_v2['prompt_id']}\n")
    
    # Query usage statistics
    print("📊 Estatísticas de uso por versão:")
    usage_stats = get_prompt_versions_with_usage(prompt_key, db_path=db_path)
    for version in usage_stats:
        print(f"  - {version['version']}: {version['usage_count']} uso(s)")
    print()
    
    # Compare versions
    print("📈 Comparação entre versões:")
    comparison = compare_prompt_versions(prompt_key, db_path=db_path)
    for version in comparison["versions"]:
        print(f"  Versão {version['version']}:")
        print(f"    - Eventos: {version['event_count']}")
        print(f"    - Tokens totais: {version['total_tokens']}")
        print(f"    - Custo total: ${version['total_cost']:.6f}")
        print(f"    - Custo médio por evento: ${version['avg_cost_per_event']:.6f}")
        print(f"    - Duração média: {version['avg_duration_ms']:.1f}ms" if version['avg_duration_ms'] else "    - Duração média: N/A")
    print()
    
    
    # Retrieve prompt by ID
    print("🔎 Recuperando prompt por ID...")
    retrieved = get_prompt(prompt_id_v1, db_path=db_path)
    assert retrieved is not None, "Should retrieve prompt"
    assert retrieved["prompt_key"] == prompt_key, "Prompt key should match"
    assert retrieved["version"] == "v1", "Version should match"
    print(f"  ✅ Prompt recuperado: {retrieved['prompt_key']} v{retrieved['version']}\n")
    
    print("=" * 80)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 80)
    print()
    print("Resumo:")
    print(f"  - Prompt key: {prompt_key}")
    print(f"  - Versões criadas: {len(versions)}")
    print(f"  - Eventos LLM registrados: 2")
    print(f"  - Banco de dados: {db_path}")
    print()


if __name__ == "__main__":
    try:
        test_prompt_versioning()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

