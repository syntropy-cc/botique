"""
Pricing module for LLM cost calculation.

Handles model pricing configuration and cost calculations.
Prices are stored in the database for easy updates.

Location: src/core/llm_pricing.py
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from .llm_log_db import db_connection, get_db_path, init_database

# Default pricing from current MODEL_COSTS
DEFAULT_PRICING = {
    "deepseek-chat": {"input": 0.00014, "output": 0.00028},
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}


def load_pricing_config(db_path: Optional[Path] = None) -> Dict[str, Dict[str, float]]:
    """
    Load pricing configuration from database.
    
    If no pricing exists, initializes with default values.
    
    Args:
        db_path: Path to database (uses default if None)
        
    Returns:
        Dictionary mapping model names to pricing dict with 'input' and 'output' keys
    """
    if db_path is None:
        db_path = get_db_path()
    
    # Ensure database is initialized
    init_database(db_path)
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT model_name, price_per_1k_input, price_per_1k_output FROM model_pricing")
        rows = cursor.fetchall()
        
        if not rows:
            # Initialize with defaults
            _initialize_default_pricing(db_path)
            return load_pricing_config(db_path)
        
        pricing = {}
        for row in rows:
            model_name = row[0]
            price_input = row[1]
            price_output = row[2]
            pricing[model_name] = {
                "input": price_input,
                "output": price_output,
            }
        
        return pricing


def _initialize_default_pricing(db_path: Optional[Path] = None) -> None:
    """
    Initialize database with default pricing.
    
    Args:
        db_path: Path to database (uses default if None)
    """
    if db_path is None:
        db_path = get_db_path()
    
    init_database(db_path)
    
    now = datetime.utcnow().isoformat() + "Z"
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        for model_name, prices in DEFAULT_PRICING.items():
            cursor.execute("""
                INSERT OR REPLACE INTO model_pricing 
                (model_name, price_per_1k_input, price_per_1k_output, currency, updated_at)
                VALUES (?, ?, ?, 'USD', ?)
            """, (
                model_name,
                prices["input"],
                prices["output"],
                now,
            ))
        
        conn.commit()


def update_pricing(
    model_name: str,
    price_input: float,
    price_output: float,
    currency: str = "USD",
    db_path: Optional[Path] = None,
) -> None:
    """
    Update pricing for a model.
    
    Args:
        model_name: Model identifier (e.g., 'deepseek-chat')
        price_input: Price per 1K input tokens
        price_output: Price per 1K output tokens
        currency: Currency code (default: 'USD')
        db_path: Path to database (uses default if None)
    """
    if db_path is None:
        db_path = get_db_path()
    
    init_database(db_path)
    
    now = datetime.utcnow().isoformat() + "Z"
    
    with db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO model_pricing 
            (model_name, price_per_1k_input, price_per_1k_output, currency, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (model_name, price_input, price_output, currency, now))
        conn.commit()


def calculate_cost(
    model: str,
    tokens_input: Optional[int],
    tokens_output: Optional[int],
    db_path: Optional[Path] = None,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Calculate cost for an LLM call.
    
    Args:
        model: Model identifier
        tokens_input: Number of input tokens
        tokens_output: Number of output tokens
        db_path: Path to database (uses default if None)
        
    Returns:
        Tuple of (cost_input, cost_output, cost_total)
        Returns (None, None, None) if pricing not found or tokens are None
    """
    if tokens_input is None or tokens_output is None:
        return (None, None, None)
    
    pricing_config = load_pricing_config(db_path)
    
    if model not in pricing_config:
        return (None, None, None)
    
    prices = pricing_config[model]
    
    # Calculate costs (prices are per 1K tokens)
    cost_input = (tokens_input / 1000.0) * prices["input"]
    cost_output = (tokens_output / 1000.0) * prices["output"]
    cost_total = cost_input + cost_output
    
    return (cost_input, cost_output, cost_total)

