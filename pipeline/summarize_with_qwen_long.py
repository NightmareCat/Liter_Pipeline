# pipeline/summarize_with_qwen_long.py
"""
Qwen长文本PDF摘要生成模块

该模块使用阿里云通义千问API对PDF文献进行摘要生成，
支持长文本处理和文件上传解析功能。
"""

from pathlib import Path
from log_init import setup_logger 
from utils.api_clients import api_manager, wait_for_file_ready

logger = setup_logger(__name__)  # 初始化日志记录器

'''
仅离线模式使用，已注释
calling by research_long_analyse.py
'''

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
    client = api_manager.get_qwen_client()
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
