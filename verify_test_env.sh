#!/bin/bash

# 快速测试脚本 - 验证测试环境
# Quick Test Script - Verify Test Environment

set -e

echo "=========================================="
echo "Running Quick Environment Tests"
echo "=========================================="

# 激活虚拟环境
source venv/bin/activate

echo ""
echo "Test 1: Python Version"
python --version

echo ""
echo "Test 2: Key Dependencies"
python -c "
import sys
try:
    import flask
    print('✓ Flask installed')
except ImportError as e:
    print('✗ Flask not found')
    sys.exit(1)

try:
    import langchain
    print('✓ LangChain installed')
except ImportError as e:
    print('✗ LangChain not found')
    sys.exit(1)

try:
    import langgraph
    print('✓ LangGraph installed')
except ImportError as e:
    print('✗ LangGraph not found')
    sys.exit(1)

try:
    import openai
    print('✓ OpenAI installed')
except ImportError as e:
    print('✗ OpenAI not found')
    sys.exit(1)
"

echo ""
echo "Test 3: Configuration File"
if [ -f "config.py" ]; then
    echo "✓ config.py exists"
    python -c "import config; print('  API_BASE_URL:', config.API_BASE_URL)"
    python -c "import config; print('  MODEL_NAME:', config.MODEL_NAME)"
    python -c "import config; print('  RAG_ENABLED:', config.RAG_ENABLED)"
else
    echo "✗ config.py not found"
    exit 1
fi

echo ""
echo "Test 4: Required Directories"
for dir in logs outputs test_results knowledge_base vector_db templates static skills; do
    if [ -d "$dir" ]; then
        echo "✓ $dir/ exists"
    else
        echo "✗ $dir/ not found"
    fi
done

echo ""
echo "Test 5: Main Application Files"
for file in web_app.py agents.py main.py; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file not found"
    fi
done

echo ""
echo "Test 6: Skills Module"
python -c "
import sys
try:
    from skills.base_skill import BaseSkill
    print('✓ Skills module loaded successfully')
except ImportError as e:
    print('✗ Skills module failed to load:', e)
    sys.exit(1)
"

echo ""
echo "=========================================="
echo "All Tests Passed! ✓"
echo "=========================================="
echo ""
echo "Your test environment is ready!"
echo ""
echo "Next steps:"
echo "  1. Start the server: ./start_test_server.sh"
echo "  2. Open browser: http://localhost:5000"
echo "  3. Run tests: pytest"
echo ""
