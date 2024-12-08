import json
from typing import Dict
from utils import run_command
from card import ContainerCard
from config import compose_dir, target_containers


class ContainerManager:
    def __init__(self, compose_dir: str) -> None:
        self.compose_dir = compose_dir  # compose_dir を保持
        self.container_cards: Dict[str, ContainerCard] = {}

    def initialize_cards(self, layout) -> None:
        """UIにカードを追加"""
        for container in target_containers:
            card = ContainerCard(
                container,
                self.compose_dir,  # compose_dir を渡す
                self.start_container,
                self.stop_container,
            )
            layout.pack_start(card.get_widget(), False, False, 5)
            self.container_cards[container["service"]] = card

    def update_container_status(self) -> None:
        """Podmanの状態を取得してUIに反映"""
        try:
            # Podmanの出力を取得
            result = run_command(["podman", "compose", "ps", "--format=json"], cwd=compose_dir)
            print(f"Podman出力:\n{result}")  # デバッグ用出力

            # 各行を個別にパースしてサービス情報を取得
            containers = {}
            for line in result.strip().splitlines():
                try:
                    container_data = json.loads(line)  # 各行をJSONパース
                    service_name = container_data.get("Service")
                    if service_name:  # サービス名が存在する場合のみ保存
                        containers[service_name] = container_data  # すべての情報を保存
                except json.JSONDecodeError as e:
                    print(f"エラー: JSONデコードに失敗しました (行: {line}) - {e}")

            # 各コンテナカードに状態を反映
            for service_name, card in self.container_cards.items():
                container_data = containers.get(service_name, {"State": "stopped", "Service": service_name})  # サービスがない場合はデフォルトデータ
                card.update_container_data(container_data)

        except Exception as e:
            print(f"エラー: 状況の更新に失敗しました - {e}")

    def start_container(self, service_name: str) -> None:
        """指定したサービスを起動"""
        try:
            run_command(["podman", "compose", "up", "-d", service_name], cwd=compose_dir)
        except Exception as e:
            print(f"エラー: コンテナ {service_name} の起動に失敗しました - {e}")

    def stop_container(self, service_name: str) -> None:
        """指定したサービスを停止"""
        try:
            run_command(["podman", "compose", "stop", service_name], cwd=compose_dir)
        except Exception as e:
            print(f"エラー: コンテナ {service_name} の停止に失敗しました - {e}")

    def start_all_containers(self) -> None:
        """すべてのサービスを起動"""
        try:
            run_command(["podman", "compose", "up", "-d"], cwd=compose_dir)
            self.update_container_status()
        except Exception as e:
            print(f"エラー: すべてのコンテナの起動に失敗しました - {e}")

    def stop_all_containers(self) -> None:
        """すべてのサービスを停止"""
        try:
            run_command(["podman", "compose", "down"], cwd=compose_dir)
            self.update_container_status()
        except Exception as e:
            print(f"エラー: すべてのコンテナの停止に失敗しました - {e}")

    def check_all_running(self) -> bool:
        """すべてのコンテナが起動中かを確認"""
        return all(card.is_running() for card in self.container_cards.values())
