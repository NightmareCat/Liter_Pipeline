# streamlit_main.py

import streamlit as st
import os
from pathlib import Path
from research_pipeline.search_similar_papers import search_similar

PDF_DIR = "./liter_source"

# 页面配置
st.set_page_config(page_title="相似论文搜索", layout="wide")

# Sidebar 输入参数
st.sidebar.title("🔍 设置搜索参数")
database_dir = st.sidebar.text_input(" 文献嵌入库路径", value="embedding_qwen_long")
research_object = st.sidebar.text_area(" 研究课题方向", value="在卫星通信系统中的信号处理优化方案", height=120)
top_k = st.sidebar.number_input(" 返回相似论文数量", min_value=1, max_value=50, value=20, step=1)

run_button = st.sidebar.button(" 开始匹配")
confirm_button = st.sidebar.button(" 确认选择")

# 全局变量缓存
if "scored_results" not in st.session_state:
    st.session_state.scored_results = []
if "selected_docs" not in st.session_state:
    st.session_state.selected_docs = []
if "search_done" not in st.session_state:
    st.session_state.search_done = False

# 主界面标题
st.title(" 相似论文智能检索系统")

# 主功能：运行 search_similar
if run_button:
    with st.spinner("正在匹配中，请稍候..."):
        try:
            scored = search_similar(research_object, database_dir, top_k)
            st.session_state.scored_results = scored
            st.session_state.selected_docs = [item["document"] for item in scored]  # 默认全选
            st.session_state.search_done = True
        except Exception as e:
            st.error(f"❌ 匹配过程中发生错误：{e}")
            st.session_state.search_done = False

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

