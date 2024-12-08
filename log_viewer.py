from utils import run_command
from gi.repository import Gtk, GLib


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

    def update_logs(self) -> None:
        """ログを取得して表示"""
        command = ["podman", "compose", "logs", self.service_name]
        logs = run_command(command, cwd=self.compose_dir)

        if logs:
            self.display_logs(logs)
        else:
            self.display_logs("エラー: ログの取得に失敗しました")

    def display_logs(self, logs: str) -> None:
        """ログを表示"""
        self.log_buffer.set_text("")  # バッファをクリア
        self.log_buffer.insert_at_cursor(logs)

        # 自動スクロールを一番下に
        GLib.idle_add(self.scroll_to_bottom)

    def scroll_to_bottom(self) -> None:
        """スクロールを一番下に"""
        end_iter = self.log_buffer.get_end_iter()
        self.log_view.scroll_to_iter(end_iter, 0.0, True, 0.0, 1.0)

    def close_window(self) -> None:
        """ウィンドウを閉じる"""
        self.destroy()
