import cmd
import shlex
import sys
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

class GhostSyncShell(cmd.Cmd):
    intro = "\n" + "=" * 50 + "\n🛡️ GhostSync-AI Interactive Environment\nاكتب 'help' أو '?' لعرض الأوامر، أو 'exit' للخروج.\n" + "=" * 50
    prompt = "ghostsync> "

    def __init__(self, main_module):
        super().__init__()
        self.main_module = main_module

    def default(self, line):
        """تمرير الأوامر مباشرة لمفسر وسائط GhostSync"""
        try:
            args_list = shlex.split(line)
            if not args_list:
                return
            
            # محاكاة استدعاء argparse
            parser = self.main_module.build_parser()
            parsed_args = parser.parse_args(args_list)

            if parsed_args.command == "scan":
                self.main_module.handle_scan(parsed_args)
            elif parsed_args.command == "vault":
                self.main_module.handle_vault(parsed_args)
            elif parsed_args.command == "cron":
                self.main_module.handle_cron(parsed_args)
            elif parsed_args.command == "doctor":
                self.main_module.handle_doctor(parsed_args)
            else:
                parser.print_help()
        except SystemExit:
            pass
        except Exception as e:
            console.print(f"[bold red]✘ خطأ في تنفيذ الأمر:[/bold red] {e}")

    def do_clear(self, arg):
        """تنظيف شاشة الطرفية"""
        os.system("clear")

    def do_exit(self, arg):
        """إنهاء الجلسة التفاعلية"""
        console.print("[cyan]تم إغلاق موجه أوامر GhostSync.[/cyan]")
        return True

    def do_quit(self, arg):
        """إنهاء الجلسة التفاعلية"""
        return self.do_exit(arg)

def start_shell(main_module):
    shell = GhostSyncShell(main_module)
    shell.cmdloop()

if __name__ == "__main__":
    import ghostsync
    start_shell(ghostsync)
