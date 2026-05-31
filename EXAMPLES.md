# Usage Examples

This document provides examples of how to use the 10-K Analysis Platform effectively.

## Example 1: Basic Analysis

### Scenario
You want to analyze Apple's latest 10-K filing to assess it as a swing trade opportunity.

### Steps

1. **Obtain 10-K Filing**
   - Visit SEC EDGAR: https://www.sec.gov/edgar/searchedgar/companysearch.html
   - Search for "Apple Inc" (ticker: AAPL)
   - Find the latest 10-K filing
   - Download as PDF or HTML

2. **Upload to Platform**
   - Open http://localhost:3000
   - Drag and drop the 10-K file or click to browse
   - Leave custom prompt empty for standard analysis
   - Click "Analyze 10-K"

3. **Wait for Analysis**
   - The platform will parse the document (~30 seconds)
   - AI analysis typically takes 2-4 minutes
   - Progress bar shows real-time status

4. **Review Results**
   - Trade Score: See overall rating (Strong Buy/Buy/Hold/Avoid)
   - Key Takeaways: Quick bullet points of most important findings
   - Financial Metrics: Revenue, margins, cash flow, working capital
   - Red Flags: Any concerning indicators
   - Catalysts: Near-term positive drivers
   - AI Insights: Comprehensive narrative analysis

5. **Download Report**
   - Click "Download Excel Report"
   - Excel file contains all 50+ metrics in structured format
   - Use for comparison with other companies
   - Track changes over multiple quarters/years

### Expected Output

**Trade Score**: 72/100 (Buy)
- Catalyst & Trend: 28/40 (RPO growth, margin expansion)
- Quality & Cash: 30/35 (Strong FCF conversion, low leverage)
- Risk: 14/25 (Some geographic concentration concerns)

**Key Takeaways**:
- Services revenue growing 15% YoY with 72% margins
- iPhone segment showing 8% growth with new product cycle
- FCF conversion at 95%, significantly above target
- Net cash position of $60B
- Geographic concentration in China represents 18% of revenue
- Strong buyback program with $90B authorization remaining

## Example 2: Sector-Specific Analysis (SaaS Company)

### Scenario
Analyzing a SaaS company (e.g., Salesforce) with focus on RPO and recurring revenue metrics.

### Custom Prompt
```
Focus on SaaS-specific metrics:
- Remaining Performance Obligations (RPO) and current RPO breakdown
- Billings calculation and year-over-year growth
- Rule of 40 calculation (growth rate + FCF margin)
- Subscription revenue vs professional services mix
- Customer retention and net dollar retention rates
- Stock-based compensation as percentage of revenue
- Capitalized commission policies
- Deferred commissions balance and amortization
```

### Expected Insights
The AI will specifically extract:
- Total RPO: $45.0B (up 18% YoY)
- Current RPO: $22.5B (up 20% YoY)
- Current RPO > Total Revenue growth indicates acceleration
- Rule of 40: 42 (15% growth + 27% FCF margin) ✓ Passes
- Subscription revenue: 93% of total (high quality recurring base)
- SBC: 12% of revenue (higher than ideal <8% threshold)
- Deferred commissions: Capitalized and amortized over 4 years

## Example 3: Semiconductor Company Analysis

### Scenario
Deep dive on a semiconductor company (e.g., NVIDIA, AMD, Intel) focusing on capacity, supply chain, and margin drivers.

### Custom Prompt
```
Focus on semiconductor-specific factors:
- Wafer supply agreements and capacity commitments
- Node/process mix (7nm, 5nm, 3nm, etc.) and impact on margins
- Inventory levels and channel inventory health
- Export control language and China exposure
- Prepayments to suppliers for capacity
- Product mix shifts (datacenter vs consumer, etc.)
- Gross margin drivers by segment
- Fab vs fabless model and related commitments
```

### Key Metrics to Watch

**Capacity Indicators**:
- Long-term supply agreements: $5.2B committed over 3 years
- Prepayments to TSMC: $1.1B for 5nm and 3nm capacity
- Lead times: Improved from 52 weeks to 26 weeks

**Margin Drivers**:
- Datacenter segment: 55% GM (up from 48% prior year)
- Gaming segment: 48% GM (down from 51% due to competitive pricing)
- Product mix shift to datacenter driving overall GM expansion

**Red Flags**:
- Inventory up 35% YoY while revenue up only 12%
- Channel inventory noted as "elevated" in MD&A
- New export control restrictions mentioned 17 times (up from 3 mentions)

## Example 4: Retail Company with SSS Focus

### Scenario
Retail company analysis with emphasis on same-store sales and inventory management.

