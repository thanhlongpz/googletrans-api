from fastapi import FastAPI, Query, HTTPException
from googletrans import Translator

app = FastAPI(
    title="Google Translate API",
    description="Unofficial translation API using googletrans",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "googletrans-api",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }


@app.get("/translate")
async def translate(
    text: str = Query(..., min_length=1, max_length=15000),
    dest: str = Query("vi", min_length=2, max_length=10),
    src: str = Query("auto", min_length=2, max_length=10),
):
    try:
        async with Translator() as translator:
            result = await translator.translate(
                text,
                dest=dest,
                src=src,
            )

        return {
            "original": result.origin,
            "translated": result.text,
            "source": result.src,
            "target": result.dest,
        }

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Translation failed: {str(error)}",
        )


@app.get("/detect")
async def detect(
    text: str = Query(..., min_length=1, max_length=15000),
):
    try:
        async with Translator() as translator:
            result = await translator.detect(text)

        return {
            "text": text,
            "language": result.lang,
            "confidence": result.confidence,
        }

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Language detection failed: {str(error)}",
        )
