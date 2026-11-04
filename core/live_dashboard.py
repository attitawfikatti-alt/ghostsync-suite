import time
import socket
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

from network_watcher import NetworkWatcher

class LiveDashboard:
    def __init__(self, target_cidr=None):
        self.watcher = NetworkWatcher()
        if target_cidr:
            self.target_cidr = target_cidr
            self.gateway = "Manual Target"
        else:
            self.gateway, self.target_cidr = self.watcher.get_gateway_info()
            
        self.discovered_hosts = []
        self.scanned_count = 0
        self.total_hosts = 254

    def build_interface(self) -> Layout:
        """بناء تخطيط الواجهة التفاعلية المقسمة"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )

        # رأس الواجهة (Header)
        progress = int((self.scanned_count / self.total_hosts) * 100) if self.total_hosts else 0
        header_text = Text()
        header_text.append("🛡️ GhostSync-AI Live Sentinel\n", style="bold cyan")
        header_text.append(f"Gateway: {self.gateway} | Target: {self.target_cidr} | التقدم: {progress}% ({self.scanned_count}/{self.total_hosts})", style="bold yellow")
        layout["header"].update(Panel(header_text, border_style="cyan"))

        # جدول الأجهزة المكتشفة لحظياً
        table = Table(title="📡 الأجهزة النشطة المرصودة حالياً", border_style="blue", expand=True)
        table.add_column("عنوان IP", style="bold yellow", width=18)
        table.add_column("المنافذ المفتوحة", style="cyan")
        table.add_column("الخدمات", style="magenta")
        table.add_column("وقت الرصد", style="green", width=12)

        if not self.discovered_hosts:
            table.add_row("-", "جاري البحث...", "-", "-")
        else:
            for host in self.discovered_hosts:
                ports = ", ".join(map(str, host["open_ports"])) if host["open_ports"] else "لا توجد"
                srvs = ", ".join(host["services"]) if host["services"] else "غير محدد"
                table.add_row(host["ip"], ports, srvs, host.get("discovered_at", "-"))

        layout["body"].update(table)
        return layout

    def probe_worker(self, ip):
        """فحص منفرد مع تسجيل توقيت الاكتشاف"""
        res = self.watcher.check_host(ip)
        self.scanned_count += 1
        if res:
            res["discovered_at"] = datetime.now().strftime("%H:%M:%S")
            self.discovered_hosts.append(res)
        return res

    def start(self):
        """بدء حلقة العرض المباشر المتزامنة مع تدفق الفحص"""
        base_ip = self.target_cidr.split("/")[0]
        prefix = ".".join(base_ip.split(".")[:3])
        ips = [f"{prefix}.{i}" for i in range(1, 255)]

        with Live(self.build_interface(), refresh_per_second=4, screen=True) as live:
            with ThreadPoolExecutor(max_workers=35) as executor:
                futures = [executor.submit(self.probe_worker, ip) for ip in ips]
                
                while any(f.running() for f in futures):
                    live.update(self.build_interface())
                    time.sleep(0.2)

                live.update(self.build_interface())
                time.sleep(1.5)

        return self.discovered_hosts

if __name__ == "__main__":
    dash = LiveDashboard()
    results = dash.start()
    print(f"\n✔ انتهى الفحص المباشر. تم رصد {len(results)} أجهزة.")
