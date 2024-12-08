import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402


def build_ui(self):
    """ユーザーインターフェースを構築します。"""
    main_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    main_layout.set_margin_start(10)
    main_layout.set_margin_end(10)
    main_layout.set_margin_top(10)
    main_layout.set_margin_bottom(10)
    self.add(main_layout)

    # 全体の稼働状況セクション
    overall_status_frame = self.build_overall_status_section()
    main_layout.pack_start(overall_status_frame, False, False, 10)

    # コンテナ表示セクション
    container_status_frame = self.build_container_status_section()
    main_layout.pack_start(container_status_frame, True, True, 10)
