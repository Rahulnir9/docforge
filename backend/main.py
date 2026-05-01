from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from parser import parse_fastapi_code
from express_parser import parse_express_code
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

def detect_framework(code: str, filename: str) -> str:
    # JS/TS files are always Express
    if filename.endswith(".js") or filename.endswith(".ts"):
        return "express"
    # Python files — check for FastAPI
    if filename.endswith(".py"):
        return "fastapi"
    # Fallback — sniff the content
    if "require('express')" in code or 'require("express")' in code:
        return "express"
    if "from fastapi" in code or "import fastapi" in code.lower():
        return "fastapi"
    return "unknown"

def parse_file(code: str, filename: str) -> list:
    framework = detect_framework(code, filename)
    if framework == "express":
        return parse_express_code(code)
    elif framework == "fastapi":
        return parse_fastapi_code(code)
    return []

@app.post("/generate")
async def generate_docs(file: UploadFile = File(...)):
    content = await file.read()
    all_routes = []

    if file.filename.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            for name in z.namelist():
                if name.endswith((".py", ".js", ".ts")):
                    code = z.read(name).decode("utf-8", errors="ignore")
                    routes = parse_file(code, name)
                    all_routes.extend(routes)
    else:
        code = content.decode("utf-8")
        all_routes = parse_file(code, file.filename)

    return {"routes": all_routes, "total": len(all_routes)}