import gi
from container import ContainerManager
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import threading
import time
from config import compose_dir


class BackendManager(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(title="Backend コンテナ管理ツール")
        self.set_border_width(10)

        # ContainerManager の初期化
        self.container_manager = ContainerManager(compose_dir)

        # ウィンドウサイズをコンテンツ量に応じて調整
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
        main_layout.set_margin_top(8)
        main_layout.set_margin_bottom(8)
        main_layout.set_margin_start(8)
        main_layout.set_margin_end(8)
        self.add(main_layout)

        # 最小横幅のみ指定
        main_layout.set_size_request(512, -1)

        # 全体の状態セクション
        overall_status_section = self.build_overall_status_section()
        main_layout.pack_start(overall_status_section, False, False, 10)

        # コンテナごとの稼働状況セクション
        container_status_frame = self.build_container_status_section()
        main_layout.pack_start(container_status_frame, True, True, 10)

    def build_overall_status_section(self) -> Gtk.Box:
        """全体の状態セクションを構築"""
        layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)

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

        return layout

    def build_container_status_section(self) -> Gtk.Frame:
        """コンテナごとの稼働状況セクションを構築"""
        frame = Gtk.Frame(label="🛠️ コンテナの稼働状況")
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
        # container_manager.get_started_container_count()
        started_count = self.container_manager.get_started_container_count()
        total_count = len(self.container_manager.container_cards)
        if (started_count == total_count) and total_count > 0:
            status_text = f"全体の状態: 全サービス起動中"
        elif started_count > 0:
            status_text = f"全体の状態: {started_count}/{total_count} サービス起動中"
        elif total_count > 0:
            status_text = f"全体の状態: 全サービス停止中"

        self.overall_status_label.set_text(f"{status_text}")

    def start_periodic_update(self) -> None:
        """状態を定期的に更新するスレッドを開始"""
        def periodic_update():
            while True:
                time.sleep(10)
                GLib.idle_add(self.update_container_status)

        threading.Thread(target=periodic_update, daemon=True).start()
