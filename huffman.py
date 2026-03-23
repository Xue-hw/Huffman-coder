import heapq
import os
import pickle
from collections import Counter

class HuffmanNode:
    """哈夫曼树节点"""
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    # 为了让 heapq 能够比较节点频率，必须实现“小于”魔术方法
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCoder:
    def __init__(self):
        self.codes = {}      # 字符 -> 编码 (e.g., 'a': '101')
        self.reverse_codes = {} # 编码 -> 字符 (解压用)

    def _get_frequencies(self, text):
        return Counter(text)

    def _build_huffman_tree(self, frequencies):
        priority_queue = [HuffmanNode(char, freq) for char, freq in frequencies.items()]
        heapq.heapify(priority_queue)

        while len(priority_queue) > 1:
            node1 = heapq.heappop(priority_queue)
            node2 = heapq.heappop(priority_queue)

            # 合并两个最小节点
            merged = HuffmanNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(priority_queue, merged)

        return heapq.heappop(priority_queue)

    def _generate_codes(self, root, current_code):
        if root is None:
            return

        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_codes[current_code] = root.char
            return

        self._generate_codes(root.left, current_code + "0")
        self._generate_codes(root.right, current_code + "1")

    def _get_encoded_text(self, text):
        return "".join([self.codes[char] for char in text])

    def _pad_encoded_text(self, encoded_text):
        """将比特流补齐为8的倍数，并记录补了几个0"""
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"
        
        # 将补零的数量转换成8位二进制，放在最前面
        padded_info = "{0:08b}".format(extra_padding)
        return padded_info + encoded_text

    def _get_byte_array(self, padded_encoded_text):
        """将 01 字符串转换成真正的字节数组"""
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b

    def compress(self, input_path):
        output_path = input_path + ".huff"
        
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # 1. 统计频率并建树
        freqs = self._get_frequencies(text)
        root = self._build_huffman_tree(freqs)
        
        # 2. 生成编码表
        self._generate_codes(root, "")

        # 3. 编码转换与补齐
        encoded_text = self._get_encoded_text(text)
        padded_encoded_text = self._pad_encoded_text(encoded_text)
        byte_array = self._get_byte_array(padded_encoded_text)

        # 4. 写入文件：先存频率表（Header），再存数据
        with open(output_path, 'wb') as output:
            pickle.dump(freqs, output)  # 使用 pickle 简单存储频率表
            output.write(byte_array)
        
        return output_path

    def decompress(self, input_path):
        output_path = input_path.replace(".huff", "_decompressed.txt")

        with open(input_path, 'rb') as f:
            # 1. 读取频率表并重建树
            freqs = pickle.load(f)
            root = self._build_huffman_tree(freqs)
            self._generate_codes(root, "")

            # 2. 读取剩下的二进制数据
            bit_string = ""
            byte = f.read(1)
            while len(byte) > 0:
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = f.read(1)

        # 3. 移除补零
        padded_info = bit_string[:8]
        extra_padding = int(padded_info, 2)
        bit_string = bit_string[8:]
        encoded_text = bit_string[:-1*extra_padding]

        # 4. 根据树结构解码
        current_code = ""
        decoded_text = ""
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_codes:
                decoded_text += self.reverse_codes[current_code]
                current_code = ""

        with open(output_path, 'w', encoding='utf-8') as output:
            output.write(decoded_text)
        
        return output_path