# 10-K Analysis Platform - Setup Guide

This guide will help you get the application up and running.

## Prerequisites

- Python 3.11 or higher
- Node.js 16 or higher
- npm or yarn
- Anthropic API key (get one at https://console.anthropic.com/)

## Quick Start

### 1. Clone and Navigate to Project

```bash
cd /path/to/ai-coding
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your Anthropic API key
# ANTHROPIC_API_KEY=your_actual_api_key_here
```

**Important**: Edit `backend/.env` and replace `your_api_key_here` with your actual Anthropic API key.

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Create .env file from example
cp .env.example .env
```

### 4. Run the Application

You'll need two terminal windows/tabs:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload
```

The backend API will be available at http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

The frontend will be available at http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Upload a 10-K filing (PDF, HTML, or TXT format)
3. (Optional) Add a custom analysis prompt to focus on specific areas
4. Click "Analyze 10-K"
5. Wait for the analysis to complete (typically 2-5 minutes)
6. View the comprehensive analysis and download the Excel report

## API Documentation

Once the backend is running, visit:
- API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## Project Structure

```
ai-coding/
├── backend/                  # Python/FastAPI backend
│   ├── app/
│   │   ├── models/          # Pydantic models
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic
│   │   │   ├── document_parser.py      # PDF/HTML parsing
│   │   │   ├── ai_analyzer.py          # Claude AI integration
│   │   │   ├── report_generator.py     # Excel generation
│   │   │   └── analysis_orchestrator.py # Workflow coordination
│   │   └── config.py        # Configuration
│   ├── uploads/             # Uploaded 10-K files
│   ├── reports/             # Generated Excel reports
│   ├── requirements.txt     # Python dependencies
│   └── main.py              # FastAPI application
│
├── frontend/                # React/TypeScript frontend
│   ├── public/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript types
│   │   ├── App.tsx          # Main app component
│   │   └── App.css          # Styles
│   └── package.json
│
└── README.md                # Project documentation
```

## Analysis Framework

The platform performs comprehensive 10-K analysis including:

### Core Analysis Areas

1. **Business (Item 1)**
   - Segment revenue and margins
   - Geographic concentration
   - Customer concentration (>10% flags)
   - Backlog/RPO trends
   - Supply agreements

2. **Risk Factors (Item 1A)**
   - New or elevated risks vs prior year
   - Export controls, cyber risks, key person risks

3. **MD&A (Item 7)**
   - Revenue bridges (organic vs M&A/FX)
   - Margin analysis and drivers
   - Operating leverage
   - FCF quality and conversion
   - Working capital metrics (DSO, DIO, DPO, CCC)
   - Accruals ratio

4. **Market Risk (Item 7A)**
   - Interest rate sensitivity
   - FX exposure and hedges
   - Commodity exposure

5. **Financials (Item 8)**
   - Debt and leverage ratios
   - SBC as % of revenue
   - Deferred revenue trends
   - Off-balance sheet commitments
   - Debt maturity schedule

6. **Controls (Item 9A)**
   - Material weaknesses

### Scoring System (0-100)

**Catalyst & Trend (40 points)**
- RPO/backlog growth > revenue growth
- Margin expansion
- Identified near-term catalysts
- Strong organic growth (>10%)
- Buyback capacity (>3% yield)

**Quality & Cash (35 points)**
- FCF conversion ≥90%
- Efficient working capital (low CCC)
- Low SBC (≤8% revenue, ≤2% dilution)
- Low leverage (Debt/EBITDA ≤2×)
- Strong interest coverage (≥6×)

**Risk (25 points)**
- Deductions for red flags
- Material weaknesses
- Customer concentration
- Near-term debt maturities
- New elevated risks

### Trade Ratings

- **Strong Buy** (≥75 score, ≥24 catalyst score): High conviction
- **Buy** (≥60 score): Positive setup
- **Hold** (≥45 score): Neutral
- **Avoid** (<45 score): Risk concerns

### Red Flags

The system automatically detects:
- FCF conversion <60% for 2+ years
- Rising DSO/DIO with slowing revenue
- Annual "restructuring" charges
- New material weaknesses
- >20% revenue concentration
- Buybacks funded by short-term debt
- Large commitment increases

### Sector-Specific Analysis

**SaaS**: RPO, current RPO, billings, Rule of 40, capitalized commissions

**Semiconductors/Hardware**: Capacity agreements, node/process mix, inventory health, export controls

**Defense/Industrials**: Funded vs unfunded backlog, book-to-bill, FFP vs cost-plus contracts

**Retail/CPG**: Same-store sales, inventory turns, shrink, lease liabilities

**Biotech/MedTech**: Cash runway, milestone calendar, burn rate

**Banks/Fintech**: NIM sensitivity, deposit beta, CECL reserves, AOCI

**Energy**: Hedge book tenor, LOE/BOE, decline rates

**REITs**: Same-store NOI, lease expiries, AFFO payout

## Excel Report Columns

The generated Excel report includes 50+ columns:

- Company identification (ticker, name, year, sector)
- Revenue metrics (total, organic growth, FX/M&A impact)
- Segment and geographic mix
- Backlog/RPO metrics
- Margin metrics (gross, operating)
- Cash flow (FCF, FCF/NI, FCF margin)
- SBC metrics (amount, % revenue, dilution)
- Working capital (DSO, DIO, DPO, CCC)
- Debt and leverage (net debt, debt/EBITDA, coverage)
- Capital allocation (buybacks, dividends, yield)
- Quality metrics (accruals ratio)
- Risk indicators (material weakness, concentration, etc.)
- Sector-specific metrics
- Catalysts
- Trade score breakdown (catalyst/quality/risk)
- Rating
- Red flags

## Troubleshooting

### Backend Issues

**ImportError or Module Not Found**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**API Key Error**
- Check that `.env` file exists in `backend/` directory
- Verify `ANTHROPIC_API_KEY` is set correctly
- No quotes needed around the API key

**Port Already in Use**
```bash
# Run on different port
uvicorn main:app --reload --port 8001
```

### Frontend Issues

**Dependencies Not Installing**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Cannot Connect to Backend**
- Verify backend is running on http://localhost:8000
- Check `frontend/.env` has correct `REACT_APP_API_URL`
- Try hard refresh in browser (Ctrl+Shift+R or Cmd+Shift+R)

**TypeScript Errors**
```bash
# Usually fixed by installing types
npm install --save-dev @types/react @types/react-dom
```

### Analysis Issues

**Document Parsing Fails**
- Ensure file is valid PDF, HTML, or TXT
- Some encrypted PDFs cannot be parsed
- Maximum file size is 20MB

**Analysis Takes Too Long**
- 10-K filings can be lengthy (100+ pages)
- Expected time: 2-5 minutes for comprehensive analysis
- Check backend logs for errors

**Missing Data in Results**
- Not all 10-Ks disclose all metrics
- Fields will show "N/A" when data isn't available
- Custom prompts can help extract specific information

## API Endpoints

### POST /api/upload
Upload a 10-K document

**Request**: multipart/form-data with file
**Response**:
```json
{
  "analysis_id": "uuid",
  "filename": "string",
  "file_size": 12345,
  "status": "pending"
}
```

### POST /api/analyze
Start analysis

**Request**:
```
analysis_id: string
custom_prompt: string (optional)
```

**Response**:
```json
{
  "analysis_id": "uuid",
  "message": "Analysis started",
  "status": "processing"
}
```

### GET /api/status/{analysis_id}
Get analysis status

**Response**:
```json
{
  "analysis_id": "uuid",
  "status": "pending|processing|completed|failed",
  "progress": 0-100,
  "message": "string",
  "result": {...},
  "error": "string"
}
```

### GET /api/report/{analysis_id}
Download Excel report

**Response**: Excel file download

### GET /api/health
Health check

## Development

### Running Tests

```bash
# Backend tests (when added)
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style

**Backend**: Follow PEP 8
```bash
# Install formatters
pip install black flake8

# Format code
black app/
flake8 app/
```

**Frontend**: Prettier and ESLint (configured in package.json)
```bash
npm run lint
```

## Production Deployment

For production deployment, you'll need to:

1. **Backend**:
   - Use a production WSGI server (Gunicorn with Uvicorn workers)
   - Set up proper database (replace in-memory storage)
   - Configure proper CORS origins
   - Use environment variables for all secrets
   - Set up file storage (S3, etc.) for uploads/reports

2. **Frontend**:
   - Build production bundle: `npm run build`
   - Serve static files with nginx or CDN
   - Update API URL to production backend

3. **Infrastructure**:
   - Use Docker containers (add Dockerfiles)
   - Set up CI/CD pipeline
   - Configure monitoring and logging
   - Add rate limiting and authentication

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
