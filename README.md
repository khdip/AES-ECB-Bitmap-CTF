# AES-ECB Bitmap CTF

## Challenge
The challenge provides `aes.bmp.enc`, described as a bitmap encrypted using AES in ECB mode. We investigate whether repeated ciphertext blocks reveal the image structure **without learning the AES key**.

**Observed result:** The recovered black-and-white pattern appears to read **`Tro11d`** (the middle two characters are digits `1`; a narrow fragment at the left edge is visible). 

## Team
Member 1 — Md Khaledul Haque | `@khdip`
Member 2 — Raita Tasnim | 

## Reproduce the result
Requirements: Python 3.10+ and Pillow.

```bash
python3 -m pip install -r requirements.txt
python3 solve.py
```

Outputs:
- `images/recovered_raw.bmp`: a valid BMP header attached to the encrypted pixel bytes; the pixel data is **not** decrypted.
- `images/recovered_clean.png`: high-contrast pattern reconstruction made by mapping the most frequent 16-byte ciphertext block to white and other blocks to black.

## Method and evidence
1. Inspect the supplied file: it begins `5a 97`, not the `42 4d` ("BM") signature expected for a standard BMP header.
2. Split the ciphertext into **16-byte blocks**, AES's fixed block size. In the supplied file, there are **57,603 complete blocks** and **1,076 unique complete blocks**. The most frequent block occurs **51,221 times**, approximately **88.9%** of complete blocks. This is strong evidence of repeated-block leakage, consistent with the stated ECB mode.
3. Estimate dimensions: **921,654 = 54 + 640 × 480 × 3** bytes, consistent with a **640×480 24-bit uncompressed BMP**. The encrypted header prevents reading dimensions directly; this is a candidate inferred from size and confirmed visually.
4. Create a new 54-byte BMP header and retain the encrypted bytes after offset 54 to produce a raw visualization.
5. Classify repeated ciphertext blocks, build a black-and-white RGB pixel stream, and flip scanlines because positive-height BMP files use bottom-up storage.
6. View the results and read the visible flag pattern; **no AES key or plaintext color values are recovered**.

**Limitation:** Counting repetitions alone cannot formally prove ECB, and a 921,654-byte file size is not divisible by 16. The challenge specifies ECB; the exact ciphertext generation/padding method is not established by the file alone. This is a pattern-recovery technique rather than cryptographic decryption.

## References and AI-use disclosure
- NIST SP 800-38A — Recommendation for Block Cipher Modes of Operation (2001): https://doi.org/10.6028/NIST.SP.800-38A
- NIST FIPS 197 — Advanced Encryption Standard: https://doi.org/10.6028/NIST.FIPS.197
- Microsoft — BITMAPINFOHEADER documentation: https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapinfoheader
- Python Pillow: https://pillow.readthedocs.io/
- OpenAI, *ChatGPT* (2026), https://chatgpt.com/ — assistance understanding ECB, explaining the reconstruction workflow, and drafting/reviewing documentation.
