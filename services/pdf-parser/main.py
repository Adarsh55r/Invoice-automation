import io
import fitz
import pytesseract
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException

app = FastAPI()
MAX_PAGES = 10


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    data = await file.read()
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception:
        raise HTTPException(status_code=400, detail="Not a valid PDF")

    pages = []
    for i, page in enumerate(doc):
        if i >= MAX_PAGES:
            break
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        pages.append(pytesseract.image_to_string(img, lang="eng"))

    text = "\n".join(pages).strip()
    if len(text) < 20:
        # Fail loudly so the error handler alerts you, instead of sending junk to the LLM
        raise HTTPException(status_code=422, detail="OCR found no readable text")

    return {"text": text, "pages": len(pages), "chars": len(text)}