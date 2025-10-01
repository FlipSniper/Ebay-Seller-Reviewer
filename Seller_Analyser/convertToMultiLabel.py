import os
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm

# 1. Load data
df_train = pd.read_csv("data/train.txt", sep="\t", header=None, names=["text"])
review_texts = df_train["text"].tolist()

# 2. Define issue descriptions
issue_descriptions = {
    "late_delivery": "The item arrived later than expected.",
    "poor_packaging": "The packaging was damaged or insufficient.",
    "wrong_item": "The item received was not what was ordered.",
    "low_quality": "The product quality was worse than expected.",
    "no_communication": "The seller did not respond to messages.",
    "refund_problem": "Issues with getting a refund or return.",
}
issue_texts = list(issue_descriptions.values())
issue_keys = list(issue_descriptions.keys())

# 3. Load model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 4. Load or encode issue embeddings
if os.path.exists("data/issue_embeddings.pt"):
    issue_embeddings = torch.load("data/issue_embeddings.pt")
else:
    issue_embeddings = model.encode(issue_texts, convert_to_tensor=True)
    torch.save(issue_embeddings, "data/issue_embeddings.pt")

# 5. Load or encode review embeddings
if os.path.exists("data/review_embeddings.pt"):
    review_embeddings = torch.load("data/review_embeddings.pt")
else:
    review_embeddings = model.encode(
        review_texts,
        batch_size=128,
        convert_to_tensor=True,
        show_progress_bar=True
    )
    torch.save(review_embeddings, "data/review_embeddings.pt")

# 6. Compute cosine similarity matrix
similarity_matrix = util.cos_sim(review_embeddings, issue_embeddings)

# 7. Tag reviews based on threshold
threshold = 0.4
tags = []
for row in tqdm(similarity_matrix, desc="🔖 Tagging reviews"):
    matched = [issue_keys[i] for i, score in enumerate(row) if score > threshold]
    tags.append(matched)

df_train["issues"] = tags

# 8. Save results
df_train.to_csv("data/train_tagged.csv", index=False)
print("✅ Done! Tagged 3.6M reviews and saved embeddings.")
