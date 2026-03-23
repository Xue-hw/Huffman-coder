import huffman
import os
import requests

def test_huffman(file_path, show_codes=True):
    """
    file_path: 目标文件路径
    show_codes: 是否在控制台显示哈夫曼编码表 (True/False)
    """
    coder = huffman.HuffmanCoder()

    # 1. 压缩
    # 内部会生成 .huff 二进制文件
    compressed_file = coder.compress(file_path)
    
    # === 功能：根据参数决定是否生成/显示编码表 ===
    if show_codes:
        print(f"\n[状态] 正在为 {file_path} 生成编码表...")
        print("-" * 30)
        # 按编码长度排序，方便观察贪心算法结果
        sorted_codes = sorted(coder.codes.items(), key=lambda x: len(x[1]))
        for char, code in sorted_codes:
            # 这里的 repr(char) 可以清晰地显示换行符 \n 或空格
            print(f"字符: {repr(char):>6} | 权重排名: 长度 {len(code):>2} | 编码: {code}")
        print("-" * 30)

    # 2. 解压
    # 内部会自动生成一个名为 '文件名_decompressed.txt' 的新文件
    decompressed_file = coder.decompress(compressed_file)

    # 3. 数据校验与报告
    original_size = os.path.getsize(file_path)
    compressed_size = os.path.getsize(compressed_file)

    print(f"\n--- 压缩任务完成 ---")
    print(f"1. 原始文件: {file_path} ({original_size} 字节)")
    print(f"2. 压缩文件: {compressed_file} ({compressed_size} 字节)")
    print(f"3. 还原文件: {decompressed_file} (已保存至磁盘)")
    print(f"4. 压缩率: {(1 - compressed_size/original_size)*100:.2f}%")
    
    # 读取两个文件进行二进制级别的比对，确保完全一致
    with open(file_path, 'rb') as f1, open(decompressed_file, 'rb') as f2:
        if f1.read() == f2.read():
            print(f"5. 最终校验: 成功 (还原文件与原文完全一致)")
        else:
            print(f"5. 最终校验: 失败 (数据在压缩/解压过程中受损)")

test_filename = "shakespeare.txt"


# # 准备测试数据
# with open(test_filename, "w", encoding='utf-8') as f:
#     # 构造一段具有明显频率分布的文本
#     #content = ("AI" * 50) + ("Python" * 30) + ("DataStructure" * 10)
#     f.write(content)


if os.path.exists(test_filename):
    test_huffman(test_filename, show_codes=False) # 大文件建议关闭编码表显示
else:
    print(f"错误：找不到文件 {test_filename}")



def download_shakespeare(filename="shakespeare.txt"):
    url = "https://www.gutenberg.org/files/100/100-0.txt"
    print(f"正在从古登堡计划下载莎士比亚全集...")
    response = requests.get(url)
    response.encoding = 'utf-8'
    with open(filename, "w", encoding='utf-8') as f:
        f.write(response.text)
    print(f"下载完成！文件已保存为: {filename}")

# 如果你本地还没有这个文件，运行一次这个函数
#download_shakespeare()
