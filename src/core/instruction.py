"""
Instruction module

Formalizes instructions according to the framework definition:
i = ⟨p, θ, φ_in, φ_out, κ⟩

Where:
- p: Prompt template function p: V* → V*
- θ: LLM configuration vector (model, temperature, max_tokens, ...)
- φ_in: Preprocessing function transforming input data to formatted prompt
- φ_out: Postprocessing function transforming LLM response to structured data
- κ: Memory context requirements (defines which memory is needed)

Execution: exec_i(d, M) = φ_out(LLM_θ(p(φ_in(d), π_κ(M))))

Location: src/core/instruction.py
"""

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from .prompt_registry import register_prompt, get_prompt
from .prompt_helpers import get_or_register_prompt


@dataclass
class Instruction:
    """
    Formal instruction definition i = ⟨p, θ, φ_in, φ_out, κ⟩.
    
    Encapsulates a complete instruction execution workflow:
    1. Preprocessing (φ_in): Transform input data to prompt format
    2. Memory projection (π_κ): Extract required memory context
    3. Template application (p): Combine inputs into final prompt
    4. LLM execution (LLM_θ): Generate response with configuration θ
    5. Postprocessing (φ_out): Transform response to structured output
    
    Framework correspondence:
    - prompt_key + prompt_template: Represents p (prompt template)
    - prompt_id: Version tracking via prompt_registry (part of I)
    - model, temperature, max_tokens: Represents θ (LLM configuration)
    - preprocess: Represents φ_in (input preprocessing)
    - postprocess: Represents φ_out (output postprocessing)
    - memory_requirements: Represents κ (memory context requirements)
    
    The execute() method implements: exec_i(d, M) = φ_out(LLM_θ(p(φ_in(d), π_κ(M))))
    """
    
    # Prompt template p: V* → V*
    prompt_key: str  # Logical identifier (e.g., "post_ideator")
    prompt_template: str  # Raw template string with variables
    prompt_id: Optional[str] = None  # Version ID from prompt_registry (auto-registered)
    
    # LLM configuration θ
    model: str = "deepseek-chat"
    temperature: float = 0.2
    max_tokens: int = 2048
    base_url: Optional[str] = None  # Optional override for LLM client
    
    # Preprocessing function φ_in: D → P
    # Transforms input data dict to formatted prompt string
    preprocess: Optional[Callable[[Dict[str, Any]], str]] = None
    
    # Postprocessing function φ_out: R → D
    # Transforms LLM response string to structured data dict
    postprocess: Optional[Callable[[str], Dict[str, Any]]] = None
    
    # Memory context requirements κ
    # Defines which memory is needed for this instruction
    # Format: {"brief_id": str, "article_slug": str, "trace_history": bool, ...}
    memory_requirements: Optional[Dict[str, Any]] = None
    
    def execute(
        self,
        input_data: Dict[str, Any],
        llm_client: Any,  # HttpLLMClient instance
        memory_context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Execute instruction: exec_i(d, M) = φ_out(LLM_θ(p(φ_in(d), π_κ(M)))).
        
        Complete execution workflow:
        1. φ_in(d): Preprocess input data
        2. π_κ(M): Extract memory context if requirements specified
        3. p(...): Apply template with inputs and memory
        4. LLM_θ(...): Execute LLM with configuration θ
        5. φ_out(...): Postprocess response
        
        Args:
            input_data: Input data dictionary (raw data d)
            llm_client: HttpLLMClient instance for LLM execution
            memory_context: Optional pre-extracted memory context (if None, 
                          instruction should extract based on memory_requirements)
        
        Returns:
            Postprocessed output (structured data after φ_out)
        """
        # Step 1: Preprocess input (φ_in)
        if self.preprocess:
            prompt_input = self.preprocess(input_data)
        else:
            prompt_input = self._default_preprocess(input_data)
        
        # Step 2: Inject memory context if required (π_κ(M))
        if memory_context or self.memory_requirements:
            prompt_input = self._inject_memory_context(prompt_input, memory_context)
        
        # Step 3: Ensure prompt is registered (for version tracking)
        if not self.prompt_id:
            self.prompt_id, _ = get_or_register_prompt(
                prompt_key=self.prompt_key,
                template=self.prompt_template,
            )
        
        # Step 4: Execute LLM (LLM_θ)
        # Use llm_client.generate() with prompt_id for tracking
        response = llm_client.generate(
            prompt=prompt_input,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            prompt_key=self.prompt_key,
            template=self.prompt_template,
            prompt_id=self.prompt_id,
        )
        
        # Step 5: Postprocess response (φ_out)
        if self.postprocess:
            return self.postprocess(response)
        else:
            return self._default_postprocess(response)
    
    def _default_preprocess(self, data: Dict[str, Any]) -> str:
        """
        Default preprocessing: simple variable substitution in template.
        
        Replaces {key} placeholders in template with values from data dict.
        This is a basic implementation of φ_in.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Formatted prompt string
        """
        template = self.prompt_template
        for key, value in data.items():
            # Convert value to string for substitution
            if isinstance(value, (dict, list)):
                # For complex types, convert to JSON string
                value_str = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                value_str = str(value)
            template = template.replace(f"{{{key}}}", value_str)
        return template
    
    def _default_postprocess(self, response: str) -> Dict[str, Any]:
        """
        Default postprocessing: attempt JSON parsing, fallback to raw text.
        
        Tries to parse response as JSON. If parsing fails, returns raw response
        wrapped in a dict. This is a basic implementation of φ_out.
        
        Args:
            response: LLM response string
            
        Returns:
            Structured data dictionary
        """
        response = response.strip()
        
        # Try to extract JSON if wrapped in markdown code blocks
        if "```json" in response:
            # Extract content between ```json and ```
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end != -1:
                response = response[start:end].strip()
        elif "```" in response:
            # Extract content between ``` and ```
            start = response.find("```") + 3
            end = response.find("```", start)
            if end != -1:
                response = response[start:end].strip()
        
        # Try JSON parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: return raw response wrapped in dict
            return {"raw": response, "text": response}
    
    def _inject_memory_context(
        self,
        prompt: str,
        memory_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Inject memory context into prompt.
        
        Implements π_κ(M) - extracts and formats memory context based on
        memory_requirements and injects it into the prompt.
        
        Args:
            prompt: Base prompt string
            memory_context: Pre-extracted memory context (from memory strategy)
        
        Returns:
            Prompt with memory context injected
        """
        if not memory_context:
            return prompt
        
        # Format memory context as a context block
        context_lines = ["=== MEMORY CONTEXT ==="]
        
        for key, value in memory_context.items():
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                value_str = str(value)
            context_lines.append(f"{key}: {value_str}")
        
        context_lines.append("======================")
        context_block = "\n".join(context_lines)
        
        # Inject context at the end of prompt
        return f"{prompt}\n\n{context_block}"
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"Instruction("
            f"prompt_key='{self.prompt_key}', "
            f"model='{self.model}', "
            f"prompt_id={self.prompt_id[:8] if self.prompt_id else None}...)"
        )

