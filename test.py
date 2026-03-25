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
coder = huffman.HuffmanCoder()#编码器
current_dir = os.path.dirname(os.path.abspath(__file__))#文件绝对目录

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




def prepare_test_data(filename):

    """根据文件绝对路径自动准备对应的测试数据"""
    file_path = os.path.join(current_dir,filename)

    if os.path.exists(file_path):
        return True

    print(f"[准备数据] 未找到 {filename}，正在自动生成/下载到: {file_path}")
    
    if filename == "shakespeare.txt":
        url = "https://www.gutenberg.org/files/100/100-0.txt"
        r = requests.get(url)
        with open(file_path, "wb") as f:
            f.write(r.content)
    elif filename == "hongloumeng.txt":
        url = "https://www.gutenberg.org/cache/epub/24264/pg24264.txt"
        r = requests.get(url)
        r.encoding = 'utf-8'
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(r.text)
    
    print(f"数据准备就绪: {file_path}")
    return True

# --- 统一执行入口 ---
if __name__ == "__main__":
    TARGET_FILENAME = "shakespeare.txt"   # 可选: "shakespeare.txt", "hongloumeng.txt"
    TARGET_FILE = os.path.join(current_dir, TARGET_FILENAME)
    if prepare_test_data(TARGET_FILENAME):
        # 检查文件大小
        is_large = os.path.getsize(TARGET_FILE) > 1024 * 1024
        # 传入绝对路径进行测试
        test_huffman_bytes(TARGET_FILE)
        #debug_specific_word(coder, "Shakespeare")

# --- 统一执行入口 ---
if __name__ == "__main__":
    user_input = input("请输入要处理的文件路径：").strip()

    # 确定目标文件
    if not user_input:
        TARGET_FILENAME = "shakespeare.txt"   # 可选: "shakespeare.txt", "hongloumeng.txt"
        TARGET_FILE = os.path.join(current_dir, TARGET_FILENAME)
        # 如果是默认文件，尝试自动准备
        if not prepare_test_data(TARGET_FILENAME):
            print("错误：无法准备默认测试数据。")
            exit()
    else:
        #支持相对路径和绝对路径
        if os.path.isabs(user_input):
            TARGET_FILE = user_input
        else:
            TARGET_FILE = os.path.abspath(os.path.join(os.getcwd(), user_input))

    #检查文件是否存在
    if not os.path.exists(TARGET_FILE):
        print(f"错误：找不到文件 '{TARGET_FILE}'，请检查路径是否正确。")
    else:
        # 执行压缩与解压流程
        # 较大的文件（如 >1MB）不适于打印繁琐的编码表，为方便测试，默认打印前 30 个字节的映射关系
        file_size = os.path.getsize(TARGET_FILE)
        is_large = file_size > 1024 * 1024
        
        test_huffman_bytes(TARGET_FILE)#show_codes=not is_large
        debug_specific_word(coder, "Shakespeare")