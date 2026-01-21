"""
快速测试脚本 - 验证格式化改进
Quick test script - Verify formatting improvements
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import init_llm

def test_formatting_with_simple_prompt():
    """使用简化的prompt测试格式化效果"""

    print("=" * 80)
    print("快速格式化测试")
    print("Quick Formatting Test")
    print("=" * 80)
    print()

    llm = init_llm()

    # 简化的测试prompt
    test_prompt = """
You are analyzing a product requirement for an AI homework assistance app.

Please provide a brief analysis in JSON format with proper formatting:

CRITICAL FORMATTING REQUIREMENTS:
- Use \\n\\n to separate major sections
- Use \\n- to create bullet points for list items
- Ensure each distinct concept is on a new line

Example format:
{
  "core_requirements": "Explicit requirements:\\n- Login functionality\\n- AI coaching\\n- Camera integration\\n\\nImplicit requirements:\\n- Differentiation opportunity\\n- PMF validation needed"
}

Now provide a brief analysis with these fields:
- core_requirements: List 3 explicit and 2 implicit requirements
- target_users: Describe 2 user segments with bullet points

Return ONLY valid JSON with proper \\n formatting.
"""

    print("发送测试请求...")
    print("Sending test request...")
    print()

    try:
        response = llm.invoke(test_prompt)

        print("LLM 响应 (LLM Response):")
        print("=" * 80)
        print(response)
        print("=" * 80)
        print()

        # 检查格式化
        print("格式化检查 (Formatting Check):")
        print("-" * 80)

        checks = {
            "包含 \\n\\n (段落分隔)": "\\n\\n" in response or "\n\n" in response,
            "包含 \\n- (列表项)": "\\n-" in response or "\n-" in response,
            "包含 JSON 结构": "{" in response and "}" in response,
        }

        for check_name, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"{status} {check_name}: {'通过' if passed else '失败'}")

        print()

        all_passed = all(checks.values())
        if all_passed:
            print("✓ 所有格式化检查通过！")
            print("✓ All formatting checks passed!")
        else:
            print("✗ 部分格式化检查失败")
            print("✗ Some formatting checks failed")

        print()
        return all_passed

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_formatting_with_simple_prompt()
    sys.exit(0 if success else 1)
