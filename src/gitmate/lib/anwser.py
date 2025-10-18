import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from mlx_lm import load, generate
from gitmate.config import MLX_MODEL, TRANSFORMERS_MODEL


def get_mlx_ai_response(message: str, git_context_str: str, system_prompt: str) -> str:
    """
    Get AI response using the local MLX model.
    
    Args:
        message: The user's natural language input
        git_context_str: The git repository context as a YAML string
        system_prompt: The system prompt for the model
    
    Returns:
        The AI-generated response as a string
    """
    # Load the model
    model, tokenizer = load(MLX_MODEL)

    # Apply the prompt 
    prompt = (
        "User message: " + message
        + "\n\n---\n\nGit Context (YAML):\n```yaml\n"
        + git_context_str
        + "\n```\n\nEnd of context."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    prompt = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True  # This tells the model the following needs to be assistant message 
    )

    result = generate(model, tokenizer, prompt=prompt, verbose=False)
    
    return result


def get_transformers_ai_response(message: str, git_context_str: str, system_prompt: str) -> str:
    """
    Get AI response using the Transformers library with auto-detected device (GPU/CPU).
    
    Args:
        message: The user's natural language input
        git_context_str: The git repository context as a YAML string
        system_prompt: The system prompt for the model
    
    Returns:
        The AI-generated response as a string
    """
    # Auto-detect device (GPU if available, otherwise CPU)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Load the model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        TRANSFORMERS_MODEL,
        dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None
    )
    tokenizer = AutoTokenizer.from_pretrained(TRANSFORMERS_MODEL)
    
    # Move model to device if not using device_map
    if device == "cpu":
        model = model.to(device)
    
    # Apply the prompt 
    prompt = (
        "User message: " + message
        + "\n\n---\n\nGit Context (YAML):\n```yaml\n"
        + git_context_str
        + "\n```\n\nEnd of context."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    # Apply chat template
    formatted_prompt = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=False
    )
    
    # Tokenize the prompt
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(device)
    
    # Generate response
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode only the new tokens (response part)
    response_tokens = outputs[0][inputs['input_ids'].shape[1]:]
    result = tokenizer.decode(response_tokens, skip_special_tokens=True)
    
    return result


# Create a registry of inference engines
INFERENCE_ENGINES = {
    'mlx': get_mlx_ai_response,
    'transformers': get_transformers_ai_response,
    # Future engines can be easily added here
}

def get_ai_response(inference_engine, message, git_context_str, system_prompt):
    """Get AI response using the specified inference engine."""
    if inference_engine not in INFERENCE_ENGINES:
        # Fallback to default engine if specified engine is not found
        print(f"Warning: Unknown inference engine '{inference_engine}', falling back to 'mlx'")
        inference_engine = 'mlx'
    
    ai_function = INFERENCE_ENGINES[inference_engine]
    return ai_function(message, git_context_str, system_prompt)

