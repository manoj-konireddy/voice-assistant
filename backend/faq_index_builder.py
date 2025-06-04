import os
import pandas as pd
import numpy as np
import cohere
import faiss
from dotenv import load_dotenv

load_dotenv()

# 🔑 Load API key from .env
api_key = os.getenv("COHERE_API_KEY")
if not api_key:
    raise ValueError("COHERE_API_KEY is not set in the .env file")

co = cohere.Client(api_key)

# 📄 Load FAQ CSV
faq_path = "faq.csv"
faq_df = pd.read_csv(faq_path)
questions = faq_df["question"].tolist()

# 🧠 Get document embeddings
response = co.embed(
    texts=questions,
    model="embed-english-v3.0",
    input_type="search_document"  # Required for v3.0
)
embeddings = np.array(response.embeddings).astype("float32")

# 🧭 Create FAISS index
embedding_size = embeddings.shape[1]
index = faiss.IndexFlatL2(embedding_size)
index.add(embeddings)

# 💾 Save index and questions
faiss.write_index(index, "faq.index")
faq_df.to_csv("faq_mapped.csv", index=False)

print("✅ FAQ index and mapping saved.")
