from gi.repository import Gtk, Pango
from log_viewer import ContainerLogViewer
import json


class ContainerCard:
    def __init__(self, container: dict, compose_dir: str, start_callback: callable, stop_callback: callable) -> None:
        self.container_name = container["name"]
        self.service_name = container["service"]
        self.compose_dir = compose_dir  # compose_dir を保持
        self.start_callback = start_callback
        self.stop_callback = stop_callback

        # メインUI構築
        self.widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # 左側: 名前と説明
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.name_label = Gtk.Label(label=self.container_name)  # 直接保持している名前を使用
        self.description_label = Gtk.Label(label=container["description"])
        self.name_label.set_xalign(0)  # 左揃え
        self.description_label.set_xalign(0)  # 左揃え
        self.name_label.set_markup(f"<b>{self.container_name}</b>")  # 太字
        info_box.pack_start(self.name_label, False, False, 0)
        info_box.pack_start(self.description_label, False, False, 0)

        # 中央: スイッチ
        self.switch = Gtk.Switch()
        self.switch.set_active(container.get("state", "stopped") == "running")  # 初期状態設定
        self.switch.connect("state-set", self.on_switch_toggled)
        self.widget.pack_start(info_box, True, True, 0)
        self.widget.pack_start(self.switch, False, False, 0)

        # 右側: メニューボタン
        menu_button = Gtk.MenuButton(label="⋮")
        menu = Gtk.Menu()
        details_item = Gtk.MenuItem(label="詳細情報")
        logs_item = Gtk.MenuItem(label="ログの確認")
        details_item.connect("activate", self.show_details)
        logs_item.connect("activate", self.show_logs)
        menu.append(details_item)
        menu.append(logs_item)
        menu.show_all()
        menu_button.set_popup(menu)
        self.widget.pack_end(menu_button, False, False, 0)

    def get_widget(self) -> Gtk.Box:
        return self.widget

    def update_container_data(self, container_data: dict) -> None:
        """状態を更新する (RAWデータも更新)"""
        self.container_data = container_data
        self.raw_output = json.dumps(container_data, ensure_ascii=False, indent=2)  # JSON整形して保持
        self.switch.set_active(container_data.get("State", "stopped") == "running")

    def on_switch_toggled(self, switch: Gtk.Switch, state: bool) -> None:
        if state:
            self.start_callback(self.service_name)
        else:
            self.stop_callback(self.service_name)

    def show_details(self, menu_item: Gtk.MenuItem) -> None:
        """詳細情報ウィンドウを開く"""
        details_window = Gtk.Window(title=f"詳細情報 - {self.container_name}")  # container_name を利用
        details_window.set_default_size(600, 400)

        # スクロール可能なエリア
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_margin_top(5)
        scroll.set_margin_bottom(5)
        scroll.set_margin_start(5)
        scroll.set_margin_end(5)

        # 詳細情報レイアウト
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # 再帰的に階層構造を作る関数
        def create_hierarchical_view(parent_layout, data, indent=0):
            if isinstance(data, dict):
                for key, value in data.items():
                    key_label = Gtk.Label()
                    key_label.set_markup(f'<b>{" " * indent}{key}:</b>')
                    key_label.set_xalign(0)
                    parent_layout.pack_start(key_label, False, False, 0)
                    create_hierarchical_view(parent_layout, value, indent + 4)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    item_label = Gtk.Label()
                    item_label.set_markup(f'<b>{" " * indent}- [{i}]</b>')
                    item_label.set_xalign(0)
                    parent_layout.pack_start(item_label, False, False, 0)
                    create_hierarchical_view(parent_layout, item, indent + 4)
            else:
                value_label = Gtk.Label(label=" " * indent + str(data))
                value_label.set_xalign(0)
                parent_layout.pack_start(value_label, False, False, 0)

        # 階層構造を生成
        create_hierarchical_view(layout, self.container_data)

        # RAWデータセクション (初期状態で非展開)
        raw_expander = Gtk.Expander(label="RAWデータ")
        raw_output_text = Gtk.TextView()
        raw_output_text.set_editable(False)
        raw_output_text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)  # 長すぎる場合に改行
        raw_output_buffer = raw_output_text.get_buffer()
        raw_output_buffer.set_text(self.raw_output)
        raw_expander.add(raw_output_text)
        raw_expander.set_expanded(False)  # 最初は非展開
        layout.pack_start(raw_expander, False, False, 0)

        # スクロールエリアにレイアウトをセット
        scroll.add(layout)

        # 閉じるボタン
        close_button = Gtk.Button(label="閉じる")
        close_button.set_margin_top(10)
        close_button.set_margin_bottom(10)
        close_button.set_margin_start(10)
        close_button.set_margin_end(10)
        close_button.connect("clicked", lambda _: details_window.close())

        # メインボックスに追加
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        main_box.pack_start(scroll, True, True, 0)
        main_box.pack_start(close_button, False, False, 0)

        details_window.add(main_box)
        details_window.show_all()

    def show_logs(self, menu_item: Gtk.MenuItem) -> None:
        """ログビューアを開く"""
        ContainerLogViewer(self.service_name, self.compose_dir).show_all()

    def is_running(self) -> bool:
        return self.switch.get_active()
