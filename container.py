import json
from typing import Dict, Callable, Optional
from utils import run_command_async, run_command
from card import ContainerCard
from config import compose_dir, target_containers


class ContainerManager:
    def __init__(self, compose_dir: str, status_callback: Optional[Callable[[str], None]] = None) -> None:
        self.compose_dir = compose_dir
        self.container_cards: Dict[str, ContainerCard] = {}
        self.status_callback = status_callback

    def set_status_callback(self, callback: Callable[[str], None]):
        self.status_callback = callback

    def initialize_cards(self, layout) -> None:
        for container in target_containers:
            card = ContainerCard(
                container,
                self.compose_dir,
                self.start_container,
                self.stop_container,
            )
            layout.pack_start(card.get_widget(), False, False, 5)
            self.container_cards[container["service"]] = card

    def update_container_status(self) -> None:
        """Podmanの状態を取得してUIに反映する。
           状態取得は同期でも問題ないが、もし重い場合は非同期化可能。
        """
        try:
            result = run_command(["podman", "compose", "ps", "--format=json"], cwd=compose_dir)
            print(f"Podman出力:\n{result}")
            containers = {}
            for line in result.strip().splitlines():
                try:
                    container_data = json.loads(line)
                    service_name = container_data.get("Service")
                    if service_name:
                        containers[service_name] = container_data
                except json.JSONDecodeError as e:
                    print(f"エラー: JSONデコードに失敗しました (行: {line}) - {e}")

            for service_name, card in self.container_cards.items():
                container_data = containers.get(service_name, {"State": "stopped", "Service": service_name})
                card.update_container_data(container_data)

        except Exception as e:
            print(f"エラー: 状況の更新に失敗しました - {e}")

    def start_container(self, service_name: str) -> None:
        run_command_async(
            ["podman", "compose", "up", "-d", service_name],
            cwd=self.compose_dir,
            start_msg=f"{service_name} 起動中...",
            done_msg=f"{service_name} が起動しました",
            fail_msg=f"{service_name} の起動に失敗しました",
            status_callback=self.status_callback,
            done_callback=self.update_container_status
        )

    def stop_container(self, service_name: str) -> None:
        run_command_async(
            ["podman", "compose", "stop", service_name],
            cwd=self.compose_dir,
            start_msg=f"{service_name} 停止中...",
            done_msg=f"{service_name} が停止しました",
            fail_msg=f"{service_name} の停止に失敗しました",
            status_callback=self.status_callback,
            done_callback=self.update_container_status
        )

    def start_all_containers(self) -> None:
        run_command_async(
            ["podman", "compose", "up", "-d"],
            cwd=self.compose_dir,
            start_msg="すべてのサービスを起動中...",
            done_msg="すべてのサービスが起動しました",
            fail_msg="すべてのコンテナの起動に失敗しました",
            status_callback=self.status_callback,
            done_callback=self.update_container_status
        )

    def stop_all_containers(self) -> None:
        run_command_async(
            ["podman", "compose", "down"],
            cwd=self.compose_dir,
            start_msg="すべてのサービスを停止中...",
            done_msg="すべてのサービスが停止しました",
            fail_msg="すべてのコンテナの停止に失敗しました",
            status_callback=self.status_callback,
            done_callback=self.update_container_status
        )

    def get_started_container_count(self) -> int:
        return sum(card.is_running() for card in self.container_cards.values())

    def check_all_running(self) -> bool:
        return all(card.is_running() for card in self.container_cards.values())
