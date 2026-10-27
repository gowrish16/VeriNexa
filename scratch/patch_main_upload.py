import os

path = r"C:\Projects\VeriNexa\backend\main.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = """@app.post("/upload")
def upload_paper(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    save_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingestion_result = ingest_pdf(save_path, title, user_id=current_user["id"])"""

replacement = """@app.post("/upload")
def upload_paper(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    safe_filename = os.path.basename(file.filename or "")
    if not safe_filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format: Only PDF documents (.pdf) are accepted."
        )

    save_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(save_path) if os.path.exists(save_path) else 0
    if file_size == 0:
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload rejected: The submitted file is empty (0 bytes)."
        )

    with open(save_path, "rb") as f_check:
        header = f_check.read(5)
    if not header.startswith(b"%PDF-"):
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Upload rejected: The submitted file does not contain a valid PDF header structure."
        )

    try:
        ingestion_result = ingest_pdf(save_path, title, user_id=current_user["id"])
    except Exception as e:
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Upload rejected: Corrupted or unparseable PDF stream ({str(e)})."
        )"""

norm_text = text.replace("\r\n", "\n")
norm_target = target.replace("\r\n", "\n")
norm_replacement = replacement.replace("\r\n", "\n")

assert norm_target in norm_text, "Upload target not found in main.py"
new_text = norm_text.replace(norm_target, norm_replacement)

with open(path, "wb") as f:
    f.write(new_text.replace("\n", "\r\n").encode("utf-8"))
print("Updated main.py upload endpoint with defensive security validation.")
