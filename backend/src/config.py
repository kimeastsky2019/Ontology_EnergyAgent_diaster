"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Energy Orchestrator Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/energy_db"
    DATABASE_POOL_SIZE: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://damcp.gngmeta.com",
        "http://damcp.gngmeta.com"
    ]
    
    # MQTT
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_IOT_DATA: str = "iot-data"
    KAFKA_TOPIC_DISASTERS: str = "disasters"
    
    # External APIs
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    WEATHER_API_KEY: str = ""
    NIED_API_URL: str = "https://api.nied.go.jp"
    
    # Ontology
    JENA_FUSEKI_URL: str = "http://localhost:3030"
    RDF_DATABASE: str = "energy_ontology"
    
    # Monitoring
    SENTRY_DSN: str = ""
    GRAFANA_URL: str = "http://localhost:3001"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()




