
from pathlib import Path
from datetime import datetime
# import os
import questionary
from log_init import setup_logger 
from research_pipeline.research_long_analyse import summarize_all_documents
from research_pipeline.search_similar_papers import search_similar
from research_pipeline.submit_summary_to_qwen import submit_summary_to_qwen
from research_pipeline.submit_summary_to_deepseek import submit_summary_to_deepseek

database_dir = "embedding_qwen_long"   #选择使用的二级处理文献库
Research_object = '在卫星通信系统中的信号处理优化方案' 
top_k = 10   #找到n篇最相关文章
summary_model = 2 #1-qwen 2-deepseek

logger = setup_logger(__name__)  # 初始化log信息

def research_sel():
    scored = search_similar(Research_object, database_dir, top_k)

    print(f"\n🔍 正在匹配课题方向：{Research_object}\n")
    print(f"📄 Top {len(scored)} 最相关论文：\n")
    for idx, item in enumerate(scored, 1):
        print(f"{idx}. 📁 {item['document']}  (匹配度: {item['similarity']:.4f})")
        print(f"- 最相关段落:\n\n  {item['best_paragraph'][:180]}...\n")
        
        
    document_list = [item["document"] for item in scored]

    # 创建多选框，默认全选
    selected = questionary.checkbox(
        "请选择需要进一步分析的文档（空格选择，回车确认）:",
        choices=[{"name": doc, "checked": True} for doc in document_list]
    ).ask()  # .ask() 执行交互

    print("你选择了:")
    for item in selected:
        print(item)

    return selected

def divideMD(selected, Research_object_tmp):
    # 输出目录：research_output/20250521
    today = datetime.today().strftime("%m%d-%H%M")
    output_root = Path("research_output") / (today + Research_object_tmp)
    output_root.mkdir(parents=True, exist_ok=True)
    
    pdf_directory = Path("liter_source")
    
    summarize_all_documents(selected, pdf_directory, output_dir = output_root, R_object =  Research_object_tmp, max_workers = 10)
        
    return  output_root

def summarize_folder_to_report(folder_path: Path, research_topic: str):
    """
    遍历指定文件夹中的所有 Markdown 文件，生成一篇综合调研报告。

    Args:
        folder_path (Path): 包含 .md 文件的目录路径（Path类型）
        research_topic (str): 调研主题
    """
    if not folder_path.exists() or not folder_path.is_dir():
        logger.error(f"❌ 路径不存在或不是文件夹: {folder_path}")
        return

    md_files = sorted(folder_path.glob("*.md"))
    if not md_files:
        logger.error("⚠️ 未找到任何 Markdown 文件。")
        return
    
    logger.info(f"📄 已读取 Markdown 文件 {len(md_files)} 个。")

    # 读取所有 Markdown 文件内容
    markdown_contents = [f.read_text(encoding="utf-8") for f in md_files]

    # 调用 API 生成报告
    if summary_model == 1:
        logger.info('正在使用Qwen Max模型进行总结')
        report = submit_summary_to_qwen(research_topic, markdown_contents)
        
    elif summary_model == 2:
        logger.info('正在使用Deepseek v3模型进行总结')
        report = submit_summary_to_deepseek(research_topic, markdown_contents)
     
    report = report.replace("][", "] [")  #解决typora的渲染问题
   
    # 输出报告
    output_path = folder_path / (research_topic+"——综合调研报告.md")
    output_path.write_text(report, encoding="utf-8")
    logger.info(f"✅ 报告已生成：{output_path}")
    

if __name__ == '__main__':

    process_trigger = 2
    if process_trigger == 1:
        selected = research_sel()   #找到最相关的K篇文章，手动选择其中的N篇
        output_root = divideMD(selected,Research_object)   #将N篇文章输出结构化结果
    elif process_trigger == 2:
        output_root = Path('.\\research_output\\0527-1519基于OTFS提升传输速率')
        Research_object = "基于OTFS提升传输速率"
        
    summarize_folder_to_report(output_root , Research_object)