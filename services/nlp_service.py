import re
from typing import Optional


class NLPService:
    """Extrai informações estruturadas dos textos de atestados médicos."""

    def __init__(self):
        # Padrão CID que aceita múltiplos formatos:
        # - CID J00, CID-10 A00, CID-10-A00, CID10 A00
        # - C.I.D.: J00, C.I.D: M54.5, C.I.D. 10 B01.1
        # - C. I. D: M54.6 (com espaços entre letras - comum em OCR)
        # - CID: (B349. ou CID: (B34.9) (com parênteses)
        # - CID: B349. (3 dígitos antes do ponto)
        # - CID - 10 (com código em linha próxima)
        # Aceita hífen ou espaço antes/depois do "10", parênteses opcionais
        # Procura código CID próximo a menções de CID (até 3 linhas de distância)
        self.cid_pattern = re.compile(
            r"C\.?\s*I\.?\s*D\.?\s*(?:-?\s*10\s*[-:]?\s*)?[:\-–]?\s*\(?\s*(?P<cid>[A-Z]{1}\d{2,3}(?:\.[0-9A-Z]{1,2})?)\.?\s*\)?",
            re.IGNORECASE,
        )
        
        # Padrão alternativo: procura códigos CID que aparecem próximos a menções de "CID"
        # (útil quando o código está em linha separada devido ao OCR)
        self.cid_context_pattern = re.compile(
            r"(?:CID|C\.?\s*I\.?\s*D\.?)[\s\S]{0,200}(?P<cid>[A-Z]{1}\d{2,3}(?:\.[0-9A-Z]{1,2})?)",
            re.IGNORECASE,
        )

        # Padrão médico que aceita Dr., Dra., DR., DRA. (maiúsculas/minúsculas)
        # Captura o nome completo mas para antes de "CRM" ou outros identificadores
        self.doctor_pattern = re.compile(
            r"\b(?:Dr|Dra|DR|DRA)\.?\s+(?P<doctor>[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ]+){0,4})(?:\s|CRM|$)",
            re.IGNORECASE,
        )

        # Padrão dias que aceita: "5 dias", "01 dias afastado", "10 (DEZ) dias de repouso", etc.
        self.days_pattern = re.compile(
            r"(?P<days>\d{1,2})\s*(?:\([^)]+\)\s*)?(?:dia(?:s)?|dias)\s*(?:afastado|de\s+(?:repouso|afastamento))?",
            re.IGNORECASE,
        )

        # Mapeamento de meses em português
        months_pt = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
            'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
            'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
        }
        months_pattern = '|'.join(months_pt.keys())
        
        # Padrões que priorizam expressões ligadas à data de emissão
        self.emission_patterns = [
            # Data por extenso: "02 de janeiro de 2025"
            re.compile(
                r"(?:(?:data\s*de\s*emiss[aã]o|emiss[aã]o|emitid[oa]\s+em|,)\s*)?(?P<day>\d{1,2})\s+de\s+(?P<month>" + months_pattern + r")\s+de\s+(?P<year>\d{4})",
                re.IGNORECASE,
            ),
            # Data numérica com contexto de emissão
            re.compile(
                r"(?:data\s*de\s*emiss[aã]o|emiss[aã]o|emitid[oa]\s+em|,)\s*(?P<date>\d{2}[/-]\d{2}[/-]\d{4})",
                re.IGNORECASE,
            ),
            re.compile(
                r"(?:data\s*de\s*emiss[aã]o|emiss[aã]o|emitid[oa]\s+em|,)\s*(?P<date>\d{4}-\d{2}-\d{2})",
                re.IGNORECASE,
            ),
        ]

        # Padrões genéricos como fallback caso a data de emissão explícita não seja encontrada
        self.generic_date_patterns = [
            # Data por extenso genérica (sem contexto específico)
            re.compile(
                r"(?P<day>\d{1,2})\s+de\s+(?P<month>" + months_pattern + r")\s+de\s+(?P<year>\d{4})",
                re.IGNORECASE,
            ),
            # Datas numéricas
            re.compile(r"(?P<date>\d{2}/\d{2}/\d{4})"),
            re.compile(r"(?P<date>\d{2}-\d{2}-\d{4})"),
            re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})"),
        ]
        
        self.months_pt = months_pt

        self.not_found_messages = {
            "cid": "CID não foi encontrado. Verifique se o texto está legível ou se segue o padrão CID-10 (ex.: J00, M54.5).",
            "doctor": "Nome do médico não foi encontrado. Certifique-se de que o prefixo 'Dr.' ou 'Dra.' esteja presente e legível.",
            "date": "Data de emissão não foi encontrada. A imagem pode estar ilegível ou sem a expressão 'emitido em'.",
            "days": "Dias de repouso não foram encontrados. Verifique se a quantidade está indicada de forma numérica no atestado.",
        }

    def extract_info(self, text: str) -> dict:
        """Retorna as informações principais do atestado com mensagens amigáveis."""

        safe_text = text or ""
        
        # Normaliza espaços múltiplos e caracteres especiais que podem vir do OCR
        # Substitui múltiplos espaços por um único espaço, preserva quebras de linha
        safe_text = re.sub(r'[ \t]+', ' ', safe_text)
        # Remove caracteres de controle que podem atrapalhar a regex
        safe_text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', safe_text)

        cid = self.extract_cid(safe_text)
        doctor = self.extract_doctor(safe_text)
        emission_date = self.extract_emission_date(safe_text)
        days = self.extract_days(safe_text)

        return {
            "CID": cid if cid else self.not_found_messages["cid"],
            "Médico": doctor if doctor else self.not_found_messages["doctor"],
            "Data de Emissão": emission_date if emission_date else self.not_found_messages["date"],
            "Dias de Repouso": self._format_days(days),
        }

    def extract_cid(self, text: str) -> Optional[str]:
        # Primeiro tenta o padrão com contexto "CID"
        match = self.cid_pattern.search(text)
        if match:
            return match.group("cid").upper()
        
        # Se não encontrou, procura códigos CID em qualquer lugar do texto
        # Padrão para códigos CID: letra maiúscula + 2-3 dígitos + opcional ponto + 1-2 dígitos/letras
        # Mas apenas se não estiver no meio de uma palavra ou número maior
        standalone_cid_pattern = re.compile(
            r'\b([A-Z]\d{2,3}(?:\.[0-9A-Z]{1,2})?)\b',
            re.IGNORECASE
        )
        
        # Procurar códigos que podem ser CID
        # CID geralmente está próximo de palavras como "CID", "diagnóstico", "doença", etc.
        # ou em linhas isoladas
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_upper = line.upper()
            # Se a linha contém "CID" ou está próxima de uma linha com "CID"
            if 'CID' in line_upper or (i > 0 and 'CID' in lines[i-1].upper()) or (i < len(lines)-1 and 'CID' in lines[i+1].upper()):
                matches = standalone_cid_pattern.findall(line)
                if matches:
                    # Retorna o primeiro código encontrado próximo a "CID"
                    return matches[0].upper()
        
        # Como último recurso, procurar códigos CID em todo o texto
        # mas apenas se estiverem em contexto médico (perto de palavras como "doença", "diagnóstico", etc.)
        medical_context = re.compile(
            r'(?:doen[çc]a|diagn[oó]stico|cid|patologia|infec[çc][aã]o|sintoma)',
            re.IGNORECASE
        )
        if medical_context.search(text):
            matches = standalone_cid_pattern.findall(text)
            if matches:
                # Retorna o primeiro código encontrado
                return matches[0].upper()
        
        return None

    def extract_doctor(self, text: str) -> Optional[str]:
        match = self.doctor_pattern.search(text)
        if match:
            # Retorna o prefixo (Dr./Dra.) + nome, mas remove "CRM" se capturado
            full_match = match.group(0).strip()
            # Remove "CRM" e tudo que vem depois se estiver presente
            if "CRM" in full_match.upper():
                full_match = full_match.split("CRM")[0].strip()
            return full_match
        return None

    def extract_emission_date(self, text: str) -> Optional[str]:
        # Tenta primeiro os padrões específicos de emissão
        for pattern in self.emission_patterns:
            match = pattern.search(text)
            if match:
                # Verifica se é data por extenso (tem grupos day, month, year)
                if "day" in match.groupdict():
                    day = match.group("day").zfill(2)
                    month = self.months_pt.get(match.group("month").lower(), "01")
                    year = match.group("year")
                    return f"{day}/{month}/{year}"
                elif "date" in match.groupdict():
                    return self._normalize_date(match.group("date"))

        # Tenta padrões genéricos
        for pattern in self.generic_date_patterns:
            match = pattern.search(text)
            if match:
                # Verifica se é data por extenso
                if "day" in match.groupdict():
                    day = match.group("day").zfill(2)
                    month = self.months_pt.get(match.group("month").lower(), "01")
                    year = match.group("year")
                    return f"{day}/{month}/{year}"
                elif "date" in match.groupdict():
                    return self._normalize_date(match.group("date"))

        return None

    def extract_days(self, text: str) -> Optional[int]:
        match = self.days_pattern.search(text)
        if match:
            return int(match.group("days"))
        return None

    def _format_days(self, days: Optional[int]) -> str:
        if days is None or days <= 0:
            return self.not_found_messages["days"]

        suffix = "dia" if days == 1 else "dias"
        return f"{days} {suffix} de repouso"

    def _normalize_date(self, date_str: str) -> str:
        if "-" in date_str:
            parts = date_str.split("-")
            if len(parts[0]) == 4:
                year, month, day = parts
            else:
                day, month, year = parts
        else:
            day, month, year = date_str.split("/")

        return f"{day.zfill(2)}/{month.zfill(2)}/{year}"


# Legacy function for backward compatibility
def extract_info(text):
    """Legacy function wrapper for backward compatibility."""
    nlp = NLPService()
    return nlp.extract_info(text)
