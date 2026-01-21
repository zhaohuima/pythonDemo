"""
测试 ProductResearcher 的格式化输出
Test ProductResearcher formatting output
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import ProductResearcher, init_llm
from logger_config import logger

def test_product_researcher_formatting():
    """测试 ProductResearcher 的输出格式"""

    print("=" * 80)
    print("测试 ProductResearcher 格式化输出")
    print("Testing ProductResearcher Formatting Output")
    print("=" * 80)
    print()

    # 初始化 LLM 和 ProductResearcher
    print("初始化 LLM 和 ProductResearcher...")
    llm = init_llm()
    researcher = ProductResearcher(llm)
    print("✓ 初始化完成\n")

    # 测试用例：与 staging 环境相同的输入
    test_input = """
I want to build an AI-powered homework assistance app for students.
The app should have:
- Login functionality for personalized experience
- AI-based coaching to provide tailored educational support
- Camera integration to scan homework and provide suggestions
"""

    print("测试输入:")
    print("-" * 80)
    print(test_input)
    print("-" * 80)
    print()

    # 执行研究
    print("执行产品研究...")
    print("(这可能需要几分钟时间...)")
    print()

    try:
        result = researcher.research(test_input)

        print("=" * 80)
        print("研究结果 (Research Result)")
        print("=" * 80)
        print()

        research_result = result.get("research_result", {})

        # 显示每个字段的原始内容（包含 \n 字符）
        for key in ["core_requirements", "target_users", "market_analysis", "market_insights"]:
            if key in research_result:
                print(f"\n{'=' * 80}")
                print(f"字段: {key}")
                print(f"Field: {key}")
                print('=' * 80)

                content = research_result[key]

                # 显示原始内容（带 \n 标记）
                print("\n原始内容 (Raw content with \\n markers):")
                print("-" * 80)
                print(repr(content)[:500] + "..." if len(repr(content)) > 500 else repr(content))
                print()

                # 显示渲染后的内容
                print("渲染后的内容 (Rendered content):")
                print("-" * 80)
                print(content[:800] + "..." if len(content) > 800 else content)
                print()

                # 检查格式化质量
                has_double_newline = "\\n\\n" in repr(content) or "\n\n" in content
                has_bullet_points = "\\n-" in repr(content) or "\n-" in content

                print("格式化检查 (Formatting check):")
                print(f"  ✓ 包含段落分隔 (\\n\\n): {'是 (Yes)' if has_double_newline else '否 (No)'}")
                print(f"  ✓ 包含列表项 (\\n-): {'是 (Yes)' if has_bullet_points else '否 (No)'}")
                print()

        print("\n" + "=" * 80)
        print("测试完成！")
        print("Test completed!")
        print("=" * 80)
        print()
        print("提示：检查上面的输出，确认：")
        print("1. 原始内容中包含 \\n\\n (段落分隔)")
        print("2. 原始内容中包含 \\n- (列表项)")
        print("3. 渲染后的内容有清晰的段落和列表结构")
        print()

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return False

    return True


if __name__ == "__main__":
    success = test_product_researcher_formatting()
    sys.exit(0 if success else 1)
