# Jogo da Forca — Especificação

## Visão Geral

Jogo da forca (Hangman) em linha de comando, implementado em Python puro. O jogador tenta adivinhar uma palavra letra por letra antes de cometer 6 erros.

## Funcionalidades

- Palavra sorteada aleatoriamente do dicionário `pythonprobr/palavras` (320k+ palavras pt-BR)
- Dica gerada por LLM gratuita (Pollinations.ai) para cada palavra
- Exibição progressiva da forca em ASCII (6 estágios)
- Validação de entrada: apenas uma letra por vez, caracteres alfabéticos
- Prevenção de letras repetidas
- Letras corretas reveladas na palavra; erros contabilizados separadamente
- Tela limpa a cada rodada (`os.system('cls'|'clear')`)
- Mensagem de vitória ou derrota ao final

## Arquitetura

```
code_l9qwz.py      # Código fonte único (~130 linhas)
spec.md            # Este documento
README.md          # Instruções de uso
```

### Funções

| Função | Descrição |
|--------|-----------|
| `buscar_palavra()` | Busca lista de palavras da URL, filtra apenas A-Z (≥4 letras) e sorteia uma |
| `gerar_dica(palavra)` | Gera dica via Pollinations.ai (LLM gratuita, sem API key) |
| `limpar_tela()` | Limpa o terminal (Windows: `cls`, Unix: `clear`) |
| `mostrar_status(erros, letras_certas, letras_erradas)` | Desenha a forca, palavra oculta, letras erradas e contagem |
| `jogar()` | Loop principal do jogo |
| `if __name__ == "__main__"` | Ponto de entrada |

### Constantes

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| `URL_PALAVRAS` | `"https://raw.githubusercontent.com/..."` | URL da lista de palavras pt-BR |
| `PALAVRA` | Sorteada em runtime | Palavra a ser adivinhada |
| `MAX_ERROS` | `6` | Número máximo de erros |
| `FORCAS` | Lista de 7 strings | Desenhos ASCII da forca (0 a 6 erros) |

## Fluxo do Jogo

1. Sorteia palavra da URL (pythonprobr/palavras)
2. Gera dica via Pollinations.ai (LLM gratuita)
3. Exibe tela de abertura com dica e número de letras
4. Aguarda ENTER
5. Loop: exibe status → lê letra → valida → verifica acerto
6. Encerra ao acertar a palavra ou atingir `MAX_ERROS`
7. Exibe resultado final

## Possíveis Melhorias Futuras

- Palavras sorteadas aleatoriamente de um banco
- Modo multiplayer (um jogador escolhe a palavra)
- Pontuação baseada em tentativas
- Interface gráfica (Tkinter ou web)
- Suporte a acentos