### Custom Prompt
```
Focus on retail-specific metrics:
- Same-store sales (SSS) or comparable store sales trends
- Store count changes and new store productivity
- Inventory turnover and days inventory outstanding
- Shrink rates and inventory reserves
- E-commerce penetration and growth rates
- Operating lease liabilities and upcoming renewals
- Store closure reserves and impairments
- Working capital efficiency
```

### Analysis Focus

**SSS Analysis**:
- Comparable store sales: +3.2% (above industry average of +1.5%)
- Store count: 1,245 stores (-15 closures of underperforming locations)
- New stores (20 opened): 78% of mature store productivity in year 1
- E-commerce: 22% of sales, growing at 28% YoY

**Inventory Health**:
- Inventory turns: 5.2x (up from 4.8x prior year) ✓ Improving
- DIO: 70 days (down from 76 days) ✓ Good trend
- Shrink rate: 1.8% (in line with prior year)
- Markdown reserve: $45M (1.2% of inventory, consistent)

## Example 5: Multi-Company Comparison

### Scenario
Analyze multiple 10-Ks from the same sector to compare and rank investment opportunities.

### Workflow

1. **Analyze Each Company**
   - Upload and analyze Company A's 10-K
   - Download Excel report
   - Repeat for Companies B, C, D

2. **Consolidate Results**
   - Open all Excel reports
   - Copy data rows into single master spreadsheet
   - Sort by total trade score

3. **Compare Key Metrics**
   ```
   Company  Score  Rating      Organic Growth  FCF/NI  Debt/EBITDA  Red Flags
   --------+------+-----------+---------------+-------+------------+-----------
   COMP-A    78   Strong Buy       15%          0.92      1.2x         0
   COMP-B    71   Buy              12%          0.88      1.8x         1
   COMP-C    58   Buy               8%          0.75      2.5x         2
   COMP-D    43   Avoid             3%          0.55      3.8x         4
   ```

4. **Identify Best Opportunities**
   - COMP-A: Highest score, strong catalysts, clean quality metrics
   - COMP-B: Good growth, slight leverage concern but manageable
   - COMP-C: Moderate scores, higher leverage limits upside
   - COMP-D: Multiple red flags, avoid

## Example 6: Red Flag Detection

### Scenario
Use the platform to identify potential problems in a company's 10-K.

### Red Flags the System Detects

1. **Poor Cash Conversion**
   - FCF/NI < 60% for 2+ consecutive years
   - Large divergence between earnings and cash flow
   - Example: NI = $500M but FCF = $200M (40% conversion)

2. **Working Capital Deterioration**
   - DSO rising while revenue flat or declining
   - Example: DSO = 85 days (prior year: 65 days) + Revenue growth: -2%
   - Indicates customers delaying payment or aggressive revenue recognition

3. **Recurring "One-Time" Charges**
   - Restructuring charges in 3+ consecutive years
   - Example: 2022: $50M restructuring, 2023: $45M restructuring, 2024: $60M restructuring
   - Suggests these are actually recurring operational issues

4. **Material Weaknesses**
   - New material weakness disclosed in Item 9A
   - Example: "Material weakness identified in revenue recognition controls"

5. **Customer Concentration**
   - >20% of revenue from single customer
   - Example: "Customer X represented 23% of revenue in 2024"
   - Catalyst: Contract renewal date identified

6. **Debt-Funded Buybacks**
   - Share buybacks while simultaneously increasing short-term debt
   - Example: Buybacks = $500M, ST debt increased by $450M
   - Financial engineering rather than cash generation

## Example 7: Catalyst Identification

### Catalysts the AI Identifies

**Product Catalysts**:
- "New product launch scheduled for Q3 2025"
- "FDA approval expected for Drug X in H2 2024"
- "5nm chip production ramp beginning Q4"

**Financial Catalysts**:
- "Debt refinancing completed, reducing annual interest by $50M"
- "Share buyback authorization increased to $10B (8% of market cap)"
- "Cost reduction initiative targeting $200M annual savings"

**Business Catalysts**:
- "Contract renewal with Customer X (18% of revenue) completed for 3 years"
- "Manufacturing capacity expansion to be operational Q1 2025"
- "Geographic expansion into Europe markets initiated"

**Margin Catalysts**:
- "Product mix shifting to 65% high-margin software (from 55%)"
- "Operating leverage evident: revenue +10%, opex +3%"
- "Gross margin expansion of 300bps expected from new manufacturing process"

## Example 8: Custom Analysis for M&A Activity

### Scenario
Company has done significant M&A, you want to understand organic growth vs acquisition-driven growth.

### Custom Prompt
```
Focus on M&A impact:
- Identify all acquisitions mentioned in the filing
- Calculate organic revenue growth excluding M&A contribution
- Analyze integration costs and charges
- Review goodwill and intangible assets from acquisitions
- Assess purchase price allocation
- Identify any impairment risks
- Compare growth rates before and after acquisitions
- Calculate ROIC on acquisitions if disclosed
```

