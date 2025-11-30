from flask import Flask, request, render_template_string
import sys
import os

# Ajusta imports para funcionar tanto como módulo quanto como script
try:
    # Tenta import relativo (quando importado como módulo)
    from .services.upload_service import UploadService
    from .services.ocr_service import OCRService
    from .services.nlp_service import NLPService
    from .services.excel_service import ExcelService
except ImportError:
    # Se falhar, usa imports absolutos (quando executado como script)
    # Adiciona o diretório atual ao path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from services.upload_service import UploadService
    from services.ocr_service import OCRService
    from services.nlp_service import NLPService
    from services.excel_service import ExcelService


HTML_PAGE = """
<!doctype html>
<html lang="pt-br">
  <head>
    <meta charset="utf-8">
    <title>Leitor de Atestados Médicos</title>
    <style>
      :root {
        color-scheme: light;
      }

      body {
        background: #f5f6fa;
        font-family: "Segoe UI", Arial, sans-serif;
        margin: 0;
        padding: 40px 0;
        color: #1f2933;
      }

      .container {
        max-width: 720px;
        margin: 0 auto;
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12);
        padding: 32px 40px 48px;
      }

      h1 {
        margin-top: 0;
        font-size: 1.9rem;
        color: #0f172a;
      }

      p.subtitle {
        margin: 0 0 24px;
        color: #475569;
      }

      form {
        display: flex;
        flex-direction: column;
        gap: 16px;
        margin-bottom: 24px;
      }

      input[type="file"] {
        padding: 14px;
        border: 1px solid #cbd5f5;
        border-radius: 8px;
        background: #f8fafc;
      }

      button {
        align-self: flex-start;
        padding: 12px 24px;
        border-radius: 8px;
        border: none;
        background: #2563eb;
        color: #fff;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s ease, transform 0.2s ease;
      }

      button:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
      }

      .alert {
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 24px;
        font-weight: 500;
      }

      .alert.success {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
      }

      .alert.error {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
      }

      .result {
        margin-top: 32px;
      }

      .result h2 {
        margin-bottom: 16px;
        color: #0f172a;
      }

      table {
        width: 100%;
        border-collapse: collapse;
        background: #f8fafc;
        border-radius: 10px;
        overflow: hidden;
      }

      th, td {
        padding: 14px 18px;
        border-bottom: 1px solid #e2e8f0;
        text-align: left;
      }

      th {
        width: 40%;
        background: #e0e7ff;
        color: #1e293b;
        font-weight: 600;
      }

      tr:last-child td {
        border-bottom: none;
      }

      td.found {
        color: #166534;
        font-weight: 500;
      }

      td.not-found {
        color: #991b1b;
        font-style: italic;
        font-size: 0.9em;
      }

      footer {
        margin-top: 40px;
        font-size: 0.85rem;
        color: #64748b;
        text-align: center;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Leitor de Atestados Médicos</h1>
      <p class="subtitle">Envie um atestado em PDF ou imagem (PNG, JPG, JPEG, WEBP) para extrair CID, médico, data de emissão e dias de repouso.</p>

      {% if error_message %}
        <div class="alert error">{{ error_message }}</div>
      {% elif status_message %}
        <div class="alert success">{{ status_message }}</div>
      {% endif %}

      <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file" accept=".pdf,.png,.jpg,.jpeg,.webp" required>
        <button type="submit">Processar atestado</button>
      </form>

      {% if result %}
        <section class="result">
          <h2>Resultado extraído</h2>
          <table>
            {% for label, value in result.items() %}
              <tr>
                <th>{{ label }}</th>
                <td class="{% if 'não foi encontrado' in value or 'não foram encontrados' in value %}not-found{% else %}found{% endif %}">
                  {{ value }}
                </td>
              </tr>
            {% endfor %}
          </table>
        </section>
      {% endif %}
    </div>
    <footer>
      Em caso de ausência de informações, o texto pode estar ilegível ou em formato diferente do esperado.
    </footer>
  </body>
</html>
"""


def create_app():
    """Aplicação Flask configurada com os serviços necessários."""

    app = Flask(__name__)

    upload_service = UploadService()
    ocr_service = OCRService()
    nlp_service = NLPService()
    excel_service = ExcelService()

    @app.route("/", methods=["GET", "POST"])
    def upload_file():
        """Processa o upload do atestado e retorna as informações extraídas."""

        result = None
        status_message = None
        error_message = None

        if request.method == "POST":
            file = request.files.get("file")

            if not file or not file.filename:
                error_message = (
                    "Nenhum arquivo foi enviado. Escolha um arquivo PNG, JPG, JPEG, WEBP ou PDF."
                )
            else:
                try:
                    file_path = upload_service.save_uploaded_file(file)
                    text = ocr_service.extract_text(file_path)
                    
                    # DEBUG: Imprime o texto extraído pelo OCR
                    print("\n" + "="*80)
                    print("TEXTO EXTRAÍDO PELO OCR:")
                    print("="*80)
                    print(text)
                    print("="*80 + "\n")
                    
                    # Verifica se o OCR retornou texto válido
                    if not text or not text.strip():
                        error_message = (
                            "O OCR não conseguiu extrair texto da imagem. "
                            "Verifique se a imagem está legível e em boa qualidade."
                        )
                    else:
                        data = nlp_service.extract_info(text)
                        
                        # Conta quantos campos foram encontrados (não são mensagens de erro)
                        found_count = sum(1 for value in data.values() 
                                        if not ("não foi encontrado" in value or "não foram encontrados" in value))
                        
                        # Salva no Excel mesmo se alguns campos não foram encontrados
                        excel_service.save_data(data)
                        
                        result = data
                        if found_count > 0:
                            status_message = f"Atestado processado com sucesso! {found_count} campo(s) encontrado(s). Os dados foram salvos na planilha."
                        else:
                            status_message = "Atestado processado, mas nenhum campo foi encontrado. Verifique se a imagem está legível."
                except Exception as exc:
                    error_message = (
                        "Não foi possível processar o atestado. Pode haver falhas de leitura da imagem ou o texto pode estar fora do padrão esperado. "
                        f"Detalhes: {exc}"
                    )

        return render_template_string(
            HTML_PAGE,
            result=result,
            status_message=status_message,
            error_message=error_message,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
