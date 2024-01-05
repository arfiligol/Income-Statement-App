import logging
from quart import render_template, request, g, session
# Quart 可能會透過 Cookie 或 Session 來辨別用戶，'g' 變數可以用來儲存「同一位用戶」不同 request 之間需要共用資料的問題
from werkzeug.utils import secure_filename

from . import lawyer_income_detail
from momshelperquart.utils.get_path import get_root_dir_path

@lawyer_income_detail.get("/")
async def index() -> str:
    return await render_template("lawyer_income_detail.html")


@lawyer_income_detail.post("/upload")
async def upload_file():
    files = await request.files
    # 檢查 request 中是否包含上傳的文件
    if 'file' not in files:
        return "No file part", 400
    
    uploaded_file = files.get("file") # 無法使用 await request.files.get() 方法 或 await request.files[]，必須先 await request.files，再針對儲存該值的變數做操作(.get() or [])

    if uploaded_file:
        # 儲存上傳的文件到本地伺服器
        # filename = secure_filename(uploaded_file.filename)
        filename = uploaded_file.filename
        root_dir = get_root_dir_path()
        file_dir = root_dir / "data" / "temp" / "files"
        file_dir.mkdir(parents=True, exist_ok=True)
        file_path = str(file_dir / filename)
        await uploaded_file.save(file_path)

    # # 儲存上傳的文件在當前 request 的上下文中
    # g.uploaded_file = await file.read()

    return "File uploaded successfullly"