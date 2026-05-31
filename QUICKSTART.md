# Quick Start Guide

Get the 10-K Analysis Platform running in 5 minutes.

## Prerequisites

- Python 3.11+
- Node.js 16+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Setup (One Time)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
```

## Running the App

### Option A: Using Start Scripts (Recommended)

**Backend** (Terminal 1):
```bash
cd backend
./start.sh              # macOS/Linux
# or
start.bat               # Windows
```

**Frontend** (Terminal 2):
```bash
cd frontend
npm start
```

### Option B: Manual Start

**Backend** (Terminal 1):
```bash
cd backend
source venv/bin/activate    # Windows: venv\Scripts\activate
uvicorn main:app --reload
```

**Frontend** (Terminal 2):
```bash
cd frontend
npm start
```

## Access the App

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## First Analysis

1. Open http://localhost:3000
2. Upload a 10-K filing (PDF, HTML, or TXT)
3. (Optional) Add custom prompt
4. Click "Analyze 10-K"
5. Wait 2-5 minutes
6. View results and download Excel report

## Where to Get 10-K Filings

**SEC EDGAR**: https://www.sec.gov/edgar/searchedgar/companysearch.html
- Search company name or ticker
- Find latest 10-K filing
- Download as PDF or view HTML

**Popular Examples**:
- Apple (AAPL): https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193&type=10-K
- Microsoft (MSFT): https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=10-K
- Tesla (TSLA): https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001318605&type=10-K

## Understanding Results

### Trade Score (0-100)
- **≥75 + Strong Catalyst**: Strong Buy
- **≥60**: Buy
- **≥45**: Hold
- **<45**: Avoid

### Score Breakdown
- **Catalyst & Trend (40 pts)**: Growth, margins, catalysts, buybacks
- **Quality & Cash (35 pts)**: FCF conversion, working capital, leverage
- **Risk (25 pts)**: Red flags, controls, debt, commitments

### Key Sections to Review
1. **Trade Score**: Overall assessment
2. **Key Takeaways**: Quick bullet points
3. **Financial Metrics**: Core numbers (revenue, margins, FCF, etc.)
4. **Red Flags**: Warning signs
5. **Catalysts**: Positive drivers
6. **AI Insights**: Detailed narrative analysis

### Excel Report
- Download for detailed metrics
- 50+ columns of data
- Compare multiple companies
- Track over time

## Common Issues

### "API Key Error"
- Check `backend/.env` file exists
- Verify `ANTHROPIC_API_KEY` is set correctly
- No quotes needed around the key

### "Cannot connect to backend"
- Ensure backend is running (http://localhost:8000)
- Check `frontend/.env` has `REACT_APP_API_URL=http://localhost:8000`
- Try hard refresh (Ctrl+Shift+R)

### "Analysis failed"
- Check file is valid 10-K (not 10-Q or other form)
- Ensure file is under 20MB
- Some encrypted PDFs cannot be parsed
- Check backend logs for errors

### "Analysis takes too long"
- 10-Ks can be 100+ pages
- Expected time: 2-5 minutes
- Very large filings (200+ pages) may take longer
- Do not refresh page during analysis

## Tips for Better Results

### 1. Use Custom Prompts
Focus the AI on specific areas:
```
Focus on:
- Segment margin trends
- Customer concentration risks
- Export control implications
- Working capital efficiency
```

### 2. Sector-Specific Keywords
- **SaaS**: "RPO, billings, Rule of 40, NRR"
- **Semis**: "capacity, node mix, inventory, export controls"
- **Retail**: "same-store sales, inventory turns, e-commerce"
- **Defense**: "backlog, book-to-bill, contract types"

### 3. Look for Red Flags
- FCF < 60% of net income
- Rising DSO with flat revenue
- Recurring "one-time" charges
- Material weaknesses in controls
- Customer concentration >20%

### 4. Compare Companies
- Analyze multiple 10-Ks from same sector
- Consolidate Excel reports
- Sort by trade score
- Compare key metrics side-by-side

### 5. Focus on Trends
- Compare year-over-year filings
- Watch for improving/deteriorating metrics
- Red flags emerge from trends

## Sample Analysis Workflow

### For a SaaS Company:
```
1. Upload 10-K
2. Custom prompt: "Focus on RPO growth, billings, Rule of 40,
   SBC as % revenue, retention rates, and margin expansion"
3. Analyze
4. Review:
   - RPO vs Revenue growth (want RPO > Revenue)
   - Rule of 40 score (want ≥40)
   - FCF margins (want ≥20%)
   - SBC % revenue (want ≤8%)
5. Download Excel for historical comparison
```

### For a Value/Quality Screen:
```
1. Upload 10-K
2. Custom prompt: "Focus on FCF quality, working capital
   efficiency, leverage, and hidden assets or catalysts"
3. Analyze
4. Review:
   - FCF/NI ratio (want ≥90%)
   - Cash Conversion Cycle (want <60 days)
   - Debt/EBITDA (want <2×)
   - Interest coverage (want >6×)
   - Red flags (want = 0)
5. Check trade score Quality & Cash component (want ≥28/35)
```

### For a Red Flag Check:
```
1. Upload 10-K
2. Custom prompt: "Focus on identifying any accounting red flags,
   quality of earnings issues, working capital concerns, or
   governance problems"
3. Analyze
4. Review:
   - Red Flags section (each flag explained)
   - Working capital trends (DSO, DIO, DPO)
   - Accruals ratio (want <0.05)
   - FCF/NI ratio (want ≥0.7)
   - Material weaknesses (want = No)
5. Read AI Insights for detailed explanation
```

## Keyboard Shortcuts

- **Ctrl/Cmd + Click** on metric: Copy value
- **Ctrl/Cmd + S**: Save/download report
- **Ctrl/Cmd + R**: Refresh page (don't use during analysis!)

## File Formats

### Supported
- ✅ PDF (.pdf)
- ✅ HTML (.html, .htm)
- ✅ Plain Text (.txt)

### Not Supported
- ❌ Word documents (.docx)
- ❌ Encrypted PDFs
- ❌ Scanned PDFs (no OCR)
- ❌ Forms 10-Q, 8-K, etc. (designed for 10-K)

## API Usage (Advanced)

### Upload File
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/10k.pdf"
```

### Start Analysis
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "analysis_id=<uuid>" \
  -F "custom_prompt=Focus on margins and FCF"
```

### Check Status
```bash
curl http://localhost:8000/api/status/<analysis_id>
```

### Download Report
```bash
curl http://localhost:8000/api/report/<analysis_id> \
  -o report.xlsx
```

## Next Steps

- **Full Documentation**: See [SETUP.md](SETUP.md)
- **Usage Examples**: See [EXAMPLES.md](EXAMPLES.md)
- **Project Overview**: See [README.md](README.md)

## Need Help?

- Check [SETUP.md](SETUP.md) Troubleshooting section
- Review [EXAMPLES.md](EXAMPLES.md) for use cases
- Open an issue on GitHub

---

**Ready to analyze?**
1. Start backend: `cd backend && ./start.sh`
2. Start frontend: `cd frontend && npm start`
3. Open http://localhost:3000
4. Upload a 10-K and click "Analyze"!
