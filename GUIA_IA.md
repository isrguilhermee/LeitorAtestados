# Guia de Uso do Sistema de IA para Leitura de Atestados

## Visão Geral

O sistema agora inclui um serviço de IA que melhora significativamente a precisão na extração de informações de atestados médicos. A IA combina:

- **Modelos de NLP avançados** (BERT em português) quando disponível
- **Validação inteligente** baseada em regras médicas
- **Correção automática** de erros comuns do OCR
- **Sistema de aprendizado** com histórico de correções

## Instalação das Dependências de IA

### Opção 1: Instalação Básica (Recomendada)

O sistema funciona sem modelos avançados, usando validação inteligente:

```bash
pip install Flask pytesseract pdf2image Pillow openpyxl werkzeug
```

### Opção 2: Instalação Completa com BERT (Opcional)

Para usar modelos de IA mais avançados:

```bash
pip install transformers torch
```

**Nota:** O modelo BERT requer ~500MB de espaço e pode demorar na primeira execução para fazer download.

## Como Funciona

### 1. Extração Híbrida

O sistema usa uma abordagem híbrida:

1. **Primeiro**: Tenta extrair usando IA avançada (se disponível)
2. **Segundo**: Usa padrões inteligentes com validação
3. **Terceiro**: Combina resultados para maior precisão
4. **Fallback**: Usa método tradicional se IA falhar

### 2. Validação Inteligente

A IA valida automaticamente:

- **CID**: Verifica se o código pertence a uma categoria válida (A-Z)
- **Médico**: Valida formato de nome (mínimo 2 palavras, maiúsculas)
- **Data**: Verifica se a data é válida e está em período razoável (2000-2026)
- **Dias**: Valida se está entre 1 e 365 dias

### 3. Correção de Erros do OCR

A IA corrige automaticamente:

- Erros comuns de leitura (ex: "0" → "O", "1" → "I")
- Espaçamentos incorretos
- Caracteres especiais mal interpretados
- Datas em formatos diferentes

## Treinando a IA

### Método 1: Treinamento Manual

Execute o script de treinamento:

```bash
python train_ai.py
```

Escolha a opção "1. Adicionar exemplo de treinamento" e:

1. Cole o texto extraído pelo OCR
2. Revise os resultados atuais
3. Digite as correções quando necessário
4. O sistema salva para aprendizado futuro

### Método 2: Treinamento em Lote

1. Crie um arquivo JSON com exemplos:

```json
[
  {
    "text": "Texto do OCR aqui...",
    "corrected": {
      "CID": "J00",
      "Médico": "Dr. João Silva",
      "Data de Emissão": "15/01/2025",
      "Dias de Repouso": "5 dias de repouso"
    }
  }
]
```

2. Use o script de treinamento:
```bash
python train_ai.py
```
Escolha opção "3. Treinamento em lote"

### Método 3: Criar Template

Para criar um template de exemplo:

```bash
python train_ai.py
```
Escolha opção "4. Criar template de treinamento em lote"

## Usando o Sistema

### Execução Normal

O sistema usa IA automaticamente quando disponível:

```bash
python app.py
```

A IA será usada automaticamente para melhorar os resultados.

### Desabilitar IA (usar apenas método tradicional)

Se quiser usar apenas o método tradicional, edite `app.py` e altere:

```python
data = extract_info_with_ai(text, use_ai=False)
```

## Melhorias Implementadas

### 1. Extração de CID Melhorada

- Busca por contexto (próximo a palavras como "diagnóstico", "CID")
- Validação de categoria válida
- Suporte a múltiplos formatos (CID-10, C.I.D., etc.)

### 2. Extração de Médico Melhorada

- Reconhece múltiplos formatos (Dr., Dra., Doutor, etc.)
- Remove automaticamente CRM e números
- Valida formato de nome

### 3. Extração de Data Melhorada

- Prioriza datas próximas a palavras-chave ("emissão", "emitido")
- Suporta datas por extenso ("15 de janeiro de 2025")
- Valida se a data é razoável

### 4. Extração de Dias Melhorada

- Busca em múltiplos contextos
- Valida faixa razoável (1-365 dias)
- Suporta formatos variados

## Visualizando Histórico de Treinamento

Para ver as correções salvas:

```bash
python train_ai.py
```

Escolha opção "2. Visualizar histórico de treinamento"

O histórico é salvo em `ai_corrections_history.json`

## Estrutura de Arquivos

```
services/
├── ai_service.py          # Serviço principal de IA
├── nlp_service.py         # Serviço NLP (atualizado para usar IA)
├── ocr_service.py         # Extração de texto
└── excel_service.py       # Exportação para Excel

train_ai.py                # Script de treinamento
ai_corrections_history.json # Histórico de correções (criado automaticamente)
```

## Solução de Problemas

### Erro: "transformers não instalado"

**Solução**: Instale com `pip install transformers torch` ou use sem (funciona normalmente)

### IA não está melhorando resultados

**Solução**: 
1. Adicione exemplos de treinamento usando `train_ai.py`
2. Verifique se o texto do OCR está legível
3. Revise os padrões em `services/ai_service.py`

### Resultados ainda incorretos

**Solução**:
1. Adicione mais exemplos de treinamento
2. Verifique a qualidade da imagem do atestado
3. Considere melhorar a qualidade do OCR (DPI mais alto)

## Próximos Passos

Para melhorar ainda mais a precisão:

1. **Colete mais exemplos**: Quanto mais exemplos de treinamento, melhor
2. **Revise correções**: Use o histórico para identificar padrões de erro
3. **Ajuste padrões**: Edite `services/ai_service.py` para adicionar novos padrões
4. **Use BERT**: Instale transformers para modelos mais avançados

## Notas Técnicas

- O sistema funciona **sem** BERT, usando validação inteligente
- BERT melhora resultados mas não é obrigatório
- Histórico de correções pode ser usado para treinar modelos customizados no futuro
- Todos os dados de treinamento são salvos localmente

