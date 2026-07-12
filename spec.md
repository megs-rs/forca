# Jogo da Forca — Especificação

## Visão Geral

Jogo da forca (Hangman) em linha de comando, implementado em Python puro. O jogador tenta adivinhar uma palavra letra por letra antes de cometer 6 erros.

## Funcionalidades

- Palavras de uma lista local curada (~270 substantivos/adjetivos pt-BR) com rotação periódica via web
- Download inicial de ~500 palavras na primeira execução
- Dicas geradas por LLM gratuita (Pollinations.ai) em português brasileiro, com cache append-only
- Limpeza automática de dicas obsoletas quando o cache de palavras rotaciona
- Pré-busca de dicas em background (loop contínuo, reinicia a cada partida)
- Mensagens de status animadas durante chamadas de rede
- Fallback visual quando a nuvem falha: `(dica indisponivel — sem conexao com a nuvem)`
- Exibição progressiva da forca em ASCII (6 estágios)
- Validação de entrada: apenas uma letra por vez, caracteres alfabéticos
- Prevenção de letras repetidas
- Letras corretas reveladas na palavra; erros contabilizados separadamente
- Tela limpa a cada rodada (`os.system('cls'|'clear')`)
- Mensagem de vitória ou derrota ao final
- Pergunta de nova partida ao encerrar

## Arquitetura

```
forca.py            # Código fonte único (~420 linhas)
palavras_base.txt   # Lista curada de palavras (substantivos/adjetivos)
spec.md             # Este documento
README.md           # Instruções de uso
```

### Arquivos de cache (gerados em runtime)

| Arquivo | Descrição |
|---------|-----------|
| `.cache_palavras.txt` | Palavras obtidas da web, com rotação de 25% a cada 10 dias. Header `# atualizado: <timestamp>` |
| `.cache_dicas.txt` | Dicas salvas por palavra (formato: `PALAVRA\tdica`). Append-only, auto-limpo na rotação |

### Funções

#### Interface do jogo

| Função | Descrição |
|--------|-----------|
| `jogar()` | Loop principal: inicia prefetch, sorteia palavra, gerencia rodadas, pergunta nova partida |
| `limpar_tela()` | Limpa o terminal (Windows: `cls`, Unix: `clear`) |
| `mostrar_status(erros, progresso, letras_erradas, dica)` | Desenha a forca, dica, palavra oculta, letras erradas e contagem |

#### Animação de status

| Função | Descrição |
|--------|-----------|
| `iniciar_animacao(msg)` | Inicia animação de status em thread daemon |
| `parar_animacao()` | Para a animação de status |

#### Sistema de palavras

| Função | Descrição |
|--------|-----------|
| `buscar_palavra()` | Carrega palavras (cache > base), dispara update se necessário, sorteia uma |
| `_carregar_palavras_base()` | Lê `palavras_base.txt` e filtra apenas ASCII alfabético (≥4 letras) |
| `_ler_cache_palavras()` | Lê `.cache_palavras.txt` (suporta header `# atualizado:` e formato legado) |
| `_salvar_cache(palavras)` | Salva palavras no cache com header de timestamp |
| `_baixar_lista_inicial()` | Download síncrono de ~500 palavras na primeira execução |
| `_ler_timestamp_cache()` | Lê timestamp do header `# atualizado:` do cache de palavras |
| `_iniciar_atualizacao_se_necessario()` | Verifica idade do cache via header; se não existe, faz download inicial; se >10 dias, dispara update em background |
| `_atualizar_cache_bg()` | Busca novas palavras da web, rotaciona 25%, limpa dicas obsoletas |

#### Sistema de dicas

| Função | Descrição |
|--------|-----------|
| `gerar_dica(palavra)` | Busca dica no cache; se ausente, busca na nuvem (2 tentativas) e salva |
| `_buscar_dica_nuvem(palavra)` | Faz request à Pollinations.ai para gerar dica |
| `_ler_cache_dicas()` | Lê `.cache_dicas.txt` em dict `{PALAVRA: dica}` |
| `_salvar_dica(palavra, dica)` | Append de dica no cache (não reescreve o arquivo) |
| `_limpar_dicas_obsoletas()` | Remove dicas de palavras que não estão em `_palavras_atuais` |
| `_prefetch_dicas_bg()` | Thread loop que pré-busca dicas para todas as palavras (2s entre requests, 30s se tudo pronto) |

