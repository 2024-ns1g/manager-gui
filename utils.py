import subprocess
import threading
from gi.repository import GLib
from typing import Optional, Callable
from command_log import LogWindow

def run_command(command: list, cwd: str = None) -> str:
    """同期的にコマンドを実行（旧）"""
    try:
        result = subprocess.check_output(command, cwd=cwd, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"エラー: コマンド実行に失敗しました - {e}")
        return ""

def run_command_async(command: list, cwd: str = None, start_msg: str = "", done_msg: str = "", fail_msg: str = "",
                               status_callback: Optional[Callable[[str], None]] = None,
                               done_callback: Optional[Callable[[], None]] = None):
    """コマンドを非同期で実行し、リアルタイムでログを別ウィンドウに表示する"""

    def worker():
        # ログウィンドウの作成
        log_window = LogWindow(title="コマンドログ")
        GLib.idle_add(log_window.show_all)

        if status_callback and start_msg:
            GLib.idle_add(status_callback, start_msg)
            GLib.idle_add(log_window.append_text, f"{start_msg}\n")

        try:
            # サブプロセスをPopenで起動
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # 標準出力を読み取るスレッド
            def read_stdout():
                for line in process.stdout:
                    GLib.idle_add(log_window.append_text, line)
            stdout_thread = threading.Thread(target=read_stdout, daemon=True)
            stdout_thread.start()

            # 標準エラーを読み取るスレッド
            def read_stderr():
                for line in process.stderr:
                    GLib.idle_add(log_window.append_text, f"ERROR: {line}")
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            stderr_thread.start()

            # プロセスの終了を待機
            process.wait()

            # スレッドの終了を待つ
            stdout_thread.join()
            stderr_thread.join()

            if process.returncode == 0:
                if status_callback and done_msg:
                    GLib.idle_add(status_callback, done_msg)
                    GLib.idle_add(log_window.append_text, f"{done_msg}\n")
                if done_callback:
                    GLib.idle_add(done_callback)
            else:
                error_message = f"{fail_msg} - Exit Code: {process.returncode}" if fail_msg else f"コマンドの実行に失敗しました: Exit Code {process.returncode}"
                if status_callback:
                    GLib.idle_add(status_callback, error_message)
                    GLib.idle_add(log_window.append_text, f"{error_message}\n")
        except FileNotFoundError as e:
            error_message = f"{fail_msg} - {e}" if fail_msg else f"コマンドの実行に失敗しました: {e}"
            if status_callback:
                GLib.idle_add(status_callback, error_message)
                GLib.idle_add(log_window.append_text, f"{error_message}\n")
            print(f"エラー: コマンド実行に失敗しました - {e}")
        except Exception as e:
            error_message = f"{fail_msg} - {e}" if fail_msg else f"予期しないエラーが発生しました: {e}"
            if status_callback:
                GLib.idle_add(status_callback, error_message)
                GLib.idle_add(log_window.append_text, f"{error_message}\n")
            print(f"エラー: {error_message}")

    threading.Thread(target=worker, daemon=True).start()
