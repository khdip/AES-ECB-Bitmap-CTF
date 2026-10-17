#!/usr/bin/env python3
"""Recover ECB block patterns from the supplied encrypted BMP, without an AES key."""
from collections import Counter
from pathlib import Path
import struct
from PIL import Image

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "aes.bmp.enc"
OUTPUT = ROOT / "images"
OUTPUT.mkdir(exist_ok=True)
data = SOURCE.read_bytes()
width, height = 640, 480
size = width * height * 3
assert len(data) == 54 + size, "Unexpected file size: check candidate BMP dimensions"

blocks = [data[i:i + 16] for i in range(0, len(data) - 15, 16)]
frequency = Counter(blocks)
background, count = frequency.most_common(1)[0]
print(f"File bytes: {len(data):,}")
print(f"Complete 16-byte blocks: {len(blocks):,}")
print(f"Unique complete blocks: {len(frequency):,}")
print(f"Most frequent complete block: {count:,} ({count/len(blocks):.1%})")
print(f"Most frequent block (hex): {background.hex()}")

# Rebuild an unencrypted 54-byte BMP header; pixel payload is still ciphertext.
header = (b"BM" + struct.pack("<IHHI", len(data), 0, 0, 54)
          + struct.pack("<IiiHHIIiiII", 40, width, height, 1, 24,
                        0, size, 2835, 2835, 0, 0))
(OUTPUT / "recovered_raw.bmp").write_bytes(header + data[54:])

# Classify each full AES-sized ciphertext block into likely background/non-background.
# Include the final partial bytes as non-background; they are not a complete AES block.
mask = bytearray()
for offset in range(0, len(data), 16):
    block = data[offset:offset + 16]
    mask.extend((b"\xff" if len(block) == 16 and block == background else b"\x00") * len(block))
pixels = bytes(mask[54:54 + size])
# BMP stores scanlines bottom-up for positive height; reflect that in a normal PNG.
img = Image.frombytes("RGB", (width, height), pixels)
img.transpose(Image.Transpose.FLIP_TOP_BOTTOM).save(OUTPUT / "recovered_clean.png")
print("Saved images/recovered_raw.bmp and images/recovered_clean.png")
print("Candidate flag: Tro11d (verify visually; first character may be clipped)")
