from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from googletrans import Translator

app = FastAPI(
    title="Google Translate API",
    description="Unofficial translation API using googletrans",
    version="1.0.0",
)

# Cho phép gọi API từ trình duyệt hoặc ứng dụng khác
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_translator():
    return Translator(
        service_urls=[
            "translate.googleapis.com",
        ]
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
        description="Ngôn ngữ đích, ví dụ: vi, en, ja",
    ),
    src: str = Query(
        "auto",
        min_length=2,
        max_length=10,
        description="Ngôn ngữ nguồn, dùng auto để tự nhận diện",
    ),
):
    translator = create_translator()

    try:
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

    finally:
        await translator.client.aclose()


@app.get("/detect")
async def detect(
    text: str = Query(
        ...,
        min_length=1,
        max_length=15000,
        description="Text cần nhận diện ngôn ngữ",
    ),
):
    translator = create_translator()

    try:
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

    finally:
        await translator.client.aclose()
