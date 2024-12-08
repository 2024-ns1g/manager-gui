import gi
gi.require_version("Gtk", "3.0")  # Gtkのバージョンを指定
from gi.repository import Gtk
import subprocess
import json
import threading
import time
from gi.repository import GLib

class BackendManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Backend コンテナ管理ツール")
        self.set_border_width(10)
        self.set_default_size(800, 600)

        # 固定パスと表示対象のコンテナ設定
        self.compose_dir = "/home/ns1g/proj/compose-configuration/backend-api"  # docker-compose.ymlが存在するディレクトリ
        self.target_containers = {
            "MinIO": "minio",  # 表示するコンテナ: 表示名とサービス名のペア
            "PostgreSQL": "postgres",
            "BackendAPI": "backend-api",
        }

        # UIの構築
        self.build_ui()

        # 初回稼働状況の更新
        self.update_container_status()


        # 状態を定期更新
        self.start_periodic_update()

    def start_periodic_update(self):
        """状態を定期的に更新するスレッドを開始します。"""
        def periodic_update():
            while True:
                time.sleep(10)  # 10秒ごとに更新
                GLib.idle_add(self.update_container_status)

        threading.Thread(target=periodic_update, daemon=True).start()


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

        return frame

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

    def update_container_status(self, button=None):
        """Podman Composeを使用してコンテナ状況を更新します。"""
        try:
            # Podman Compose の状態を取得
            result = subprocess.check_output(
                ["podman", "compose", "ps", "--format=json"],
                cwd=self.compose_dir,
                text=True,
            )

            # デバッグ用に出力
            print("コマンド出力（デバッグ用）:")
            print(result)

            # 出力を解析
            containers = {}
            for line in result.strip().splitlines():
                container = json.loads(line)
                service_name = container.get("Service")
                state = container.get("State")
                containers[service_name] = state  # コンテナ名と状態をマッピング

            all_running = True

            # 管理対象コンテナの状態を更新
            for display_name, service_name in self.target_containers.items():
                if service_name in containers:
                    # コンテナが動作中の場合
                    state = containers[service_name]
                    if state == "running":
                        status_text = "起動中"
                    else:
                        status_text = "停止中"
                        all_running = False
                else:
                    # 出力に含まれていない場合は停止中とみなす
                    status_text = "停止中"
                    all_running = False

                # 状態ラベルを更新
                if service := self.container_cards.get(service_name):
                    service["status_label"].set_text(f"状態: {status_text}")

            # 全体の状態を更新
            self.overall_status_label.set_text(
                "全体の状態: すべて起動中" if all_running else "全体の状態: 一部停止中"
            )
        except Exception as e:
            print(f"エラー: 状況の更新に失敗しました: {e}")
            self.overall_status_label.set_text("全体の状態: 更新失敗")



    def start_container(self, button, service_name):
        """指定されたサービスを起動します。"""
        try:
            subprocess.run(
                ["podman", "compose", "up", "-d", service_name],
                cwd=self.compose_dir,
                check=True,
            )
            self.update_container_status()
        except Exception as e:
            print(f"エラー: サービス {service_name} の起動に失敗しました: {e}")

    def stop_container(self, button, service_name):
        """指定されたサービスを停止します。"""
        try:
            subprocess.run(
                ["podman", "compose", "stop", service_name],
                cwd=self.compose_dir,
                check=True,
            )
            self.update_container_status()
        except Exception as e:
            print(f"エラー: サービス {service_name} の停止に失敗しました: {e}")

    def start_all_containers(self, button):
        """すべてのサービスを起動します。"""
        try:
            subprocess.run(
                ["podman", "compose", "up", "-d"],
                cwd=self.compose_dir,
                check=True,
            )
            self.update_container_status()
        except Exception as e:
            print(f"エラー: すべてのサービスの起動に失敗しました: {e}")

    def stop_all_containers(self, button):
        """すべてのサービスを停止します。"""
        try:
            subprocess.run(
                ["podman", "compose", "down"],
                cwd=self.compose_dir,
                check=True,
            )
            self.update_container_status()
        except Exception as e:
            print(f"エラー: すべてのサービスの停止に失敗しました: {e}")


# 実行
if __name__ == "__main__":
    app = BackendManager()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
