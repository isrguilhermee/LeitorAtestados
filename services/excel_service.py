from openpyxl import Workbook, load_workbook
import os

def save_to_excel(data, filename="atestados.xlsx"):
    if os.path.exists(filename):
        wb = load_workbook(filename)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["CID", "Médico", "Data de Início", "Dias de Afastamento"])

    ws.append([
        data["CID"],
        data["Médico"],
        data["Data de Início"],
        data["Dias de Afastamento"],
    ])

    wb.save(filename)
