# Liter_Pipeline - 文献处理管道系统

一个用于学术文献处理、摘要生成、嵌入向量计算和相似性搜索的自动化管道系统。

## 功能特性

- 📄 PDF文档解析与文本提取
- 🤖 多模型摘要生成（Qwen、DeepSeek、SiliconFlow）
- 🔍 文本嵌入向量计算与相似性搜索
- 🗄️ 数据库管理与检索
- 🌐 Web界面交互（Streamlit）
- ⚡ 多线程并发处理
- 🔧 统一配置管理

## 安装流程

### 1. 克隆项目

```bash
git clone https://github.com/NightmareCat/Liter_Pipeline.git
cd Liter_Pipeline
```

### 2. 环境配置

推荐使用 Python 3.10.x

```bash
pip install -r requirements.txt
```

### 3. 本地环境配置

#### 预训练模型缓存

```bash
python ./pipeline/get_embedding_bgem3.py
```
运行后将 `/model_cache` 下文件保存（约4.5GB）

#### 离线包下载

```bash
pip download -r requirements.txt -d packages
```

### 4. 离线环境部署

- 将 `/model_cache` 目录放置在项目根目录
- 将 `packages` 目录放置在项目根目录
- 安装离线包：

```bash
pip install --no-index --find-links=packages -r requirements.txt
```

## 配置说明

### API密钥配置（推荐使用.env文件）

系统支持从 `.env` 文件读取API密钥，避免敏感信息泄露：

1. **复制模板文件**：
```bash
cp .env.example .env
```

2. **编辑.env文件**，填入您的实际API密钥：
```env
# 阿里云通义千问API密钥
QWEN_API_KEY=your_actual_qwen_api_key_here

# DeepSeek API密钥  
DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here

# SiliconFlow (Solid) API密钥
SOLID_API_KEY=your_actual_siliconflow_api_key_here
```

3. **确保.gitignore包含.env文件**（系统已默认配置）

### 备选配置方式

如果您仍希望在代码中配置，可以编辑 `config/settings.py` 文件，但**不推荐**此方式：
```python
# API配置（不推荐，请使用.env文件）
API_CONFIG = {
    "qwen": {
        "api_key": "your_qwen_api_key_here"  # 阿里云通义千问API密钥
    },
    "deepseek": {
        "api_key": "your_deepseek_api_key_here"  # DeepSeek API密钥
    },
    "siliconflow": {
        "api_key": "your_siliconflow_api_key_here"  # SiliconFlow API密钥
    }
}
```

### 路径配置

系统会自动创建以下目录结构：
- `liter_source/` - 原始文献PDF文件
- `markdown_out/` - 处理后的Markdown文件
- `embedding_out/` - 嵌入向量输出
- `embedding_qwen_long/` - Qwen长文本嵌入
- `research_output/` - 研究输出结果
- `model_cache/` - 模型缓存文件

## 使用说明

### 数据库管理

```bash
python database_main.py
```

### Web界面检索

```bash
streamlit run streamlit_main.py
```

### 文献处理流程

#### 1. PDF解析
```bash
python pipeline/parse_pdf.py
```

#### 2. 摘要生成
```bash
# 使用Qwen生成摘要
python pipeline/summarize_with_qwen_long.py

# 使用DeepSeek生成摘要  
python pipeline/summarize_with_deepseek.py
```

#### 3. 嵌入向量计算
```bash
# 使用BGE-M3模型
python pipeline/get_embedding_bgem3.py

# 使用Qwen模型
python pipeline/run_embedding_qwen.py
```

#### 4. 研究分析
```bash
# 相似论文搜索
python research_pipeline/search_similar_papers.py

# 长文档分析
python research_pipeline/research_long_analyse.py

# 提交摘要到AI服务
python research_pipeline/submit_summary_to_qwen.py
python research_pipeline/submit_summary_to_deepseek.py
```

## 项目结构

```
Liter_Pipeline/
├── config/                 # 配置文件
│   └── settings.py        # 统一配置管理
├── pipeline/              # 数据处理管道
│   ├── parse_pdf.py       # PDF解析
│   ├── summarize_with_qwen_long.py    # Qwen摘要
│   ├── summarize_with_deepseek.py     # DeepSeek摘要
│   ├── get_embedding_bgem3.py         # BGE-M3嵌入
│   └── run_embedding_qwen.py          # Qwen嵌入
├── research_pipeline/     # 研究分析管道
│   ├── search_similar_papers.py       # 相似论文搜索
│   ├── research_long_analyse.py       # 长文档分析
│   ├── submit_summary_to_qwen.py      # Qwen摘要提交
│   └── submit_summary_to_deepseek.py  # DeepSeek摘要提交
├── utils/                 # 工具函数
│   └── api_clients.py     # API客户端统一管理
├── database_main.py       # 数据库管理主程序
├── research_main.py       # 研究分析主程序
├── streamlit_main.py      # Web界面主程序
├── requirements.txt       # 依赖包列表
└── README.md             # 项目说明文档
```

## API服务支持

### 支持的AI服务
1. **阿里云通义千问 (Qwen)**
   - 模型：qwen-max, qwen-plus, qwen-turbo
   - 用途：文本摘要、内容分析

2. **DeepSeek**
   - 模型：deepseek-chat
   - 用途：文本摘要、对话生成

3. **SiliconFlow**
   - 用途：嵌入向量计算、模型推理

### 统一API管理

系统通过 `utils/api_clients.py` 提供统一的API客户端管理：
- 自动重试机制
- 错误处理统一化
- 配置集中管理
- 多线程支持

## 性能优化

### 多线程处理
系统使用 `ThreadPoolExecutor` 进行并发处理，显著提高批量处理效率。

### 缓存机制
- 模型文件本地缓存
- 处理结果持久化存储
- 避免重复计算

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查 `config/settings.py` 中的API密钥配置
   - 确认API服务配额和权限

2. **内存不足**
   - 减少并发线程数（修改 `MAX_WORKERS` 配置）
   - 分批处理大型文件

3. **模型下载失败**
   - 检查网络连接
   - 手动下载模型文件到 `model_cache/`

### 日志查看

系统会自动生成日志文件，查看最新日志：
```bash
tail -f pipeline.log
```

## 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者：NightmareCat
- GitHub: [https://github.com/NightmareCat](https://github.com/NightmareCat)
- 问题反馈：请通过GitHub Issues提交

## 更新日志

### v1.0.0 (2024-09-10)
- ✅ 完成代码重构和结构优化
- ✅ 实现统一配置管理
- ✅ 集成多AI服务API
- ✅ 添加完整文档
- ✅ 优化性能和多线程处理
