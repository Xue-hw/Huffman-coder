# import heapq
# import os
# import pickle
# from collections import Counter
# import struct # 用于处理二进制数据打包

# class HuffmanNode:
#     def __init__(self, char, freq):
#         self.char = char
#         self.freq = freq
#         self.left = None
#         self.right = None

#     def __lt__(self, other):
#         return self.freq < other.freq

# class HuffmanCoder:
#     def __init__(self):
#         self.codes = {}
#         self.reverse_codes = {}

#     def _build_tree(self, freqs):
#         pq = [HuffmanNode(c, f) for c, f in freqs.items()]
#         heapq.heapify(pq)
#         if len(pq) == 1: # 处理只有一个字符的特殊情况
#             node = heapq.heappop(pq)
#             root = HuffmanNode(None, node.freq)
#             root.left = node
#             return root
#         while len(pq) > 1:
#             n1, n2 = heapq.heappop(pq), heapq.heappop(pq)
#             merged = HuffmanNode(None, n1.freq + n2.freq)
#             merged.left, merged.right = n1, n2
#             heapq.heappush(pq, merged)
#         return heapq.heappop(pq)

#     def _generate_codes(self, root, current_code):
#         if root is None: return
#         if root.char is not None:
#             self.codes[root.char] = current_code
#             self.reverse_codes[current_code] = root.char
#             return
#         self._generate_codes(root.left, current_code + "0")
#         self._generate_codes(root.right, current_code + "1")

#     def compress(self, input_path):
#         output_path = input_path + ".huff"
        
#         # 方案 A：使用 'r' 模式读取字符，而不是字节
#         with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
#             text = f.read()
        
#         if not text: return None

#         # 统计字符频率 (此时包含汉字、标点、英文字母)
#         freqs = Counter(text)
#         root = self._build_tree(freqs)
        
#         # 范式化逻辑（建议保留，因为字符多，范式存码长更省空间）
#         lengths = {}
#         self._get_lengths(root, 0, lengths)
#         self.codes = self._generate_canonical_codes(lengths)

#         # 编码数据：每个 char 对应一个 code
#         encoded_str = "".join([self.codes[c] for c in text])
        
#         # 存储时需要注意：pickle 存储的是 {字符: 码长}
#         with open(output_path, 'wb') as output:
#             pickle.dump(lengths, output)
        
#         # 弃用pickle版本，在文件较小时表现更好
#         # with open(output_path, 'wb') as output:
#         #     # 写入 256 个频率，每个 4 字节 (I 代表无符号 32 位整数)
#         #     for i in range(256):
#         #         freq = freqs.get(i, 0)
#         #         output.write(struct.pack('I', freq))
#         #     output.write(byte_arr)

#         return output_path

#     def decompress(self, input_path):
#         # 任务要求：输出为文本文件
#         output_path = input_path.replace(".huff", "_decompressed.txt")

#         with open(input_path, 'rb') as f:
#             freqs = pickle.load(f)
#             root = self._build_tree(freqs)
#             self.reverse_codes = {}
#             self._generate_codes(root, "")
        
#         # 弃用pickle版本，在文件较小时表现更好
#         # with open(input_path, 'rb') as f:
#         #     freqs = {}
#         #     for i in range(256):
#         #         freq_bytes = f.read(4)
#         #         freq = struct.unpack('I', freq_bytes)[0]
#         #         if freq > 0:
#         #             freqs[i] = freq

#             # 读取二进制数据并转为比特位
#             bit_string = ""
#             byte = f.read(1)
#             while byte:
#                 # 关键：使用 byte[0] 直接获取整数值
#                 bit_string += format(byte[0], '08b')
#                 byte = f.read(1)

#         extra_padding = int(bit_string[:8], 2)
#         encoded_data = bit_string[8 : -extra_padding if extra_padding > 0 else None]

#         # 译码为字节序列
#         decoded_bytes = bytearray()
#         curr = ""
#         for bit in encoded_data:
#             curr += bit
#             if curr in self.reverse_codes:
#                 decoded_bytes.append(self.reverse_codes[curr])
#                 curr = ""

