# pipeline/summarize_with_qwen.py
import os
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from log_init import setup_logger 

load_dotenv()
logger = setup_logger(__name__)  # 初始化log信息
client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def wait_for_file_ready(client, file_id, max_retries=30, interval=2):
    for _ in range(max_retries):
        try:
            file_info = client.files.retrieve(file_id)
            if getattr(file_info, "status", "") == "processed":
                return True
        except Exception:
            pass
        time.sleep(interval)
    return False

def upload_and_summarize_pdf(pdf_path: Path, output_dir: Path, prompt: str):
    logger.info(f"[Qwen] Uploading {pdf_path.name} ...")
    file_object = client.files.create(file=pdf_path, purpose="file-extract") # type: ignore
    file_id = file_object.id

    # 新增：等待解析完成
    if not wait_for_file_ready(client, file_id):
        raise Exception(f"文件 {pdf_path.name} 长时间未解析成功，跳过。")

    messages = [
        {'role': 'system', 'content': '你是一个具有通信领域专业背景的研究助手，请你参考专业知识协助我进行文献整理。'},
        {'role': 'system', 'content': f'fileid://{file_id}'},
        {'role': 'user', 'content': prompt}
    ]

    logger.info(f"[Qwen] Generating summary for {pdf_path.name} ...")
    completion = client.chat.completions.create(
        model="qwen-long",
        messages=messages, # type: ignore
        stream=True,
        stream_options={"include_usage": True}
    ) # type: ignore

    summary = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content:
            summary += chunk.choices[0].delta.content

    summary = summary.replace('\\[', '$').replace('\\]', '$')

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "summary.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(summary)
    logger.info(f"[Qwen] Saved summary to {out_path}")
