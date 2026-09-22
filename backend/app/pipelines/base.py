"""Base pipeline class."""
from abc import ABC, abstractmethod
from app.models.schemas import PipelineResult, PipelineMetrics
import time


class BasePipeline(ABC):
    """Base class for all RAG pipelines."""
    
    @abstractmethod
    async def run(self, question: str) -> PipelineResult:
        """Run the pipeline on a question."""
        pass
    
    def create_metrics(self) -> PipelineMetrics:
        """Create empty metrics object."""
        return PipelineMetrics()
    
    def track_time(self, start_time: float) -> float:
        """Calculate elapsed time in milliseconds."""
        return (time.time() - start_time) * 1000
