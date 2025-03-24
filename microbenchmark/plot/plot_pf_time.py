import re
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime

def parse_pagefault_log(file_path):
    """解析pageclient.log日志文件，提取PageFault处理时间"""
    pending_events = {}  # 未完成的PF事件 {地址: 触发时间}
    completed = []       # 已完成事件 (触发时间, 完成时间, 处理时间)
    timeline = []        # 按时间顺序的处理时间
    
    # 正则表达式模式（优化匹配精度）
    # time_pattern = re.compile(r'^$(\d+\.\d+)$')  # 匹配行首时间戳
    time_pattern = re.compile(r'^(\d+\.\d+)*')
    pf_start_re = re.compile(r'.*get PF: (\S+).*')  # 过滤非目标行
    pf_end_re = re.compile(r'.*写完, addr:(\S+).*')  # 精确匹配地址
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            # 提取时间戳
            # time_match = time_pattern.match(line)
            # print(time_match.group(1))
            # if not time_match:
            #     continue  # 跳过无时间戳的行
            
            # timestamp = float(time_match.group(1))
            
            # print(timestamp)
            
            if "get PF" in line:
                timestamp=float(line[1:10])
                addr=line[-13:-1]
                # if addr in pending_events:
                #     continue
                    # print(f"警告：重复触发未完成的PF地址 {addr} (行号:{line_num})")
                pending_events[addr] = timestamp
    
    # for key in pending_events.keys():
    #     print(f"Key: {key}.")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:  
        for line_num, line in enumerate(f, 1):
            
            if "写完, addr:" in line:
                timestamp=float(line[1:10])
                addr=line.split("addr:")[1].split(",")[0]
                # print(addr)
                if addr in pending_events:
                    start_time = pending_events.pop(addr)
                    process_time = timestamp - start_time
                    completed.append((start_time, timestamp, process_time))
                    timeline.append(process_time)
                # 
                    
                # else:
                #     print(f"警告：未匹配的完成事件 {addr} (行号:{line_num})")
                
                
    
    return completed, timeline

def visualize_pf_timeline(timeline):
    """可视化PageFault处理时间趋势"""
    plt.figure(figsize=(14, 7))
    
    # 主折线图（带透明度调节）
    plt.plot(timeline, 
             marker='o', markersize=5,
             linestyle='-', linewidth=1.2,
             color='#2c7fb8', alpha=0.7,
             label='time')
    
    # 辅助元素
    # plt.title('PageFault处理时间趋势分析\n(基于pageclient.log日志)', 
    #          fontsize=14, pad=20)
    plt.xlabel('page fault', fontsize=12)
    plt.ylabel('time/s', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # 统计标注（参考网页5、6的可视化技巧）
    avg_time = sum(timeline)/len(timeline)
    max_time = max(timeline)
    plt.axhline(avg_time, color='#d62728', linestyle='--', 
                label=f'avgtime {avg_time:.4f}s')
    plt.annotate(f'max {max_time:.4f}s', 
                 xy=(timeline.index(max_time), max_time),
                 xytext=(+20, +30), textcoords='offset points',
                 arrowprops=dict(arrowstyle='->', color='#2ca02c'))
    
    plt.legend()
    plt.tight_layout()
    plt.savefig('pf_timeline.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    # 执行日志分析
    events, timeline = parse_pagefault_log("keylog/log8/pageclient.log")
    
    # 控制台输出统计信息（参考网页1的数据分析模式）
    print(f"分析完成，共处理 {len(events)} 次PageFault")
    if events:
        print(f"平均处理时间: {sum(t[2] for t in events)/len(events):.6f}s")
        print(f"最大处理时间: {max(t[2] for t in events):.6f}s")
        print(f"最小处理时间: {min(t[2] for t in events):.6f}s")
    
    # 生成可视化图表（参考网页5、6的可视化规范）
    # timeline=[i for i in timeline if i<0.0005]
    visualize_pf_timeline(timeline)