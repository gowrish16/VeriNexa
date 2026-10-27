import os

path = r"C:\Projects\VeriNexa\backend\main.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = """    with open(save_path, "rb") as f_check:
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
        )"""

replacement = """    with open(save_path, "rb") as f_check:
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

    import pymupdf
    try:
        doc = pymupdf.open(save_path)
        if doc.is_encrypted:
            doc.close()
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except Exception:
                    pass
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Upload rejected: Password-protected or encrypted PDFs are not supported."
            )
        if doc.page_count == 0:
            doc.close()
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except Exception:
                    pass
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Upload rejected: The submitted PDF has 0 pages."
            )
        doc.close()
    except HTTPException:
        raise
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

assert norm_target in norm_text, "Target not found in main.py"
new_text = norm_text.replace(norm_target, norm_replacement)

with open(path, "wb") as f:
    f.write(new_text.replace("\n", "\r\n").encode("utf-8"))
print("Patched main.py with pymupdf validation successfully.")
