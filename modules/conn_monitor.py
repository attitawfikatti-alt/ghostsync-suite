import subprocess
import shutil
from core.logger import log_info, log_warn

def get_active_connections():
    print("\n\033[96m=== مراقبة الاتصالات الشبكية الحية (Live Sockets & Remote Conns) ===\033[0m")
    
    cmd = None
    if shutil.which("ss"):
        cmd = ["ss", "-tuna"]
    elif shutil.which("netstat"):
        cmd = ["netstat", "-tuna"]

    if not cmd:
        log_warn("الأداتان ss و netstat غير متوفرتين. قم بتثبيت: pkg install iproute2 net-tools")
        return

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = proc.stdout.strip().split("\n")
        
        print(f"{'Protocol':<8} | {'State':<12} | {'Local Address':<22} | {'Remote Address':<22}")
        print("-" * 72)

        active_count = 0
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 5:
                proto = parts[0]
                state = parts[1] if len(parts) > 5 else "ESTAB"
                local = parts[-2]
                remote = parts[-1]

                # تمييز الاتصالات المنشأة فعلياً
                if "ESTAB" in state or "ESTABLISHED" in state:
                    print(f"{proto:<8} | \033[92m{state:<12}\033[0m | {local:<22} | \033[93m{remote:<22}\033[0m")
                    active_count += 1
                elif "LISTEN" in state:
                    print(f"{proto:<8} | \033[94m{state:<12}\033[0m | {local:<22} | {remote:<22}")

        print("=" * 72)
        log_info(f"تم رصد {active_count} اتصال نشط (ESTABLISHED) في الوقت الفعلي.")
    except Exception as e:
        log_warn(f"تعذر استعراض المقابس: {e}")
