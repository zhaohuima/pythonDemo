# Product Researcher Agent Performance Testing

This testing framework evaluates the Product Researcher agent's performance using 30 test cases across 5 product categories.

## Overview

The testing system consists of 5 main components:

1. **test_case_loader.py** - Extracts test cases from PDF document
2. **agent_executor.py** - Executes the Product Researcher agent
3. **llm_scorer.py** - Scores outputs using SiliconFlow Seed-OSS-36B-Instruct model
4. **report_generator.py** - Generates detailed reports and exports
5. **run_performance_test.py** - Main orchestration script

## Installation

Install the required dependencies:

```bash
pip install -r requirements-test.txt
```

## Usage

### Run All Tests

```bash
python run_performance_test.py
```

### Run Specific Tests

```bash
# Run specific test IDs
python run_performance_test.py --test-ids "1.1,1.2,2.3"

# Run tests for a specific category
python run_performance_test.py --category "AI Agent"

# Custom output directory
python run_performance_test.py --output-dir "results_2026_01_18"

# Verbose mode
python run_performance_test.py --verbose
```

## Test Categories

The 30 test cases cover 5 product categories:

1. **AI Agent Products** (6 tests) - Customer support, sales qualification, code review, personal finance, recruiting, meeting assistant
2. **Enterprise Internal Software** (6 tests) - Knowledge management, onboarding, communication, IT asset management, project management, analytics
3. **Hardware Products** (6 tests) - Security camera, fitness wearable, wireless earbuds, smart speaker, e-reader, robot vacuum
4. **Software Tools (SaaS)** (6 tests) - Video conferencing, password manager, email marketing, design collaboration, time tracking, API management
5. **Consumer Mobile Apps** (6 tests) - Dating app, food delivery, language learning, meditation, photo editing, budgeting

## Scoring System

Each test case is scored across 4 dimensions (40 points total):

- **Dimension A: User Requirements** (10 points) - Understanding of explicit and implicit user needs
- **Dimension B: Target Users** (10 points) - User segment definition and unmet needs identification
- **Dimension C: Market Analysis** (10 points) - Competitor identification and market positioning
- **Dimension D: Market Insights** (10 points) - Actionable recommendations and market opportunities

Scores are assigned as: 10 (excellent), 7 (good), 4 (fair), or 1 (poor) for each dimension.

Pass threshold: ≥28/40 (70%)

## Output

After execution, the `test_results/` directory will contain:

- **detailed_report_YYYYMMDD_HHMMSS.md** - Comprehensive markdown report with:
  - Executive summary
  - Category breakdown
  - Individual test results with scores and reasoning
  - Low-scoring tests analysis

- **test_scores_YYYYMMDD_HHMMSS.csv** - CSV export with all scores

- **test_results_YYYYMMDD_HHMMSS.xlsx** - Excel workbook with:
  - Summary sheet with aggregate statistics
  - Detailed scores sheet
  - Per-category analysis sheets

## Example Output

```
================================================================================
Product Researcher Agent Performance Test
================================================================================
Started: 2026-01-18 14:30:22

[1/4] Loading test cases from PDF...
  ✓ Loaded 30 test cases

[2/4] Initializing components...
  ✓ Agent executor initialized
  ✓ LLM scorer initialized

[3/4] Running 30 test cases...

[1/30] Test 1.1: AI Customer Support Agent
  Category: AI Agent
  ✓ Agent execution completed (45.2s)
  ✓ Scoring completed (8.3s)
  Score: 32/40 (80.0%)
    - User Requirements: 7/10
    - Target Users: 10/10
    - Market Analysis: 7/10
    - Market Insights: 8/10

...

[4/4] Generating reports...
  ✓ Detailed report: test_results/detailed_report_20260118_143022.md
  ✓ CSV export: test_results/test_scores_20260118_143022.csv
  ✓ Excel export: test_results/test_results_20260118_143022.xlsx

================================================================================
Test Results Summary
================================================================================
Total tests run: 30
Successful: 30
Failed: 0
Average score: 31.2/40 (78.0%)
Pass rate (≥28/40): 86.7%

Reports generated:
  - Detailed report: test_results/detailed_report_20260118_143022.md
  - CSV export: test_results/test_scores_20260118_143022.csv
  - Excel export: test_results/test_results_20260118_143022.xlsx

================================================================================
✓ Testing complete!
================================================================================
```

## Testing Individual Components

Each component can be tested independently:

```bash
# Test PDF loader
python test_case_loader.py

# Test agent executor
python agent_executor.py

# Test LLM scorer
python llm_scorer.py

# Test report generator
python report_generator.py
```

## Configuration

The testing system uses the API configuration from `config.py`:

- **API_KEY** - SiliconFlow API key
- **API_BASE_URL** - SiliconFlow API endpoint (https://api.siliconflow.cn/v1)
- **MODEL_NAME** - Model for agent execution (deepseek-ai/DeepSeek-V2.5)

The scorer uses a separate model:
- **Scoring Model** - Pro/Seed-OSS-36B-Instruct (hardcoded in llm_scorer.py)
- **Temperature** - 0.1 (for consistent scoring)

## Execution Time

- **Per test case**: 30-60 seconds (agent execution + scoring)
- **Full test suite (30 cases)**: 15-30 minutes
- **Sample run (3 cases)**: 2-5 minutes

## Troubleshooting

### PDF Loading Issues

If test cases fail to load from PDF:
- Verify PDF path is correct
- Check PDF is not corrupted
- Ensure pdfplumber is installed correctly

### Agent Execution Failures

If agent execution fails:
- Check API key in config.py
- Verify network connectivity to SiliconFlow API
- Check API rate limits

### Scoring Errors

If scoring fails:
- Verify Seed-OSS-36B-Instruct model is available
- Check API response format
- Review error messages in output

### Memory Issues

If running out of memory:
- Run tests in smaller batches using `--test-ids`
- Close other applications
- Increase system memory allocation

## Notes

- The test cases are extracted from "Product Master Test Case-User and market Research.pdf"
- Scoring uses LLM evaluation for consistency and scalability
- Results are cached to avoid re-scoring
- The system supports resuming from failures (future enhancement)

## License

This testing framework is part of the Product Master project.
