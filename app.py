from flask import Flask, request, jsonify, render_template_string
from services.upload_service import save_uploaded_file
from services.ocr_service import extract_text
from services.nlp_service import extract_info
from services.excel_service import save_to_excel

app = Flask(__name__)

HTML_PAGE = """
<!doctype html>
<html lang="pt-br">
  <body style="font-family: Arial; padding: 20px;">
    <h2>Upload de Atestado</h2>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file" required>
      <input type="submit" value="Enviar">
    </form>
    {% if result %}
      <h3>Resultado extraído:</h3>
      <pre>{{ result }}</pre>
    {% endif %}
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def upload_file():
    result = None
    if request.method == "POST":
        file = request.files["file"]
        try:
            file_path = save_uploaded_file(file)
            text = extract_text(file_path)
            data = extract_info(text)
            save_to_excel(data)
            result = data
        except Exception as e:
            result = {"erro": str(e)}

    return render_template_string(HTML_PAGE, result=result)

if __name__ == "__main__":
    app.run(debug=True)
