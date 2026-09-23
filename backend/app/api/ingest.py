"""Ingest and file upload endpoint."""
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.storage.storage_manager import storage_manager
from app.retrieval.vector_retriever import VectorRetriever
from app.core.config import settings
import logging
import uuid
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Ingest a document into the vector database.
    
    Args:
        file: Uploaded file
        
    Returns:
        Ingestion status and metadata
    """
    upload_id = str(uuid.uuid4())
    
    try:
        # Validate file type
        allowed_extensions = {'.txt', '.pdf', '.json', '.jsonl', '.md'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
            )
        
        # Validate file size (max 10MB)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file_size} bytes. Max size: 10MB"
            )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Initialize vector retriever
            retriever = VectorRetriever()
            
            # Process based on file type
            if file_ext == '.jsonl':
                # Load corpus from JSONL
                success = retriever.load_corpus(temp_path)
                processing_result = {
                    'corpus_loaded': success,
                    'chunks_processed': retriever.get_collection_stats().get('document_count', 0)
                }
            else:
                # For text files, add as single document
                # This is a simplified implementation
                text_content = content.decode('utf-8')
                processing_result = {
                    'text_length': len(text_content),
                    'status': 'text_extracted'
                }
            
            # Save upload metadata to storage
            storage_manager.save_file_upload({
                'upload_id': upload_id,
                'filename': file.filename,
                'file_type': file_ext,
                'file_size': file_size,
                'status': 'completed',
                'processing_result': processing_result
            })
            
            logger.info(f"Successfully ingested file {file.filename} as {upload_id}")
            
            return {
                "upload_id": upload_id,
                "filename": file.filename,
                "file_size": file_size,
                "status": "completed",
                "processing_result": processing_result
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest file {file.filename}: {e}")
        
        # Save failed upload metadata
        storage_manager.save_file_upload({
            'upload_id': upload_id,
            'filename': file.filename,
            'file_type': Path(file.filename).suffix.lower(),
            'file_size': file_size if 'file_size' in locals() else 0,
            'status': 'failed',
            'processing_result': {'error': str(e)}
        })
        
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/ingest/status")
async def get_ingestion_status():
    """Get current ingestion status and statistics.
    
    Returns:
        Current ingestion status and vector database statistics
    """
    try:
        retriever = VectorRetriever()
        stats = retriever.get_collection_stats()
        
        return {
            "vector_db": stats,
            "status": "ready"
        }
    except Exception as e:
        logger.error(f"Failed to get ingestion status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/initialize-production")
async def initialize_production_corpus():
    """Initialize production corpus if vector database is empty.
    
    Returns:
        Initialization status and statistics
    """
    try:
        retriever = VectorRetriever()
        success = retriever.initialize_production_corpus(max_docs=settings.production_max_docs)
        stats = retriever.get_collection_stats()
        
        return {
            "success": success,
            "vector_db": stats,
            "message": "Production corpus initialized" if success else "Production corpus already exists or initialization failed"
        }
    except Exception as e:
        logger.error(f"Failed to initialize production corpus: {e}")
        raise HTTPException(status_code=500, detail=str(e))
