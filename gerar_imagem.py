from openai import OpenAI

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

try:
    response = client.images.generate(
        model="openai/dall-e-3",
        prompt="A futuristic robot with neon lights, cyberpunk style",
        size="1024x1024"
    )
    
    print("Tipo:", type(response))
    print("Response:", response)
    
    if isinstance(response, str):
        print("\n>>> URL:", response)
    elif hasattr(response, 'data'):
        print("\n>>> URL:", response.data[0].url)
        
except Exception as e:
    print("ERRO:", str(e))