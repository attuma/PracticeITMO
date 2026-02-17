import io
import uvicorn
import pdfplumber
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import parser
import checker

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        return {"status": "error", "message": "Invalid file type"}

    try:
        file_bytes = await file.read()

        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            data = parser.extract_data(pdf)
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)