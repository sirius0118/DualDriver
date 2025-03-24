import re
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

totol_num=[0]*10

def parse_score_log(score_file):
    """解析分档文件，构建地址->档次映射字典[1,2](@ref)"""
    tier_map = {}
    current_tier = -1
    
    with open(score_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # 检测分档标题行[1](@ref)
            if '档页面:' in line:
                current_tier = int(line.split('档')[0])
            else:
                tier_map[line[0:12]] = current_tier
                totol_num[current_tier]+=1
    return tier_map

def extract_addresses(log_file):
    """从日志中提取目标地址[6,8](@ref)"""
    pattern = re.compile(r'get PF:\s*(\S+)')
    addresses = []
    
    with open(log_file, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                addr = match.group(1).strip()
                addresses.append(addr)
    print(f"Total Requests: {len(addresses)}")
    return addresses[:20000]

def visualize_tiers(tier_map, addresses):
    """生成分档散点图[9,11](@ref)"""
    tiers = []
    missing_indices = []
    
    # 生成档次序列
    for idx, addr in enumerate(addresses):
        tier = tier_map.get(addr, -1)
        tiers.append(tier)
        if tier == -1:
            missing_indices.append(idx)

    # 创建画布
    plt.figure(figsize=(20, 10))
    cmap = get_cmap('tab10')
    
    # 绘制有效数据点
    valid_scatter = plt.scatter(
        x=range(len(tiers)),
        y=tiers,
        c=[t if t != -1 else 10 for t in tiers],  # 特殊处理缺失值
        cmap=cmap,
        s=50,
        # alpha=0.7,
        edgecolors='w',
        linewidth=0.5
    )
    
    # 标注缺失值
    if missing_indices:
        plt.scatter(
            x=missing_indices,
            y=[-1]*len(missing_indices),
            marker='x',
            color='red',
            s=60,
            label='Missing Address'
        )
    
    # 设置图表样式
    plt.title('Address Tier Distribution in Page Requests', fontsize=14, pad=20)
    plt.xlabel('Request Sequence', fontsize=12)
    plt.ylabel('Tier Level (0-9)', fontsize=12)
    plt.ylim(-1.5, 9.5)
    plt.grid(True, alpha=0.3)
    
    # 配置颜色条
    cbar = plt.colorbar(valid_scatter, ticks=range(10))
    cbar.set_label('Tier Level')
    
    # 添加统计信息
    stats_text = f"Total Requests: {len(addresses)}\nMissing Addresses: {len(missing_indices)}"
    plt.annotate(stats_text, 
                xy=(0.78, 0.15), 
                xycoords='axes fraction',
                bbox=dict(boxstyle="round", alpha=0.1))
    
    plt.tight_layout()
    plt.savefig("result.png")
    plt.show()

def hit_info_analyze(tier_map, addresses):
    is_exist={}
    hit_num=[0]*10
    for idx, addr in enumerate(addresses):
        a=is_exist.get(addr,0)
        if a==1:
            continue
        is_exist[addr]=1
        tier = tier_map.get(addr, -1)
        if tier!=-1:
            hit_num[tier]+=1
    print(hit_num)
    print(totol_num)



if __name__ == "__main__":
    tier_mapping = parse_score_log('./log6/score.log')
    addr_sequence = extract_addresses('./log6/pageclient.log')
    visualize_tiers(tier_mapping, addr_sequence)
    hit_info_analyze(tier_mapping, addr_sequence)