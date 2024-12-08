import os


compose_dir = os.getenv("COMPOSE_DIR", "/home/ns1g/proj/compose-configuration/backend-api")

target_containers = [
    {"name": "MinIO", "service": "minio", "description": "オブジェクトストレージサービス"},
    {"name": "PostgreSQL", "service": "postgres", "description": "リレーショナルデータベース"},
    {"name": "BackendAPI", "service": "backend-api", "description": "アプリケーションバックエンド"},
]
