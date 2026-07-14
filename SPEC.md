# Jogo da Forca — Especificação

## Visão Geral

Jogo da forca (Hangman) em linha de comando, implementado em Python puro. O jogador tenta adivinhar uma palavra letra por letra antes de cometer 6 erros.

## Funcionalidades

- Palavras de uma lista local curada (266 substantivos/adjetivos pt-BR) com rotação periódica via web
- Download inicial de ~500 palavras na primeira execução
- Filtros automáticos em camadas: `PALAVRAS_PROIBIDAS`, `_VERBOS_INFINITIVOS`, `_VERBOS_CONJUGACAO` (regex), `_INGLES_COMUNS`
- Sistema de dicas via LLM com 3 mirrors: OpenRouter (gratuito, API key) → Pollinations.ai (sem key) → dicionário local (~200 dicas)
- Cache de dicas append-only, sincronizado automaticamente com cache de palavras
- Pré-busca de dicas em background (loop contínuo, reinicia a cada partida)
- Mensagens de status animadas durante chamadas de rede
- Configuração interativa de API key na primeira execução (com opção de pular)
- Placar: vitórias, derrotas, tempo mínimo/máximo
- Log detalhado de tentativas de conexão LLM
- Exibição progressiva da forca em ASCII (6 estágios)
- Validação de entrada: apenas uma letra por vez, caracteres alfabéticos
- Prevenção de letras repetidas
- Letras corretas reveladas na palavra; erros contabilizados separadamente
- Tela limpa a cada rodada (`os.system('cls'|'clear')`)
- Mensagem de vitória ou derrota ao final
- Pergunta de nova partida ao encerrar

## Arquitetura

```
forca.py            # Código fonte único (~1150 linhas)
palavras_base.txt   # Lista curada de palavras (266 substantivos/adjetivos)
spec.md             # Este documento
README.md           # Instruções de uso
```

### Arquivos de cache (gerados em runtime)

| Arquivo | Descrição |
|---------|-----------|
| `.cache_palavras.txt` | Palavras obtidas da web, com rotação de 25% a cada 10 dias. Header `# atualizado: <timestamp>` |
| `.cache_dicas.txt` | Dicas salvas por palavra (formato: `PALAVRA\tdica`). Append-only, auto-limpo na rotação |
| `.forca_config` | Configuração persistente (API key do OpenRouter) |
| `.forca_log.txt` | Log detalhado de cada tentativa de conexão LLM (timestamps, HTTP codes, corpo) |
| `.forca_placar.txt` | Placar: vitórias, derrotas, tempo mínimo/máximo |

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
| `_filtrar_palavra(palavra)` | Filtra palavra: verifica PALAVRAS_PROIBIDAS, _VERBOS_INFINITIVOS, _VERBOS_CONJUGACAO (regex), _INGLES_COMUNS |
| `_carregar_palavras_base()` | Lê `palavras_base.txt`, aplica `_filtrar_palavra()` |
| `_ler_cache_palavras()` | Lê `.cache_palavras.txt` (suporta header `# atualizado:` e formato legado), aplica `_filtrar_palavra()` |
| `_salvar_cache(palavras)` | Salva palavras no cache com header de timestamp |
| `_baixar_lista_inicial()` | Download síncrono de ~500 palavras na primeira execução |
| `_ler_timestamp_cache()` | Lê timestamp do header `# atualizado:` do cache de palavras |
| `_iniciar_atualizacao_se_necessario()` | Verifica idade do cache via header; se não existe, faz download inicial; se >10 dias, dispara update em background |
| `_atualizar_cache_bg()` | Busca novas palavras da web, rotaciona 25%, limpa dicas obsoletas |

#### Sistema de dicas (3 mirrors)

| Função | Descrição |
|--------|-----------|
| `gerar_dica(palavra)` | Busca dica no cache; se ausente, busca na nuvem via mirrors e salva |
| `_buscar_dica_openrouter(palavra, api_key, modelo)` | POST com system message e `reasoning: {enabled: false}` para evitar raciocínio em inglês |
| `_buscar_dica_pollinations(palavra, modelo)` | GET sem key, fallback automático |
| `_ler_cache_dicas()` | Lê `.cache_dicas.txt` em dict `{PALAVRA: dica}` |
| `_salvar_dica(palavra, dica)` | Append de dica no cache (não reescreve o arquivo) |
| `_limpar_dicas_obsoletas()` | Remove dicas de palavras que não estão em `_palavras_atuais` |
| `_prefetch_dicas_bg()` | Thread loop que pré-busca dicas para todas as palavras (2s entre requests, 30s se tudo pronto) |

