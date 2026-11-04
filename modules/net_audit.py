import socket
import subprocess
from core.logger import log_info, log_warn, log_error

COMMON_PORTS = [22, 80, 443, 5555, 8000, 8080, 8022, 9090]

def scan_port(ip, port, timeout=0.4):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False

def audit_localhost():
    log_info("بدء تدقيق المنافذ والخدمات المحلية (localhost)...")
    open_local = []
    for port in COMMON_PORTS:
        if scan_port("127.0.0.1", port, timeout=0.2):
            open_local.append(port)
    return open_local

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def run_audit(subnet_prefix=None):
    local_ip = get_local_ip()
    log_info(f"عنوان IP المحلي للجهاز: {local_ip}")

    # فحص المنافذ المحلية
    local_ports = audit_localhost()
    if local_ports:
        log_warn(f"منافذ مفتوحة محلياً على هذا الجهاز: {local_ports}")
    else:
        log_info("لم يتم رصد منافذ شائعة مفتوحة على الجهاز المحلي.")

    if not subnet_prefix:
        if local_ip == '127.0.0.1':
            log_warn("الجهاز غير متصل بشبكة Wi-Fi محلية.")
            return [{"ip": "127.0.0.1", "open_ports": local_ports, "is_local": True}]
        parts = local_ip.split('.')
        subnet_prefix = f"{parts[0]}.{parts[1]}.{parts[2]}."

    log_info(f"بدء فحص النطاق المحلي: {subnet_prefix}1 إلى {subnet_prefix}254...")
    active_hosts = []

    # إدراج فحص الجهاز نفسه أولاً
    active_hosts.append({
        "ip": local_ip,
        "open_ports": local_ports,
        "is_local": True
    })

    # فحص الأجهزة المتصلة على نفس الشبكة (عينة سريعة لأول 30 عنواناً أو المنافذ الحيوية)
    for i in range(1, 35):
        target_ip = f"{subnet_prefix}{i}"
        if target_ip == local_ip:
            continue
        
        found_ports = []
        for port in [5555, 8022, 22, 80]:
            if scan_port(target_ip, port, timeout=0.15):
                found_ports.append(port)

        if found_ports:
            log_info(f"جهاز نشط: {target_ip} | منافذ مفتوحة: {found_ports}")
            active_hosts.append({
                "ip": target_ip,
                "open_ports": found_ports,
                "is_local": False
            })

    log_info(f"اكتمل الفحص. إجمالي الأجهزة المسجلة: {len(active_hosts)}")
    return active_hosts
