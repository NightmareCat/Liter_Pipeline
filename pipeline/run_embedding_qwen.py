# pipeline/run_embedding_qwen.py

import os
import json
import re
# import numpy as np
import requests
from pathlib import Path
from tqdm import tqdm
from openai import OpenAI

from log_init import setup_logger 
from pipeline.get_embedding_bgem3 import get_embedding_bge_m3


logger = setup_logger(__name__)  # 初始化log信息

MAX_TOKENS = 8192
MAX_LINES = 10
Embedding_Model_select = 3 # 1-qwen embedding3  2- BGE-M3(本地)  3- BGE-M3（硅基）


def read_markdown(md_path: Path) -> str:
    """读取 summary.md 内容"""
    with open(md_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def get_qwen_embedding(text_list: list) -> list:
    """调用通义 embedding 接口"""
    client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    response = client.embeddings.create(
        input=text_list,
        model="text-embedding-v3"
    )
    return [item.embedding for item in response.data]

def get_query_embedding_bgem3(text_list:list) :
    """
    使用BAAI/bge-m3模型获取文本列表的向量表示
    
    通过调用SiliconFlow API服务，将输入的文本列表转换为对应的向量嵌入表示。
    
    参数:
        text_list (list): 需要转换为向量的文本字符串列表
        
    返回:
        list: 文本对应的向量嵌入列表，每个元素是一个数值向量；如果请求失败则返回空列表
    """
    url = "https://api.siliconflow.cn/v1/embeddings"
    api_key=os.getenv("SOLID_API_KEY")

    payload = {
        "model": "BAAI/bge-m3",
        "input":  text_list,
        "encoding_format": "float"
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        # 提取所有 embedding
        embeddings = [item["embedding"] for item in response_json["data"]]
    else:
        print("Error:", response.status_code, response.text)
        embeddings = []
    return embeddings

def run_embedding_on_folder(root_dir: Path):
    """
    批量处理指定目录下的每个子目录中的 summary.md 文件，生成对应的文本嵌入向量并保存为 JSON 文件。

    参数:
        root_dir (Path): 包含多个子目录的根目录路径，每个子目录中应包含一个 summary.md 文件。

    返回值:
        无返回值。处理结果将写入到与每个子目录同名的 .json 文件中。
    """
       
    # 统计输出
    processed_count = 0
    skipped_count = 0
    
    for subdir in tqdm(list(root_dir.iterdir()), desc="Embedding summaries"):
        if subdir.is_dir():
            md_path = subdir / "summary.md"
            output_path = root_dir / f"{subdir.name}.json"\
            
             # ✅ 若已存在 json 文件，则跳过该任务
            if output_path.exists():
                # logger.error(f"[跳过] {output_path.name} 已存在，未重新提交。")
                skipped_count += 1
                continue
            
            if md_path.exists():
                try:
                    text = read_markdown(md_path)
                    if len(text.strip()) == 0:
                        logger.warning(f"[警告] {md_path} 内容为空，跳过。")
                        continue
                    
                    # 1. 先按照"技术要点"进行切分
                    split_pattern = r"(?=^##\s*技术要点)"  # 保留标题行本身，作为下一段开头
                    chunks = re.split(split_pattern, text, flags=re.MULTILINE)
                    
                    #删去字符串列表的第一项（默认为技术要点）
                    del chunks[0]
                    
                    # 2. 再确保每段不超过 MAX_TOKENS 字符
                    trimmed_chunks = []
                    for chunk in chunks:
                        while len(chunk) > MAX_TOKENS:
                            trimmed_chunks.append(chunk[:MAX_TOKENS])
                            chunk = chunk[MAX_TOKENS:]
                        trimmed_chunks.append(chunk)
                    
                    # 3. 最多取前 10 段，多余的合并进最后一段
                    if len(trimmed_chunks) > MAX_LINES:
                        trimmed_chunks = trimmed_chunks[:MAX_LINES - 1] + ['\n'.join(trimmed_chunks[MAX_LINES - 1:])]
                    if Embedding_Model_select == 1:
                        embedding_list = get_qwen_embedding(trimmed_chunks)
                    elif Embedding_Model_select == 2:
                        embedding_tensor = get_embedding_bge_m3(trimmed_chunks)
                        embedding_list = embedding_tensor.cpu().tolist()
                    elif Embedding_Model_select == 3:
                        embedding_list = get_query_embedding_bgem3(trimmed_chunks)

                    # embedding = np.mean(embedding_list, axis=0).tolist()  # 块之间做平均，舍弃

                    output_data = {
                        "folder": subdir.name,
                        "text": text,#[:500],
                        "embeddings": [  # 每个段落的嵌入及对应原文
                            {
                                "chunk_index": i,
                                "text": chunk,
                                "embedding": vec
                            }
                            for i, (chunk, vec) in enumerate(zip(trimmed_chunks, embedding_list))
                        ]
                    }

                    output_path = root_dir / f"{subdir.name}.json"
                    processed_count += 1
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(output_data, f, ensure_ascii=False, indent=2)

                except Exception as e:
                    logger.error(f"[错误] 处理 {md_path} 时异常：{e}")
                    
    logger.info(f"\n✅ 总共处理: {processed_count} 篇 | 跳过: {skipped_count} 篇\n")