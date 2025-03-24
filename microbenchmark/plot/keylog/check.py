import sys

def parse_print_log(log_file):
    """解析print.log文件，统计地址的access/dirty次数"""
    addr_access = {}
    with open(log_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            addr, operation = parts[0].lower(), parts[1]
            if addr not in addr_access:
                addr_access[addr] = {'access': 0, 'dirty': 0}
            if operation == 'access':
                addr_access[addr]['access'] += 1
            elif operation == 'dirty':
                addr_access[addr]['dirty'] += 1
    return addr_access

def parse_addr_record(record_file):
    """解析addr_record.txt文件，提取地址和读写模式"""
    addr_modes = {}
    with open(record_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            addr = parts[0].lstrip('0x').lower()  # 去除0x前缀
            mode = parts[1].upper()
            addr_modes[addr] = mode
    return addr_modes

def validate_access_rules(addr_modes, addr_access):
    """验证地址访问模式规则"""
    results = []
    for addr, mode in addr_modes.items():
        if addr not in addr_access:
            results.append((addr, mode, 'Error', 'Address not found in print.log'))
            continue
            
        dirty_count = addr_access[addr]['dirty']
        if mode == 'W':
            status = 'Pass' if dirty_count >= 1 else f'Fail (dirty={dirty_count})'
        elif mode == 'R':
            status = 'Pass' if dirty_count <= 1 else f'Fail (dirty={dirty_count})'
        else:
            status = 'Error (invalid mode)'
            
        results.append((addr, mode, dirty_count, status))
    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python analyzer.py print.log addr_record.txt")
        sys.exit(1)
        
    log_file, record_file = sys.argv[1], sys.argv[2]
    
    # 数据解析
    addr_access = parse_print_log(log_file)
    addr_modes = parse_addr_record(record_file)
    
    # 规则验证
    validation_results = validate_access_rules(addr_modes, addr_access)
    
    # 输出结果
    print(f"{'Address':<18} {'Mode':<5} {'Dirty Count':<12} Status")
    print('-' * 50)
    for addr, mode, dirty, status in validation_results:
        if isinstance(dirty, int):
            print(f"{addr:<18} {mode:<5} {dirty:<12} {status}")
        else:
            print(f"{addr:<18} {mode:<5} {'N/A':<12} {status}")

if __name__ == '__main__':
    main()