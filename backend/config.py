from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "gemma3:1b"
    chroma_db_path: str = "./chroma_db"
    
    class Config:
        env_file = ".env"

settings = Settings()