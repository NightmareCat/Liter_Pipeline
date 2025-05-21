# pipeline/run_embedding_qwen.py

import os
import json
from pathlib import Path
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
from log_init import setup_logger 

load_dotenv()
logger = setup_logger(__name__)  # 初始化log信息

client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def read_markdown(md_path: Path) -> str:
    """读取 summary.md 内容"""
    with open(md_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def get_qwen_embedding(text: str) -> list:
    """调用通义 embedding 接口"""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-v3"
    )
    return response.data[0].embedding

def run_embedding_on_folder(root_dir: Path):
    """批量处理每个子目录中的 summary.md，生成 embedding"""
    for subdir in tqdm(list(root_dir.iterdir()), desc="Embedding summaries"):
        if subdir.is_dir():
            md_path = subdir / "summary.md"
            if md_path.exists():
                try:
                    text = read_markdown(md_path)
                    if len(text.strip()) == 0:
                        logger.warning(f"[警告] {md_path} 内容为空，跳过。")
                        continue

                    embedding = get_qwen_embedding(text)

                    output_data = {
                        "folder": subdir.name,
                        "text": text[:1000],  # 前1000字符预览
                        "embedding": embedding
                    }

                    output_path = root_dir / f"{subdir.name}.json"
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(output_data, f, ensure_ascii=False, indent=2)

                except Exception as e:
                    logger.error(f"[错误] 处理 {md_path} 时异常：{e}")