### Constantes

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| `URL_PALAVRAS` | `"https://raw.githubusercontent.com/hermitdave/..."` | URL das 50k palavras mais frequentes pt-BR (para rotação) |
| `MAX_ERROS` | `6` | Número máximo de erros |
| `FORCAS` | Lista de 7 strings | Desenhos ASCII da forca (0 a 6 erros) |
| `CACHE_IDADE_MAX` | `864000` (10 dias) | Idade máxima do cache de palavras em segundos |
| `DICA_CACHE` | `.cache_dicas.txt` | Caminho do arquivo de cache de dicas |

## Sistema de Palavras Híbrido

```
buscar_palavra()
  ├─ _palavras_atuais vazio?
  │    ├─ SIM: carrega base + cache
  │    │    ├─ cache tem algo → usa cache
  │    │    └─ cache vazio → usa base
  │    └─ NÃO: usa _palavras_atuais
  └─ _iniciar_atualizacao_se_necessario()
       ├─ cache não existe → _baixar_lista_inicial() (síncrono, com animação)
       ├─ cache >10 dias → _atualizar_cache_bg() (background)
       │    ├─ Baixa novas palavras da web
       │    ├─ Rotaciona 25%: remove 25% antigas, insere 25% novas
       │    ├─ Salva novo cache com header de timestamp
       │    ├─ Atualiza _palavras_atuais
       │    └─ _limpar_dicas_obsoletas() — remove dicas de palavras que saíram
       └─ cache válido → nada faz
```

### Decisão: base ou cache?

| Situação | Fonte usada |
|----------|------------|
| 1ª execução, sem cache | `palavras_base.txt` + download síncrono da web |
| Execução seguinte, cache válido | `.cache_palavras.txt` |
| Execução >10 dias | `.cache_palavras.txt` + background update 25% |

## Sistema de Dicas com Cache e Limpeza

```
jogar()
  ├─ Dispara _prefetch_dicas_bg() (loop contínuo)
  │     └─ Para cada palavra sem dica cacheada:
  │           └─ Busca dica na Pollinations.ai (2s intervalo)
  │           └─ Append em .cache_dicas.txt
  │     └─ Se tudo pronto → wait 30s e reassume
  │
  ├─ gerar_dica(palavra):
  │     ├─ Cache hit → retorna instantaneamente
  │     └─ Cache miss → busca nuvem (2 tentativas), salva
  │          └─ Falha → retorna fallback "(dica indisponivel...)"
  │
  └─ Rotação de palavras (a cada 10 dias):
       └─ _limpar_dicas_obsoletas()
            └─ Remove dicas de palavras que não estão mais no jogo
```

### Format dos caches

**`.cache_palavras.txt`:**
```
# atualizado: 1783883998
ABELHA
COBRA
ELEFANTE
```

**`.cache_dicas.txt`:**
```
ABELHA	Inseto que produz mel
COBRA	Reptil peconhento
```

## Animação de Status

Função `iniciar_animacao(msg)` cria uma thread daemon que imprime:
```
Gerando dica .  
Gerando dica .. 
Gerando dica ...
Gerando dica  ..
Gerando dica   .
```
Usada durante: busca de palavras, geração de dicas, download inicial.

## Fluxo do Jogo

1. Inicia pré-busca de dicas em background (loop contínuo)
2. Sorteia palavra (cache da web ou base local)
3. Obtém dica (cache ou nuvem, com fallback se falhar)
4. Loop: exibe status → lê letra → valida → verifica acerto
5. Encerra ao acertar a palavra ou atingir `MAX_ERROS`
6. Exibe resultado final, pergunta nova partida
7. Se sim, limpa tela e volta ao passo 1

## Possíveis Melhorias Futuras

- Modo multiplayer (um jogador escolhe a palavra)
- Pontuação baseada em tentativas
- Interface gráfica (Tkinter ou web)
- Suporte a acentos
- Indicador visual de progresso do prefetch de dicas
- Limitar tamanho do cache de dicas (cap max)
