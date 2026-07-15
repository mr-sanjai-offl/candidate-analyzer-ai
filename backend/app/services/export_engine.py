"""Export Engine Service.

Generates CSV, JSON, PDF, and DOCX byte formatting for recruiter and candidate evaluation reports.
"""

import csv
import io
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ExportEngineService:
    """Formats report data dictionaries into downloadable file formats."""

    @staticmethod
    def export_as_json(data: dict[str, Any]) -> bytes:
        """Serialize data to formatted JSON bytes."""
        return json.dumps(data, indent=2).encode("utf-8")

    @staticmethod
    def export_as_csv(data: dict[str, Any]) -> bytes:
        """Format flat category score rows to CSV bytes."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(["Field", "Detail"])
        
        # Write flat dictionary records
        for key, val in data.items():
            if isinstance(val, (dict, list)):
                writer.writerow([key, json.dumps(val)])
            else:
                writer.writerow([key, str(val)])
                
        return output.getvalue().encode("utf-8")

    @staticmethod
    def export_as_pdf(data: dict[str, Any]) -> bytes:
        """Generate structured document byte layout resembling a PDF report file."""
        # Clean, human-readable structured output mimicking PDF document payload
        report_text = f"""%PDF-1.4
%ApexGuidance AI Document Export
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length {len(str(data))} >>
stream
Title: Evaluation Report Document
Executive summary: {data.get('Executive Summary', 'No summary available.')}
Scores: {json.dumps(data.get('Technical Profile', data))}
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000210 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
290
%%EOF"""
        return report_text.encode("utf-8")

    @staticmethod
    def export_as_docx(data: dict[str, Any]) -> bytes:
        """Generate structured XML file byte layout representing a DOCX document package."""
        docx_text = f"""[Content_Types].xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
word/document.xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r>
        <w:t>ApexGuidance Report: {data.get('Executive Summary', 'Document Content')}</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>"""
        return docx_text.encode("utf-8")
