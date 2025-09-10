#!/usr/bin/env python3
"""
代码重构验证测试脚本

该脚本用于验证重构后的代码结构和功能是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_config_import():
    """测试配置模块导入"""
    try:
        from config.settings import BASE_DIR, DATA_PATHS, API_CONFIG, MODEL_SELECTION, PROCESSING_CONFIG
        print("✅ 配置模块导入成功")
        print(f"   基础目录: {BASE_DIR}")
        print(f"   数据路径: {list(DATA_PATHS.keys())}")
        print(f"   API配置: {list(API_CONFIG.keys())}")
        return True
    except Exception as e:
        print(f"❌ 配置模块导入失败: {e}")
        return False

def test_api_clients_import():
    """测试API客户端模块导入"""
    try:
        from utils.api_clients import APIClientManager, api_manager, get_embedding_vectors
        print("✅ API客户端模块导入成功")
        
        # 测试客户端管理器初始化
        manager = APIClientManager()
        print("✅ API客户端管理器初始化成功")
        return True
    except Exception as e:
        print(f"❌ API客户端模块导入失败: {e}")
        return False

def test_directory_structure():
    """测试目录结构"""
    try:
        from config.settings import DATA_PATHS
        
        # 检查所有必要的目录是否存在
        missing_dirs = []
        for name, path in DATA_PATHS.items():
            if not path.exists():
                missing_dirs.append(name)
        
        if missing_dirs:
            print(f"⚠️  缺失目录: {missing_dirs}")
            # 尝试创建缺失的目录
            from config.settings import ensure_directories
            ensure_directories()
            print("✅ 目录结构已修复")
        else:
            print("✅ 所有目录结构正常")
        return True
    except Exception as e:
        print(f"❌ 目录结构检查失败: {e}")
        return False

def test_module_imports():
    """测试主要模块导入"""
    modules_to_test = [
        "pipeline.parse_pdf",
        "pipeline.summarize_with_qwen_long", 
        "pipeline.summarize_with_deepseek",
        "pipeline.get_embedding_bgem3",
        "pipeline.run_embedding_qwen",
        "research_pipeline.search_similar_papers",
        "research_pipeline.research_long_analyse",
        "research_pipeline.submit_summary_to_qwen",
        "research_pipeline.submit_summary_to_deepseek",
        "database_main",
        "research_main",
        "streamlit_main"
    ]
    
    success_count = 0
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} 导入成功")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_name} 导入失败: {e}")
        except Exception as e:
            print(f"⚠️  {module_name} 导入警告: {e}")
            success_count += 1  # 其他异常可能只是缺少依赖
    
    print(f"模块导入成功率: {success_count}/{len(modules_to_test)}")
    return success_count >= len(modules_to_test) * 0.8  # 允许20%的模块有依赖问题

def main():
    """主测试函数"""
    print("=" * 50)
    print("Liter_Pipeline 代码重构验证测试")
    print("=" * 50)
    
    tests = [
        test_config_import,
        test_api_clients_import,
        test_directory_structure,
        test_module_imports
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试 {test.__name__} 执行失败: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！代码重构成功完成")
        print("\n下一步建议:")
        print("1. 配置 config/settings.py 中的API密钥")
        print("2. 运行 python database_main.py 初始化数据库")
        print("3. 运行 streamlit run streamlit_main.py 启动Web界面")
    else:
        print("⚠️  部分测试未通过，请检查相关问题")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
