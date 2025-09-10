#!/usr/bin/env python3
"""
测试.env文件配置功能
"""

import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

print("=== .env文件配置测试 ===")
print()

# 测试环境变量读取
qwen_key = os.getenv("QWEN_API_KEY")
deepseek_key = os.getenv("DEEPSEEK_API_KEY") 
solid_key = os.getenv("SOLID_API_KEY")

print("环境变量读取结果:")
print(f"QWEN_API_KEY: {'已设置' if qwen_key and qwen_key != 'your_qwen_api_key_here' else '未设置或为默认值'}")
print(f"DEEPSEEK_API_KEY: {'已设置' if deepseek_key and deepseek_key != 'your_deepseek_api_key_here' else '未设置或为默认值'}")
print(f"SOLID_API_KEY: {'已设置' if solid_key and solid_key != 'your_siliconflow_api_key_here' else '未设置或为默认值'}")
print()

# 测试配置模块
try:
    from config import settings
    print("✅ 配置模块导入成功")
    
    # 检查API配置
    qwen_config = settings.API_CONFIG["qwen"]
    deepseek_config = settings.API_CONFIG["deepseek"]
    siliconflow_config = settings.API_CONFIG["siliconflow"]
    
    print("✅ API配置读取成功")
    print(f"Qwen API密钥: {'已从环境变量加载' if qwen_config['api_key'] != 'your_qwen_api_key_here' else '使用默认值'}")
    print(f"DeepSeek API密钥: {'已从环境变量加载' if deepseek_config['api_key'] != 'your_deepseek_api_key_here' else '使用默认值'}")
    print(f"SiliconFlow API密钥: {'已从环境变量加载' if siliconflow_config['api_key'] != 'your_siliconflow_api_key_here' else '使用默认值'}")
    
except Exception as e:
    print(f"❌ 配置模块导入失败: {e}")

print()
print("=== 测试完成 ===")
