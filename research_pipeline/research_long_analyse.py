from importlib.machinery import PathFinder
import os
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from prompts import devide_prompt
from log_init import setup_logger 

logger = setup_logger(__name__)  # 初始化log信息


def process_single_pdf(document_name: str, pdf_dir: Path ,output_root:Path,R_object:str) -> str:
    """
    对单个 PDF 进行上传、总结，并输出 Markdown 文件
    返回日志字符串
    """
    Research_object = R_object
        # 初始化 Qwen 客户端
    client = OpenAI(
        api_key=os.getenv("QWEN_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    pdf_path = pdf_dir / f"{document_name}.pdf"
    if not pdf_path.exists():
        logger.error(f"[跳过] 文件不存在: {pdf_path}")
        return ' '

    try:
        # 上传 PDF 文件
        file_obj = client.files.create(file=pdf_path, purpose="file-extract") # type: ignore
        file_id = file_obj.id
        logger.info(f"[上传成功] {document_name} → file-id: {file_id}")

        # 调用 qwen-long 进行内容总结
        completion = client.chat.completions.create(
            model="qwen-long",
            messages=[
                {'role': 'system', 'content': '你是一个具有通信领域专业背景的研究助手，请你参考专业知识协助我进行文献整理'},
                {'role': 'system', 'content': f'fileid://{file_id}'},
                {'role': 'user', 'content': devide_prompt.format(Research_object=Research_object)}
            ],
            stream=True,
            stream_options={"include_usage": True}
        )

        # 拼接 stream 输出
        full_content = ""
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                full_content += chunk.choices[0].delta.content
        
        #修复long模型不会转换latex标识符的问题        
        full_content = full_content.replace('\\[', '$').replace('\\]', '$')
        
        # 保存为 Markdown 文件
        md_path = output_root / f"{document_name}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# 论文总结 - {document_name}\n\n")
            f.write(full_content.strip())

        logger.info(f"[完成] {document_name} 总结保存至 {md_path.name}")

    except Exception as e:
        logger.error(f"[错误] {document_name} 处理失败: {e}")

def summarize_all_documents(document_list: List[str], pdf_dir: Path,  output_dir: Path  , R_object: str, max_workers: int = 4 ):
    """
    多线程方式并发处理文档
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_doc = {
            executor.submit(process_single_pdf, doc, pdf_dir, output_dir,R_object): doc
            for doc in document_list
        }

        for future in as_completed(future_to_doc):
            if future.result() is not None:
                print(future.result())

if __name__ == "__main__":
    # 示例输入：请替换为实际 PDF 文件名（无扩展名）
    example_documents = [
        "面向低轨星座的空间频谱兼容分析方法研究_张少峰",
        "面向低轨卫星的协同频谱感知与共享技术研究_王运峰"
    ]
    pdf_directory = Path("liter_source")
    Research_object = '提升弱场下卫星的终端接入能力'
    
    # 输出目录：research_output/20250521
    today = datetime.today().strftime("%m%d-%H%M")
    output_root = Path("research_output") / today
    output_root.mkdir(parents=True, exist_ok=True)

    summarize_all_documents(example_documents, pdf_directory, max_workers=8, output_dir = output_root, R_object = Research_object)



