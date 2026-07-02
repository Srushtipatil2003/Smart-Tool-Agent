from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

API_KEY = "your api key"

embed = GoogleGenAIEmbedding(
    model="models/text-embedding-004",
    api_key=API_KEY
)

print(embed.get_text_embedding("Hello"))