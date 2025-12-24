from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Placeholder: save file to uploads/ and call pdf_service
    return {"filename": file.filename}
