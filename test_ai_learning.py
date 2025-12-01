"""
Script para testar se o aprendizado da IA está funcionando corretamente.
"""

from services.ai_service import AIService
from services.ocr_service import OCRService
import os


def test_learning():
    """Testa se o sistema está aprendendo com as correções."""
    
    print("=" * 80)
    print("TESTE DE APRENDIZADO DA IA")
    print("=" * 80)
    print()
    
    ai_service = AIService()
    
    # Verifica se há histórico
    if not ai_service.corrections_history:
        print("⚠ Nenhuma correção encontrada no histórico!")
        print("  Execute 'python train_ai.py' primeiro para adicionar exemplos.")
        return
    
    print(f"✓ Encontradas {len(ai_service.corrections_history)} correções no histórico")
    print()
    
    # Testa com o primeiro exemplo do histórico
    if ai_service.corrections_history:
        first_correction = ai_service.corrections_history[0]
        test_text = first_correction.get('text_full') or first_correction.get('text_snippet', '')
        expected_result = first_correction.get('corrected', {})
        
        if not test_text:
            print("⚠ Texto de teste não encontrado no histórico!")
            return
        
        print("Testando com texto do histórico de treinamento...")
        print("-" * 80)
        print(f"Texto (primeiros 200 caracteres): {test_text[:200]}...")
        print()
        
        # Extrai informações
        result = ai_service.extract_with_ai(test_text)
        
        print("Resultado esperado (do treinamento):")
        for key, value in expected_result.items():
            print(f"  {key}: {value}")
        print()
        
        print("Resultado obtido:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        print()
        
        # Compara resultados
        matches = 0
        total = len(expected_result)
        
        for key in expected_result.keys():
            expected = expected_result.get(key, '')
            obtained = result.get(key, '')
            
            # Remove mensagens de erro para comparação
            if 'não foi encontrado' in expected or 'não foram encontrados' in expected:
                if 'não foi encontrado' in obtained or 'não foram encontrados' in obtained:
                    matches += 1
            elif expected == obtained:
                matches += 1
        
        accuracy = (matches / total) * 100 if total > 0 else 0
        
        print("=" * 80)
        print(f"Precisão: {matches}/{total} campos corretos ({accuracy:.1f}%)")
        print("=" * 80)
        
        if accuracy >= 75:
            print("✓ Teste PASSOU! A IA está aprendendo corretamente.")
        else:
            print("⚠ Teste FALHOU! A IA não está aplicando as correções aprendidas.")
            print()
            print("Possíveis causas:")
            print("  1. O texto do OCR pode variar entre execuções")
            print("  2. A similaridade pode estar muito baixa")
            print("  3. O texto completo pode não estar sendo salvo")
    
    print()
    print("Para testar com um arquivo de imagem:")
    print("  python test_ai_learning.py <caminho_do_arquivo>")


def test_with_file(file_path: str):
    """Testa com um arquivo específico."""
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo não encontrado: {file_path}")
        return
    
    print("=" * 80)
    print("TESTE COM ARQUIVO")
    print("=" * 80)
    print()
    
    # Extrai texto
    ocr = OCRService()
    text = ocr.extract_text(file_path)
    
    print(f"Texto extraído (primeiros 300 caracteres):")
    print(text[:300])
    print()
    print("-" * 80)
    print()
    
    # Extrai informações com IA
    ai_service = AIService()
    result = ai_service.extract_with_ai(text)
    
    print("Resultado da extração:")
    for key, value in result.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_with_file(sys.argv[1])
    else:
        test_learning()

