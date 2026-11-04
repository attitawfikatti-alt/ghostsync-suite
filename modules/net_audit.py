import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor
from core.config import CRITICAL_PORTS, SCAN_TIMEOUT
from core.logger import log_info, log_warn

def check_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(SCAN_TIMEOUT)
            if s.connect_ex((ip, port)) == 0:
                return port
    except Exception:
        pass
    return None

def scan_target(ip):
    open_ports = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda p: check_port(ip, p), CRITICAL_PORTS)
        open_ports = [p for p in results if p is not None]
    return open_ports

def get_active_hosts():
    hosts = []
    try:
        res = subprocess.run(["ip", "neigh"], stdout=subprocess.PIPE, text=True)
        for line in res.stdout.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 5 and parts[4] != "FAILED":
                hosts.append(parts[0])
    except Exception:
        pass
    return list(set(hosts))

def run_audit():
    log_info("بدء فحص الشبكة المحلية والأجهزة المتصلة...")
    hosts = get_active_hosts()
    if not hosts:
        log_warn("لم يتم العثور على أجهزة نشطة في جدول الجوار (ARP). تأكد من اتصال Wi-Fi.")
        return []

    log_info(f"تم رصد {len(hosts)} جهاز متصل. جاري تدقيق المنافذ المفتوحة...")
    report = []
    for ip in hosts:
        open_p = scan_target(ip)
        status = {"ip": ip, "open_ports": open_p}
        report.append(status)
        if 5555 in open_p:
            log_warn(f"تنبيه أمني: المنفذ 5555 (ADB) مفتوح على الهدف {ip}!")
        elif open_p:
            log_info(f"الهدف {ip} يحتوي على منافذ مفتوحة: {open_p}")
        else:
            log_info(f"الهدف {ip}: لا توجد منافذ حرجة مكشوفة.")
    return report
