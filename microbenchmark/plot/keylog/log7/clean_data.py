def process_log_file(input_path, output_path):
    """处理日志文件的核心函数"""
    try:
        # 读取原始文件（自动关闭文件）
        with open(input_path, 'r', encoding='utf-8', errors='replace') as infile:
            raw_lines = infile.readlines()

        # 处理过滤和清洗
        processed_lines = []
        for idx, line in enumerate(raw_lines, 1):
            # 判断是否包含目标关键词
            if 'get PF' in line or '写完' in line:
                # 去除首尾空格并保留换行符（网页6、7的处理方式）
                cleaned = line.strip() + '\n'  # 确保每行有独立换行
                processed_lines.append(cleaned)
                print(f"保留第{idx}行：{cleaned.strip()}")  # 调试信息

        # 写入新文件
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.writelines(processed_lines)
            
        print(f"处理完成！共保留 {len(processed_lines)} 行")
        
    except FileNotFoundError:
        print(f"错误：文件 {input_path} 未找到")
    except Exception as e:
        print(f"发生未知错误：{str(e)}")

if __name__ == "__main__":
    # 文件路径配置
    input_log = "pageclient.log"
    output_log = "new.log"
    
    # 执行处理
    process_log_file(input_log, output_log)