import threading
import sys


def notify_report_ready(on_click=None):
    """Show a Windows toast notification. Falls back silently on non-Windows."""
    if sys.platform != "win32":
        return
    threading.Thread(target=_show_toast, args=(on_click,), daemon=True).start()


def _show_toast(on_click):
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(
            "AIApp",
            "Report Ready for Review!",
            duration=10,
            threaded=False,
            callback_on_click=on_click,
        )
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.MessageBeep(0)
        except Exception:
            pass
