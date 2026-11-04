#!/data/data/com.termux/files/usr/bin/bash
export PATH="/data/data/com.termux/files/usr/bin:$PATH"
cd ~/ghostsync
python3 cli.py audit >> ~/ghostsync/logs/cron_audit.log 2>&1
python3 cli.py sync >> ~/ghostsync/logs/cron_sync.log 2>&1
