# Jogo da Forca

Jogo da forca clássico em Python puro para terminal.

## Requisitos

- Python 3.6+

## Como jogar

```bash
python forca.py
```

Digite uma letra por vez. Você tem 6 erros antes de ser enforcado. Ao final de cada partida, perguntado se deseja jogar novamente.

## Como funciona

**Palavras**: Lista local curada (~270 substantivos e adjetivos pt-BR em `palavras_base.txt`). Na primeira execução, baixa ~500 palavras da web para o cache. A cada 10 dias, 25% do cache é rotacionado com novas palavras da web em background.

**Dicas**: Geradas por IA gratuita (Pollinations.ai) em português brasileiro. Dicas são cacheadas localmente (append-only). Enquanto o jogador joga, dicas para todas as palavras são pré-buscadas em background. Dicas de palavras que saíram do cache são automaticamente limpas na rotação.

**Experiência**: Mensagens de status animadas durante chamadas de rede. Se a nuvem falhar, mensagem de fallback é exibida.

## Estrutura do projeto

```
forca.py            # Código principal (~420 linhas)
palavras_base.txt   # Lista curada de substantivos/adjetivos pt-BR
spec.md             # Especificação técnica
README.md           # Este arquivo
```

### Arquivos de cache (gerados automaticamente)

```
.cache_palavras.txt # Palavras da rotação da web (ignorado pelo git)
.cache_dicas.txt    # Dicas cacheadas por palavra (ignorado pelo git)
```
