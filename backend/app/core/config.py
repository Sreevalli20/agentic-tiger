"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    llm_provider: str = "google"
    llm_api_key: str = ""
    llm_model: str = "gemini-1.5-flash"
    llm_base_url: str = "https://api.openai.com/v1"
    
    # Alternative Google AI key variable
    google_api_key: str = ""
    
    # TigerGraph Configuration
    tg_host: str = "localhost"
    tg_port: int = 14240
    tg_secret: str = ""
    tg_graphname: str = "Transaction_Fraud"
    
    # Vector Database Configuration
    vector_db_path: str = "./data/vector_db"
    
    # Storage Database Configuration
    storage_db_path: str = "./data/graphprobe.db"
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173", "https://frontend-81rdtgomo-siris-projects-3809a50.vercel.app"]
    
    # Data Configuration
    data_path: str = "./data"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_retrieval: int = 5
    
    # Agent Configuration
    max_agent_iterations: int = 10
    evidence_sufficiency_threshold: float = 0.8
    max_token_budget: int = 10000
    
    # Benchmark Configuration
    benchmark_output_path: str = "./evaluation/results"
    max_concurrent_benchmarks: int = 3
    
    # Production Configuration
    production_mode: bool = True
    production_corpus_path: str = "./corpus_production.jsonl"
    production_max_docs: int = 40
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
