#!/usr/bin/env python3
"""
分析 Product Research 模块的执行时间对比
Compare execution time between old (single prompt) and new (parallel skills) approaches
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

def parse_log_file(log_path: str) -> List[Dict]:
    """解析日志文件，提取执行时间信息"""
    events = []

    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        # 提取时间戳
        time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        if not time_match:
            continue

        timestamp = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')

        # 检查关键事件
        if 'ProductResearcher.research() called' in line:
            events.append({
                'type': 'research_start',
                'time': timestamp,
                'line': line.strip()
            })
        elif 'Using Parallel Skill mode' in line:
            events.append({
                'type': 'parallel_mode',
                'time': timestamp,
                'line': line.strip()
            })
        elif 'Using fallback LLM mode' in line:
            events.append({
                'type': 'fallback_mode',
                'time': timestamp,
                'line': line.strip()
            })
        elif 'Parallel Skill research completed successfully' in line:
            events.append({
                'type': 'parallel_complete',
                'time': timestamp,
                'line': line.strip()
            })
        elif 'ProductResearcher.research() completed with fallback' in line:
            events.append({
                'type': 'fallback_complete',
                'time': timestamp,
                'line': line.strip()
            })
        elif 'LLM async API call successful' in line:
            events.append({
                'type': 'async_call_complete',
                'time': timestamp,
                'line': line.strip()
            })
        elif 'LLM API call successful' in line and 'async' not in line:
            events.append({
                'type': 'sync_call_complete',
                'time': timestamp,
                'line': line.strip()
            })
        elif 'Workflow execution time:' in line:
            time_match = re.search(r'Workflow execution time: ([\d.]+) seconds', line)
            if time_match:
                events.append({
                    'type': 'workflow_time',
                    'time': timestamp,
                    'duration': float(time_match.group(1)),
                    'line': line.strip()
                })

    return events

def analyze_research_sessions(events: List[Dict]) -> List[Dict]:
    """分析每个 research 会话的执行时间"""
    sessions = []
    current_session = None

    for event in events:
        if event['type'] == 'research_start':
            if current_session:
                sessions.append(current_session)
            current_session = {
                'start_time': event['time'],
                'mode': None,
                'end_time': None,
                'duration': None,
                'async_calls': 0,
                'sync_calls': 0
            }
        elif current_session:
            if event['type'] == 'parallel_mode':
                current_session['mode'] = 'parallel'
            elif event['type'] == 'fallback_mode':
                current_session['mode'] = 'fallback'
            elif event['type'] in ['parallel_complete', 'fallback_complete']:
                current_session['end_time'] = event['time']
                current_session['duration'] = (event['time'] - current_session['start_time']).total_seconds()
                sessions.append(current_session)
                current_session = None
            elif event['type'] == 'async_call_complete':
                current_session['async_calls'] += 1
            elif event['type'] == 'sync_call_complete':
                current_session['sync_calls'] += 1

    if current_session:
        sessions.append(current_session)

    return sessions

def main():
    log_dir = Path('/Users/mazhaohui/pythonDemo/logs')

    # 分析最近的日志文件
    log_files = sorted(log_dir.glob('product_master_*.log'), reverse=True)[:5]

    print("=" * 80)
    print("Product Research 执行时间分析 | Execution Time Analysis")
    print("=" * 80)
    print()

    all_sessions = []

    for log_file in log_files:
        print(f"\n📄 分析日志: {log_file.name}")
        print("-" * 80)

        events = parse_log_file(str(log_file))
        sessions = analyze_research_sessions(events)

        if not sessions:
            print("  未找到 research 会话")
            continue

        for i, session in enumerate(sessions, 1):
            if session['duration'] is None:
                continue

            mode = session['mode'] or 'unknown'
            duration = session['duration']
            async_calls = session['async_calls']
            sync_calls = session['sync_calls']

            print(f"\n  会话 {i}:")
            print(f"    模式: {mode}")
            print(f"    执行时间: {duration:.2f} 秒")
            print(f"    异步调用: {async_calls}")
            print(f"    同步调用: {sync_calls}")

            all_sessions.append({
                'file': log_file.name,
                'mode': mode,
                'duration': duration,
                'async_calls': async_calls,
                'sync_calls': sync_calls
            })

    # 统计对比
    print("\n" + "=" * 80)
    print("📊 执行模式对比统计 | Mode Comparison Statistics")
    print("=" * 80)

    parallel_sessions = [s for s in all_sessions if s['mode'] == 'parallel']
    fallback_sessions = [s for s in all_sessions if s['mode'] == 'fallback']

    if parallel_sessions:
        parallel_times = [s['duration'] for s in parallel_sessions]
        print(f"\n✨ 并行模式 (Parallel Skills):")
        print(f"   会话数: {len(parallel_sessions)}")
        print(f"   平均执行时间: {sum(parallel_times) / len(parallel_times):.2f} 秒")
        print(f"   最快: {min(parallel_times):.2f} 秒")
        print(f"   最慢: {max(parallel_times):.2f} 秒")
        print(f"   总异步调用: {sum(s['async_calls'] for s in parallel_sessions)}")

    if fallback_sessions:
        fallback_times = [s['duration'] for s in fallback_sessions]
        print(f"\n🔄 回退模式 (Fallback - Single Prompt):")
        print(f"   会话数: {len(fallback_sessions)}")
        print(f"   平均执行时间: {sum(fallback_times) / len(fallback_times):.2f} 秒")
        print(f"   最快: {min(fallback_times):.2f} 秒")
        print(f"   最慢: {max(fallback_times):.2f} 秒")
        print(f"   总同步调用: {sum(s['sync_calls'] for s in fallback_sessions)}")

    # 性能对比
    if parallel_sessions and fallback_sessions:
        parallel_avg = sum(s['duration'] for s in parallel_sessions) / len(parallel_sessions)
        fallback_avg = sum(s['duration'] for s in fallback_sessions) / len(fallback_sessions)
        improvement = ((fallback_avg - parallel_avg) / fallback_avg) * 100

        print(f"\n🚀 性能提升:")
        print(f"   并行模式平均: {parallel_avg:.2f} 秒")
        print(f"   回退模式平均: {fallback_avg:.2f} 秒")
        print(f"   性能提升: {improvement:.1f}%")
        print(f"   时间节省: {fallback_avg - parallel_avg:.2f} 秒")

    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
