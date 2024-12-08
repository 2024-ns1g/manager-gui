import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ui import BackendManager


def main() -> None:
    """アプリケーションのエントリーポイント"""
    app = BackendManager()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
