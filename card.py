from gi.repository import Gtk


class ContainerCard:
    def __init__(self, container: dict, start_callback: callable, stop_callback: callable) -> None:
        self.service_name = container["service"]
        self.start_callback = start_callback
        self.stop_callback = stop_callback

        # メインUI構築
        self.widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # 左側: タイトルと説明
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.title_label = Gtk.Label(label=container["name"])
        self.description_label = Gtk.Label(label=container["description"])
        self.title_label.set_xalign(0)  # 左揃え
        self.description_label.set_xalign(0)  # 左揃え
        info_box.pack_start(self.title_label, False, False, 0)
        info_box.pack_start(self.description_label, False, False, 0)

        # 右側: スイッチ
        self.switch = Gtk.Switch()
        self.switch.connect("state-set", self.on_switch_toggled)
        self.widget.pack_start(info_box, True, True, 0)
        self.widget.pack_end(self.switch, False, False, 0)

    def get_widget(self) -> Gtk.Box:
        """ウィジェット全体を返す"""
        return self.widget

    def update_status(self, state: str) -> None:
        """状態を更新する"""
        self.switch.set_active(state == "running")

    def on_switch_toggled(self, switch: Gtk.Switch, state: bool) -> None:
        """スイッチ操作のコールバック"""
        if state:
            self.start_callback(self.service_name)
        else:
            self.stop_callback(self.service_name)

    def is_running(self) -> bool:
        """現在の状態が「起動中」かを確認"""
        return self.switch.get_active()
