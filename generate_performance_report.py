#!/usr/bin/env python3
"""
生成 Product Research 执行时间对比的可视化图表
Generate visualization charts for execution time comparison
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import json

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

    if current_session:
        sessions.append(current_session)

    return sessions

def generate_html_report(all_sessions: List[Dict]):
    """生成 HTML 可视化报告"""

    parallel_sessions = [s for s in all_sessions if s['mode'] == 'parallel' and s['duration']]
    fallback_sessions = [s for s in all_sessions if s['mode'] == 'fallback' and s['duration']]

    parallel_times = [s['duration'] for s in parallel_sessions]
    fallback_times = [s['duration'] for s in fallback_sessions]

    # 计算统计数据
    parallel_avg = sum(parallel_times) / len(parallel_times) if parallel_times else 0
    fallback_avg = sum(fallback_times) / len(fallback_times) if fallback_times else 0

    parallel_min = min(parallel_times) if parallel_times else 0
    parallel_max = max(parallel_times) if parallel_times else 0
    fallback_min = min(fallback_times) if fallback_times else 0
    fallback_max = max(fallback_times) if fallback_times else 0

    improvement = ((fallback_avg - parallel_avg) / fallback_avg * 100) if fallback_avg > 0 else 0

    # 生成分布数据
    parallel_dist = {
        '0-5s': len([t for t in parallel_times if t <= 5]),
        '5-10s': len([t for t in parallel_times if 5 < t <= 10]),
        '10-15s': len([t for t in parallel_times if 10 < t <= 15]),
        '15-20s': len([t for t in parallel_times if 15 < t <= 20]),
        '20+s': len([t for t in parallel_times if t > 20]),
    }

    fallback_dist = {
        '0-20s': len([t for t in fallback_times if t <= 20]),
        '20-50s': len([t for t in fallback_times if 20 < t <= 50]),
        '50-100s': len([t for t in fallback_times if 50 < t <= 100]),
        '100-200s': len([t for t in fallback_times if 100 < t <= 200]),
        '200+s': len([t for t in fallback_times if t > 200]),
    }

    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Research 执行时间对比分析</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .content {{
            padding: 40px;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}

        .metric-card.parallel {{
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        }}

        .metric-card.fallback {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }}

        .metric-card.improvement {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        }}

        .metric-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}

        .metric-unit {{
            font-size: 0.8em;
            color: #666;
            margin-left: 5px;
        }}

        .charts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}

        .chart-container {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .chart-title {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}

        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        .comparison-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}

        .comparison-table td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}

        .comparison-table tr:hover {{
            background: #f5f5f5;
        }}

        .comparison-table .parallel {{
            color: #27ae60;
            font-weight: 600;
        }}

        .comparison-table .fallback {{
            color: #e74c3c;
            font-weight: 600;
        }}

        .footer {{
            background: #f5f5f5;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Product Research 执行时间对比分析</h1>
            <p>并行模式 vs 回退模式性能对比</p>
        </div>

        <div class="content">
            <!-- 关键指标 -->
            <div class="metrics">
                <div class="metric-card parallel">
                    <div class="metric-label">并行模式平均时间</div>
                    <div class="metric-value">{parallel_avg:.2f}<span class="metric-unit">秒</span></div>
                </div>
                <div class="metric-card fallback">
                    <div class="metric-label">回退模式平均时间</div>
                    <div class="metric-value">{fallback_avg:.2f}<span class="metric-unit">秒</span></div>
                </div>
                <div class="metric-card improvement">
                    <div class="metric-label">性能提升</div>
                    <div class="metric-value">{improvement:.1f}<span class="metric-unit">%</span></div>
                </div>
                <div class="metric-card improvement">
                    <div class="metric-label">时间节省</div>
                    <div class="metric-value">{fallback_avg - parallel_avg:.2f}<span class="metric-unit">秒</span></div>
                </div>
            </div>

            <!-- 图表 -->
            <div class="charts">
                <div class="chart-container">
                    <div class="chart-title">📊 执行时间对比</div>
                    <canvas id="comparisonChart"></canvas>
                </div>
                <div class="chart-container">
                    <div class="chart-title">📈 执行时间分布</div>
                    <canvas id="distributionChart"></canvas>
                </div>
            </div>

            <!-- 对比表格 -->
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>指标</th>
                        <th class="parallel">并行模式</th>
                        <th class="fallback">回退模式</th>
                        <th>差异</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>平均执行时间</td>
                        <td class="parallel">{parallel_avg:.2f} 秒</td>
                        <td class="fallback">{fallback_avg:.2f} 秒</td>
                        <td>快 {fallback_avg/parallel_avg:.1f}x</td>
                    </tr>
                    <tr>
                        <td>最快执行时间</td>
                        <td class="parallel">{parallel_min:.2f} 秒</td>
                        <td class="fallback">{fallback_min:.2f} 秒</td>
                        <td>-</td>
                    </tr>
                    <tr>
                        <td>最慢执行时间</td>
                        <td class="parallel">{parallel_max:.2f} 秒</td>
                        <td class="fallback">{fallback_max:.2f} 秒</td>
                        <td>-</td>
                    </tr>
                    <tr>
                        <td>执行会话数</td>
                        <td class="parallel">{len(parallel_sessions)}</td>
                        <td class="fallback">{len(fallback_sessions)}</td>
                        <td>-</td>
                    </tr>
                    <tr>
                        <td>API 调用方式</td>
                        <td class="parallel">异步并行 (4个)</td>
                        <td class="fallback">同步顺序 (1个)</td>
                        <td>-</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>分析时间: 2026-01-21 | 数据来源: 日志文件分析 (product_master_*.log)</p>
        </div>
    </div>

    <script>
        // 执行时间对比图表
        const comparisonCtx = document.getElementById('comparisonChart').getContext('2d');
        new Chart(comparisonCtx, {{
            type: 'bar',
            data: {{
                labels: ['平均时间', '最快时间', '最慢时间'],
                datasets: [
                    {{
                        label: '并行模式',
                        data: [{parallel_avg:.2f}, {parallel_min:.2f}, {parallel_max:.2f}],
                        backgroundColor: '#84fab0',
                        borderColor: '#27ae60',
                        borderWidth: 2
                    }},
                    {{
                        label: '回退模式',
                        data: [{fallback_avg:.2f}, {fallback_min:.2f}, {fallback_max:.2f}],
                        backgroundColor: '#fa709a',
                        borderColor: '#e74c3c',
                        borderWidth: 2
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'top',
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '执行时间 (秒)'
                        }}
                    }}
                }}
            }}
        }});

        // 执行时间分布图表
        const distributionCtx = document.getElementById('distributionChart').getContext('2d');
        new Chart(distributionCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['0-5s', '5-10s', '10-15s', '15-20s', '20+s'],
                datasets: [{{
                    label: '并行模式分布',
                    data: [{parallel_dist['0-5s']}, {parallel_dist['5-10s']}, {parallel_dist['10-15s']}, {parallel_dist['15-20s']}, {parallel_dist['20+s']}],
                    backgroundColor: [
                        '#84fab0',
                        '#8fd3f4',
                        '#a8edea',
                        '#fed6e3',
                        '#ffeaa7'
                    ],
                    borderColor: '#fff',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    return html

def main():
    log_dir = Path('/Users/mazhaohui/pythonDemo/logs')
    log_files = sorted(log_dir.glob('product_master_*.log'), reverse=True)[:5]

    all_sessions = []

    for log_file in log_files:
        events = parse_log_file(str(log_file))
        sessions = analyze_research_sessions(events)
        all_sessions.extend(sessions)

    # 生成 HTML 报告
    html_content = generate_html_report(all_sessions)

    output_path = Path('/Users/mazhaohui/pythonDemo/performance_report.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML 报告已生成: {output_path}")
    print(f"📊 请在浏览器中打开: file://{output_path}")

if __name__ == '__main__':
    main()
