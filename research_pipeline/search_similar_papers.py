# search_similar_papers.py

import os
import json
import numpy as np
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Tuple
from pipeline.get_embedding_bgem3 import get_embedding_bge_m3

load_dotenv()
Embedding_Model_select = 2 # 1-qwen embedding3  2- BGE-M3

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

def load_all_embeddings(folder: Path) -> List[Tuple[str, str, List[Tuple[str, np.ndarray]]]]:
    """
    加载所有论文的 embedding
    返回 (文件名, 预览摘要, 向量列表[(段落文本, 向量)]) 的列表
    """
    results = []
    for file in folder.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "embeddings" in data:
            # 多段嵌入格式
            vec_list = [
                (item["text"], np.array(item["embedding"]))
                for item in data["embeddings"]
            ]
        elif "embedding" in data:
            # 向后兼容单段格式
            vec_list = [(data.get("text", ""), np.array(data["embedding"]))]
        else:
            continue  # 非法数据，跳过

        preview = data.get("text", "")[:200].replace("\n", " ").strip()
        results.append((file.stem, preview, vec_list))

    return results

def search_similar(query: str, data_folder: str, top_k: int = 5) -> List[dict]:
    """
    对给定查询进行匹配，返回结构化结果。
    每个结果包含：论文名、相似度、最相关段落。
    """
    query_vec = get_query_embedding(query)
    if Embedding_Model_select == 1:
        query_vec = get_query_embedding(query)
    elif Embedding_Model_select == 2:
        embedding_tensor = get_embedding_bge_m3(query)
        query_vec = embedding_tensor.cpu().tolist()
    
    papers = load_all_embeddings(Path(data_folder))

    scored = []
    for name, preview, vec_list in papers:
        best_score = -1.0
        best_text = ""
        for para_text, vec in vec_list:
            score = cosine_similarity(query_vec, vec)
            if score > best_score:
                best_score = score
                best_text = para_text
        scored.append({
            "document": name,
            "similarity": round(float(best_score), 4),
            "best_paragraph": best_text
        })

    # 排序后返回 top_k 个结果
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    query = "提升弱场下卫星的干扰抑制能力"
    results = search_similar(query, "embedding_qwen_long", top_k=8)

    print(f"\n🔍 正在匹配课题方向：{query}\n")
    print(f"📄 Top {len(results)} 最相关论文：\n")
    for idx, item in enumerate(results, 1):
        print(f"{idx}. 📁 {item['document']}  (匹配度: {item['similarity']:.4f})")
        print(f"- 最相关段落:\n\n  {item['best_paragraph'][:180]}...\n")
