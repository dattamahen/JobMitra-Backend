from fastapi import APIRouter
from fastapi.responses import Response
from datetime import date

sitemap_router = APIRouter()

STATIC_URLS = [
    ("https://www.jobmouka.com/", "1.0", "daily"),
    ("https://www.jobmouka.com/login", "0.8", "monthly"),
    ("https://www.jobmouka.com/signup", "0.8", "monthly"),
    ("https://www.jobmouka.com/privacy", "0.3", "yearly"),
    ("https://www.jobmouka.com/android-app", "0.5", "monthly"),
]

def _url_entry(loc: str, priority: str, changefreq: str, lastmod: str = None) -> str:
    lastmod_tag = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
    return (
        f"<url>"
        f"<loc>{loc}</loc>"
        f"{lastmod_tag}"
        f"<changefreq>{changefreq}</changefreq>"
        f"<priority>{priority}</priority>"
        f"</url>"
    )

@sitemap_router.get("/sitemap.xml", include_in_schema=False)
async def sitemap():
    today = str(date.today())
    urls = [_url_entry(loc, priority, freq, today) for loc, priority, freq in STATIC_URLS]

    # Dynamically add job listing URLs from DB
    try:
        from db import db
        jobs = db.database["job_listings"].find(
            {"status": "active"},
            {"job_id": 1, "updated_at": 1}
        ).limit(5000)
        async for job in jobs:
            job_id = job.get("job_id") or str(job["_id"])
            lastmod = str(job.get("updated_at", today))[:10]
            urls.append(_url_entry(
                f"https://www.jobmouka.com/jobs/{job_id}",
                "0.9", "daily", lastmod
            ))
    except Exception:
        pass  # DB unavailable — serve static URLs only

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(urls)
        + "</urlset>"
    )
    return Response(content=xml, media_type="application/xml")


@sitemap_router.get("/robots.txt", include_in_schema=False)
async def robots():
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Disallow: /dashboard\n"
        "Disallow: /profile\n\n"
        "Sitemap: https://www.jobmouka.com/sitemap.xml\n"
    )
    return Response(content=content, media_type="text/plain")
