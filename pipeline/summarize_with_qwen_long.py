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
    """
    等待文件处理完成
    
    该函数通过轮询方式检查文件状态，直到文件处理完成或达到最大重试次数
    
    参数:
        client: 文件服务客户端对象，用于调用文件相关API
        file_id: 文件唯一标识符，用于查询文件状态
        max_retries: 最大重试次数，默认为30次
        interval: 轮询间隔时间(秒)，默认为2秒
    
    返回值:
        bool: 如果文件在重试次数内处理完成返回True，否则返回False
    """
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
    """
    上传PDF文件并生成摘要内容。
    
    该函数首先将PDF文件上传至服务端进行解析，待解析完成后，
    使用指定模型对文件内容进行摘要生成，并将结果保存为Markdown文件。
    
    参数:
        pdf_path (Path): 待处理的PDF文件路径。
        output_dir (Path): 摘要输出目录路径。
        prompt (str): 用户提供的摘要生成提示语。
    
    返回值:
        无返回值。摘要内容将被写入到output_dir下的summary.md文件中。
    """
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
        model = "qwen-long-latest",
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
