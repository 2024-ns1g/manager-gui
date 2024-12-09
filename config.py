import os

compose_dir = os.getenv("COMPOSE_DIR", "/home/ns1g/proj/compose-configuration/backend-api")

target_containers = [
    {
        "name": "MinIO",
        "service": "minio",
        "description": "オブジェクトストレージサービス",
        "links": [
            {"name": "WebUI", "url": "http://127.0.0.1:9000"},
        ],
    },
    {
        "name": "PostgreSQL",
        "service": "postgres",
        "description": "リレーショナルデータベース",
        "links": [],
    },
    {
        "name": "BackendAPI",
        "service": "backend-api",
        "description": "アプリケーションバックエンド",
        "links": [
            {"name": "APIドキュメント", "url": "http://localhost:8080/docs"},
        ],
    },
]

enable_log = False
