from pathlib import Path
# from pipeline.parse_pdf import parse_pdf_to_markdown
from pipeline.summarize_with_deepseek import summarize_markdown
from pipeline.summarize_with_qwen_long import upload_and_summarize_pdf
from concurrent.futures import ThreadPoolExecutor, as_completed
from pipeline.run_embedding_qwen import run_embedding_on_folder

from log_init import setup_logger 
from prompts import pdf_analyse_prompts
import subprocess
import shutil
import os

path_liter = Path("liter_source")       # 文档目录
path_markdown = Path("markdown_out")    # MD目录
path_embedding = Path("embedding_out")  # embedding目录
path_embedding_qwen  = Path("embedding_qwen_long") # embedding目录

logger = setup_logger(__name__)  # 初始化log信息

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def run_stage1_pdf_to_md():
    src_dir = path_liter
    out_dir = path_markdown
    ensure_dir(out_dir)

    for pdf in src_dir.glob("*.pdf"):
        folder_name = pdf.stem
        target_folder = out_dir / folder_name
        if target_folder.exists():
            logger.warning(f"[跳过] 已处理过：{folder_name}")
            continue

        logger.info(f"[STEP 1] 处理 PDF → Markdown: {folder_name}")
        ensure_dir(target_folder)

        # 生成 config dict
        config = {
            "pdf_path": str(pdf),
            "output_dir": str(target_folder),
            "lang": "ch",
            "use_angle_cls": True,
            "layout_analysis": True,
            "table": True,
            "ocr_order": True,
            "save_visual": False
        }

        # parse_pdf_to_markdown(config)
        
def run_stage1_pdf_to_md_magic_pdf():
    source_dir = Path("liter_source")
    output_dir = Path("markdown_out")

    pdf_files = list(source_dir.glob("*.pdf"))
    print(f"[MagicPDF] 检测到 {len(pdf_files)} 个PDF文件...")

    for pdf_path in pdf_files:
        pdf_stem = pdf_path.stem
        target_dir = output_dir / pdf_stem
        final_md_path = target_dir / f"{pdf_stem}.md"

        if final_md_path.exists():
            print(f"[MagicPDF] 已存在，跳过：{final_md_path}")
            continue

        target_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "magic-pdf",
            "-p", str(pdf_path),
            "--output-dir", str(target_dir)
        ]

        print(f"[MagicPDF] 处理中：{pdf_path.name}")
        try:
            subprocess.run(cmd, check=True)
            print(f"[MagicPDF] ✅ 处理完成，开始整理文件结构...")

            # 获取magic-pdf嵌套路径
            nested_auto_dir = target_dir / pdf_stem / "auto"
            if not nested_auto_dir.exists():
                print(f"[MagicPDF] ⚠ 未找到预期的输出目录：{nested_auto_dir}")
                continue

            # 遍历并复制 auto/ 下的所有内容
            for item in nested_auto_dir.iterdir():
                dest_path = target_dir / item.name
                if item.is_file():
                    shutil.copy2(item, dest_path)
                elif item.is_dir():
                    dest_path.mkdir(exist_ok=True)
                    for subitem in item.iterdir():
                        shutil.copy2(subitem, dest_path / subitem.name)
                        
            shutil.rmtree(target_dir / pdf_stem) #复制后删除原auto目录
            print(f"[MagicPDF] ✅ 文件整理完成：{pdf_stem}")

        except subprocess.CalledProcessError as e:
            print(f"[MagicPDF] ❌ 处理失败：{pdf_path.name}")
            print(e)

def run_stage2_md_to_summary():
    markdown_root = path_markdown
    summary_root = path_embedding
    max_workers = 8  # 可根据 CPU 核心和网络能力调整

    tasks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for subdir in markdown_root.iterdir():
            if not subdir.is_dir():
                continue

            md_files = list(subdir.glob("*.md"))
            if not md_files:
                continue

            target_dir = summary_root / subdir.name
            if target_dir.exists():
                print(f"[跳过] 已存在总结目录：{target_dir}")
                continue

            md_file = md_files[0]  # 每个子目录只取一个 md 文件处理
            out_dir = summary_root / subdir.name
            #  动态传入配置（不写入 config.json）
            summarize_cfg = {
                "model": "deepseek-chat",
                "prompt_template": pdf_analyse_prompts,
                "output_dir": str(out_dir)
            }

            
            print(f"[提交] 总结任务：{md_file}")
            tasks.append(
                executor.submit(summarize_markdown, str(md_file), summarize_cfg)
            )

        for future in as_completed(tasks):
            try:
                result = future.result()
                print(f"[完成] {result}")
            except Exception as e:
                print(f"[错误] 总结失败：{e}")


def run_stage12_pdf_to_summary():
    source_dir = path_liter
    target_root = path_embedding_qwen
    prompt = pdf_analyse_prompts
    task_num = 8 # 设置最大线程数（你有20线程，但I/O绑定任务建议使用8-12个）
    
    # 获取所有未处理的 PDF 文件
    tasks = []
    for pdf_path in source_dir.glob("*.pdf"):
        pdf_name = pdf_path.stem
        target_dir = target_root / pdf_name
        if (target_dir / "summary.md").exists():
            # logger.warning(f"[跳过] {pdf_name} 已存在摘要，跳过处理。")
            continue
        tasks.append((pdf_path, target_dir))

    logger.info(f"[计划处理] 共需处理 {len(tasks)} 个 PDF 文件。\n")

    max_workers = min(task_num, os.cpu_count())

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(upload_and_summarize_pdf, pdf_path, target_dir, prompt): pdf_path.name
            for pdf_path, target_dir in tasks
        }

        for future in as_completed(futures):
            pdf_name = futures[future]
            try:
                future.result()
                logger.info(f"[完成] {pdf_name} 摘要生成成功。\n")
            except Exception as e:
                logger.error(f"[错误] 处理 {pdf_name} 时出错：{e}\n")

def main():
    # run_stage1_pdf_to_md() #使用基础OCR
    # run_stage1_pdf_to_md_magic_pdf()  # 使用 magic-pdf
    # run_stage2_md_to_summary() #使用 Deepseek 进行语义压缩
    run_stage12_pdf_to_summary() #使用 Qwen long 进行pdf信息压缩
    run_embedding_on_folder(path_embedding_qwen) #使用 Qwen embeddingv3模型对每个知识点语义向量化处理
    
if __name__ == "__main__":
    main()
