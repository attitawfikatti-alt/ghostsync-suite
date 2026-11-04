#!/usr/bin/env python3
import sys
import os
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(base_dir, "core"))

from network_watcher import NetworkWatcher
from crypto_vault import CryptoVault
from ai_analyzer import AIAnalyzer
from telegram_notifier import send_telegram_alert, load_telegram_config
from live_dashboard import LiveDashboard
from local_auditor import LocalAuditor

console = Console()

def print_banner():
    console.print(Panel.fit(
        "[bold cyan]GhostSync-AI[/bold cyan] | [bold green]Edge Sentinel & Secure Vault[/bold green]",
        border_style="cyan"
    ))

def handle_scan(args):
    print_banner()

    if getattr(args, "local", False):
        with console.status("[bold magenta]جاري فحص المنافذ والخدمات العاملة محلياً على الجهاز..."):
            auditor = LocalAuditor()
            active_services = auditor.audit_localhost()
        console.print(auditor.generate_table(active_services))
        return

    watcher = NetworkWatcher()
    target = args.target

    if not target:
        gw_ip, target = watcher.get_gateway_info()
    else:
        gw_ip = "Manual Target"

    if getattr(args, "live", False):
        dash = LiveDashboard(target_cidr=target)
        devices = dash.start()
    else:
        with console.status(f"[bold green]جاري فحص النطاق ({target})..."):
            devices = watcher.scan_network(target)

    table = Table(title=f"📡 نتائج فحص النطاق ({target})", border_style="blue")
    table.add_column("عنوان IP", style="bold yellow")
    table.add_column("المنافذ المفتوحة", style="cyan")
    table.add_column("الخدمات", style="magenta")

    for dev in devices:
        ports_str = ", ".join(map(str, dev["open_ports"])) if dev["open_ports"] else "لا توجد"
        services_str = ", ".join(dev["services"]) if dev["services"] else "غير محدد"
        table.add_row(dev["ip"], ports_str, services_str)

    console.print(table)

    ai_report = ""
    if getattr(args, "ai", False):
        with console.status("[bold yellow]جاري تقييم المخاطر وتوليد التوصيات..."):
            analyzer = AIAnalyzer()
            ai_report = analyzer.evaluate_scan(devices)
        console.print(Panel(ai_report, title="🛡️ تقرير التقييم الأمني", border_style="green"))

    report_path = watcher.save_report(devices, ai_report)
    console.print(f"[bold green]✔ تم حفظ تقرير التدقيق (Markdown + HTML):[/bold green]\n{report_path}")

    if getattr(args, "notify", False):
        tg_cfg = load_telegram_config()
        if tg_cfg.get("enabled"):
            with console.status("[bold magenta]جاري التشفير والإرسال إلى تيليجرام..."):
                vault = CryptoVault()
                passphrase = args.passphrase or "DefaultGhostPass_2026"
                enc_path = vault.encrypt_file(report_path, passphrase=passphrase)
                msg = f"🚨 *GhostSync Alert*\n• *Target:* `{target}`\n• *Hosts:* `{len(devices)}`"
                send_telegram_alert(msg, file_path=enc_path)
                console.print("[bold green]✔ تم إرسال الإشعار والملف المشفر بنجاح.[/bold green]")
        else:
            console.print("[yellow][!] ميزة تيليجرام معطلة داخل config/settings.json[/yellow]")

def handle_vault(args):
    print_banner()
    vault = CryptoVault()

    if args.encrypt:
        passphrase = args.passphrase or console.input("[bold yellow]أدخل كلمة مرور التشفير: [/bold yellow]", password=True)
        out = vault.encrypt_file(args.encrypt, passphrase)
        console.print(f"[bold green]✔ تم التشفير بنجاح:[/bold green]\n{out}")

    elif args.decrypt:
        passphrase = args.passphrase or console.input("[bold yellow]أدخل كلمة مرور فك التشفير: [/bold yellow]", password=True)
        out = vault.decrypt_file(args.decrypt, passphrase, args.output)
        console.print(f"[bold green]✔ تم فك التشفير وحفظ الملف في:[/bold green]\n{out}")

    elif getattr(args, "cleanup", None):
        removed = vault.cleanup_old_archives(keep_latest=args.cleanup)
        if removed:
            console.print(f"[bold yellow]✔ تم حذف {len(removed)} أرشيفات قديمة للحفاظ على المساحة.[/bold yellow]")
        else:
            console.print("[green]الخزينة ضمن الحدود المسموحة، لم يتم حذف أي ملف.[/green]")

    elif args.list:
        files = vault.list_vault()
        table = Table(title="🔒 محتويات الخزينة المشفرة", border_style="yellow")
        table.add_column("الملف المشفر", style="bold white")
        for f in files:
            table.add_row(f)
        console.print(table)

