import faiss
import pandas as pd
import numpy as np
import cohere
import os
from dotenv import load_dotenv

load_dotenv()
co = cohere.Client(os.getenv("COHERE_API_KEY"))

faq_df = pd.read_csv("faq_mapped.csv")
faq_index = faiss.read_index("faq.index")


def search_faq(query):
    try:
        # Convert query to embedding
        response = co.embed(
            texts=[query], model="embed-english-v3.0", input_type="search_query")
        query_embedding = np.array(response.embeddings).astype("float32")

        D, I = faq_index.search(query_embedding, k=1)
        top_idx = I[0][0]
        distance = D[0][0]

        if distance < 1.0:
            return faq_df.iloc[top_idx]["answer"]
        else:
            return None
    except Exception as e:
        return None
