import socket
from rich.table import Table

class LocalAuditor:
    def __init__(self):
        # المنافذ الشائعة للخدمات المحلية وبيئات التطوير على أندرويد
        self.local_services = [
            (3000, "Node.js / React Dev Server"),
            (5000, "Flask / Python Web App"),
            (5555, "ADB Wireless Daemon"),
            (8000, "Django / HTTP Python Server"),
            (8080, "Local Proxy / Dev Server"),
            (8888, "Jupyter Notebook / Web Admin"),
            (9050, "Tor SOCKS5 Proxy")
        ]

    def audit_localhost(self):
        """فحص المنافذ المفتوحة على واجهة الاسترجاع الداخلي 127.0.0.1"""
        active_local = []
        for port, service in self.local_services:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.2)
            try:
                result = sock.connect_ex(("127.0.0.1", port))
                if result == 0:
                    active_local.append({"port": port, "service": service})
            except Exception:
                pass
            finally:
                sock.close()
        return active_local

    def generate_table(self, active_services):
        table = Table(title="📱 الخدمات المكتشفة على المضيف المحلي (Localhost: 127.0.0.1)", border_style="magenta")
        table.add_column("المنفذ (Port)", style="bold yellow", width=12)
        table.add_column("الخدمة المحتملة", style="cyan")
        table.add_column("مستوى التنبيه", style="bold")

        if not active_services:
            table.add_row("-", "لا توجد خدمات تطوير أو منافذ مكشوفة محلياً", "[green]آمن[/green]")
        else:
            for item in active_services:
                alert = "[bold red]عالي[/bold red]" if item["port"] == 5555 else "[bold yellow]متوسط[/bold yellow]"
                table.add_row(str(item["port"]), item["service"], alert)

        return table

if __name__ == "__main__":
    auditor = LocalAuditor()
    found = auditor.audit_localhost()
    print(f"تم رصد {len(found)} خدمات محلية نشطة.")
