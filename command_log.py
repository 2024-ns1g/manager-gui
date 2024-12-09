import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class LogWindow(Gtk.Window):
    def __init__(self, title="ログ"):
        super().__init__(title=title)
        self.set_default_size(600, 400)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.textview)

        self.add(scrolled_window)

        self.buffer = self.textview.get_buffer()

    def append_text(self, text: str):
        """テキストを追加し、スクロールを下に移動する"""
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert(end_iter, text)
        mark = self.buffer.create_mark(None, self.buffer.get_end_iter(), False)
        self.textview.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

