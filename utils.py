import subprocess


def run_command(command: list, cwd: str = None) -> str:
    """指定されたコマンドを実行し、出力を文字列として返す"""
    try:
        result = subprocess.check_output(command, cwd=cwd, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"エラー: コマンド実行に失敗しました - {e}")
        return ""
