import socket
from core.logger import log_info, log_warn, log_error
from core.notifier import send_alert

COMMON_PORTS = [22, 80, 443, 5555, 8000, 8080, 8022, 9090]

def scan_port(ip, port, timeout=0.3):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except:
        return False

def audit_localhost():
    open_local = []
    for port in COMMON_PORTS:
        if scan_port("127.0.0.1", port, timeout=0.15):
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

def evaluate_port_risk(port):
    if port == 5555:
        return "\033[91m[HIGH] ADB Remote\033[0m"
    elif port in [80, 8080, 8000, 9090]:
        return "\033[93m[WARN] HTTP/Cleartext\033[0m"
    elif port in [22, 8022, 443]:
        return "\033[92m[SAFE] Encrypted/SSH\033[0m"
    return f"\033[94m[INFO] Port {port}\033[0m"

def print_audit_banner():
    print("\n" + "=" * 55)
    print(f"{'IP Address':<18} | {'Port':<8} | {'Risk Assessment'}")
    print("-" * 55)

def run_audit(subnet_prefix=None):
    local_ip = get_local_ip()
    local_ports = audit_localhost()
    
    print_audit_banner()
    for p in local_ports:
        print(f"{'127.0.0.1 (Local)':<18} | {p:<8} | {evaluate_port_risk(p)}")

    if not subnet_prefix:
        if local_ip == '127.0.0.1':
            return [{"ip": "127.0.0.1", "open_ports": local_ports, "is_local": True}]
        parts = local_ip.split('.')
        subnet_prefix = f"{parts[0]}.{parts[1]}.{parts[2]}."

    active_hosts = [{
        "ip": local_ip,
        "open_ports": local_ports,
        "is_local": True
    }]

    for i in range(1, 35):
        target_ip = f"{subnet_prefix}{i}"
        if target_ip == local_ip:
            continue
        
        found = []
        for port in [5555, 8022, 22, 80, 8080]:
            if scan_port(target_ip, port, timeout=0.15):
                found.append(port)
                print(f"{target_ip:<18} | {port:<8} | {evaluate_port_risk(port)}")

        if found:
            active_hosts.append({
                "ip": target_ip,
                "open_ports": found,
                "is_local": False
            })

    print("=" * 55)
    log_info(f"اكتمل الفحص بنجاح. الأجهزة المكتشفة: {len(active_hosts)}")
    adb_hosts = [h["ip"] for h in active_hosts if 5555 in h.get("open_ports", [])]
    if adb_hosts:
        send_alert("تحذير أمني حرج", f"تم رصد منافذ ADB مفتوحة على: {ad_hosts_str := ", ".join(adb_hosts)}")
    return active_hosts