### Analysis Output

**Acquisitions**:
- Acquired Company X for $2.5B (Jan 2024)
- Acquired Company Y for $800M (Aug 2024)

**Revenue Bridge**:
- Total revenue growth: 18% ($10.0B → $11.8B)
- M&A contribution: 12% ($1.2B)
- FX impact: -2% ($200M headwind)
- **Organic growth: 8%** ($800M)

**Integration Costs**:
- One-time integration charges: $120M
- Expected synergies: $150M annually (starting 2025)
- Cost to achieve synergies: $200M over 18 months

**Balance Sheet Impact**:
- Goodwill increased to $5.2B (from $3.0B)
- Intangible assets: $1.8B (customer lists, technology, trade names)
- Debt/EBITDA increased to 2.8x (from 1.5x) due to acquisition debt

## Tips for Effective Analysis

### 1. Compare Year-Over-Year
- Analyze consecutive years to see trends
- Watch for improving or deteriorating metrics
- Red flags often emerge from trends, not snapshots

### 2. Cross-Reference Sections
- Business description → Risks → Financials
- Look for consistency in narrative
- Discrepancies may indicate issues

### 3. Focus on Cash Flow
- Earnings can be manipulated more easily than cash
- FCF/NI ratio is critical quality metric
- Watch working capital changes carefully

### 4. Understand the Business Model
- High-margin vs low-margin business
- Capital-intensive vs asset-light
- Recurring revenue vs transactional
- Each has different "good" metrics

### 5. Sector Comparisons
- Compare metrics to industry averages
- Sector-specific ratios are most relevant
- Use peer analysis for context

### 6. Read the Risks
- Item 1A is often most valuable section
- New risks or elevated language = important
- Companies must disclose material risks

### 7. Check the Footnotes
- Revenue recognition policies
- Share-based compensation
- Off-balance sheet arrangements
- Related party transactions

### 8. Validate the Score
- Don't rely solely on the score
- Read the AI insights
- Check red flags carefully
- Use score as starting point, not end point

## Common Patterns

### "RPO > Rev" Grind-Up
**Pattern**: Current RPO growing faster than revenue
**What it means**: Backlog building, future revenue acceleration likely
**Action**: Accumulate ahead of acceleration showing in revenue

### "WC Snap-Back" FCF Beat
**Pattern**: Working capital was source of cash (negative), returning to normal
**What it means**: Temporary FCF boost from working capital release
**Action**: Strong quarter likely, but check if sustainable

### "Margin Inflection"
**Pattern**: First sequential GM uptick after several quarters of decline
**What it means**: Potential trend reversal in margins
**Action**: Early signal of improving fundamentals

### "Debt Wall Cleared"
**Pattern**: Major debt refinancing or paydown completed
**What it means**: Removes overhang, frees up cash for growth/returns
**Action**: De-risking event often leads to multiple expansion

### "Recurring Specials Stop"
**Pattern**: Several years of "one-time" charges finally end
**What it means**: GAAP earnings will jump as adjustments stop
**Action**: Valuation may re-rate as earnings quality improves

## Getting Better Results

### Provide Context in Custom Prompts
Good: "Focus on AWS segment margin trends and competitive positioning versus Azure and GCP"
Better than: "Look at AWS"

### Be Specific About Concerns
Good: "Assess cyber risk exposure given recent breaches in industry and disclosure of customer data security"
Better than: "Check risks"

### Request Calculations
Good: "Calculate Rule of 40, EV/Sales, EV/EBITDA, and P/FCF ratios using balance sheet data"
Better than: "Give me valuation metrics"

### Ask for Comparisons
Good: "Compare current quarter metrics to prior year same quarter and to full year guidance"
Better than: "Show me the numbers"

## Advanced Use Cases

### 1. Earnings Preview
- Analyze 10-K before earnings call
- Identify key questions for management
- Understand business model deeply
- Track guidance vs actual results

### 2. Short Thesis Development
- Focus on red flags
- Identify accounting quality issues
- Find competitive vulnerabilities
- Assess debt covenant risks

### 3. Deep Value Screening
- Low valuation metrics
- Strong cash generation
- Low leverage
- Hidden assets or catalysts

### 4. Quality Growth
- High ROIC
- Strong FCF conversion
- Durable competitive advantages
- Margin expansion opportunities

### 5. Event-Driven
- M&A integration analysis
- Spin-off preparation
- Management changes
- Regulatory milestones

## Support

For questions or issues, please refer to:
- README.md: Project overview
- SETUP.md: Installation and configuration
- GitHub Issues: Report bugs or request features
