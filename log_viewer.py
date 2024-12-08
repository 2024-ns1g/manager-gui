import re
from utils import run_command
from gi.repository import Gtk, Pango


class ContainerLogViewer(Gtk.Window):
    def __init__(self, service_name: str, compose_dir: str) -> None:
        super().__init__(title=f"ログビューアー - {service_name}")
        self.service_name = service_name
        self.compose_dir = compose_dir
        self.set_border_width(10)
        self.set_default_size(800, 600)

        # UI構築
        self.build_ui()

        # 初期ログの取得
        self.update_logs()

    def build_ui(self) -> None:
        """UIを構築"""
        main_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_layout)

        # ログ表示エリア
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.log_buffer = self.log_view.get_buffer()

        # 色付きテキストのためのタグテーブル
        self.tag_table = self.log_buffer.get_tag_table()
        self.create_text_tags()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.log_view)
        main_layout.pack_start(scroll, True, True, 0)

        # ボタンエリア
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_layout.pack_start(button_box, False, False, 0)

        # 更新ボタン
        update_button = Gtk.Button(label="更新")
        update_button.connect("clicked", lambda _: self.update_logs())
        button_box.pack_start(update_button, False, False, 0)

        # 閉じるボタン
        close_button = Gtk.Button(label="閉じる")
        close_button.connect("clicked", lambda _: self.close_window())
        button_box.pack_start(close_button, False, False, 0)

    def create_text_tags(self) -> None:
        """ログの色付け用タグを作成"""
        colors = {
            "red": "#FF0000",
            "green": "#00FF00",
            "yellow": "#FFFF00",
            "blue": "#0000FF",
            "magenta": "#FF00FF",
            "cyan": "#00FFFF",
            "reset": None,
        }
        for name, color in colors.items():
            tag = Gtk.TextTag(name=name)  # 名前を指定してタグを作成
            if color:
                tag.set_property("foreground", color)  # 色を設定
            self.tag_table.add(tag)

    def update_logs(self) -> None:
        """ログを取得して表示"""
        command = ["podman", "compose", "logs", self.service_name]
        logs = run_command(command, cwd=self.compose_dir)

        if logs:
            self.display_logs_with_colors(logs)
        else:
            self.display_logs_with_colors("エラー: ログの取得に失敗しました")

    def display_logs_with_colors(self, logs: str) -> None:
        """ログを色付きで表示"""
        self.log_buffer.set_text("")  # バッファをクリア
        ansi_regex = re.compile(r'\x1b\[([0-9;]*)m')  # ANSIシーケンスの正規表現
        cursor = 0

        while True:
            match = ansi_regex.search(logs, cursor)
            if not match:
                break

            start, end = match.span()
            # ANSIエスケープシーケンス前のテキストを追加
            self.append_colored_text(logs[cursor:start], "reset")

            # 色を取得
            ansi_codes = match.group(1).split(";")
            color_tag = self.ansi_to_tag(ansi_codes)
            cursor = end

            # 次のテキストを探す
            next_match = ansi_regex.search(logs, cursor)
            text_end = next_match.start() if next_match else len(logs)
            self.append_colored_text(logs[cursor:text_end], color_tag)
            cursor = text_end

        # 最後の部分をリセット色で表示
        self.append_colored_text(logs[cursor:], "reset")

        # 自動スクロールを一番下に
        end_iter = self.log_buffer.get_end_iter()
        self.log_view.scroll_to_iter(end_iter, 0.0, True, 0.0, 1.0)

    def append_colored_text(self, text: str, tag_name: str) -> None:
        """指定されたタグでテキストを追加"""
        end_iter = self.log_buffer.get_end_iter()
        self.log_buffer.insert_with_tags_by_name(end_iter, text, tag_name)

    def ansi_to_tag(self, ansi_codes: list[str]) -> str:
        """ANSIコードをタグ名に変換"""
        if "31" in ansi_codes:  # 赤
            return "red"
        elif "32" in ansi_codes:  # 緑
            return "green"
        elif "33" in ansi_codes:  # 黄
            return "yellow"
        elif "34" in ansi_codes:  # 青
            return "blue"
        elif "35" in ansi_codes:  # マゼンタ
            return "magenta"
        elif "36" in ansi_codes:  # シアン
            return "cyan"
        else:
            return "reset"

    def close_window(self) -> None:
        """ウィンドウを閉じる"""
        self.destroy()
