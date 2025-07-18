import heapq
from collections import defaultdict
import os
import pickle

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def get_frequency(data):
    freq = defaultdict(int)
    for byte in data:
        freq[byte] += 1
    return freq

def build_huffman_tree(freq_map):
    heap = [Node(byte, freq) for byte, freq in freq_map.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = Node(None, n1.freq + n2.freq)
        merged.left = n1
        merged.right = n2
        heapq.heappush(heap, merged)

    return heap[0] if heap else None

def build_codes(root):
    codes = {}

    def generate_code(node, current_code):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = current_code
        generate_code(node.left, current_code + "0")
        generate_code(node.right, current_code + "1")

    generate_code(root, "")
    return codes

def encode_data(data, codes):
    encoded_text = ''.join(codes[byte] for byte in data)
    extra_padding = 8 - len(encoded_text) % 8
    encoded_text += "0" * extra_padding
    padded_info = "{0:08b}".format(extra_padding)
    final_bits = padded_info + encoded_text
    return bytearray(int(final_bits[i:i+8], 2) for i in range(0, len(final_bits), 8))

def decode_data(encoded_bytes, codes):
    bit_string = ''.join(bin(byte)[2:].rjust(8, '0') for byte in encoded_bytes)
    extra_padding = int(bit_string[:8], 2)
    encoded_text = bit_string[8:-extra_padding]
    reverse_map = {v: k for k, v in codes.items()}
    current_code = ""
    decoded_bytes = bytearray()

    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_map:
            decoded_bytes.append(reverse_map[current_code])
            current_code = ""

    return decoded_bytes


def compress(input_path, output_path):
    with open(input_path, "rb") as f:
        data = f.read()

    freq_map = get_frequency(data)
    root = build_huffman_tree(freq_map)
    codes = build_codes(root)
    encoded_bytes = encode_data(data, codes)

    with open(output_path, "wb") as f:
        
        f.write(pickle.dumps(codes) + b"HUFFMAN-CODES-END")
        f.write(encoded_bytes)

    return codes

def decompress(input_path, output_path):
    with open(input_path, "rb") as f:
        content = f.read()

    marker = b'HUFFMAN-CODES-END'
    marker_index = content.find(marker)

    if marker_index == -1:
        raise ValueError("Invalid compressed file: Huffman code section not found.")

    codes = pickle.loads(content[:marker_index])
    encoded_bytes = content[marker_index + len(marker):]
    decoded_bytes = decode_data(encoded_bytes, codes)

    with open(output_path, "wb") as f:
        f.write(decoded_bytes)
