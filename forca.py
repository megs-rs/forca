import os
import random
import time
import urllib.error
import urllib.request
import urllib.parse
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "forca"
CACHE_ARQUIVO = CACHE_DIR / "palavras.txt"
CACHE_IDADE_MAX = 10 * 86400  # 10 dias em segundos

# Configurações do jogo
URL_PALAVRAS = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/pt_br/pt_br_50k.txt"
PALAVRA = ""
MAX_ERROS = 6

# Desenhos da forca em ASCII
FORCAS = [
    '''
       +---+
       |   |
           |
           |
           |
           |
      ========''',
    '''
       +---+
       |   |
       O   |
           |
           |
           |
      ========''',
    '''
       +---+
       |   |
       O   |
       |   |
           |
           |
      ========''',
    '''
       +---+
       |   |
       O   |
      /|   |
           |
           |
      ========''',
    '''
       +---+
       |   |
       O   |
      /|\\  |
           |
           |
      ========''',
    '''
       +---+
       |   |
       O   |
      /|\\  |
      /    |
           |
      ========''',
    '''
       +---+
       |   |
       O   |
      /|\\  |
      / \\  |
           |
      ========''',
]

def buscar_palavra():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if CACHE_ARQUIVO.exists():
        idade = time.time() - CACHE_ARQUIVO.stat().st_mtime
        if idade <= CACHE_IDADE_MAX:
            with open(CACHE_ARQUIVO) as f:
                linhas = f.read().splitlines()
            palavras = (l.split()[0].strip().upper() for l in linhas if l.strip())
            validas = [p for p in palavras if p.isascii() and p.isalpha() and len(p) >= 4]
            return random.choice(validas)
    with urllib.request.urlopen(URL_PALAVRAS) as f:
        CACHE_ARQUIVO.write_bytes(f.read())
    with open(CACHE_ARQUIVO) as f:
        linhas = f.read().splitlines()
    palavras = (l.split()[0].strip().upper() for l in linhas if l.strip())
    validas = [p for p in palavras if p.isascii() and p.isalpha() and len(p) >= 4]
    return random.choice(validas)

def gerar_dica(palavra):
    prompt = f"Dica curta sobre '{palavra}' em português brasileiro, sem revelar a palavra:"
    url = "https://text.pollinations.ai/" + urllib.parse.quote(prompt)
    for _ in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as f:
                return f.read().decode().strip()
        except Exception:
            time.sleep(3)
    return None

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_status(erros, letras_certas, letras_erradas, dica=None):
    limpar_tela()
    print("=" * 40)
    print("           JOGO DA FORCA")
    print("=" * 40)
    print(FORCAS[min(erros, MAX_ERROS)])
    if dica:
        print(f"DICA: {dica}")
    print(f"\n{' '.join(letras_certas)}")
    print(f"\nLetras erradas: {' '.join(letras_erradas)}")
    print(f"Erros: {erros}/{MAX_ERROS}")

def jogar():
    global PALAVRA
    PALAVRA = buscar_palavra()
    dica = gerar_dica(PALAVRA)
    
    erros = 0
    letras_adivinhadas = set()
    letras_erradas = []
    
    progresso = ['_'] * len(PALAVRA)
    
    while erros < MAX_ERROS and '_' in progresso:
        mostrar_status(erros, progresso, letras_erradas, dica)
        
        tentativa = input("\nDigite uma letra: ").strip().upper()
        
        # Validação
        if len(tentativa) != 1 or not tentativa.isalpha():
            print("Entrada inválida! Digite apenas uma letra.")
            input("Pressione ENTER para continuar...")
            continue
            
        if tentativa in letras_adivinhadas:
            print("Você já tentou essa letra!")
            input("Pressione ENTER para continuar...")
            continue
            
        letras_adivinhadas.add(tentativa)
        
        # Verifica acerto
        if tentativa in PALAVRA:
            for i, letra in enumerate(PALAVRA):
                if letra == tentativa:
                    progresso[i] = letra
        else:
            erros += 1
            letras_erradas.append(tentativa)

    # Fim de jogo
    mostrar_status(erros, progresso, letras_erradas, dica)
    
    if '_' not in progresso:
        print("\n🎉 PARABÉNS! Você venceu!")
    else:
        print(f"\n💀 ENFORCADO! A palavra era: {PALAVRA}")
    
    print("\nObrigado por jogar!")

if __name__ == "__main__":
    jogar()