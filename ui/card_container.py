import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


def build_container_status_section(self):
    """コンテナごとの稼働状況セクションを構築します。"""
    frame = Gtk.Frame(label="🛠️ コンテナの稼働状況")
    layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    frame.add(layout)

    # 各コンテナの表示領域を設定
    self.container_cards = {}
    for display_name, container_name in self.target_containers.items():
        card = self.create_container_card(display_name, container_name)
        layout.pack_start(card, False, False, 10)

    return frame
