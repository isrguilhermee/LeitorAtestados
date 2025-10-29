import re

def extract_info(text):
    cid = re.search(r"CID[:\s]*([A-Z]\d{2}\.\d|\d{3})", text)
    medico = re.search(r"(Dr\.?\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ\s]+)", text)
    data = re.search(r"(\d{2}/\d{2}/\d{4})", text)
    dias = re.search(r"(\d+)\s*dias", text)

    return {
        "CID": cid.group(1) if cid else "",
        "Médico": medico.group(1) if medico else "",
        "Data de Início": data.group(1) if data else "",
        "Dias de Afastamento": int(dias.group(1)) if dias else 0,
    }
