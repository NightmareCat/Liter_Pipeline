# pipeline/run_embedding_qwen.py

import os
import json
import re
import numpy as np
from pathlib import Path
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
from log_init import setup_logger 

load_dotenv()
logger = setup_logger(__name__)  # 初始化log信息

MAX_TOKENS = 8192
MAX_LINES = 10

client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def read_markdown(md_path: Path) -> str:
    """读取 summary.md 内容"""
    with open(md_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def get_qwen_embedding(text_list: list) -> list:
    """调用通义 embedding 接口"""
    response = client.embeddings.create(
        input=text_list,
        model="text-embedding-v3"
    )
    return [item.embedding for item in response.data]

def run_embedding_on_folder(root_dir: Path):
    """批量处理每个子目录中的 summary.md，生成 embedding"""
       
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
                    
                    # 1. 先按照技术要点进行切分
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

                    embedding_list = get_qwen_embedding(trimmed_chunks)
                    embedding = np.mean(embedding_list, axis=0).tolist()

                    output_data = {
                        "folder": subdir.name,
                        "text": text[:500],
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