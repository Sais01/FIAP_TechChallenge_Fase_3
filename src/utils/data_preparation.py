import json
import re
import os

def anonimizar_texto_regex(texto: str) -> str:
    """
    Aplica técnicas de pré-processamento e anonimização.
    Remove CPFs, telefones e nomes próprios que simulam dados reais.
    """
    if not texto:
        return ""
    
    # Mascarar números de CPF
    texto = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', '[CPF_ANONIMIZADO]', texto)
    # Mascarar telefones com ou sem parênteses no DDD
    texto = re.sub(
        r'(?<!\d)(?:\+?55[\s.-]*)?(?:\(\d{2}\)|\d{2})[\s.-]*\d{4,5}[-.\s]?\d{4}(?!\d)',
        '[TELEFONE_REMOVIDO]',
        texto,
    )
    texto = re.sub(r'\bramal\s\d{4}\b', 'ramal [OCULTO]', texto, flags=re.IGNORECASE)
    # Mascarar nomes próprios após pronomes/títulos (Dr., Dra., Paciente, paciente)
    texto = re.sub(r'\b(Dr\.|Dra\.|Paciente|paciente)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', r'\1 [NOME_OCULTO]', texto)
    # Mascarar nomes que aparecem após "teste:"
    texto = re.sub(r'(?<=teste:\s)[A-Z][a-z]+\s[A-Z][a-z]+', '[NOME_OCULTO]', texto)
    
    return texto

def processar_dados_internos(caminho_entrada: str) -> list:
    """Lê os dados sintéticos do hospital e aplica a curadoria."""
    print(f"Lendo dados sintéticos de: {caminho_entrada}")
    
    if not os.path.exists(caminho_entrada):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_entrada}. Crie o arquivo JSON sintético primeiro.")

    with open(caminho_entrada, 'r', encoding='utf-8') as file:
        dados_brutos = json.load(file)
    
    dados_processados = []
    
    for item in dados_brutos:
        # Formatando para instrução de fine-tuning (Instruction-Tuning)
        dados_processados.append({
            "instruction": "Você é o assistente virtual médico do hospital. Responda à dúvida clínica com base nos protocolos internos.",
            "context": anonimizar_texto_regex(item["pergunta"]),
            "response": anonimizar_texto_regex(item["resposta"])
        })
        
    return dados_processados

def exportar_jsonl(dados: list, caminho_saida: str):
    """Exporta para o formato esperado pelos modelos LLM no Colab."""
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        for entrada in dados:
            f.write(json.dumps(entrada, ensure_ascii=False) + '\n')
    print(f"Dataset de treino salvo com sucesso em: {caminho_saida}")

if __name__ == "__main__":
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "raw_hospital_protocols.json")
    PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "medical_dataset_curated.jsonl")
    
    # Execução do pipeline
    dataset_final = processar_dados_internos(RAW_DATA_PATH)
    exportar_jsonl(dataset_final, PROCESSED_DATA_PATH)