from typing import Dict, Optional
import uuid
import asyncio
from datetime import datetime

from app.services.document_parser import DocumentParser
from app.services.ai_analyzer import AIAnalyzer
from app.services.report_generator import ReportGenerator
from app.models.schemas import AnalysisStatus, AnalysisResult


class AnalysisOrchestrator:
    """Orchestrates the entire 10-K analysis workflow"""

    def __init__(self, reports_dir: str = "./reports"):
        self.parser = DocumentParser()
        self.analyzer = AIAnalyzer()
        self.report_gen = ReportGenerator(reports_dir)
        self.analyses: Dict[str, Dict] = {}  # In-memory storage (use DB in production)

    def create_analysis(self, file_path: str, filename: str, file_size: int) -> str:
        """
        Create a new analysis job
        Returns analysis_id
        """
        analysis_id = str(uuid.uuid4())

        self.analyses[analysis_id] = {
            "status": AnalysisStatus.PENDING,
            "progress": 0,
            "file_path": file_path,
            "filename": filename,
            "file_size": file_size,
            "created_at": datetime.utcnow(),
            "message": "Analysis queued",
            "result": None,
            "error": None
        }

        return analysis_id

    async def run_analysis(self, analysis_id: str, custom_prompt: Optional[str] = None):
        """
        Run the complete analysis workflow asynchronously
        """
        try:
            # Update status
            self._update_status(analysis_id, AnalysisStatus.PROCESSING, 10, "Parsing document...")

            # Parse document
            file_path = self.analyses[analysis_id]["file_path"]
            sections = await asyncio.to_thread(self.parser.parse, file_path)
            metadata = await asyncio.to_thread(self.parser.extract_metadata, sections)

            self._update_status(analysis_id, AnalysisStatus.PROCESSING, 30, "Running AI analysis...")

            # AI Analysis
            analysis_result = await asyncio.to_thread(
                self.analyzer.analyze_10k,
                sections,
                metadata,
                custom_prompt
            )

            self._update_status(analysis_id, AnalysisStatus.PROCESSING, 70, "Calculating trade score...")

            # Calculate trade score
            trade_score = self.analyzer.calculate_trade_score(analysis_result)
            analysis_result['trade_score'] = trade_score

            self._update_status(analysis_id, AnalysisStatus.PROCESSING, 85, "Generating Excel report...")

            # Generate report
            report_path = await asyncio.to_thread(
                self.report_gen.generate_excel_report,
                analysis_result,
                analysis_id
            )

            # Build final result
            result = AnalysisResult(
                analysis_id=analysis_id,
                ticker=analysis_result.get('ticker') or 'Unknown',
                company_name=analysis_result.get('company_name') or 'Unknown',
                fiscal_year=analysis_result.get('fiscal_year'),
                sector=analysis_result.get('sector') or 'Other',
                financial_metrics=analysis_result.get('financial_metrics', {}),
                sector_metrics=analysis_result.get('sector_metrics', {}),
                risk_indicators=analysis_result.get('risk_indicators', {}),
                catalyst_info={
                    "catalysts": analysis_result.get('catalysts', []),
                    "catalyst_calendar": {}
                },
                trade_score=trade_score,
                segments=analysis_result.get('segments'),
                geographic_concentration=analysis_result.get('geographic_concentration'),
                top_customers=analysis_result.get('top_customers'),
                ai_insights=analysis_result.get('ai_insights', ''),
                key_takeaways=analysis_result.get('key_takeaways', []),
                excel_report_path=report_path
            )

            self._update_status(
                analysis_id,
                AnalysisStatus.COMPLETED,
                100,
                "Analysis complete",
                result.dict()
            )

        except Exception as e:
            self._update_status(
                analysis_id,
                AnalysisStatus.FAILED,
                0,
                "Analysis failed",
                error=str(e)
            )
            raise

    def _update_status(
        self,
        analysis_id: str,
        status: AnalysisStatus,
        progress: int,
        message: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """Update analysis status"""
        if analysis_id in self.analyses:
            self.analyses[analysis_id].update({
                "status": status,
                "progress": progress,
                "message": message,
                "result": result,
                "error": error
            })

    def get_status(self, analysis_id: str) -> Optional[Dict]:
        """Get analysis status"""
        return self.analyses.get(analysis_id)

    def get_report_path(self, analysis_id: str) -> Optional[str]:
        """Get report file path"""
        analysis = self.analyses.get(analysis_id)
        if analysis and analysis.get("result"):
            return analysis["result"].get("excel_report_path")
        return None
