import huffman
import os

def test_huffman(file_path):
    coder = huffman.HuffmanCoder()

    # 压缩
    compressed_file = coder.compress(file_path)
    # 解压
    decompressed_file = coder.decompress(compressed_file)

    # 计算大小
    original_size = os.path.getsize(file_path)
    compressed_size = os.path.getsize(compressed_file)

    print(f"--- 压缩报告 ---")
    print(f"原始文件: {original_size} 字节")
    print(f"压缩文件: {compressed_size} 字节")
    print(f"压缩率: {(1 - compressed_size/original_size)*100:.2f}%")
    print(f"校验结果: {'成功' if open(file_path).read() == open(decompressed_file).read() else '失败'}")

# 创建一个测试文件
with open("test.txt", "w") as f:
    f.write("aaaaabbbbcccdde" * 100) # 重复性越高，压缩率越高

test_huffman("test.txt")