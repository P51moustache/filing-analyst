import PyPDF2
from pathlib import Path
from typing import Dict, Optional
from bs4 import BeautifulSoup
import re


class DocumentParser:
    """Parse 10-K documents from various formats"""

    def __init__(self):
        self.sections = {}

    def parse(self, file_path: str) -> Dict[str, str]:
        """
        Parse document and extract sections
        Returns dict with section names as keys and content as values
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == '.pdf':
            return self._parse_pdf(file_path)
        elif extension in ['.html', '.htm']:
            return self._parse_html(file_path)
        elif extension == '.txt':
            return self._parse_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    def _parse_pdf(self, file_path: str) -> Dict[str, str]:
        """Parse PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")

        return self._extract_sections(text)

    def _parse_html(self, file_path: str) -> Dict[str, str]:
        """Parse HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                soup = BeautifulSoup(file.read(), 'lxml')

                # Remove script, style elements, and hidden XBRLdivs
                for element in soup(["script", "style", "meta"]):
                    element.decompose()

                # Remove hidden divs (often contain XBRL metadata)
                for div in soup.find_all('div', style=True):
                    if 'display:none' in div.get('style', ''):
                        div.decompose()

                # Get text with better separator handling
                text = soup.get_text(separator='\n', strip=True)

                # Clean up excessive whitespace
                lines = []
                for line in text.splitlines():
                    line = line.strip()
                    if line and len(line) > 1:  # Skip very short lines
                        lines.append(line)
                text = '\n'.join(lines)

        except Exception as e:
            raise ValueError(f"Error parsing HTML: {str(e)}")

        return self._extract_sections(text)

    def _parse_text(self, file_path: str) -> Dict[str, str]:
        """Parse plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
        except Exception as e:
            raise ValueError(f"Error parsing text file: {str(e)}")

        return self._extract_sections(text)

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract major sections from 10-K text
        Returns dict with section names and their content
        """
        sections = {
            "full_text": text,
            "item_1_business": "",
            "item_1a_risk_factors": "",
            "item_7_mda": "",
            "item_7a_market_risk": "",
            "item_8_financials": "",
            "item_9a_controls": ""
        }

        # Clean up text
        text = re.sub(r'\s+', ' ', text)

        # Pattern to find Item sections (various formats)
        patterns = {
            "item_1_business": [
                r'ITEM\s+1[\.\s]+BUSINESS',
                r'ITEM\s+1[\s\-]+BUSINESS',
                r'Item\s+1[\.\s]+Business',
            ],
            "item_1a_risk_factors": [
                r'ITEM\s+1A[\.\s]+RISK\s+FACTORS',
                r'ITEM\s+1A[\s\-]+RISK\s+FACTORS',
                r'Item\s+1A[\.\s]+Risk\s+Factors',
            ],
            "item_7_mda": [
                r'ITEM\s+7[\.\s]+MANAGEMENT[\'\']?S\s+DISCUSSION',
                r'ITEM\s+7[\s\-]+MANAGEMENT[\'\']?S\s+DISCUSSION',
                r'Item\s+7[\.\s]+Management[\'\']?s\s+Discussion',
            ],
            "item_7a_market_risk": [
                r'ITEM\s+7A[\.\s]+QUANTITATIVE\s+AND\s+QUALITATIVE',
                r'Item\s+7A[\.\s]+Quantitative\s+and\s+Qualitative',
            ],
            "item_8_financials": [
                r'ITEM\s+8[\.\s]+FINANCIAL\s+STATEMENTS',
                r'Item\s+8[\.\s]+Financial\s+Statements',
            ],
            "item_9a_controls": [
                r'ITEM\s+9A[\.\s]+CONTROLS\s+AND\s+PROCEDURES',
                r'Item\s+9A[\.\s]+Controls\s+and\s+Procedures',
            ]
        }

        # Extract each section
        for section_key, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    start = matches[0].start()
                    # Find the next item or end of document
                    next_item = re.search(
                        r'ITEM\s+\d+[A-Z]?[\.\s\-]',
                        text[start + 50:],
                        re.IGNORECASE
                    )
                    if next_item:
                        end = start + 50 + next_item.start()
                    else:
                        end = len(text)

                    sections[section_key] = text[start:end]
                    break

        return sections

    def extract_metadata(self, sections: Dict[str, str]) -> Dict[str, Optional[str]]:
        """Extract basic metadata from document"""
        metadata = {
            "ticker": None,
            "company_name": None,
            "fiscal_year": None,
            "filing_date": None
        }

        text = sections.get("full_text", "")[:5000]  # Check first 5000 chars

        # Try to find company name
        company_patterns = [
            r'COMPANY NAME:\s*([^\n]+)',
            r'CONFORMED NAME:\s*([^\n]+)',
            r'(?:company|corporation|incorporated|inc\.|corp\.)\s+([A-Z][A-Za-z\s&,\.]+)',
        ]
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["company_name"] = match.group(1).strip()
                break

        # Try to find ticker
        ticker_patterns = [
            r'TRADING SYMBOL:\s*([A-Z]{1,5})',
            r'TICKER SYMBOL:\s*([A-Z]{1,5})',
            r'NYSE:\s*([A-Z]{1,5})',
            r'NASDAQ:\s*([A-Z]{1,5})',
        ]
        for pattern in ticker_patterns:
            match = re.search(pattern, text)
            if match:
                metadata["ticker"] = match.group(1).strip()
                break

        # Try to find fiscal year
        year_pattern = r'(?:fiscal year|year ended|december 31,|fiscal)\s+(\d{4})'
        match = re.search(year_pattern, text, re.IGNORECASE)
        if match:
            metadata["fiscal_year"] = match.group(1)

        return metadata
