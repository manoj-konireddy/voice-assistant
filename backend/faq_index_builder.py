# backend/faq_index_builder.py

import os
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

print("🔄 Generating embeddings using local model...")

# Set path to your CSV file
faq_path = os.path.join(os.path.dirname(__file__), "faq.csv")
print(f"🔍 Looking for file at: {faq_path}")

# Load FAQ CSV
faq_df = pd.read_csv(faq_path)
questions = faq_df["question"].tolist()

# Load local embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')  # lightweight and fast

# Generate embeddings
embeddings = model.encode(questions, convert_to_numpy=True).astype("float32")

# Save embeddings
np.save("faq_embeddings.npy", embeddings)

# Create and save FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, "faq.index")

# Save mapped FAQ for use in search
faq_df.to_csv("faq_mapped.csv", index=False)

print("✅ Embeddings, index, and mapped FAQ saved using SentenceTransformer.")
