#!/bin/bash
echo "=== Test Progress Monitor ==="
echo "Current time: $(date)"
echo ""

OUTPUT_FILE="/private/tmp/claude/-Users-mazhaohui-pythonDemo/tasks/b5923e3.output"

# Count completed agent executions
AGENT_COMPLETED=$(grep -c "ProductResearcher.research() completed" "$OUTPUT_FILE" 2>/dev/null || echo "0")
echo "Agent executions completed: $AGENT_COMPLETED / 30"

# Count completed scorings
SCORING_COMPLETED=$(grep -c "Scoring completed" "$OUTPUT_FILE" 2>/dev/null || echo "0")
echo "Scorings completed: $SCORING_COMPLETED / 30"

# Show recent test if available
RECENT_TEST=$(grep "Test [0-9]" "$OUTPUT_FILE" 2>/dev/null | tail -1)
if [ -n "$RECENT_TEST" ]; then
    echo ""
    echo "Most recent test: $RECENT_TEST"
fi

# Show recent score if available
RECENT_SCORE=$(grep "Score:" "$OUTPUT_FILE" 2>/dev/null | tail -1)
if [ -n "$RECENT_SCORE" ]; then
    echo "Most recent score: $RECENT_SCORE"
fi

# Estimate progress
if [ "$AGENT_COMPLETED" -gt 0 ]; then
    PROGRESS=$((AGENT_COMPLETED * 100 / 30))
    echo ""
    echo "Progress: $PROGRESS%"
    
    # Estimate time remaining (assuming 2 min per test)
    REMAINING=$((30 - AGENT_COMPLETED))
    TIME_REMAINING=$((REMAINING * 2))
    echo "Estimated time remaining: ~$TIME_REMAINING minutes"
fi

echo ""
echo "To check again, run: bash check_test_progress.sh"