#### Configuração

| Função | Descrição |
|--------|-----------|
| `_configurar_api_key()` | Setup interativo na primeira execução: instrui usuário, valida key, salva em `.forca_config` |
| `_ler_api_key()` | Lê API key de `.forca_config` |
| `_salvar_api_key(key)` | Salva API key no arquivo de configuração |

#### Placar e log

| Função | Descrição |
|--------|-----------|
| `_carregar_placar()` | Carrega placar de `.forca_placar.txt` |
| `_salvar_placar(venceu, tempo)` | Atualiza placar com resultado e tempo da partida |
| `_exibir_placar()` | Exibe resumo: vitórias, derrotas, tempo min/max |
| `_log_tentativa(palavra, mirror, http_code, ok, msg)` | Registra detalhes de cada tentativa de conexão |

### Constantes

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| `URL_PALAVRAS` | `"https://raw.githubusercontent.com/hermitdave/..."` | URL das 50k palavras mais frequentes pt-BR (para rotação) |
| `MAX_ERROS` | `6` | Número máximo de erros |
| `FORCAS` | Lista de 7 strings | Desenhos ASCII da forca (0 a 6 erros) |
| `CACHE_IDADE_MAX` | `864000` (10 dias) | Idade máxima do cache de palavras em segundos |
| `DICA_CACHE` | `.cache_dicas.txt` | Caminho do arquivo de cache de dicas |
| `PROMPT_DICA` | String em português | Prompt para geração de dicas via LLM |
| `PALAVRAS_PROIBIDAS` | Set de ~150+ palavras | Verbos, pronomes, adjetivos inadequados, nomes próprios |
| `_VERBOS_INFINITIVOS` | Set de ~300+ verbos | Verbos em infinitivo para filtrar |
| `_VERBOS_CONJUGACAO` | Regex | Padrões de verbos conjugados: -OU, -EI, -IU, -ANDO, -ENDO, -INDO, etc. |
| `_INGLES_COMUNS` | Set de ~200 palavras | Palavras em inglês frequentes para filtrar |

### Models testados

| Mirror | Modelo | Status |
|--------|--------|--------|
| OpenRouter | `openrouter/free` | Router automático entre modelos gratuitos disponíveis |
| Pollinations | GET (sem key) | Funcional, mais lento |

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

### Fluxo de Filtragem

```
_palavra_candidata
  ├─ len < 4? → REJEITA
  ├─ não é ASCII? → REJEITA
  ├─ PALAVRAS_PROIBIDAS? → REJEITA
  ├─ _VERBOS_INFINITIVOS? → REJEITA
  ├─ _VERBOS_CONJUGACAO (regex)? → REJEITA
  ├─ _INGLES_COMUNS? → REJEITA
  └─ ACEITA
```

## Sistema de Dicas com 3 Mirrors

```
gerar_dica(palavra)
  ├─ Cache hit → retorna instantaneamente
  └─ Cache miss → _buscar_dica_nuvem(palavra)
       ├─ 1º: OpenRouter (POST, com API key)
       │    ├─ System message: "Responda APENAS em portugues brasileiro"
       │    ├─ reasoning: {enabled: false} (evita raciocínio em inglês)
       │    ├─ Sucesso → salva dica
       │    └─ Falha → log + tenta próximo mirror
       ├─ 2º: Pollinations (GET, sem key)
       │    ├─ Sucesso → salva dica
       │    └─ Falha → log + tenta próximo mirror
       ├─ 3º: Dicionário local (~200 dicas pré-escritas)
       │    ├─ Palavra existe → salva dica
       │    └─ Palavra não existe → fallback "(dica indisponivel...)"
       └─ Salva no cache (append)
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

1. Configuração de API key (primeira execução)
2. Inicia pré-busca de dicas em background (loop contínuo)
3. Sorteia palavra (cache da web ou base local)
4. Obtém dica (cache → OpenRouter → Pollinations → local → fallback)
5. Loop: exibe status → lê letra → valida → verifica acerto
6. Encerra ao acertar a palavra ou atingir `MAX_ERROS`
7. Exibe resultado, atualiza e exibe placar
8. Pergunta nova partida
9. Se sim, limpa tela e volta ao passo 2

## Possíveis Melhorias Futuras

- Modo multiplayer (um jogador escolhe a palavra)
- Interface gráfica (Tkinter ou web)
- Suporte a acentos
- Indicador visual de progresso do prefetch de dicas
- Limitar tamanho do cache de dicas (cap max)
- Estatísticas detalhadas no placar (palavras mais erradas, streaks)
