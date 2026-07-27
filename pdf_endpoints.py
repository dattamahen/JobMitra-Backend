"""
PDF generation endpoint using Playwright for pixel-perfect A4 output.
"""
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from auth_endpoints import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/resume", tags=["PDF"])

_executor = ThreadPoolExecutor(max_workers=2)


class PDFRequest(BaseModel):
    html: str
    filename: str = "resume"


def _generate_pdf_in_thread(html: str) -> bytes:
    """Use sync_playwright in a worker thread.
    async_playwright spawns a subprocess whose transport is not implemented on
    Windows ProactorEventLoop (used by uvicorn). sync_playwright avoids that
    entirely and works correctly inside a ThreadPoolExecutor.
    """
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page()
        page.set_content(html, wait_until='networkidle')
        pdf_bytes = page.pdf(
            format='A4',
            print_background=True,
            margin={'top': '12.7mm', 'bottom': '12.7mm', 'left': '12.7mm', 'right': '12.7mm'},
        )
        browser.close()
        return pdf_bytes


@router.post("/generate-pdf-test", include_in_schema=False)
async def generate_pdf_test(request: PDFRequest):
    """No-auth test endpoint"""
    try:
        loop = asyncio.get_running_loop()
        pdf_bytes = await loop.run_in_executor(_executor, _generate_pdf_in_thread, request.html)
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
        pdf_bytes = await loop.run_in_executor(_executor, _generate_pdf_in_thread, request.html)

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
