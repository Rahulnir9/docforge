from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from parser import parse_fastapi_code
import zipfile, io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "DocForge is running"}

@app.post("/generate")
async def generate_docs(file: UploadFile = File(...)):
    content = await file.read()
    all_routes = []

    if file.filename.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            for name in z.namelist():
                if name.endswith(".py"):
                    code = z.read(name).decode("utf-8", errors="ignore")
                    routes = parse_fastapi_code(code)
                    all_routes.extend(routes)

    elif file.filename.endswith(".py"):
        code = content.decode("utf-8")
        all_routes = parse_fastapi_code(code)

    return {"routes": all_routes, "total": len(all_routes)}