#         # 任务要求：写回文本文件
#         with open(output_path, 'wb') as output:
#             output.write(decoded_bytes)
        
#         return output_path


import heapq
import pickle
from collections import Counter

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCoder:
    def __init__(self):
        self.codes = {}
        self.reverse_codes = {}

    def _build_tree(self, freqs):
        pq = [HuffmanNode(c, f) for c, f in freqs.items()]
        heapq.heapify(pq)
        if len(pq) == 0: return None
        if len(pq) == 1:
            node = heapq.heappop(pq)
            root = HuffmanNode(None, node.freq)
            root.left = node
            return root
        while len(pq) > 1:
            n1, n2 = heapq.heappop(pq), heapq.heappop(pq)
            merged = HuffmanNode(None, n1.freq + n2.freq)
            merged.left, merged.right = n1, n2
            heapq.heappush(pq, merged)
        return heapq.heappop(pq)

    def _get_lengths(self, root, current_len, lengths):
        """获取字符对应的编码长度"""
        if root is None: return
        if root.char is not None:
            lengths[root.char] = current_len
            return
        self._get_lengths(root.left, current_len + 1, lengths)
        self._get_lengths(root.right, current_len + 1, lengths)

    def _generate_canonical_codes(self, lengths):
        """根据长度生成范式哈夫曼编码"""
        if not lengths: return {}
        # 排序：先按长度，再按字符字典序
        sorted_items = sorted(lengths.items(), key=lambda x: (x[1], x[0]))
        
        codes = {}
        current_code = 0
        last_len = sorted_items[0][1]

        for char, length in sorted_items:
            current_code <<= (length - last_len)
            codes[char] = format(current_code, f'0{length}b')
            current_code += 1
            last_len = length
        return codes

    def compress(self, input_path):
        output_path = input_path + ".huff"
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        if not text: return None

        # 1. 统计字符频率并获取码长
        freqs = Counter(text)
        root = self._build_tree(freqs)
        lengths = {}
        self._get_lengths(root, 0, lengths)

        # 2. 生成范式编码并转换数据
        self.codes = self._generate_canonical_codes(lengths)
        encoded_str = "".join([self.codes[c] for c in text])
        
        # 3. 补齐位处理
        extra_padding = (8 - len(encoded_str) % 8) % 8
        full_bit_str = "{0:08b}".format(extra_padding) + encoded_str + ("0" * extra_padding)
        
        # 4. 写入文件
        byte_arr = bytearray()
        for i in range(0, len(full_bit_str), 8):
            byte_arr.append(int(full_bit_str[i:i+8], 2))

        with open(output_path, 'wb') as output:
            pickle.dump(lengths, output) # 方案A存储字符码长表
            output.write(byte_arr)
        return output_path

    def decompress(self, input_path):
        output_path = input_path.replace(".huff", "_decompressed.txt")
        with open(input_path, 'rb') as f:
            # 1. 加载码长表并重建范式映射
            lengths = pickle.load(f)
            self.codes = self._generate_canonical_codes(lengths)
            self.reverse_codes = {v: k for k, v in self.codes.items()}

            # 2. 读取二进制数据
            bit_string = ""
            chunk = f.read(1024*64) # 分块读取提高性能
            while chunk:
                bit_string += "".join(format(b, '08b') for b in chunk)
                chunk = f.read(1024*64)

        if not bit_string: return None
        extra_padding = int(bit_string[:8], 2)
        encoded_data = bit_string[8 : -extra_padding if extra_padding > 0 else None]

        # 3. 译码为字符串（注意：方案A处理的是字符）
        decoded_chars = []
        curr = ""
        for bit in encoded_data:
            curr += bit
            if curr in self.reverse_codes:
                decoded_chars.append(self.reverse_codes[curr])
                curr = ""

        # 4. 写回文本文件 (使用 utf-8 编码)
        with open(output_path, 'w', encoding='utf-8') as output:
            output.write("".join(decoded_chars))
        return output_path