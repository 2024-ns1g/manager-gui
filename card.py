import webbrowser
from gi.repository import Gtk


class ContainerCard:
    def __init__(self, container: dict, raw_output: str, start_callback: callable, stop_callback: callable) -> None:
        self.service_name = container["service"]
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.container_data = container
        self.raw_output = raw_output

        # メインUI構築
        self.widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # 左側: タイトルと説明
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.title_label = Gtk.Label(label=container["name"])
        self.description_label = Gtk.Label(label=container["description"])
        self.title_label.set_xalign(0)
        self.description_label.set_xalign(0)
        info_box.pack_start(self.title_label, False, False, 0)
        info_box.pack_start(self.description_label, False, False, 0)

        # 中央: スイッチ
        self.switch = Gtk.Switch()
        self.switch.set_active(container.get("state", "stopped") == "running")
        self.switch.connect("state-set", self.on_switch_toggled)
        self.widget.pack_start(info_box, True, True, 0)
        self.widget.pack_start(self.switch, False, False, 0)

        # 右側: メニューボタン
        menu_button = Gtk.MenuButton(label="⋮")
        menu = Gtk.Menu()

        # 詳細情報メニュー
        details_item = Gtk.MenuItem(label="詳細情報")
        details_item.connect("activate", self.show_details)
        menu.append(details_item)

        # ログビューアメニュー
        logs_item = Gtk.MenuItem(label="ログビューア")
        logs_item.connect("activate", self.show_logs)
        menu.append(logs_item)

        # リンクを開くメニュー
        links_submenu = Gtk.Menu()
        for link in container.get("links", []):
            link_item = Gtk.MenuItem(label=link["name"])
            link_item.connect("activate", self.open_link, link["url"])
            links_submenu.append(link_item)
        links_submenu.show_all()

        links_item = Gtk.MenuItem(label="リンクを開く")
        links_item.set_submenu(links_submenu)
        menu.append(links_item)

        menu.show_all()
        menu_button.set_popup(menu)
        self.widget.pack_end(menu_button, False, False, 0)

    def get_widget(self) -> Gtk.Box:
        return self.widget

    def update_container_data(self, container_data: dict) -> None:
        """状態を更新する (RAWデータも更新)"""
        self.container_data = container_data
        self.raw_output = ""  # RAW出力を初期化
        self.switch.set_active(container_data.get("State", "stopped") == "running")

    def on_switch_toggled(self, switch: Gtk.Switch, state: bool) -> None:
        if state:
            self.start_callback(self.service_name)
        else:
            self.stop_callback(self.service_name)

    def show_details(self, menu_item: Gtk.MenuItem) -> None:
        """詳細情報ウィンドウを開く"""
        details_window = Gtk.Window(title=f"詳細情報 - {self.container_data['name']}")
        details_window.set_default_size(600, 400)

        # レイアウト
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        layout.set_margin_top(10)
        layout.set_margin_bottom(10)
        layout.set_margin_start(10)
        layout.set_margin_end(10)

        # 情報表示
        for key, value in self.container_data.items():
            info_label = Gtk.Label(label=f"{key}: {value}")
            info_label.set_xalign(0)
            layout.pack_start(info_label, False, False, 0)

        # RAWデータ表示
        raw_expander = Gtk.Expander(label="RAWデータ")
        raw_text_view = Gtk.TextView()
        raw_text_view.set_editable(False)
        raw_text_view.get_buffer().set_text(self.raw_output)
        raw_expander.add(raw_text_view)
        layout.pack_start(raw_expander, False, False, 0)

        # 閉じるボタン
        close_button = Gtk.Button(label="閉じる")
        close_button.connect("clicked", lambda _: details_window.destroy())
        layout.pack_start(close_button, False, False, 0)

        details_window.add(layout)
        details_window.show_all()

    def show_logs(self, menu_item: Gtk.MenuItem) -> None:
        """ログビューアを開く"""
        logs_window = Gtk.Window(title=f"ログビューア - {self.service_name}")
        logs_window.set_default_size(800, 600)

        # レイアウト
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # ログ表示エリア
        log_text_view = Gtk.TextView()
        log_text_view.set_editable(False)
        log_buffer = log_text_view.get_buffer()

        # ログを取得
        from utils import run_command  # 必要なら utils.py の run_command を使用
        logs = run_command(["podman", "compose", "logs", self.service_name])
        log_buffer.set_text(logs)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(log_text_view)
        layout.pack_start(scroll, True, True, 0)

        # 更新ボタン
        update_button = Gtk.Button(label="更新")
        update_button.connect("clicked", lambda _: log_buffer.set_text(run_command(["podman", "compose", "logs", self.service_name])))
        layout.pack_start(update_button, False, False, 0)

        # 閉じるボタン
        close_button = Gtk.Button(label="閉じる")
        close_button.connect("clicked", lambda _: logs_window.destroy())
        layout.pack_start(close_button, False, False, 0)

        logs_window.add(layout)
        logs_window.show_all()

    def open_link(self, menu_item: Gtk.MenuItem, url: str) -> None:
        """リンクを開く"""
        webbrowser.open(url)

    def is_running(self) -> bool:
        """現在のスイッチの状態が「起動中」かを確認"""
        return self.switch.get_active()
