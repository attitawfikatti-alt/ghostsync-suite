import os
import time
import hashlib
from cryptography.fernet import Fernet
from core.logger import log_info

def run_benchmark(sizes_mb=[1, 5, 10]):
    print("\n\033[96m=== اختبار أداء وسرعة التشفير (GhostSync Benchmark) ===\033[0m")
    key = Fernet.generate_key()
    fernet = Fernet(key)

    print(f"{'Data Size':<12} | {'Operation':<14} | {'Time (s)':<10} | {'Throughput (MB/s)'}")
    print("-" * 55)

    for mb in sizes_mb:
        payload_bytes = os.urandom(mb * 1024 * 1024)

        # 1. اختبار التشفير
        t0 = time.perf_counter()
        encrypted = fernet.encrypt(payload_bytes)
        t_enc = time.perf_counter() - t0
        enc_speed = mb / t_enc if t_enc > 0 else 0
        print(f"{f'{mb} MB':<12} | {'Encryption':<14} | {t_enc:<10.3f} | \033[92m{enc_speed:>7.2f} MB/s\033[0m")

        # 2. اختبار فك التشفير
        t0 = time.perf_counter()
        fernet.decrypt(encrypted)
        t_dec = time.perf_counter() - t0
        dec_speed = mb / t_dec if t_dec > 0 else 0
        print(f"{f'{mb} MB':<12} | {'Decryption':<14} | {t_dec:<10.3f} | \033[94m{dec_speed:>7.2f} MB/s\033[0m")

        # 3. اختبار تجزئة SHA-256
        t0 = time.perf_counter()
        hashlib.sha256(payload_bytes).hexdigest()
        t_hash = time.perf_counter() - t0
        hash_speed = mb / t_hash if t_hash > 0 else 0
        print(f"{f'{mb} MB':<12} | {'SHA-256 Hash':<14} | {t_hash:<10.3f} | \033[93m{hash_speed:>7.2f} MB/s\033[0m")
        print("-" * 55)

    log_info("اكتمل اختبار الأداء بنجاح.")
