import socket
import subprocess
import re
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

class NetworkWatcher:
    def __init__(self, ports_to_check=None):
        self.ports = ports_to_check or [
            (53, "DNS Resolver"),
            (80, "HTTP Control Panel"),
            (443, "HTTPS Web"),
            (5555, "Wireless ADB"),
            (8080, "Web Proxy / Admin")
        ]
        self.reports_dir = os.path.expanduser("~/ghostsync/reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def get_gateway_info(self):
        """استخراج عنوان البوابة ونطاق الشبكة الفرعية الافتراضية"""
        try:
            route_out = subprocess.check_output(["ip", "route"], text=True)
            for line in route_out.splitlines():
                if "default via" in line:
                    gw = line.split()[2]
                    subnet = ".".join(gw.split(".")[:3]) + ".0/24"
                    return gw, subnet
        except Exception:
            pass
        return "192.168.1.1", "192.168.1.0/24"

    def check_host(self, ip):
        """فحص المنافذ المفتوحة لجهاز محدد"""
        open_ports = []
        services = []
        for port, service in self.ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            try:
                res = s.connect_ex((ip, port))
                if res == 0:
                    open_ports.append(port)
                    services.append(service)
            except Exception:
                pass
            finally:
                s.close()

        if open_ports:
            return {"ip": ip, "open_ports": open_ports, "services": services}
        return None

    def scan_network(self, target_cidr=None):
        """تنفيذ مسح متعدد المسارات (Multi-threaded) لنطاق معين"""
        if not target_cidr:
            _, target_cidr = self.get_gateway_info()

        base_ip = target_cidr.split("/")[0]
        prefix = ".".join(base_ip.split(".")[:3])
        ips_to_scan = [f"{prefix}.{i}" for i in range(1, 255)]

        active_devices = []
        with ThreadPoolExecutor(max_workers=45) as executor:
            results = executor.map(self.check_host, ips_to_scan)
            for r in results:
                if r:
                    active_devices.append(r)
        return active_devices

    def save_report(self, devices, ai_analysis=""):
        """حفظ التقرير بصيغتي Markdown و HTML"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_path = os.path.join(self.reports_dir, f"scan_{timestamp}.md")
        html_path = os.path.join(self.reports_dir, f"scan_{timestamp}.html")

        # 1. تقرير Markdown
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# GhostSync Network Audit - {timestamp}\n\n")
            f.write("| IP Address | Open Ports | Services |\n")
            f.write("|---|---|---|\n")
            for dev in devices:
                ports = ", ".join(map(str, dev["open_ports"]))
                srvs = ", ".join(dev["services"])
                f.write(f"| {dev['ip']} | {ports} | {srvs} |\n")
            
            if ai_analysis:
                f.write(f"\n## Security Evaluation\n{ai_analysis}\n")

        # 2. تقرير HTML متجاوب بتصميم داكن
        rows = "".join([
            f"<tr><td><b>{d['ip']}</b></td><td>{', '.join(map(str, d['open_ports']))}</td><td>{', '.join(d['services'])}</td></tr>"
            for d in devices
        ])
        html_content = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>GhostSync Audit Report</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }}
h1, h2 {{ color: #58a6ff; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: #161b22; border-radius: 8px; overflow: hidden; }}
th, td {{ padding: 12px; text-align: right; border-bottom: 1px solid #30363d; }}
th {{ background: #21262d; color: #f0f6fc; }}
.box {{ background: #161b22; border-left: 4px solid #3fb950; padding: 15px; border-radius: 6px; margin-top: 20px; white-space: pre-wrap; }}
</style>
</head>
<body>
<h1>🛡️ تقرير الفحص الأمني (GhostSync-AI)</h1>
<p>وقت الفحص: <code>{timestamp}</code> | الأجهزة المكتشفة: <b>{len(devices)}</b></p>
<table>
<thead><tr><th>عنوان IP</th><th>المنافذ المفتوحة</th><th>الخدمات المحتملة</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<div class="box"><h2>التقييم الأمني:</h2>{ai_analysis or 'لا توجد ملاحظات.'}</div>
</body>
</html>"""
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return md_path
