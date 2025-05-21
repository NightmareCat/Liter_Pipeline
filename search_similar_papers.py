# search_similar_papers.py

import os
import json
import numpy as np
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Tuple

load_dotenv()

client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def get_query_embedding(query: str) -> np.ndarray:
    response = client.embeddings.create(
        input=query,
        model="text-embedding-v3"
    )
    return np.array(response.data[0].embedding)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def load_all_embeddings(folder: Path) -> List[Tuple[str, str, np.ndarray]]:
    """加载所有论文的 embedding，返回 (文件名, 文本预览, 向量) 列表"""
    results = []
    for file in folder.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        vec = np.array(data["embedding"])
        preview = data["text"][:200].replace("\n", " ").strip()
        results.append((file.stem, preview, vec))
    return results

def search_similar(query: str, data_folder: str, top_k: int = 5):
    print(f"\n🔍 正在匹配课题方向：{query}\n")
    query_vec = get_query_embedding(query)
    papers = load_all_embeddings(Path(data_folder))

    scored = []
    for name, preview, vec in papers:
        score = cosine_similarity(query_vec, vec)
        scored.append((score, name, preview))

    scored.sort(reverse=True)

    print(f"📄 Top {top_k} 最相关论文：\n")
    for rank, (score, name, preview) in enumerate(scored[:top_k], 1):
        print(f"{rank}. 📁 {name}  (相似度: {score:.4f})")
        print(f"   摘要预览: {preview[:80]}...\n")

if __name__ == "__main__":
    # 示例调用
    search_similar("提升弱场下卫星的通信速率", "embedding_qwen_long", top_k=20)
