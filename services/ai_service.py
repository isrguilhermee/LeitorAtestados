"""
Serviço de IA para extração e validação inteligente de informações de atestados médicos.
Usa modelos de NLP pré-treinados e técnicas de processamento de linguagem natural.
"""

import re
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import json
import os


class AIService:
    """
    Serviço de IA para melhorar a extração e validação de informações de atestados.
    Combina modelos de NLP com regras de validação e correção.
    """
    
    def __init__(self, use_advanced_nlp: bool = True):
        """
        Inicializa o serviço de IA.
        
        Args:
            use_advanced_nlp: Se True, tenta usar modelos avançados (requer transformers)
        """
        self.use_advanced_nlp = use_advanced_nlp
        self.nlp_model = None
        
        # Tenta carregar modelo avançado se disponível
        if use_advanced_nlp:
            try:
                from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
                # Modelo BERT em português para NER (Named Entity Recognition)
                try:
                    self.nlp_model = pipeline(
                        "ner",
                        model="neuralmind/bert-base-portuguese-cased",
                        tokenizer="neuralmind/bert-base-portuguese-cased",
                        aggregation_strategy="simple"
                    )
                    print("✓ Modelo BERT carregado com sucesso")
                except Exception as e:
                    print(f"⚠ Não foi possível carregar modelo BERT: {e}")
                    print("  Usando método híbrido (regex + validação inteligente)")
                    self.use_advanced_nlp = False
            except ImportError:
                print("⚠ Biblioteca 'transformers' não instalada. Use: pip install transformers torch")
                print("  Usando método híbrido (regex + validação inteligente)")
                self.use_advanced_nlp = False
        
        # Base de conhecimento para validação
        self._init_validation_rules()
        
        # Histórico de correções para aprendizado
        self.corrections_history = []
        self.load_corrections_history()
    
    def _init_validation_rules(self):
        """Inicializa regras de validação baseadas em conhecimento médico."""
        
        # Padrões válidos de CID-10
        self.valid_cid_categories = {
            'A': 'Doenças infecciosas e parasitárias',
            'B': 'Doenças infecciosas e parasitárias',
            'C': 'Neoplasias (tumores)',
            'D': 'Doenças do sangue',
            'E': 'Doenças endócrinas',
            'F': 'Transtornos mentais',
            'G': 'Doenças do sistema nervoso',
            'H': 'Doenças dos olhos e ouvidos',
            'I': 'Doenças do aparelho circulatório',
            'J': 'Doenças do aparelho respiratório',
            'K': 'Doenças do aparelho digestivo',
            'L': 'Doenças da pele',
            'M': 'Doenças do sistema osteomuscular',
            'N': 'Doenças do aparelho geniturinário',
            'O': 'Gravidez, parto e puerpério',
            'P': 'Algumas afecções originadas no período perinatal',
            'Q': 'Malformações congênitas',
            'R': 'Sintomas e sinais anormais',
            'S': 'Lesões por causas externas',
            'T': 'Lesões por causas externas',
            'U': 'Códigos para situações especiais',
            'V': 'Causas externas de morbidade',
            'W': 'Causas externas de morbidade',
            'X': 'Causas externas de morbidade',
            'Y': 'Causas externas de morbidade',
            'Z': 'Fatores que influenciam o estado de saúde'
        }
        
        # Prefixos comuns de nomes de médicos
        self.doctor_prefixes = ['dr', 'dra', 'doctor', 'doutor', 'doutora']
        
        # Padrões de datas válidas
        self.date_patterns = [
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{4}-\d{2}-\d{2}',
        ]
    
    def extract_with_ai(self, text: str) -> Dict[str, any]:
        """
        Extrai informações usando IA avançada combinada com validação.
        
        Args:
            text: Texto extraído do OCR
            
        Returns:
            Dicionário com informações extraídas e validadas
        """
        # Normaliza o texto
        normalized_text = self._normalize_text(text)
        
        # PRIMEIRO: Verifica se há correções aprendidas para este texto
        learned_correction = self._find_similar_correction(normalized_text)
        if learned_correction:
            print("✓ Usando correção aprendida do histórico de treinamento")
            return learned_correction
        
        # Extração usando método híbrido
        if self.use_advanced_nlp and self.nlp_model:
            # Usa modelo BERT para identificar entidades
            entities = self._extract_with_bert(normalized_text)
            results = self._merge_extractions(normalized_text, entities)
        else:
            # Usa método baseado em contexto e padrões inteligentes
            results = self._extract_with_smart_patterns(normalized_text)
        
        # Valida e corrige os resultados
        validated_results = self._validate_and_correct(results, normalized_text)
        
        # Aplica padrões aprendidos do histórico
        validated_results = self._apply_learned_patterns(normalized_text, validated_results)
        
        return validated_results
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza o texto para melhor processamento."""
        # Remove caracteres de controle
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        # Normaliza espaços
        text = re.sub(r'[ \t]+', ' ', text)
        # Preserva quebras de linha importantes
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def _extract_with_bert(self, text: str) -> List[Dict]:
        """Extrai entidades usando modelo BERT."""
        try:
            # Limita o tamanho do texto para o modelo
            max_length = 512
            if len(text) > max_length:
                # Processa em chunks
                chunks = [text[i:i+max_length] for i in range(0, len(text), max_length-100)]
                entities = []
                for chunk in chunks:
                    chunk_entities = self.nlp_model(chunk)
                    entities.extend(chunk_entities)
                return entities
            else:
                return self.nlp_model(text)
        except Exception as e:
            print(f"Erro ao usar BERT: {e}")
            return []
    
    def _extract_with_smart_patterns(self, text: str) -> Dict[str, any]:
        """
        Extração inteligente usando padrões contextuais e análise semântica.
        """
        results = {
            'cid': None,
            'doctor': None,
            'date': None,
            'days': None,
            'confidence': {}
        }
        
        # Extração de CID com contexto melhorado
        results['cid'] = self._extract_cid_smart(text)
        
        # Extração de médico com validação
        results['doctor'] = self._extract_doctor_smart(text)
        
        # Extração de data com validação
        results['date'] = self._extract_date_smart(text)
        
        # Extração de dias
        results['days'] = self._extract_days_smart(text)
        
        return results
    
    def _extract_cid_smart(self, text: str) -> Optional[str]:
        """Extrai CID com validação inteligente."""
        # Padrões mais flexíveis para CID
        patterns = [
            r'CID[:\s\-]*(?:10[:\s\-]*)?([A-Z]\d{2,3}(?:\.\d{1,2})?)',
            r'C\.?\s*I\.?\s*D\.?\s*(?:10[:\s\-]*)?[:\s\-]*([A-Z]\d{2,3}(?:\.\d{1,2})?)',
            r'(?:diagn[oó]stico|c[oó]digo)[:\s]*([A-Z]\d{2,3}(?:\.\d{1,2})?)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                cid = match.group(1).upper()
                if self._validate_cid(cid):
                    return cid
        
        # Busca por padrão standalone próximo a palavras-chave
        medical_keywords = ['cid', 'diagnóstico', 'doença', 'código', 'classificação']
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_upper = line.upper()
            # Verifica se há palavras-chave próximas
            context_lines = lines[max(0, i-2):min(len(lines), i+3)]
            context = ' '.join(context_lines).upper()
            
            if any(keyword in context for keyword in medical_keywords):
                # Procura padrão CID na linha
                cid_match = re.search(r'\b([A-Z]\d{2,3}(?:\.\d{1,2})?)\b', line, re.IGNORECASE)
                if cid_match:
                    cid = cid_match.group(1).upper()
                    if self._validate_cid(cid):
                        return cid
        
        return None
    
    def _validate_cid(self, cid: str) -> bool:
        """Valida se um código CID é válido."""
        if not cid or len(cid) < 3:
            return False
        
        # Verifica se começa com letra válida
        first_char = cid[0].upper()
        if first_char not in self.valid_cid_categories:
            return False
        
        # Verifica formato básico
        if not re.match(r'^[A-Z]\d{2,3}(?:\.\d{1,2})?$', cid):
            return False
        
        return True
    
    def _extract_doctor_smart(self, text: str) -> Optional[str]:
        """Extrai nome do médico com validação."""
        # Padrões para médico
        patterns = [
            r'(?:Dr|Dra|DR|DRA|Doutor|Doutora)\.?\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ]+){1,4})',
            r'Assinado\s+por[:\s]+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ]+){1,4})',
            r'M[eé]dico[:\s]+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ]+){1,4})',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                doctor_name = match.group(1).strip()
                # Remove CRM e outros identificadores
                doctor_name = re.sub(r'\s*CRM.*$', '', doctor_name, flags=re.IGNORECASE)
                doctor_name = re.sub(r'\s*\d+.*$', '', doctor_name)
                
                if len(doctor_name) > 3 and self._looks_like_name(doctor_name):
                    return doctor_name
        
        return None
    
    def _looks_like_name(self, text: str) -> bool:
        """Verifica se o texto parece um nome válido."""
        # Nome deve ter pelo menos 2 palavras e começar com maiúscula
        words = text.split()
        if len(words) < 2:
            return False
        
        # Todas as palavras devem começar com maiúscula
        return all(word[0].isupper() for word in words if word)
    
    def _extract_date_smart(self, text: str) -> Optional[str]:
        """Extrai data de emissão com validação."""
        # Prioriza datas próximas a palavras-chave de emissão
        emission_keywords = ['emissão', 'emitido', 'data', 'dia']
        
        # Busca por padrões de data com contexto
        date_patterns = [
            r'(?:data\s+de\s+emiss[aã]o|emitid[oa]\s+em|emiss[aã]o)[:\s]*(\d{2}[/-]\d{2}[/-]\d{4})',
            r'(?:data\s+de\s+emiss[aã]o|emitid[oa]\s+em|emiss[aã]o)[:\s]*(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 1:
                    date_str = match.group(1)
                    if self._validate_date(date_str):
                        return self._normalize_date(date_str)
                elif len(match.groups()) == 3:
                    day, month, year = match.groups()
                    date_str = self._format_date_extenso(day, month, year)
                    if date_str:
                        return date_str
        
        # Busca genérica por datas válidas
        generic_pattern = r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b'
        matches = re.finditer(generic_pattern, text)
        
        for match in matches:
            date_str = match.group(1)
            if self._validate_date(date_str):
                # Verifica se está em contexto relevante
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].lower()
                
                if any(keyword in context for keyword in emission_keywords):
                    return self._normalize_date(date_str)
        
        return None
    
    def _validate_date(self, date_str: str) -> bool:
        """Valida se uma data é válida."""
        try:
            # Tenta diferentes formatos
            formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    # Verifica se a data é razoável (não muito antiga nem futura)
                    current_year = datetime.now().year
                    if 2000 <= date_obj.year <= current_year + 1:
                        return True
                except ValueError:
                    continue
            return False
        except:
            return False
    
    def _normalize_date(self, date_str: str) -> str:
        """Normaliza data para formato DD/MM/YYYY."""
        # Remove separadores diferentes
        date_str = date_str.replace('-', '/')
        
        parts = date_str.split('/')
        if len(parts) == 3:
            if len(parts[0]) == 4:  # YYYY/MM/DD
                year, month, day = parts
            else:  # DD/MM/YYYY
                day, month, year = parts
            
            return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        
        return date_str
    
    def _format_date_extenso(self, day: str, month: str, year: str) -> Optional[str]:
        """Formata data por extenso para DD/MM/YYYY."""
        months_pt = {
            'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
            'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
            'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
        }
        
        month_num = months_pt.get(month.lower())
        if month_num:
            return f"{day.zfill(2)}/{month_num}/{year}"
        return None
    
    def _extract_days_smart(self, text: str) -> Optional[int]:
        """Extrai dias de repouso com validação."""
        patterns = [
            r'(\d{1,2})\s*(?:\([^)]+\)\s*)?(?:dia|dias)\s*(?:de\s+)?(?:repouso|afastamento|afastado)',
            r'(?:repouso|afastamento)[:\s]*(\d{1,2})\s*(?:dia|dias)',
            r'(\d{1,2})\s*(?:dia|dias)\s*(?:de\s+)?(?:repouso|afastamento)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                days = int(match.group(1))
                # Validação: dias devem ser razoáveis (1 a 365)
                if 1 <= days <= 365:
                    return days
        
        return None
    
    def _merge_extractions(self, text: str, entities: List[Dict]) -> Dict:
        """Combina extrações do BERT com padrões."""
        results = self._extract_with_smart_patterns(text)
        
        # Usa entidades do BERT para melhorar resultados
        for entity in entities:
            entity_text = entity.get('word', '').strip()
            entity_label = entity.get('entity_group', '')
            
            # Melhora extração baseada em labels do BERT
            if 'PER' in entity_label and not results['doctor']:
                if self._looks_like_name(entity_text):
                    results['doctor'] = entity_text
        
        return results
    
    def _validate_and_correct(self, results: Dict, original_text: str) -> Dict[str, str]:
        """
        Valida e corrige os resultados extraídos.
        """
        validated = {}
        
        # Valida e formata CID
        cid = results.get('cid')
        if cid and self._validate_cid(cid):
            validated['CID'] = cid
        else:
            validated['CID'] = "CID não foi encontrado. Verifique se o texto está legível ou se segue o padrão CID-10 (ex.: J00, M54.5)."
        
        # Valida médico
        doctor = results.get('doctor')
        if doctor and len(doctor) > 3:
            validated['Médico'] = doctor
        else:
            validated['Médico'] = "Nome do médico não foi encontrado. Certifique-se de que o prefixo 'Dr.' ou 'Dra.' esteja presente e legível."
        
        # Valida data
        date = results.get('date')
        if date and self._validate_date(date):
            validated['Data de Emissão'] = date
        else:
            validated['Data de Emissão'] = "Data de emissão não foi encontrada. A imagem pode estar ilegível ou sem a expressão 'emitido em'."
        
        # Valida dias
        days = results.get('days')
        if days and 1 <= days <= 365:
            suffix = "dia" if days == 1 else "dias"
            validated['Dias de Repouso'] = f"{days} {suffix} de repouso"
        else:
            validated['Dias de Repouso'] = "Dias de repouso não foram encontrados. Verifique se a quantidade está indicada de forma numérica no atestado."
        
        return validated
    
    def save_correction(self, original: Dict, corrected: Dict, text: str):
        """
        Salva uma correção para aprendizado futuro.
        
        Args:
            original: Resultado original (com erros)
            corrected: Resultado corrigido manualmente
            text: Texto original do OCR
        """
        correction = {
            'original': original,
            'corrected': corrected,
            'text_snippet': text[:500],  # Primeiros 500 caracteres
            'text_full': text,  # Texto completo para melhor matching
            'timestamp': datetime.now().isoformat()
        }
        
        self.corrections_history.append(correction)
        self.save_corrections_history()
    
    def load_corrections_history(self):
        """Carrega histórico de correções."""
        history_file = 'ai_corrections_history.json'
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.corrections_history = json.load(f)
            except:
                self.corrections_history = []
        else:
            self.corrections_history = []
    
    def save_corrections_history(self):
        """Salva histórico de correções."""
        history_file = 'ai_corrections_history.json'
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.corrections_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def _find_similar_correction(self, text: str) -> Optional[Dict[str, str]]:
        """
        Procura no histórico por um texto similar e retorna a correção aprendida.
        
        Args:
            text: Texto normalizado atual
            
        Returns:
            Dicionário com correção se encontrada, None caso contrário
        """
        if not self.corrections_history:
            return None
        
        # Normaliza o texto atual para comparação
        text_normalized = self._normalize_for_comparison(text)
        
        best_match = None
        best_similarity = 0.0
        similarity_threshold = 0.70  # 70% de similaridade (reduzido para melhor matching)
        
        for correction in self.corrections_history:
            # Tenta usar texto completo primeiro, depois snippet
            history_text = correction.get('text_full', '') or correction.get('text_snippet', '')
            if not history_text:
                continue
            
            history_normalized = self._normalize_for_comparison(history_text)
            
            # Calcula similaridade
            similarity = self._calculate_similarity(text_normalized, history_normalized)
            
            if similarity > best_similarity and similarity >= similarity_threshold:
                best_similarity = similarity
                best_match = correction.get('corrected', {})
        
        if best_match:
            print(f"✓ Texto similar encontrado no histórico (similaridade: {best_similarity:.1%})")
            return best_match
        
        return None
    
    def _normalize_for_comparison(self, text: str) -> str:
        """Normaliza texto para comparação (remove espaços extras, minúsculas, etc)."""
        # Remove espaços múltiplos e converte para minúsculas
        text = re.sub(r'\s+', ' ', text.lower().strip())
        # Remove caracteres especiais que podem variar
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similaridade entre dois textos usando método simples de palavras comuns.
        
        Args:
            text1: Primeiro texto
            text2: Segundo texto
            
        Returns:
            Valor entre 0.0 e 1.0 representando similaridade
        """
        if not text1 or not text2:
            return 0.0
        
        # Divide em palavras
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calcula interseção e união
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        # Similaridade de Jaccard
        jaccard = len(intersection) / len(union)
        
        # Também verifica similaridade de sequência (para textos muito similares)
        # Usa o tamanho do texto menor como base
        min_len = min(len(text1), len(text2))
        max_len = max(len(text1), len(text2))
        
        if max_len == 0:
            return 0.0
        
        # Se textos são muito diferentes em tamanho, reduz similaridade
        size_ratio = min_len / max_len
        if size_ratio < 0.5:  # Se um texto é menos da metade do outro
            jaccard *= 0.7
        
        return jaccard
    
    def _apply_learned_patterns(self, text: str, results: Dict[str, str]) -> Dict[str, str]:
        """
        Aplica padrões aprendidos do histórico de correções.
        Procura por padrões específicos que foram corrigidos anteriormente.
        
        Args:
            text: Texto normalizado
            results: Resultados atuais da extração
            
        Returns:
            Resultados com padrões aprendidos aplicados
        """
        if not self.corrections_history:
            return results
        
        # Extrai padrões comuns das correções
        for correction in self.corrections_history:
            corrected = correction.get('corrected', {})
            history_text = correction.get('text_snippet', '')
            
            if not history_text:
                continue
            
            # Procura por padrões específicos no texto atual que correspondem ao histórico
            # Por exemplo, se no histórico havia um CID específico em um contexto similar
            
            # Verifica se há padrões de CID similares
            for key in ['CID', 'Médico', 'Data de Emissão', 'Dias de Repouso']:
                corrected_value = corrected.get(key, '')
                
                # Se o resultado atual está errado mas temos uma correção válida
                if (key in results and 
                    ('não foi encontrado' in results[key] or 'não foram encontrados' in results[key]) and
                    corrected_value and 
                    'não foi encontrado' not in corrected_value and 
                    'não foram encontrados' not in corrected_value):
                    
                    # Verifica se o contexto é similar
                    # Procura por palavras-chave que aparecem no histórico
                    history_words = set(history_text.lower().split())
                    current_words = set(text.lower().split())
                    
                    # Se há palavras-chave em comum significativas
                    common_keywords = history_words.intersection(current_words)
                    if len(common_keywords) >= 5:  # Pelo menos 5 palavras em comum
                        # Aplica a correção aprendida
                        results[key] = corrected_value
                        print(f"✓ Aplicado padrão aprendido para {key}")
        
        return results


# Função de compatibilidade
def extract_with_ai(text: str) -> Dict[str, str]:
    """Função wrapper para compatibilidade."""
    ai_service = AIService()
    return ai_service.extract_with_ai(text)

