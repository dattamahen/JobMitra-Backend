"""
PDF generation endpoint.
Uses multiprocessing.Process (spawn) so Playwright runs in a completely
isolated process with its own event loop — no conflict with FastAPI's loop.
"""
import asyncio
import logging
import multiprocessing
import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from auth_endpoints import get_current_user
import pdf_worker
from email_service import email_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/resume", tags=["PDF"])


class PDFRequest(BaseModel):
    html: str
    filename: str = "resume"


def _generate_pdf_sync(html: str) -> bytes:
    """Spawn a fresh process, run Playwright inside it, return PDF bytes."""
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = os.path.join(tmp, "output.pdf")

        ctx = multiprocessing.get_context("spawn")
        error_queue = ctx.Queue()
        proc = ctx.Process(target=pdf_worker.run, args=(html, pdf_path, error_queue))
        proc.start()
        proc.join(timeout=60)

        if proc.exitcode is None:
            proc.kill()
            raise RuntimeError("PDF worker timed out after 60s")

        err = error_queue.get_nowait() if not error_queue.empty() else "worker exited with no result"
        if err is not None:
            raise RuntimeError(f"PDF worker failed:\n{err}")

        with open(pdf_path, "rb") as f:
            return f.read()


@router.post("/generate-pdf-test", include_in_schema=False)
async def generate_pdf_test(request: PDFRequest):
    try:
        pdf_bytes = await asyncio.to_thread(_generate_pdf_sync, request.html)
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
        pdf_bytes = await asyncio.to_thread(_generate_pdf_sync, request.html)

        if not pdf_bytes:
            raise ValueError("Playwright returned empty PDF")

        response = Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{request.filename}.pdf"',
                "Content-Length": str(len(pdf_bytes)),
            },
        )

        # Fire-and-forget: notify admin + nudge user in parallel
        first_name = current_user.get("first_name", "")
        last_name = current_user.get("last_name", "")
        user_email = current_user.get("email", "")
        asyncio.create_task(asyncio.to_thread(
            email_service.send_cv_download_admin_notification, first_name, last_name, user_email
        ))
        asyncio.create_task(asyncio.to_thread(
            email_service.send_cv_download_user_nudge, user_email, first_name
        ))

        return response
    except Exception as e:
        logger.error("PDF generation failed: %s", repr(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {repr(e)}")
