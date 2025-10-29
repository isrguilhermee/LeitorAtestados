import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = r"C:\Projetos\LeitorAtestados\uploads"  # pasta fora do OneDrive
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    # cria pasta se não existir
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)
        return path
    else:
        raise ValueError("Formato de arquivo não permitido. Use PDF ou imagem.")
