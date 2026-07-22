import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

app = FastAPI(title="Photo Gallery API")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
}

photos_db: list[dict] = []


@app.post("/photos/upload", status_code=201)
async def upload_photo(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Дозволені лише файли JPEG та PNG.",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Файл завеликий. Максимальний розмір — {MAX_FILE_SIZE // (1024 * 1024)}MB.",
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Файл порожній.")

    extension = ALLOWED_CONTENT_TYPES[file.content_type]
    unique_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as f:
        f.write(content)

    photo_record = {
        "filename": unique_filename,
        "original_name": file.filename,
        "uploaded_at": datetime.now(),
    }
    photos_db.append(photo_record)

    return {
        "message": "Фото успішно завантажено.",
        "filename": unique_filename,
        "url": f"/photos/{unique_filename}",
    }


@app.get("/photos/list")
def list_photos():
    sorted_photos = sorted(photos_db, key=lambda p: p["uploaded_at"], reverse=True)

    return {
        "count": len(sorted_photos),
        "photos": [
            {
                "filename": p["filename"],
                "url": f"/photos/{p['filename']}",
                "uploaded_at": p["uploaded_at"].isoformat(),
            }
            for p in sorted_photos
        ],
    }


@app.get("/photos/{filename}")
def get_photo(filename: str):
    safe_filename = Path(filename).name
    file_path = UPLOAD_DIR / safe_filename

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Фото не знайдено.")

    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8004)