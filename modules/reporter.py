import os
import datetime
import subprocess
import shutil
from core.config import BASE_DIR
from core.logger import log_info, log_error

def export_audit_html(audit_data, ai_report_text=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_dir = os.path.join(BASE_DIR, "storage", "reports")
    os.makedirs(html_dir, exist_ok=True)
    html_path = os.path.join(html_dir, f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

    rows = ""
    for host in audit_data:
        ip = host.get("ip", "Unknown")
        ports = host.get("open_ports", [])
        is_local = host.get("is_local", False)
        
        status_badge = '<span class="badge local">Local Host</span>' if is_local else '<span class="badge remote">LAN Host</span>'
        
        port_badges = []
        for p in ports:
            if p == 5555:
                port_badges.append(f'<span class="badge danger">Port {p} (ADB)</span>')
            elif p in [80, 8080, 8000]:
                port_badges.append(f'<span class="badge warn">Port {p} (HTTP)</span>')
            else:
                port_badges.append(f'<span class="badge safe">Port {p}</span>')
        
        ports_str = " ".join(port_badges) if port_badges else '<span class="badge safe">No standard ports</span>'
        rows += f"<tr><td>{ip}</td><td>{status_badge}</td><td>{ports_str}</td></tr>"

    ai_section = ""
    if ai_report_text:
        ai_section = f"""
        <div class="card">
            <h2>🧠 AI Security Evaluation</h2>
            <div class="ai-box">{ai_report_text.replace(chr(10), '<br>')}</div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GhostSync Audit Report - {timestamp}</title>
<style>
body {{ background-color: #0f172a; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 1.5rem; }}
.container {{ max-width: 900px; margin: 0 auto; }}
.header {{ border-bottom: 2px solid #334155; padding-bottom: 1rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; }}
h1 {{ color: #38bdf8; margin: 0; font-size: 1.5rem; }}
.time {{ color: #94a3b8; font-size: 0.9rem; }}
.card {{ background-color: #1e293b; border-radius: 10px; padding: 1.2rem; margin-bottom: 1.5rem; border: 1px solid #334155; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ padding: 0.8rem; text-align: left; border-bottom: 1px solid #334155; }}
th {{ color: #94a3b8; font-weight: 600; }}
.badge {{ display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }}
.danger {{ background-color: #ef4444; color: #fff; }}
.warn {{ background-color: #f59e0b; color: #000; }}
.safe {{ background-color: #10b981; color: #fff; }}
.local {{ background-color: #6366f1; color: #fff; }}
.remote {{ background-color: #475569; color: #fff; }}
.ai-box {{ background-color: #0b1120; padding: 1rem; border-radius: 6px; border-left: 4px solid #38bdf8; font-family: monospace; line-height: 1.6; font-size: 0.9rem; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🛡️ GhostSync Audit Dashboard</h1>
        <span class="time">{timestamp}</span>
    </div>
    <div class="card">
        <h2>🌐 Network Devices & Audited Ports</h2>
        <table>
            <thead>
                <tr><th>Host Address</th><th>Type</th><th>Observed Ports</th></tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    {ai_section}
</div>
</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    log_info(f"تم إنشاء تقرير الويب بنجاح: {html_path}")
    
    # فتح التقرير تلقائياً في المتصفح إذا توفر أمر termux-open
    if shutil.which("termux-open"):
        subprocess.run(["termux-open", html_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_info("تم فتح التقرير في المتصفح.")
    return html_path
