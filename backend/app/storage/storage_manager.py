"""Storage manager for persistent data using SQLite."""
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class StorageManager:
    """SQLite-based storage manager for persistent application data."""
    
    def __init__(self, db_path: str = None):
        """Initialize storage manager.
        
        Args:
            db_path: Path to SQLite database file (defaults to env var or ./data/graphprobe.db)
        """
        if db_path is None:
            from app.core.config import settings
            # Try to get from config or use default
            db_path = getattr(settings, 'storage_db_path', './data/graphprobe.db')
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Investigation results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investigations (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    pipeline TEXT NOT NULL,
                    answer TEXT,
                    confidence REAL,
                    evidence TEXT,
                    citations TEXT,
                    metrics TEXT,
                    graph_context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Benchmark runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_runs (
                    run_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    total_questions INTEGER,
                    completed_questions INTEGER,
                    configuration TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Benchmark results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_results (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    question_id TEXT,
                    question TEXT,
                    pipeline TEXT,
                    answer TEXT,
                    confidence REAL,
                    metrics TEXT,
                    evaluation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (run_id) REFERENCES benchmark_runs(run_id)
                )
            """)
            
            # Agent traces table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_traces (
                    trace_id TEXT PRIMARY KEY,
                    run_id TEXT,
                    question TEXT,
                    steps TEXT,
                    tools_used TEXT,
                    evidence_collected TEXT,
                    strategy_changes TEXT,
                    stop_reason TEXT,
                    timing TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # File uploads table (for tracking uploads)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_uploads (
                    upload_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_type TEXT,
                    file_size INTEGER,
                    status TEXT,
                    processing_result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_run_id ON benchmark_results(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_investigations_created ON investigations(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_runs_status ON benchmark_runs(status)")
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
    
    def save_investigation(self, investigation_data: Dict[str, Any]) -> str:
        """Save investigation result to database.
        
        Args:
            investigation_data: Investigation result data
            
        Returns:
            Investigation ID
        """
        investigation_id = investigation_data.get('id') or str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO investigations 
                (id, question, pipeline, answer, confidence, evidence, citations, metrics, graph_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                investigation_id,
                investigation_data.get('question'),
                investigation_data.get('pipeline'),
                investigation_data.get('answer'),
                investigation_data.get('confidence'),
                json.dumps(investigation_data.get('evidence', [])),
                json.dumps(investigation_data.get('citations', [])),
                json.dumps(investigation_data.get('metrics', {})),
                json.dumps(investigation_data.get('graph_context', {}))
            ))
            conn.commit()
            logger.info(f"Saved investigation {investigation_id}")
            return investigation_id
    
    def get_investigation(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve investigation by ID.
        
        Args:
            investigation_id: Investigation ID
            
        Returns:
            Investigation data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM investigations WHERE id = ?", (investigation_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'question': row['question'],
                    'pipeline': row['pipeline'],
                    'answer': row['answer'],
                    'confidence': row['confidence'],
                    'evidence': json.loads(row['evidence']) if row['evidence'] else [],
                    'citations': json.loads(row['citations']) if row['citations'] else [],
                    'metrics': json.loads(row['metrics']) if row['metrics'] else {},
                    'graph_context': json.loads(row['graph_context']) if row['graph_context'] else {},
                    'created_at': row['created_at']
                }
            return None
    
    def save_benchmark_run(self, run_data: Dict[str, Any]) -> str:
        """Save benchmark run metadata.
        
        Args:
            run_data: Benchmark run data
            
        Returns:
            Run ID
        """
        run_id = run_data.get('run_id') or str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO benchmark_runs 
                (run_id, status, total_questions, completed_questions, configuration, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                run_id,
                run_data.get('status', 'in_progress'),
                run_data.get('total_questions', 0),
                run_data.get('completed_questions', 0),
                json.dumps(run_data.get('configuration', {}))
            ))
            conn.commit()
            logger.info(f"Saved benchmark run {run_id}")
            return run_id
    
    def save_benchmark_result(self, result_data: Dict[str, Any]) -> str:
        """Save individual benchmark result.
        
        Args:
            result_data: Benchmark result data
            
        Returns:
            Result ID
        """
        result_id = result_data.get('id') or str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO benchmark_results 
                (id, run_id, question_id, question, pipeline, answer, confidence, metrics, evaluation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result_id,
                result_data.get('run_id'),
                result_data.get('question_id'),
                result_data.get('question'),
                result_data.get('pipeline'),
                result_data.get('answer'),
                result_data.get('confidence'),
                json.dumps(result_data.get('metrics', {})),
                json.dumps(result_data.get('evaluation', {}))
            ))
            conn.commit()
            logger.info(f"Saved benchmark result {result_id}")
            return result_id
    
    def get_benchmark_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve benchmark run by ID.
        
        Args:
            run_id: Benchmark run ID
            
        Returns:
            Benchmark run data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM benchmark_runs WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'run_id': row['run_id'],
                    'status': row['status'],
                    'total_questions': row['total_questions'],
                    'completed_questions': row['completed_questions'],
                    'configuration': json.loads(row['configuration']) if row['configuration'] else {},
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
    
    def get_benchmark_results(self, run_id: str) -> List[Dict[str, Any]]:
        """Retrieve all results for a benchmark run.
        
        Args:
            run_id: Benchmark run ID
            
        Returns:
            List of benchmark results
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM benchmark_results WHERE run_id = ?", (run_id,))
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'run_id': row['run_id'],
                    'question_id': row['question_id'],
                    'question': row['question'],
                    'pipeline': row['pipeline'],
                    'answer': row['answer'],
                    'confidence': row['confidence'],
                    'metrics': json.loads(row['metrics']) if row['metrics'] else {},
                    'evaluation': json.loads(row['evaluation']) if row['evaluation'] else {},
                    'created_at': row['created_at']
                })
            return results
    
    def get_all_benchmark_runs(self) -> List[Dict[str, Any]]:
        """Retrieve all benchmark runs.
        
        Returns:
            List of benchmark run summaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT run_id, status, total_questions, completed_questions, created_at, updated_at
                FROM benchmark_runs 
                ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            
            runs = []
            for row in rows:
                runs.append({
                    'run_id': row['run_id'],
                    'status': row['status'],
                    'total_questions': row['total_questions'],
                    'completed_questions': row['completed_questions'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            return runs
    
    def save_agent_trace(self, trace_data: Dict[str, Any]) -> str:
        """Save agent execution trace.
        
        Args:
            trace_data: Agent trace data
            
        Returns:
            Trace ID
        """
        trace_id = trace_data.get('trace_id') or str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO agent_traces 
                (trace_id, run_id, question, steps, tools_used, evidence_collected, strategy_changes, stop_reason, timing)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trace_id,
                trace_data.get('run_id'),
                trace_data.get('question'),
                json.dumps(trace_data.get('steps', [])),
                json.dumps(trace_data.get('tools_used', [])),
                json.dumps(trace_data.get('evidence_collected', [])),
                json.dumps(trace_data.get('strategy_changes', [])),
                trace_data.get('stop_reason'),
                json.dumps(trace_data.get('timing', {}))
            ))
            conn.commit()
            logger.info(f"Saved agent trace {trace_id}")
            return trace_id
    
    def get_agent_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent trace by ID.
        
        Args:
            trace_id: Agent trace ID
            
        Returns:
            Agent trace data or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM agent_traces WHERE trace_id = ?", (trace_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'trace_id': row['trace_id'],
                    'run_id': row['run_id'],
                    'question': row['question'],
                    'steps': json.loads(row['steps']) if row['steps'] else [],
                    'tools_used': json.loads(row['tools_used']) if row['tools_used'] else [],
                    'evidence_collected': json.loads(row['evidence_collected']) if row['evidence_collected'] else [],
                    'strategy_changes': json.loads(row['strategy_changes']) if row['strategy_changes'] else [],
                    'stop_reason': row['stop_reason'],
                    'timing': json.loads(row['timing']) if row['timing'] else {},
                    'created_at': row['created_at']
                }
            return None
    
    def save_file_upload(self, upload_data: Dict[str, Any]) -> str:
        """Save file upload metadata.
        
        Args:
            upload_data: File upload data
            
        Returns:
            Upload ID
        """
        upload_id = upload_data.get('upload_id') or str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO file_uploads 
                (upload_id, filename, file_type, file_size, status, processing_result)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                upload_id,
                upload_data.get('filename'),
                upload_data.get('file_type'),
                upload_data.get('file_size'),
                upload_data.get('status', 'uploaded'),
                json.dumps(upload_data.get('processing_result', {}))
            ))
            conn.commit()
            logger.info(f"Saved file upload {upload_id}")
            return upload_id
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics.
        
        Returns:
            Storage statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count investigations
            cursor.execute("SELECT COUNT(*) FROM investigations")
            stats['investigations_count'] = cursor.fetchone()[0]
            
            # Count benchmark runs
            cursor.execute("SELECT COUNT(*) FROM benchmark_runs")
            stats['benchmark_runs_count'] = cursor.fetchone()[0]
            
            # Count benchmark results
            cursor.execute("SELECT COUNT(*) FROM benchmark_results")
            stats['benchmark_results_count'] = cursor.fetchone()[0]
            
            # Count agent traces
            cursor.execute("SELECT COUNT(*) FROM agent_traces")
            stats['agent_traces_count'] = cursor.fetchone()[0]
            
            # Count file uploads
            cursor.execute("SELECT COUNT(*) FROM file_uploads")
            stats['file_uploads_count'] = cursor.fetchone()[0]
            
            # Database size
            stats['database_size_bytes'] = self.db_path.stat().st_size
            
            return stats


# Global storage manager instance
storage_manager = StorageManager()
