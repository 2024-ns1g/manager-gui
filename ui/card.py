import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


def create_container_card(self, display_name, container_name):
    """コンテナ情報を表示するカードを作成します。"""
    card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    card.set_border_width(20)  # マージンを大きくする

    # タイトルラベル（絵文字付き）
    title_label = Gtk.Label(label=f"⚙️ {display_name} ({container_name})")
    title_label.set_xalign(0)
    card.pack_start(title_label, False, False, 0)

    # 状態ラベル（デフォルトは未確認）
    status_label = Gtk.Label(label="状態: 未確認")
    status_label.set_xalign(0)
    card.pack_start(status_label, False, False, 0)

    # 起動・停止ボタン（絵文字付き）
    button_layout = Gtk.Box(spacing=10)
    start_button = Gtk.Button(label="▶️ 起動")
    stop_button = Gtk.Button(label="⏹️ 停止")
    start_button.connect("clicked", self.start_container, container_name)
    stop_button.connect("clicked", self.stop_container, container_name)
    button_layout.pack_start(start_button, True, True, 0)
    button_layout.pack_start(stop_button, True, True, 0)
    card.pack_start(button_layout, False, False, 0)

    # 状態ラベルを辞書に登録
    self.container_cards[container_name] = {"status_label": status_label}

    return card
