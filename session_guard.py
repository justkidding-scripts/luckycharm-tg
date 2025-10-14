#!/usr/bin/env python3
"""
Session Guard: Protects Telegram accounts from accidental logout.
- Monkey-patches Telethon's TelegramClient.log_out to block unintended logouts.
- Periodically backs up all *.session files.
- Provides restore helpers for corrupted/missing sessions.

Usage:
    from session_guard import SessionGuard
    guard = SessionGuard()
    guard.enable_logout_protection()
    guard.start_backup_scheduler(interval_sec=300)

To force a real logout in code (advanced):
    os.environ['ALLOW_TELEGRAM_LOGOUT'] = '1'
    await client._orig_log_out()   # direct original method

Backups are placed in ./session_backups/<session_name>/<timestamp>.session
"""
from __future__ import annotations
import os
import shutil
import threading
import time
from datetime import datetime
from glob import glob
from typing import List, Optional

class SessionGuard:
    def __init__(self, sessions_glob: str = "*.session", backup_root: str = "session_backups"):
        self.sessions_glob = sessions_glob
        self.backup_root = backup_root
        self._backup_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        os.makedirs(self.backup_root, exist_ok=True)

    def list_session_files(self) -> List[str]:
        return sorted(glob(self.sessions_glob))

    def _backup_path(self, session_file: str) -> str:
        base = os.path.basename(session_file)
        name = base.rsplit(".session", 1)[0]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        d = os.path.join(self.backup_root, name)
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, f"{name}.{ts}.session")

    def backup_session(self, session_file: str) -> Optional[str]:
        try:
            if not os.path.exists(session_file):
                return None
            target = self._backup_path(session_file)
            shutil.copy2(session_file, target)
            return target
        except Exception:
            return None

    def backup_all_sessions(self) -> int:
        count = 0
        for f in self.list_session_files():
            if self.backup_session(f):
                count += 1
        return count

    def latest_backup_for(self, session_name: str) -> Optional[str]:
        d = os.path.join(self.backup_root, session_name)
        if not os.path.isdir(d):
            return None
        files = sorted(glob(os.path.join(d, f"{session_name}.*.session")))
        return files[-1] if files else None

    def restore_session(self, session_name: str) -> bool:
        """Restore latest backup into working directory as <session_name>.session"""
        try:
            latest = self.latest_backup_for(session_name)
            if not latest:
                return False
            target = f"{session_name}.session"
            shutil.copy2(latest, target)
            return True
        except Exception:
            return False

    def start_backup_scheduler(self, interval_sec: int = 300):
        if self._backup_thread and self._backup_thread.is_alive():
            return
        self._stop_event.clear()
        self._backup_thread = threading.Thread(target=self._backup_loop, args=(interval_sec,), daemon=True)
        self._backup_thread.start()

    def stop_backup_scheduler(self):
        self._stop_event.set()
        if self._backup_thread and self._backup_thread.is_alive():
            self._backup_thread.join(timeout=2)

    def _backup_loop(self, interval_sec: int):
        while not self._stop_event.is_set():
            try:
                self.backup_all_sessions()
            except Exception:
                pass
            # Sleep in small chunks to be interruptible
            for _ in range(int(interval_sec)):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def enable_logout_protection(self) -> bool:
        """Monkey-patch Telethon's TelegramClient.log_out to block by default.
        Use environment variable ALLOW_TELEGRAM_LOGOUT=1 to bypass deliberately.
        """
        try:
            from telethon import TelegramClient  # type: ignore
        except Exception:
            return False

        if getattr(TelegramClient, "_logout_guard_enabled", False):
            return True

        # Preserve original
        if not hasattr(TelegramClient, "_orig_log_out"):
            TelegramClient._orig_log_out = TelegramClient.log_out  # type: ignore[attr-defined]

        def guarded_log_out(self, *args, **kwargs):  # type: ignore[no-redef]
            allow = os.environ.get("ALLOW_TELEGRAM_LOGOUT") == "1"
            if not allow:
                raise RuntimeError("Logout blocked by SessionGuard. Set ALLOW_TELEGRAM_LOGOUT=1 and call _orig_log_out() to bypass.")
            # If allowed, call original
            return TelegramClient._orig_log_out(self, *args, **kwargs)

        TelegramClient.log_out = guarded_log_out  # type: ignore[assignment]
        TelegramClient._logout_guard_enabled = True  # type: ignore[attr-defined]
        return True

# Convenience singleton
_guard_singleton: Optional[SessionGuard] = None

def get_session_guard() -> SessionGuard:
    global _guard_singleton
    if _guard_singleton is None:
        _guard_singleton = SessionGuard()
    return _guard_singleton
