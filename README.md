# Jogo da Forca

Jogo da forca clássico em Python puro para terminal.

## Requisitos

- Python 3.6+

## Como jogar

```bash
python forca.py
```

Na primeira execução, o jogo pergunta se você quer configurar uma chave de API gratuita (OpenRouter) para dicas melhores. Você pode pular — o jogo funciona sem ela.

Digite uma letra por vez. Você tem 6 erros antes de ser enforcado. Ao final de cada partida, é perguntado se deseja jogar novamente.

## Funcionalidades

**Palavras**: Lista local curada (266 substantivos e adjetivos pt-BR em `palavras_base.txt`). Sistema de filtros em camadas:
1. `PALAVRAS_PROIBIDAS` — verbos infinitivos, pronomes, adjetivos inadequados
2. `_VERBOS_INFINITIVOS` — lista expandida de verbos em infinitivo
3. `_VERBOS_CONJUGACAO` — regex para formas conjugadas (-OU, -EI, -ANDO, -ENDO, etc.)
4. `_INGLES_COMUNS` — palavras em inglês frequentes

Na primeira execução, baixa ~500 palavras da web para o cache. A cada 10 dias, 25% do cache é rotacionado com novas palavras da web em background.

**Dicas via LLM**: Sistema de mirrors com 3 camadas:
1. **OpenRouter** (gratuito, com API key) — modelo `openrouter/free` (router automático entre modelos gratuitos) com system message para português e `reasoning: {enabled: false}` para evitar raciocínio em inglês
2. **Pollinations.ai** (sem key) — fallback automático
3. **Dicionário local** — ~200 dicas pré-escritas para último recurso

Dicas são cacheadas localmente (append-only). Cache de dicas sincroniza automaticamente com o cache de palavras — dicas de palavras removidas são limpas no início de cada jogo.

**Placar**: Registra vitórias, derrotas, tempo mínimo e máximo de cada sessão.

**Log**: Detalhes de cada tentativa de conexão são salvos em `.forca_log.txt` para diagnóstico.

## Estrutura do projeto

```
forca.py            # Código principal (~1150 linhas)
palavras_base.txt   # Lista curada de 266 substantivos/adjetivos pt-BR
spec.md             # Especificação técnica
README.md           # Este arquivo
```

### Arquivos de cache (gerados automaticamente, ignorados pelo git)

```
.cache_palavras.txt # Palavras da rotação da web
.cache_dicas.txt    # Dicas cacheadas por palavra
.forca_config       # Configuração (API key do OpenRouter)
.forca_log.txt      # Log de tentativas de conexão
.forca_placar.txt   # Placar (vitórias/derrotas/tempo)
```
