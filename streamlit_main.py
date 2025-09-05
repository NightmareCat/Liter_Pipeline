# streamlit_main.py
import os
os.environ["STREAMLIT_WATCHER_TYPE"] = "none"
import streamlit as st
from pathlib import Path
from research_pipeline.search_similar_papers import search_similar
from research_main import summarize_folder_to_report,divideMD

PDF_DIR = "./liter_source"


# 页面配置
st.set_page_config(page_title="相似论文搜索", layout="wide")



# 全局变量缓存
if "scored_results" not in st.session_state:
    st.session_state.scored_results = []
if "selected_docs" not in st.session_state:
    st.session_state.selected_docs = []
if "search_done" not in st.session_state:
    st.session_state.search_done = False
# 初始化 session_state 中的标记变量
if "disable_b" not in st.session_state:
    st.session_state.disable_b = True
# 按钮 A 的回调函数：设置 disable_b 为 True
def disable_b_callback():
    st.session_state.disable_b = False


# Sidebar 输入参数
st.sidebar.title("🔍 设置搜索参数")
database_dir = st.sidebar.text_input(" 文献嵌入库路径", value="embedding_qwen_long")
research_object = st.sidebar.text_area(" 研究课题方向", value="提高卫星系统的接入成功率", height=120)
top_k = st.sidebar.number_input(" 返回相似论文数量", min_value=1, max_value=50, value=20, step=1)

run_button = st.sidebar.button(" 开始匹配")
confirm_button = st.sidebar.button(" 确认选择", on_click=disable_b_callback)
summary_button =st.sidebar.button("开始总结选中文章", disabled=st.session_state.disable_b)


# 主界面标题
st.title(" 相似论文智能检索系统")

# 主功能：运行 search_similar
if run_button:
    """运行匹配按钮"""
    with st.spinner("正在匹配中，请稍候..."):
        try:
            scored = search_similar(research_object, database_dir, top_k)
            st.session_state.scored_results = scored
            st.session_state.selected_docs = []#[item["document"] for item in scored]  # 默认全选
            st.session_state.search_done = True
        except Exception as e:
            st.error(f"❌ 匹配过程中发生错误：{e}")
            st.session_state.search_done = False

if confirm_button:
    """确认选择按钮"""
    selected = st.session_state.selected_docs
    if selected:
        print(f"\n 你选择了以下{len(selected)}篇文档进行分析：\n")
        print(f"\n 调研课题：{research_object}\n")
        for item in selected:
            print(f" - {item}")
    else:
        print("\n⚠️ 你没有选择任何文档。")

if summary_button:
    """总结按钮"""
    selected = st.session_state.selected_docs
    print(f"\n 调研课题：{research_object}\n")
    output_root = divideMD(selected, research_object)   #将N篇文章输出结构化结果
    summarize_folder_to_report(output_root , research_object)

# ✅ 展示逻辑从 if run_button 中拿出来，保持页面刷新后依然显示
if st.session_state.search_done and st.session_state.scored_results:
    st.success(f"已找到 {len(st.session_state.scored_results)} 篇最相关论文：")

    for idx, item in enumerate(st.session_state.scored_results, 1):
        doc_key = f"select_{item['document']}"
        checked = st.checkbox(f"{idx}. 📁 {item['document']} (匹配度: {item['similarity']:.4f})",
                              value=item["document"] in st.session_state.selected_docs,
                              key=doc_key)

        # ✅ 同步更新选择状态
        if checked and item["document"] not in st.session_state.selected_docs:
            st.session_state.selected_docs.append(item["document"])
        elif not checked and item["document"] in st.session_state.selected_docs:
            st.session_state.selected_docs.remove(item["document"])

        pdf_path = os.path.join(PDF_DIR, item["document"] + ".pdf")
        if os.path.exists(pdf_path):
            pdf_path = os.path.join(PDF_DIR, item["document"] + ".pdf")
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_data = f.read()
                st.download_button(
                    label="📥 下载原始 PDF",
                    data=pdf_data,
                    file_name=item["document"] + ".pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("⚠️ 原始 PDF 文件不存在")
        else:
            st.warning("⚠️ 原始 PDF 文件不存在")

        st.markdown("**最相关段落：**")
        st.info(item["best_paragraph"])
        st.divider()
