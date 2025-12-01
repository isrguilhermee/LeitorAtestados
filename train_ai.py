"""
Script para treinar e melhorar o modelo de IA com dados de exemplo.
Permite adicionar correções e exemplos para melhorar a precisão.
"""

import json
import os
from datetime import datetime
from services.ai_service import AIService
from services.ocr_service import OCRService
from services.nlp_service import NLPService


def add_training_example():
    """Adiciona um exemplo de treinamento manualmente."""
    print("=" * 80)
    print("ADICIONAR EXEMPLO DE TREINAMENTO")
    print("=" * 80)
    print()
    
    # Solicita texto do OCR
    print("Cole o texto extraído pelo OCR (ou deixe em branco para usar arquivo):")
    text = input("> ").strip()
    
    if not text:
        file_path = input("Digite o caminho do arquivo de imagem/PDF: ").strip()
        if os.path.exists(file_path):
            ocr = OCRService()
            text = ocr.extract_text(file_path)
            print(f"\nTexto extraído:\n{text}\n")
        else:
            print("Arquivo não encontrado!")
            return
    
    # Extrai informações usando método atual
    ai_service = AIService()
    current_results = ai_service.extract_with_ai(text)
    
    print("\nResultados atuais da IA:")
    print("-" * 80)
    for key, value in current_results.items():
        print(f"{key}: {value}")
    print()
    
    # Solicita correções
    print("Digite as correções (deixe em branco para manter o valor atual):")
    corrected = {}
    
    for key in ['CID', 'Médico', 'Data de Emissão', 'Dias de Repouso']:
        current_value = current_results.get(key, '')
        print(f"\n{key} (atual: {current_value})")
        new_value = input("Novo valor: ").strip()
        
        if new_value:
            corrected[key] = new_value
        else:
            # Se não foi encontrado, mantém mensagem de erro
            if 'não foi encontrado' in current_value or 'não foram encontrados' in current_value:
                corrected[key] = current_value
            else:
                corrected[key] = current_value
    
    # Salva correção
    ai_service.save_correction(current_results, corrected, text)
    
    print("\n✓ Correção salva com sucesso!")
    print(f"Total de correções no histórico: {len(ai_service.corrections_history)}")


def view_training_history():
    """Visualiza o histórico de treinamento."""
    ai_service = AIService()
    
    print("=" * 80)
    print("HISTÓRICO DE TREINAMENTO")
    print("=" * 80)
    print()
    
    if not ai_service.corrections_history:
        print("Nenhuma correção salva ainda.")
        return
    
    print(f"Total de correções: {len(ai_service.corrections_history)}\n")
    
    for i, correction in enumerate(ai_service.corrections_history[-10:], 1):  # Últimas 10
        print(f"Correção #{i} - {correction.get('timestamp', 'N/A')}")
        print("-" * 80)
        print("Original:")
        for key, value in correction.get('original', {}).items():
            print(f"  {key}: {value}")
        print("\nCorrigido:")
        for key, value in correction.get('corrected', {}).items():
            print(f"  {key}: {value}")
        print("\n" + "=" * 80 + "\n")


def batch_train_from_file():
    """Treina com múltiplos exemplos de um arquivo JSON."""
    print("=" * 80)
    print("TREINAMENTO EM LOTE")
    print("=" * 80)
    print()
    
    file_path = input("Digite o caminho do arquivo JSON com exemplos: ").strip()
    
    if not os.path.exists(file_path):
        print("Arquivo não encontrado!")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            examples = json.load(f)
        
        if not isinstance(examples, list):
            print("Erro: O arquivo deve conter uma lista de exemplos.")
            return
        
        ai_service = AIService()
        count = 0
        
        for example in examples:
            text = example.get('text', '')
            corrected = example.get('corrected', {})
            
            if not text or not corrected:
                continue
            
            # Extrai resultado atual
            current = ai_service.extract_with_ai(text)
            
            # Salva correção
            ai_service.save_correction(current, corrected, text)
            count += 1
        
        print(f"\n✓ {count} exemplos adicionados ao histórico de treinamento!")
        
    except Exception as e:
        print(f"Erro ao processar arquivo: {e}")


def create_example_template():
    """Cria um template de arquivo JSON para treinamento em lote."""
    template = [
        {
            "text": "Texto extraído do OCR aqui...",
            "corrected": {
                "CID": "J00",
                "Médico": "Dr. João Silva",
                "Data de Emissão": "15/01/2025",
                "Dias de Repouso": "5 dias de repouso"
            }
        },
        {
            "text": "Outro exemplo de texto...",
            "corrected": {
                "CID": "M54.5",
                "Médico": "Dra. Maria Santos",
                "Data de Emissão": "20/01/2025",
                "Dias de Repouso": "10 dias de repouso"
            }
        }
    ]
    
    filename = "training_examples_template.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Template criado: {filename}")
    print("Edite este arquivo com seus exemplos e use 'Treinamento em lote' para carregá-los.")


def main():
    """Menu principal."""
    while True:
        print("\n" + "=" * 80)
        print("SISTEMA DE TREINAMENTO DA IA - LEITOR DE ATESTADOS")
        print("=" * 80)
        print()
        print("1. Adicionar exemplo de treinamento")
        print("2. Visualizar histórico de treinamento")
        print("3. Treinamento em lote (de arquivo JSON)")
        print("4. Criar template de treinamento em lote")
        print("5. Sair")
        print()
        
        choice = input("Escolha uma opção: ").strip()
        
        if choice == '1':
            add_training_example()
        elif choice == '2':
            view_training_history()
        elif choice == '3':
            batch_train_from_file()
        elif choice == '4':
            create_example_template()
        elif choice == '5':
            print("\nAté logo!")
            break
        else:
            print("\nOpção inválida!")


if __name__ == "__main__":
    main()

