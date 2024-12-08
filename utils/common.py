import subprocess
from typing import List


def run_command(command: List[str], cwd: str = None) -> str:
    """コマンドを実行して標準出力を返す"""
    result = subprocess.check_output(command, cwd=cwd, text=True)
    return result
