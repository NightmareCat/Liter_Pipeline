
from pathlib import Path
from datetime import datetime
import shutil
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
    """
    研究课题相似性搜索和文档选择函数
    
    该函数执行以下操作：
    1. 基于研究对象在数据库中搜索最相似的文档
    2. 显示搜索结果及其匹配度
    3. 提供交互式界面让用户选择需要进一步分析的文档
    
    参数:
        无显式参数，但依赖以下全局变量：
        - Research_object: 研究课题对象
        - database_dir: 数据库目录路径
        - top_k: 返回结果数量上限
    
    返回值:
        list: 用户选中的文档列表
    """
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
    """
    处理选中的PDF文件，将其复制到输出目录并生成摘要文档
    
    参数:
        selected: list - 选中的PDF文件名列表（不包含.pdf后缀）
        Research_object_tmp: str - 研究对象的临时标识，用于构建输出目录名
    
    返回值:
        Path对象 - 输出目录的路径
        
    calling:
    research_long_analyse
    """
    # 输出目录：research_output/20250521
    today = datetime.today().strftime("%m%d-%H%M")
    output_root = Path("research_output") / (today + Research_object_tmp)
    output_root.mkdir(parents=True, exist_ok=True)
    
    pdf_directory = Path("liter_source")
    
    # 复制选中的PDF文件到输出目录
    for filename in selected:
        src_file = pdf_directory / (filename + ".pdf")  # 添加.pdf后缀
        dest_file = output_root / (filename + ".pdf")
        shutil.copy(src_file, dest_file)
    
    summarize_all_documents(selected, pdf_directory, output_dir = output_root, R_object =  Research_object_tmp, max_workers = 10)
        
    return  output_root

def summarize_folder_to_report(folder_path: Path, research_topic: str):
    """
    遍历指定文件夹中的所有 Markdown 文件，生成一篇综合调研报告。

    Args:
        folder_path (Path): 包含 .md 文件的目录路径（Path类型）
        research_topic (str): 调研主题
        
    calling:
    submit_summary_to_qwen/submit_summary_to_deepseek
    
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
    output_path = folder_path / ("综合调研报告——" + research_topic+ ".md")
    output_path.write_text(report, encoding="utf-8")
    logger.info(f"✅ 报告已生成：{output_path}")
    

if __name__ == '__main__':

    #手动操作
    process_trigger = 2
    if process_trigger == 1:
        selected = research_sel()   #找到最相关的K篇文章，手动选择其中的N篇
        output_root = divideMD(selected,Research_object)   #将N篇文章输出结构化结果
        summarize_folder_to_report(output_root , Research_object)
    elif process_trigger == 2:
        output_root = Path('.\\research_output\\0612-1046LDPC译码改良')
        Research_object = "LDPC译码改良"
        summarize_folder_to_report(output_root , Research_object)
    elif process_trigger == 3:
        selected = research_sel()   #找到最相关的K篇文章，手动选择其中的N篇
        print(selected)