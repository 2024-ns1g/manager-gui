import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


def build_overall_status_section(self):
    """全体の稼働状況セクションを構築します。"""
    frame = Gtk.Frame(label="🖥️ 全体の状態")
    layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    layout.set_border_width(20)  # マージンを大きくする
    frame.add(layout)

    # 全体の状態ラベル
    self.overall_status_label = Gtk.Label(label="全体の状態: 未確認")
    self.overall_status_label.set_xalign(0)
    layout.pack_start(self.overall_status_label, False, False, 0)

    # 一括操作ボタン（絵文字付き）
    button_layout = Gtk.Box(spacing=10)
    start_all_button = Gtk.Button(label="🟢 すべて起動")
    stop_all_button = Gtk.Button(label="🔴 すべて停止")
    start_all_button.connect("clicked", self.start_all_containers)
    stop_all_button.connect("clicked", self.stop_all_containers)
    button_layout.pack_start(start_all_button, True, True, 0)
    button_layout.pack_start(stop_all_button, True, True, 0)
    layout.pack_start(button_layout, False, False, 0)
