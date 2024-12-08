import gi
from container import ContainerManager
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import threading
import time


class BackendManager(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(title="Backend コンテナ管理ツール")
        self.set_border_width(10)
        self.container_manager = ContainerManager()

        # ウィンドウサイズ調整
        self.set_resizable(False)

        # UIの構築
        self.build_ui()

        # 初回状態の更新
        self.update_container_status()

        # 状態を定期的に更新
        self.start_periodic_update()

    def build_ui(self) -> None:
        """UI全体を構築"""
        main_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_layout.set_margin_top(15)
        main_layout.set_margin_bottom(15)
        main_layout.set_margin_start(15)
        main_layout.set_margin_end(15)
        self.add(main_layout)

        # 全体の状態セクション
        overall_status_frame = self.build_overall_status_section()
        main_layout.pack_start(overall_status_frame, False, False, 10)

        # コンテナごとの稼働状況セクション
        container_status_frame = self.build_container_status_section()
        main_layout.pack_start(container_status_frame, True, True, 10)

    def build_overall_status_section(self) -> Gtk.Frame:
        """全体の状態セクションを構築"""
        frame = Gtk.Frame(label="🖥️ 全体の状態")
        frame.set_margin_bottom(10)
        layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        frame.add(layout)

        # 全体の状態ラベル
        self.overall_status_label = Gtk.Label(label="全体の状態: 未確認")
        self.overall_status_label.set_xalign(0)
        layout.pack_start(self.overall_status_label, True, True, 0)

        # ボタンセクション
        button_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_layout.set_halign(Gtk.Align.END)
        start_all_button = Gtk.Button(label="🟢 すべて起動")
        stop_all_button = Gtk.Button(label="🔴 すべて停止")
        start_all_button.connect("clicked", lambda _: self.container_manager.start_all_containers())
        stop_all_button.connect("clicked", lambda _: self.container_manager.stop_all_containers())
        button_layout.pack_start(start_all_button, False, False, 0)
        button_layout.pack_start(stop_all_button, False, False, 0)

        layout.pack_end(button_layout, False, False, 0)

        return frame

    def build_container_status_section(self) -> Gtk.Frame:
        """コンテナごとの稼働状況セクションを構築"""
        frame = Gtk.Frame(label="🛠️ コンテナの稼働状況")
        frame.set_margin_bottom(10)
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        layout.set_margin_top(10)
        layout.set_margin_bottom(10)
        layout.set_margin_start(10)
        layout.set_margin_end(10)
        frame.add(layout)

        # ContainerManagerにカードを初期化
        self.container_manager.initialize_cards(layout)

        return frame

    def update_container_status(self) -> None:
        """コンテナの状態を更新"""
        self.container_manager.update_container_status()
        status_text = "すべて起動中" if self.container_manager.check_all_running() else "一部停止中"
        self.overall_status_label.set_text(f"全体の状態: {status_text}")

    def start_periodic_update(self) -> None:
        """状態を定期的に更新するスレッドを開始"""
        def periodic_update():
            while True:
                time.sleep(10)
                GLib.idle_add(self.update_container_status)

        threading.Thread(target=periodic_update, daemon=True).start()
