"""
PDF generation endpoint — uses a child Python process to run Playwright,
completely bypassing Windows ProactorEventLoop / subprocess transport issues.
"""
import logging
import asyncio
import subprocess
import sys
import tempfile
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from auth_endpoints import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/resume", tags=["PDF"])


class PDFRequest(BaseModel):
    html: str
    filename: str = "resume"


# Inline script executed in the child process — no imports from this app needed.
_PLAYWRIGHT_SCRIPT = """
import sys, asyncio

# Must be set before playwright imports on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

html_file  = sys.argv[1]
output_file = sys.argv[2]

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
    )
    page = browser.new_page()
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    page.set_content(html, wait_until="networkidle")
    page.pdf(
        path=output_file,
        format="A4",
        print_background=True,
        margin={"top": "12.7mm", "bottom": "12.7mm", "left": "12.7mm", "right": "12.7mm"},
    )
    browser.close()
"""


def _run_playwright_subprocess(html: str) -> bytes:
    """Write HTML to a temp file, run playwright in a fresh child process,
    read back the PDF bytes. No asyncio involvement at all."""
    with tempfile.TemporaryDirectory() as tmp:
        html_path = os.path.join(tmp, "input.html")
        pdf_path  = os.path.join(tmp, "output.pdf")
        script_path = os.path.join(tmp, "gen.py")

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(_PLAYWRIGHT_SCRIPT)

        result = subprocess.run(
            [sys.executable, script_path, html_path, pdf_path],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr or "Playwright child process failed")

        with open(pdf_path, "rb") as f:
            return f.read()


@router.post("/generate-pdf-test", include_in_schema=False)
async def generate_pdf_test(request: PDFRequest):
    """No-auth test endpoint"""
    try:
        loop = asyncio.get_running_loop()
        pdf_bytes = await loop.run_in_executor(None, _run_playwright_subprocess, request.html)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{request.filename}.pdf"'},
        )
    except Exception as e:
        logger.error("PDF test failed: %s", repr(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {repr(e)}")


@router.post("/generate-pdf")
async def generate_pdf(
    request: PDFRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        loop = asyncio.get_running_loop()
        pdf_bytes = await loop.run_in_executor(None, _run_playwright_subprocess, request.html)

        if not pdf_bytes:
            raise ValueError("Playwright returned empty PDF")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{request.filename}.pdf"',
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except Exception as e:
        logger.error("PDF generation failed: %s", repr(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {repr(e)}")
