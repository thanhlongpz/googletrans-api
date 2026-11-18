from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Google Translate API",
    description="Unofficial translation API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "googletrans-api",
        "version": "2.0.0",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


async def google_translate(
    text: str,
    source: str = "auto",
    target: str = "vi",
):
    params = {
        "client": "gtx",
        "sl": source,
        "tl": target,
        "dt": "t",
        "q": text,
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120 Safari/537.36"
        ),
        "Accept": "application/json,text/plain,*/*",
    }

    timeout = httpx.Timeout(20.0, connect=10.0)

    async with httpx.AsyncClient(
        timeout=timeout,
        headers=headers,
        follow_redirects=True,
    ) as client:
        response = await client.get(
            GOOGLE_TRANSLATE_URL,
            params=params,
        )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list) or not data:
        raise ValueError("Google returned an unexpected response")

    translated_parts = []

    # data[0] chứa các đoạn dịch
    for item in data[0] or []:
        if isinstance(item, list) and item and item[0]:
            translated_parts.append(str(item[0]))

    translated_text = "".join(translated_parts).strip()

    if not translated_text:
        raise ValueError("Google returned empty translation")

    detected_source: Optional[str] = None

    # Một số response có ngôn ngữ nguồn ở data[2]
    if len(data) > 2 and isinstance(data[2], str):
        detected_source = data[2]

    return {
        "original": text,
        "translated": translated_text,
        "source": detected_source or source,
        "target": target,
    }


@app.get("/translate")
async def translate(
    text: str = Query(
        ...,
        min_length=1,
        max_length=15000,
        description="Text cần dịch",
    ),
    dest: str = Query(
        "vi",
        min_length=2,
        max_length=10,
        description="Ngôn ngữ đích, ví dụ vi, en, ja",
    ),
    src: str = Query(
        "auto",
        min_length=2,
        max_length=10,
        description="Ngôn ngữ nguồn hoặc auto",
    ),
):
    try:
        return await google_translate(
            text=text,
            source=src,
            target=dest,
        )

    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "Google Translate returned HTTP "
                f"{error.response.status_code}"
            ),
        )

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Translation failed: {str(error)}",
        )


@app.get("/detect")
async def detect(
    text: str = Query(
        ...,
        min_length=1,
        max_length=15000,
        description="Text cần nhận diện ngôn ngữ",
    ),
):
    try:
        result = await google_translate(
            text=text,
            source="auto",
            target="en",
        )

        return {
            "text": text,
            "language": result["source"],
        }

    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "Google Translate returned HTTP "
                f"{error.response.status_code}"
            ),
        )

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Detection failed: {str(error)}",
        )
