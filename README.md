# GhostSync Suite 🛡️

A modular security auditing, local encryption vault, and cloud synchronization suite built for Android/Termux environments.

## Features
- **Network Audit**: Fast LAN discovery, open port detection (ADB 5555, SSH 8022/22, HTTP/HTTPS).
- **Vault Engine**: Symmetric AES/Fernet encryption for sensitive files (`storage/vault/`).
- **AI Analysis**: Security posture recommendations powered by Gemini API with local fallback heuristics.
- **Cloud Sync**: Zero-knowledge encrypted backup via `rclone` integration.

## Installation & Setup
```bash
git clone git@github.com:attitawfikatti-alt/ghostsync-suite.git ~/ghostsync
cd ~/ghostsync
python3 cli.py
```

## Architecture
- `core/`: Global configurations and structured logging.
- `modules/net_audit.py`: LAN scanner and socket auditing.
- `modules/vault.py`: Cryptographic key management and encryption.
- `modules/ai_engine.py`: Security reporting and risk evaluation.
- `modules/sync_engine.py`: Remote cloud synchronization.
