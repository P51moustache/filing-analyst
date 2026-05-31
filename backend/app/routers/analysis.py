from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse
from typing import Optional
import os
import uuid
import aiofiles

from app.config import settings
from app.models.schemas import (
    UploadResponse,
    AnalysisStatusResponse,
    AnalysisStatus
)
from app.services.analysis_orchestrator import AnalysisOrchestrator

router = APIRouter(prefix="/api", tags=["analysis"])

# Initialize orchestrator
orchestrator = AnalysisOrchestrator(reports_dir=settings.reports_dir)

# Ensure directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.reports_dir, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_10k(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a 10-K document for analysis
    Accepts PDF, HTML, or TXT files
    """
    # Validate file extension
    allowed_extensions = ['.pdf', '.html', '.htm', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset

    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_file_size / 1024 / 1024}MB"
        )

    # Save under a generated name to avoid path traversal and filename collisions;
    # the original filename is kept only as a display label.
    safe_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(settings.upload_dir, safe_name)

    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    # Create analysis
    analysis_id = orchestrator.create_analysis(file_path, file.filename, file_size)

    return UploadResponse(
        analysis_id=analysis_id,
        filename=file.filename,
        file_size=file_size,
        status=AnalysisStatus.PENDING
    )


@router.post("/analyze")
async def start_analysis(
    background_tasks: BackgroundTasks,
    analysis_id: str = Form(...),
    custom_prompt: Optional[str] = Form(None)
) -> dict:
    """
    Start analysis of uploaded document
    """
    # Check if analysis exists
    status = orchestrator.get_status(analysis_id)
    if not status:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Check if already processing or completed
    if status["status"] in [AnalysisStatus.PROCESSING, AnalysisStatus.COMPLETED]:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis already {status['status']}"
        )

    # Start analysis in background
    background_tasks.add_task(orchestrator.run_analysis, analysis_id, custom_prompt)

    return {
        "analysis_id": analysis_id,
        "message": "Analysis started",
        "status": "processing"
    }


@router.get("/status/{analysis_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(analysis_id: str) -> AnalysisStatusResponse:
    """
    Get status of an analysis
    """
    status = orchestrator.get_status(analysis_id)

    if not status:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return AnalysisStatusResponse(
        analysis_id=analysis_id,
        status=status["status"],
        progress=status["progress"],
        message=status["message"],
        result=status.get("result"),
        error=status.get("error")
    )


@router.get("/report/{analysis_id}")
async def download_report(analysis_id: str):
    """
    Download Excel report for completed analysis
    """
    report_path = orchestrator.get_report_path(analysis_id)

    if not report_path or not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        report_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(report_path)
    )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "10-K Analysis API is running"}
