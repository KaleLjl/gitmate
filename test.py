from mlx_lm import load, generate

model, tokenizer = load("src/gitmate/models/Qwen3-4B-Instruct-2507-MLX-4bit")

prompt = "Write a story about Einstein"

messages = [{"role": "user", "content": prompt}]
prompt = tokenizer.apply_chat_template(
    messages, add_generation_prompt=True
)

text = generate(model, tokenizer, prompt=prompt, verbose=True)

print(text)
