import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import parser
import checker

app = FastAPI(title="PDF Normocontrol Checker")

templates = Jinja2Templates(directory="templates")

os.makedirs("temp_uploads", exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Отображает главную страницу"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Принимает файл, сохраняет, проверяет и возвращает результат"""

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join("temp_uploads", unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            data = parser.load(file_path)
            results = checker.run_all(data)

            total_errors = sum(len(errs) for errs in results.values())

            return {
                "status": "success",
                "filename": file.filename,
                "total_errors": total_errors,
                "details": results
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)