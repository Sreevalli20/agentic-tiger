"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_base_url: str = "https://api.openai.com/v1"
    
    # TigerGraph Configuration
    tigergraph_host: str = "localhost"
    tigergraph_port: int = 14240
    tigergraph_username: str = "tigergraph"
    tigergraph_password: str = "tigergraph"
    tigergraph_graph: str = "graphrag_hackathon"
    
    # Vector Database Configuration
    vector_db_path: str = "./data/vector_db"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