def handle_cron(args):
    print_banner()
    import subprocess
    cron_cmd = os.path.expanduser("~/ghostsync/core/cron_task.sh")

    if args.enable:
        subprocess.run("crond", shell=True)
        cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout or ""
        lines = [l for l in cur.splitlines() if "ghostsync" not in l]
        lines.append(f"0 0 * * * {cron_cmd}")
        new_crontab = "\n".join(lines) + "\n"
        subprocess.run(["crontab", "-"], input=new_crontab, text=True)
        console.print("[bold green]✔ تم تفعيل الجدولة اليومية بنجاح (كل ليلة عند الساعة 00:00).[/bold green]")

    elif args.disable:
        cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout or ""
        lines = [l for l in cur.splitlines() if "ghostsync" not in l]
        new_crontab = "\n".join(lines) + "\n" if lines else ""
        subprocess.run(["crontab", "-"], input=new_crontab, text=True)
        console.print("[bold yellow]✔ تم تعطيل جدولة الفحص التلقائي.[/bold yellow]")

    elif args.status:
        cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout or ""
        active = any("ghostsync" in l for l in cur.splitlines())
        status_text = "[bold green]مفعلة (Active)[/bold green]" if active else "[bold red]معطلة (Inactive)[/bold red]"
        console.print(Panel(f"حالة الجدولة التلقائية: {status_text}\nالمهمة: 0 0 * * * ~/ghostsync/core/cron_task.sh", title="🕒 Cron Status"))

def handle_doctor(args):
    print_banner()
    import shutil
    import subprocess

    table = Table(title="🔍 فحص تكامل النظام والبيئة التشغيلية (System Doctor)", border_style="cyan")
    table.add_column("المكون / التبعية", style="bold white")
    table.add_column("الحالة", style="bold")
    table.add_column("التفاصيل", style="dim")

    gpg_bin = shutil.which("gpg")
    table.add_row("محرك التشفير GPG", "[green]✔ متوفر[/green]" if gpg_bin else "[red]✘ مفقود[/red]", gpg_bin or "pkg install gnupg")

    try:
        import rich
        table.add_row("مكتبة واجهة المستخدم Rich", "[green]✔ مثبتة[/green]", f"الإصدار جاهزة")
    except ImportError:
        table.add_row("مكتبة Rich", "[red]✘ مفقودة[/red]", "pip install rich")

    crond_running = subprocess.run(["pgrep", "crond"], capture_output=True).returncode == 0
    table.add_row("خدمة الجدولة crond", "[green]✔ تعمل[/green]" if crond_running else "[yellow]! متوقفة[/yellow]", "شغّل: crond")

    rep_dir = os.path.expanduser("~/ghostsync/reports")
    vault_dir = os.path.expanduser("~/ghostsync/vault")
    rep_count = len(os.listdir(rep_dir)) if os.path.exists(rep_dir) else 0
    v_count = len(os.listdir(vault_dir)) if os.path.exists(vault_dir) else 0

    table.add_row("مجلد التقارير (reports)", "[green]✔ متاح[/green]", f"{rep_count} ملفات")
    table.add_row("مجلد الخزينة (vault)", "[green]✔ متاح[/green]", f"{v_count} حاويات مشفرة")

    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="GhostSync-AI CLI")
    subparsers = parser.add_subparsers(dest="command")

    # أمر الفحص
    scan_p = subparsers.add_parser("scan", help="فحص أمني للشبكة")
    scan_p.add_argument("--target", type=str, help="نطاق IP مخصص")
    scan_p.add_argument("--local", action="store_true", help="فحص المنافذ المحلية 127.0.0.1")
    scan_p.add_argument("--live", action="store_true", help="لوحة حية")
    scan_p.add_argument("--ai", action="store_true", help="تقييم ذكي")
    scan_p.add_argument("--notify", action="store_true", help="إشعار تيليجرام")
    scan_p.add_argument("--passphrase", type=str, help="كلمة المرور")

    # أمر الخزينة
    vault_p = subparsers.add_parser("vault", help="إدارة الخزينة")
    vault_p.add_argument("--encrypt", type=str, help="مسار ملف للتشفير")
    vault_p.add_argument("--decrypt", type=str, help="مسار ملف مشفر")
    vault_p.add_argument("--output", type=str, help="مسار الاستخراج")
    vault_p.add_argument("--passphrase", type=str, help="كلمة المرور")
    vault_p.add_argument("--list", action="store_true", help="عرض الملفات")
    vault_p.add_argument("--cleanup", type=int, nargs="?", const=5, help="تنظيف الخزينة")

    # أمر الجدولة
    cron_p = subparsers.add_parser("cron", help="الجدولة الزمنية")
    cron_p.add_argument("--enable", action="store_true")
    cron_p.add_argument("--disable", action="store_true")
    cron_p.add_argument("--status", action="store_true")

    # أمر الفحص الذاتي
    subparsers.add_parser("doctor", help="التحقق من جاهزية النظام والتبعيات")

    # أمر موجه الأوامر التفاعلي
    subparsers.add_parser("shell", help="الدخول إلى موجه الأوامر التفاعلي")

    args = parser.parse_args()

    if args.command == "scan":
        handle_scan(args)
    elif args.command == "vault":
        handle_vault(args)
    elif args.command == "cron":
        handle_cron(args)
    elif args.command == "doctor":
        handle_doctor(args)
    elif args.command == "shell":
        from interactive_shell import start_shell
        start_shell(sys.modules[__name__])
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
