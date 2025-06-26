import faiss
import pandas as pd
import numpy as np
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("MY_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

# Load FAQs and FAISS index
faq_df = pd.read_csv("faq_mapped.csv")
faq_index = faiss.read_index("faq.index")

# Load your FAQ embeddings (must match the FAISS index)
faq_embeddings = np.load("faq_embeddings.npy")  # If you have this saved
assert len(faq_df) == len(
    faq_embeddings), "FAQ size and embeddings do not match"

# Embedding model name compatible with OpenRouter (DeepSeek doesn't do embeddings yet)
# You must use OpenRouter with this name
embedding_model = "openai/text-embedding-ada-002"


def get_embedding(text):
    try:
        response = openai.Embedding.create(
            model=embedding_model,
            input=text
        )
        return np.array(response['data'][0]['embedding'], dtype=np.float32)
    except Exception as e:
        print(f"Embedding error: {e}")
        return None


def search_faq(user_input, top_k=1):
    query_vec = get_embedding(user_input)
    if query_vec is None:
        return "Sorry, I couldn't process your request."

    # Search the FAISS index
    distances, indices = faq_index.search(np.array([query_vec]), top_k)
    context = ""
    for idx in indices[0]:
        context += f"{faq_df.iloc[idx]['question']} → {faq_df.iloc[idx]['answer']}\n"

    return context.strip()


def generate_response(user_input):
    faq_context = search_faq(user_input, top_k=2)

    prompt_messages = [
        {"role": "system", "content": "You are a helpful assistant. Use the following FAQ context to answer questions:\n" + faq_context},
        {"role": "user", "content": user_input}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=prompt_messages,
            max_tokens=300,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"
