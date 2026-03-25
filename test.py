import huffman
import os
import requests
from collections import Counter

CONTROL_CHARS = {
    0:  "NULL (空)",
    1:  "SOH (标题开始)",
    2:  "STX (正文开始)",
    3:  "ETX (正文结束)",
    4:  "EOT (传输结束)",
    7:  "BEL (响铃)",
    8:  "BS (退格)",
    9:  "TAB (制表符)",
    10: "LF (换行符)",
    11: "VT (垂直制表)",
    12: "FF (换页)",
    13: "CR (回车)",
    26: "EOF (文件结束)",
    27: "ESC (转义)",
    32: "SPACE (空格)",
    127: "DEL (删除)"
}
coder = huffman.HuffmanCoder()

def show_top_characters(file_path, top_k=10):
    """真正显示文件中出现频率最高的字符（包括汉字）"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    counter = Counter(text)
    print(f"\n[文本分析] 出现频率最高的 {top_k} 个字符:")
    for char, count in counter.most_common(top_k):
        # 转换不可见字符
        display = repr(char) if ord(char) < 32 or ord(char) > 126 else char
        print(f"字符: {display: <5} | 出现次数: {count}")


def test_huffman_bytes(file_path, show_codes=True):
    # 升级为字节流处理    
    show_top_characters(file_path)
    # 1. 压缩
    # 确保 huffman.py 内部使用的是 open(file_path, 'rb')
    compressed_file = coder.compress(file_path)
    if show_codes:
        print(f"\n[状态] 正在为 {file_path} 生成字节映射编码表...")
        print("-" * 50)

        # 此时 char_key 是字符串（字符）
        sorted_codes = sorted(coder.codes.items(), key=lambda x: len(x[1]))
        
        print(f"{'字符':<8} | {'可视化含义':<15} | {'码长':<6} | {'哈夫曼编码'}")
        print("-" * 50)
        
        for char_key, code in sorted_codes[:60]:
            display_char = ""
            
            # 获取字符的 Unicode 编码值用于判断
            try:
                val = ord(char_key)
            except TypeError:
                val = -1 # 防御性编程

            # 1. 处理控制字符
            if val in CONTROL_CHARS:
                display_char = CONTROL_CHARS[val]
            # 2. 处理可见 ASCII 字符
            elif 32 <= val <= 126:
                display_char = repr(char_key)
            # 3. 处理汉字或其他多字节字符
            elif val > 126:
                display_char = f"{char_key}"
            # 4. 其他
            else:
                display_char = f"特殊({hex(val) if val != -1 else '?'})"

            # 打印时，Key 处直接显示字符或其十六进制
            key_show = char_key if val > 32 else f"0x{val:02x}"
            print(f"{key_show:<8} | {display_char:<15} | {len(code):<8} | {code}")
        if len(sorted_codes) > 30:
            print(f"... 剩余 {len(sorted_codes)-30} 个字节映射已省略 ...")
        print("-" * 50)

    # 2. 解压
    decompressed_file = coder.decompress(compressed_file)

    # 3. 数据校验与报告
    original_size = os.path.getsize(file_path)
    compressed_size = os.path.getsize(compressed_file)

    print(f"\n--- 字节流压缩任务报告 ---")
    print(f"1. 目标文件: {file_path}")
    print(f"2. 原始大小: {original_size} 字节")
    print(f"3. 压缩大小: {compressed_size} 字节")
    print(f"4. 压缩率:   {(1 - compressed_size/original_size)*100:.2f}%")
    
    # 二进制严格校验
    # with open(file_path, 'rb') as f1, open(decompressed_file, 'rb') as f2:
    #     if f1.read() == f2.read():
    #         print(f"5. 最终校验: 成功 (字节级完全一致)")
    #     else:
    #         print(f"5. 最终校验: 失败 (数据损坏)")
    with open(file_path, 'r', encoding='utf-8') as f1, \
     open(decompressed_file, 'r', encoding='utf-8') as f2:
        if f1.read() == f2.read():
            print("5. 最终校验: 成功 (字符级完全一致)")
        else:
            print(f"5. 最终校验: 失败 (数据损坏)")

def debug_specific_word(coder, word="红楼梦"):
    print(f"\n[特定词汇编码分析]: {word}")
    for char in word:
        byte_seq = char.encode('utf-8')
        print(f" 字符 '{char}':")
        for b in byte_seq:
            print(f"   字节 {hex(b)} -> 编码: {coder.codes.get(b, '未映射')}")


TARGET_FILE = "hongloumeng.txt"  # 可选: "shakespeare.txt", "hongloumeng.txt"

def prepare_test_data(filename):
    """根据文件名自动准备对应的测试数据"""
    if os.path.exists(filename):
        return True

    print(f"[准备数据] 未找到 {filename}，正在自动生成/下载...")
    
    if filename == "shakespeare.txt":
        url = "https://www.gutenberg.org/files/100/100-0.txt"
        r = requests.get(url)
        with open(filename, "wb") as f:
            f.write(r.content)
            
    elif filename == "hongloumeng.txt":
        url = "https://www.gutenberg.org/cache/epub/24264/pg24264.txt"
        r = requests.get(url)
        r.encoding = 'utf-8'
        with open(filename, "w", encoding='utf-8') as f:
            f.write(r.text)
                        
    else:
        print(f"警告：未定义的测试文件类型 {filename}，请确保该文件已存在于目录下。")
        return False
        
    print(f"数据准备就绪: {filename}")
    return True

# --- 统一执行入口 ---
if __name__ == "__main__":
    if prepare_test_data(TARGET_FILE):
        # 如果文件很大（大于 1MB），建议关闭编码表显示以防刷屏
        is_large = os.path.getsize(TARGET_FILE) > 1024 * 1024
        test_huffman_bytes(TARGET_FILE)#show_codes=not is_large
        #debug_specific_word(coder, "Shakespeare")