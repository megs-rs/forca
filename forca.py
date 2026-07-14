import json
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# Caminhos
DIR_BASE = Path(__file__).parent
ARQ_PALAVRAS_BASE = DIR_BASE / "palavras_base.txt"
CACHE_ARQUIVO = DIR_BASE / ".cache_palavras.txt"
CACHE_IDADE_MAX = 10 * 86400  # 10 dias em segundos
ARQ_CONFIG = DIR_BASE / ".forca_config"
ARQ_LOG = DIR_BASE / ".forca_log.txt"
ARQ_PLACAR = DIR_BASE / ".forca_placar.txt"

# Configuracoes do jogo
URL_PALAVRAS = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2016/pt_br/pt_br_50k.txt"
MAX_ERROS = 6

# Palavras proibidas (inadequadas para jogo)
PALAVRAS_PROIBIDAS = {
    "ESTUPRAR", "ESTUPRO", "ESTUPRADOR", "ESTUPRADA",
    "ASSEDIAR", "ASSEDIO", "ASSEDIADO", "ASSEDIADA",
    "ASSASSINAR", "ASSASSINO", "ASSASSINA", "ASSASSINATO",
    "VIOLAR", "VIOLACAO", "VIOLADOR", "VIOLADA",
    "SUICIDIO", "SUICIDAR", "SUICIDA",
    "DROGAS", "DROGA", "TRAFFICO", "TRAFFICANTE",
    "PEDOFILIA", "PEDOFILO", "PEDOFILA",
    "TERRORISMO", "TERRORISTA", "TERRORIZAR",
    "GENOCIDIO", "ETNICIDA", "HOMICIDIO",
    "TORTURAR", "TORTURA", "TORTURADOR",
    "SEQUESTRO", "SEQUESTRADOR", "SEQUESTRAR",
    "EXTORCION", "EXTORQUIR",
    "BOMBASTISMO", "BOMBA",
    "ARMA", "ARMAS", "ARMAMENTO",
    "CRACK", "COCAINA", "HEROINA", "MARIJUANA",
    "PORNOGRAFIA", "PORNO", "PORNÔ",
    "PUTARIA", "PUTA", "PROSTITUICAO", "PROSTITUIR",
    "XINGAMENTO", "XINGAR", "BUCETA", "CUSAO",
    "PENIS", "VAGINA", "BUNDA", "CU",
    "MERDA", "PORRA", "FODER", "FODENDO", "FUDENDO",
    "CARALHO", "PQP", "PQP", "KRL", "FDP",
    "FILHAPUTA", "FILHO DA PUTA",
    "Corno", "CORNOS", "ADULTERIO", "ADULTERAR",
    "INCESTO", "INCESTUOSO",
    "NECROFILIA", "NECROFILO",
    "BESTIALIDADE", "ZOOFILIA",
    "CANCER", "AIDS", "HIV",
    "COVID", "CORONAVIRUS",
    "EBOLA", "PESTE",
    "LEBRA", "LEPROSO", "HANSENIASE",
    "DEFICIENCIA", "DEFICIENTE", "INVALIDO",
    "RETARDADO", "BURRO", "IDIOTA", "IMBECIL",
    "ANEMIA", "DIABETES", "HIPERTENSAO",
    "DEPRESSAO", "DEPRIMENTE", "SUICIDA",
    "ESQUIZOFRENIA", "BIPOLAR", "PSICOPATA",
    "ALCOOLATRA", "ALCOLATRA", "BEBADAO",
    "GORDO", "GORDA", "OBESO", "OBESA",
    "MAGRO", "MAGRA", "ANOREXICO", "BULIMICO",
    "FEIO", "FEIA", "DEFOMEN",
    "BANDIDO", "CRIMINOSO", "CRIMINOSA",
    "MARGINAL", "MARGINALIZADO",
    "CORRUPTO", "CORRUPCAO", "CORROMPIDO",
    "MARCIA", "DROGAS",
    "FEMICIDIO", "FEMICIDA",
    "PATRICIDIO", "MATRICIDIO", "FILICIDIO",
    "INFANTICIDIO", "AVOCIDIO",
    "HEMORRAGIA", "HEMORRAGICA",
    "INTOXICACAO", "ENVENENAR", "ENVENENAMENTO",
    "ASFIXIA", "ASFIXIAR",
    "IMOLACAO", "IMOLAR",
    # Verbos (nao serve para jogo da forca)
    "ACALMAR", "AGENDAR", "AGILIZAR", "ARRECADAR", "BROTAR",
    "CANSAR", "CHOCAR", "COLHER", "CONSTITUIR", "CONTRARIAR",
    "CORRIGIR", "DESTRANCAR", "DOMICILIAR", "ENFRAQUECER",
    "ENGAJAR", "ESTICAR", "ESTUPRAR", "GAGUEJAR", "INFRINGIR",
    "MARCHAR", "PRONUNCIAR", "PROTEGER", "RECONQUISTAR", "REPORTAR",
    "RESTAR", "SOBRECARREGAR", "SOLTAR", "VARRER",
    # Pronomes
    "ALGUEM", "NINGUEM", "TODOS", "TODAS", "CADA", "OUTRO", "OUTRA",
    "OUTROS", "OUTRAS", "MESMO", "MESMA", "PROPRIO", "PROPRIA",
    "ESTE", "ESTA", "ESSE", "ESSA", "AQUELE", "AQUELA",
    "AQUELES", "AQUELAS", "ISTO", "ISSO", "AQUILO",
}

import re

# Verbos infinitivos comuns que devem ser filtrados
_VERBOS_INFINITIVOS = {
    "ACALMAR", "AGENDAR", "AGILIZAR", "ARRECADAR", "BROTAR",
    "CANSAR", "CHOCAR", "COLHER", "CONSTITUIR", "CONTRARIAR",
    "CORRIGIR", "DESTRANCAR", "DOMICILIAR", "ENFRAQUECER",
    "ENGAJAR", "ESTICAR", "ESTUPRAR", "GAGUEJAR", "INFRINGIR",
    "MARCHAR", "PRONUNCIAR", "PROTEGER", "RECONQUISTAR", "REPORTAR",
    "RESTAR", "SOBRECARREGAR", "SOLTAR", "VARRER",
    "INSPECIONAR", "PAQUERAR", "ESTABILIZAR", "PUXAR", "BABAR",
    "TOMAR", "SONHAR", "ABANDONAR", "SACANEAR", "FABRICAR",
    "NAVEGAR", "EXPLORAR", "SALDAR", "CONQUISTAR", "DESEJAR",
    "PERMITIR", "IMPRIMIR", "CONTINUAR", "INSERIR", "ENTRAR",
    "CAVALGAR", "RUMAR", "SURPREENDER", "RENUNCIAR", "CORROMPER",
}

# Palavras curtas em ingles comuns (4-5 letras)
_INGLES_COMUNS = {
    "BODY", "BLOOD", "BRAIN", "BURN", "CAMP", "CASE", "CASH", "CHARM",
    "CHIP", "CLUB", "COAT", "COOK", "CORN", "CREW", "CROW", "DARK",
    "DAWN", "DEAL", "DEBT", "DIRT", "DISH", "DOCK", "DOOR", "DUST",
    "FARM", "FEAR", "FILM", "FIRE", "FISH", "FOAM", "FOLK", "FOOD",
    "FORD", "FORM", "FROG", "FUEL", "GAME", "GATE", "GIFT", "GIRL",
    "GOLD", "GOLF", "HAIR", "HALF", "HAND", "HANG", "HAZE", "HELM",
    "HERB", "HERO", "HILL", "HOBBY", "HOOD", "HOPE", "HORN", "HORSE",
    "HUNT", "IRON", "JAIL", "JAZZ", "JEWEL", "KICK", "KINGDOM", "KNOT",
    "LACE", "LAKE", "LAND", "LAVA", "LEAF", "LION", "LOCK", "LORD",
    "LUCK", "MAGIC", "MAIZE", "MAPLE", "MARCH", "MASK", "MEDAL", "MELON",
    "MOLE", "MOON", "MUSEUM", "NEST", "NOON", "NOTE", "OLIVE", "OPERA",
    "ORBIT", "OVEN", "OWLS", "PANDA", "PARK", "PEARL", "PIANO", "PILOT",
    "PINE", "PLANET", "PLANT", "PLAZA", "PLUMB", "PLUME", "POEM", "POET",
    "POLE", "POLICE", "POND", "PRINCE", "PULSE", "QUEEN", "RABBIT", "RAIL",
    "RAIN", "RIVER", "ROAD", "ROBOT", "ROCK", "ROOF", "ROOM", "ROOT",
    "ROSE", "SAINT", "SALAD", "SATIN", "SAUCE", "SCALE", "SCARF", "SCENE",
    "SEAL", "SHARK", "SHEEP", "SHELF", "SHIP", "SHIRT", "SHOCK", "SHOOT",
    "SKILL", "SKULL", "SLATE", "SLAVE", "SLEEP", "SLOPE", "SMILE", "SMITH",
    "SMOKE", "SNAKE", "SOLAR", "SOLID", "SONG", "SPACE", "SPARE", "SPARK",
    "SPEAK", "SPEED", "SPEND", "SPICE", "SPINE", "SPLIT", "SPRAY", "SQUAD",
    "STACK", "STAFF", "STAGE", "STAIN", "STAKE", "STAMP", "STAND", "STARK",
    "STATE", "STEAK", "STEAL", "STEAM", "STEEL", "STEEP", "STERN", "STICK",
    "STIFF", "STILL", "STOCK", "STONE", "STOOD", "STORM", "STORY", "STOVE",
    "STRIP", "STUCK", "STUDY", "STUFF", "STYLE", "SUGAR", "SUNNY", "SUPER",
    "SWEET", "SWING", "TABLE", "TASTE", "TEACH", "THEME", "THICK", "THINK",
    "THORN", "THREE", "THROW", "TIGER", "TITLE", "TODAY", "TOKEN", "TOOTH",
    "TOPAZ", "TOTAL", "TOUCH", "TOWER", "TRACK", "TRADE", "TRAIL", "TRAIN",
    "TRAIT", "TRASH", "TRICK", "TRUCK", "TRULY", "TRUMP", "TRUNK", "TRUST",
    "TRUTH", "TUNER", "ULTRA", "UNCLE", "UNDER", "UNION", "UNITE", "UNITY",
    "UNTIL", "UPPER", "UPSET", "URBAN", "USAGE", "USUAL", "UTTER", "VALID",
    "VALUE", "VAULT", "VERSE", "VIDEO", "VIOLA", "VIRUS", "VISIT", "VISTA",
    "VITAL", "VOCAL", "VODKA", "VOICE", "VOTER", "WAIST", "WASTE", "WATCH",
    "WATER", "WEARY", "WEIRD", "WHALE", "WHEAT", "WHEEL", "WHERE", "WHICH",
    "WHILE", "WHITE", "WHOLE", "WHOSE", "WIDER", "WITCH", "WOMAN", "WORLD",
    "WORRY", "WORSE", "WORST", "WORTH", "WOULD", "WOUND", "WRITE", "WRONG",
    "WROTE", "YACHT", "YIELD", "YOUNG", "YOURS", "YOUTH", "ZEBRA",
}

# Sufixos que indicam verbo conjugado (confiaveis)
_VERBOS_CONJUGACAO = re.compile(
    r"OU$|EI$|IU$|ANDO$|ENDO$|INDO$|AVA[SM]?$|IAM[OS]?$|"
    r"AREI$|EREI$|IREI$|ARI[AO]M?$|ERI[AO]M?$|IRI[AO]M?$|"
    r"ADO$|IDO$|ARAM$|ERAM$|IRAM$|ASSE$|ESSE$|ISSE$|EMOS$",
    re.IGNORECASE
)

# Palavras curtas em ingles comuns (4-5 letras)
_INGLES_COMUNS = {
    "BODY", "BLOOD", "BRAIN", "BURN", "CAMP", "CASE", "CASH", "CHARM",
    "CHIP", "CLUB", "COAT", "COOK", "CORN", "CREW", "CROW", "DARK",
    "DAWN", "DEAL", "DEBT", "DIRT", "DISH", "DOCK", "DOOR", "DUST",
    "FARM", "FEAR", "FILM", "FIRE", "FISH", "FOAM", "FOLK", "FOOD",
    "FORD", "FORM", "FROG", "FUEL", "GAME", "GATE", "GIFT", "GIRL",
    "GOLD", "GOLF", "HAIR", "HALF", "HAND", "HANG", "HAZE", "HELM",
    "HERB", "HERO", "HILL", "HOBBY", "HOOD", "HOPE", "HORN", "HORSE",
    "HUNT", "IRON", "JAIL", "JAZZ", "JEWEL", "KICK", "KINGDOM", "KNOT",
    "LACE", "LAKE", "LAND", "LAVA", "LEAF", "LION", "LOCK", "LORD",
    "LUCK", "MAGIC", "MAIZE", "MAPLE", "MARCH", "MASK", "MEDAL", "MELON",
    "MOLE", "MOON", "MUSEUM", "NEST", "NOON", "NOTE", "OLIVE", "OPERA",
    "ORBIT", "OVEN", "OWLS", "PANDA", "PARK", "PEARL", "PIANO", "PILOT",
    "PINE", "PLANET", "PLANT", "PLAZA", "PLUMB", "PLUME", "POEM", "POET",
    "POLE", "POLICE", "POND", "PRINCE", "PULSE", "QUEEN", "RABBIT", "RAIL",
    "RAIN", "RIVER", "ROAD", "ROBOT", "ROCK", "ROOF", "ROOM", "ROOT",
    "ROSE", "SAINT", "SALAD", "SATIN", "SAUCE", "SCALE", "SCARF", "SCENE",
    "SEAL", "SHARK", "SHEEP", "SHELF", "SHIP", "SHIRT", "SHOCK", "SHOOT",
    "SKILL", "SKULL", "SLATE", "SLAVE", "SLEEP", "SLOPE", "SMILE", "SMITH",
    "SMOKE", "SNAKE", "SOLAR", "SOLID", "SONG", "SPACE", "SPARE", "SPARK",
    "SPEAK", "SPEED", "SPEND", "SPICE", "SPINE", "SPLIT", "SPRAY", "SQUAD",
    "STACK", "STAFF", "STAGE", "STAIN", "STAKE", "STAMP", "STAND", "STARK",
    "STATE", "STEAK", "STEAL", "STEAM", "STEEL", "STEEP", "STERN", "STICK",
    "STIFF", "STILL", "STOCK", "STONE", "STOOD", "STORM", "STORY", "STOVE",
    "STRIP", "STUCK", "STUDY", "STUFF", "STYLE", "SUGAR", "SUNNY", "SUPER",
    "SWEET", "SWING", "TABLE", "TASTE", "TEACH", "THEME", "THICK", "THINK",
    "THORN", "THREE", "THROW", "TIGER", "TITLE", "TODAY", "TOKEN", "TOOTH",
    "TOPAZ", "TOTAL", "TOUCH", "TOWER", "TRACK", "TRADE", "TRAIL", "TRAIN",
    "TRAIT", "TRASH", "TRICK", "TRUCK", "TRULY", "TRUMP", "TRUNK", "TRUST",
    "TRUTH", "TUNER", "ULTRA", "UNCLE", "UNDER", "UNION", "UNITE", "UNITY",
    "UNTIL", "UPPER", "UPSET", "URBAN", "USAGE", "USUAL", "UTTER", "VALID",
    "VALUE", "VAULT", "VERSE", "VIDEO", "VIOLA", "VIRUS", "VISIT", "VISTA",
    "VITAL", "VOCAL", "VODKA", "VOICE", "VOTER", "WAIST", "WASTE", "WATCH",
    "WATER", "WEARY", "WEIRD", "WHALE", "WHEAT", "WHEEL", "WHERE", "WHICH",
    "WHILE", "WHITE", "WHOLE", "WHOSE", "WIDER", "WITCH", "WOMAN", "WORLD",
    "WORRY", "WORSE", "WORST", "WORTH", "WOULD", "WOUND", "WRITE", "WRONG",
    "WROTE", "YACHT", "YIELD", "YOUNG", "YOURS", "YOUTH", "ZEBRA",
}


def _filtrar_palavra(palavra):
    """Retorna True se a palavra e adequada para o jogo da forca."""
    p = palavra.upper().strip()
    if not p.isascii() or not p.isalpha() or len(p) < 4:
        return False
    if p in PALAVRAS_PROIBIDAS:
        return False
    if p in _INGLES_COMUNS:
        return False
    if p in _VERBOS_INFINITIVOS:
        return False
    if _VERBOS_CONJUGACAO.search(p):
        return False
    return True


# Palavras atuais do jogo (atualizadas em background)
_palavras_atuais = []


def _log(mensagem):
    """Registra mensagem no arquivo de log com timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{timestamp}] {mensagem}\n"
    with open(ARQ_LOG, "a") as f:
        f.write(linha)

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


# ── Placar ─────────────────────────────────────────────────────────

def _ler_placar():
    if not ARQ_PLACAR.exists():
        return {"vitorias": 0, "derrotas": 0, "tempo_min": None, "tempo_max": None}
    placar = {"vitorias": 0, "derrotas": 0, "tempo_min": None, "tempo_max": None}
    with open(ARQ_PLACAR) as f:
        for l in f:
            l = l.strip()
            if "=" in l:
                k, v = l.split("=", 1)
                k = k.strip()
                v = v.strip()
                if k in ("vitorias", "derrotas"):
                    placar[k] = int(v)
                elif k in ("tempo_min", "tempo_max") and v != "N/A":
                    placar[k] = float(v)
    return placar


def _salvar_placar(placar):
    with open(ARQ_PLACAR, "w") as f:
        f.write(f"vitorias={placar['vitorias']}\n")
        f.write(f"derrotas={placar['derrotas']}\n")
        f.write(f"tempo_min={placar['tempo_min'] if placar['tempo_min'] is not None else 'N/A'}\n")
        f.write(f"tempo_max={placar['tempo_max'] if placar['tempo_max'] is not None else 'N/A'}\n")


def _atualizar_placar(venceu, tempo):
    placar = _ler_placar()
    if venceu:
        placar["vitorias"] += 1
    else:
        placar["derrotas"] += 1
    if placar["tempo_min"] is None or tempo < placar["tempo_min"]:
        placar["tempo_min"] = tempo
    if placar["tempo_max"] is None or tempo > placar["tempo_max"]:
        placar["tempo_max"] = tempo
    _salvar_placar(placar)
    return placar


def _formatar_tempo(segundos):
    if segundos < 60:
        return f"{segundos:.0f}s"
    minutos = int(segundos // 60)
    segs = int(segundos % 60)
    return f"{minutos}m{segs:02d}s"


def _mostrar_placar(placar):
    total = placar["vitorias"] + placar["derrotas"]
    print()
    print("=" * 40)
    print("           PLACAR")
    print("=" * 40)
    print(f"  Vitorias:  {placar['vitorias']}")
    print(f"  Derrotas:  {placar['derrotas']}")
    print(f"  Total:     {total} jogos")
    if placar["tempo_min"] is not None:
        print(f"  Tempo min: {_formatar_tempo(placar['tempo_min'])}")
    else:
        print(f"  Tempo min: N/A")
    if placar["tempo_max"] is not None:
        print(f"  Tempo max: {_formatar_tempo(placar['tempo_max'])}")
    else:
        print(f"  Tempo max: N/A")
    print("=" * 40)


# ── Animacao de status ──────────────────────────────────────────────

_parar_animacao = threading.Event()
_thread_animacao = None


def _animar_thread(msg, stop_event):
    frames = [".  ", ".. ", "...", " ..", "  ."]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{msg} {frames[i % len(frames)]}  ")
        sys.stdout.flush()
        i += 1
        stop_event.wait(0.4)
    sys.stdout.write("\r" + " " * (len(msg) + 10) + "\r")
    sys.stdout.flush()


def iniciar_animacao(msg):
    global _thread_animacao
    parar_animacao()
    _parar_animacao.clear()
    _thread_animacao = threading.Thread(target=_animar_thread, args=(msg, _parar_animacao), daemon=True)
    _thread_animacao.start()


def parar_animacao():
    _parar_animacao.set()
    global _thread_animacao
    if _thread_animacao and _thread_animacao.is_alive():
        _thread_animacao.join(timeout=1)
    _thread_animacao = None


# ── Sistema de palavras hibrido ─────────────────────────────────────

def _carregar_palavras_base():
    if not ARQ_PALAVRAS_BASE.exists():
        return []
    with open(ARQ_PALAVRAS_BASE) as f:
        return [l.strip().upper() for l in f if l.strip() and _filtrar_palavra(l.strip())]


def _ler_cache_palavras():
    if not CACHE_ARQUIVO.exists():
        return []
    with open(CACHE_ARQUIVO) as f:
        linhas = f.read().splitlines()
    if not linhas or not linhas[0].startswith("#"):
        palavras = [l.strip().upper() for l in linhas if l.strip()]
        return [p for p in palavras if _filtrar_palavra(p)]
    palavras = []
    for l in linhas:
        if l.startswith("#"):
            continue
        if l.strip():
            palavras.append(l.strip().upper())
    return [p for p in palavras if _filtrar_palavra(p)]


def _salvar_cache(palavras):
    with open(CACHE_ARQUIVO, "w") as f:
        f.write(f"# atualizado: {time.time():.0f}\n")
        for p in palavras:
            f.write(p.upper() + "\n")


def _limpar_dicas_obsoletas():
    dicas = _ler_cache_dicas()
    if not dicas:
        return
    set_palavras = set(_palavras_atuais)
    limpas = {k: v for k, v in dicas.items() if k in set_palavras}
    removidas = len(dicas) - len(limpas)
    if removidas > 0:
        _log(f"Dicas obsoletas removidas: {removidas}")
        with open(DICA_CACHE, "w") as f:
            for k, v in limpas.items():
                f.write(f"{k}\t{v}\n")


def _atualizar_cache_bg():
    try:
        req = urllib.request.Request(URL_PALAVRAS, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            dados = resp.read().decode()
        linhas = dados.splitlines()
        novas = []
        for l in linhas:
            partes = l.strip().split()
            if partes:
                p = partes[0].upper()
                if _filtrar_palavra(p):
                    novas.append(p)
        if not novas:
            return
        atuais = _ler_cache_palavras()
        set_atual = set(atauais)
        candidatas = [p for p in novas if p not in set_atual]
        random.shuffle(candidatas)
        qtd_novas = max(1, len(atauais) // 4)
        escolhidas = candidatas[:qtd_novas]
        if atuais:
            remover_qtd = min(qtd_novas, len(atauais))
            random.shuffle(atauais)
            restantes = atuais[remover_qtd:]
        else:
            restantes = []
        resultado = restantes + escolhidas
        random.shuffle(resultado)
        _salvar_cache(resultado)
        _palavras_atuais[:] = resultado
        _limpar_dicas_obsoletas()
    except Exception:
        pass


def _baixar_lista_inicial():
    try:
        iniciar_animacao("Baixando lista de palavras")
        req = urllib.request.Request(URL_PALAVRAS, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            dados = resp.read().decode()
        linhas = dados.splitlines()
        novas = []
        for l in linhas:
            partes = l.strip().split()
            if partes:
                p = partes[0].upper()
                if _filtrar_palavra(p):
                    novas.append(p)
        if novas:
            random.shuffle(novas)
            _salvar_cache(novas[:500])
            _palavras_atuais[:] = novas[:500]
    except Exception:
        pass
    finally:
        parar_animacao()


def _ler_timestamp_cache():
    if not CACHE_ARQUIVO.exists():
        return None
    with open(CACHE_ARQUIVO) as f:
        first = f.readline().strip()
    if first.startswith("# atualizado:"):
        try:
            return float(first.split(":", 1)[1].strip())
        except (ValueError, IndexError):
            return None
    return None


def _iniciar_atualizacao_se_necessario():
    if not CACHE_ARQUIVO.exists():
        _baixar_lista_inicial()
        return
    ts = _ler_timestamp_cache()
    if ts is None or (time.time() - ts) > CACHE_IDADE_MAX:
        t = threading.Thread(target=_atualizar_cache_bg, daemon=True)
        t.start()


def buscar_palavra():
    global _palavras_atuais
    if not _palavras_atuais:
        base = _carregar_palavras_base()
        cache = _ler_cache_palavras()
        if cache:
            _palavras_atuais = cache
        else:
            _palavras_atuais = base
        _limpar_dicas_obsoletas()
        _iniciar_atualizacao_se_necessario()
    if not _palavras_atuais:
        _palavras_atuais = _carregar_palavras_base()
    return random.choice(_palavras_atuais)


# ── Dica via LLM com cache local e mirrors ─────────────────────────

DICA_CACHE = DIR_BASE / ".cache_dicas.txt"
_prefetch_parar = threading.Event()

PROMPT_DICA = "Dica curta sobre a palavra '{palavra}' em portugues do Brasil (pt-BR). Responda apenas em portugues brasileiro, sem revelar a palavra. Seja breve e direto."

MODELOS_POLLINATIONS = [
    "openai",
    "openai-fast",
    "mistral",
]

MODELOS_OPENROUTER = [
    "openai/gpt-oss-120b:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
]

DICAS_LOCAIS = {
    "CASA": "Um lugar onde moramos, com telhado e portas.",
    "MESA": "Mobilia com tampo plano e quatro pes, usada para comer.",
    "CADEIRA": "Assento com encosto e quatro pes.",
    "LIVRO": "Conjunto de paginas com texto, usado para ler.",
    "ESCOLA": "Lugar onde estudamos e aprendemos.",
    "CARRO": "Veiculo com quatro rodas que anda pela rua.",
    "MOTO": "Veiculo de duas rodas motorizado.",
    "AGUA": "Liquido transparente que todos precisam beber.",
    "SOL": "Estrela que brilha no ceu e aquece a terra.",
    "LUA": "Satelite natural da terra, brilha a noite.",
    "MAR": "Grande quantidade de agua salgada.",
    "RIO": "Corrente de agua que vai do alto ao mar.",
    "ARVORE": "Planta grande com tronco e folhas.",
    "FLOR": "Parte colorida das plantas.",
    "GATO": "Animal domestico que mia e caça ratos.",
    "CACHORRO": "Animal domestico mais fiel ao homem.",
    "PASSARO": "Animal com asas que voa pelo ceu.",
    "PEIXE": "Animal que vive na agua e nada.",
    "CAVALO": "Animal grande usado para montar e trabalhar.",
    "FRUTA": "Alimento doce que vem das arvores.",
    "BANANA": "Fruta amarela e doce em formato curvo.",
    "UVA": "Fruta pequena e roxa, usada para fazer vinho.",
    "LEITE": "Bebida branca vinda de animais.",
    "PAO": "Alimento feito com farinha e fermentado.",
    "ARROZ": "Graos brancos que comemos no dia a dia.",
    "FEIJAO": "Graos pequenos que fazemos no feijao.",
    "CAFE": "Bebida escura e amarga que nos acorda.",
    "CHA": "Bebida feita com plantas em agua quente.",
    "SUCO": "Bebida feita de frutas espremidas.",
    "SAL": "Tempero branco que usamos na comida.",
    "ACUCAR": "Tempero doce que adoça as bebidas.",
    "SALGADO": "Tempero com sabor de sal.",
    "DOCE": "Alimento com muito acucar e sabor bom.",
    "AMARGO": "Sabor oposto ao doce, desagradavel.",
    "AZEDO": "Sabor como limao ou vinagre.",
    "DOCENTE": "Relacionado a escola e ensino.",
    "ALUNO": "Pessoa que estuda em uma escola.",
    "PROFESSOR": "Pessoa que ensina na escola.",
    "MEDICO": "Profissional que cuida da saude.",
    "ENFERMEIRO": "Profissional que ajuda o medico.",
    "ADVOGADO": "Profissional que defende pessoas na justica.",
    "ENGENHEIRO": "Profissional que projeta construcoes.",
    "CANTOR": "Pessoa que canta musicas.",
    "ATOR": "Pessoa que atua em pecas ou filmes.",
    "DANCARINO": "Pessoa que dança profissionalmente.",
    "PINTOR": "Profissional que pinta quadros ou paredes.",
    "COZINHEIRO": "Profissional que prepara comida.",
    "RELOGIO": "Objeto que mostra a hora.",
    "CELULAR": "Aparelho telefonico portatil.",
    "COMPUTADOR": "Maquina eletronica para processar dados.",
    "INTERNET": "Rede mundial de computadores.",
    "JANELA": "Abertura na parede para entrar luz e ar.",
    "PORTA": "Abertura na parede para entrar e sair.",
    "PAREDE": "Estrutura vertical que divide ambientes.",
    "CHAO": "Superficie onde pisamos.",
    "TETO": "Parte superior que cobre o ambiente.",
    "ESPELHO": "Objeto que reflete nossa imagem.",
    "LAMPADA": "Objeto que ilumina o ambiente.",
    "VENTILADOR": "Aparelho que movimenta o ar.",
    "GELADEIRA": "Aparelho que mantem a comida fria.",
    "FOGAO": "Aparelho para cozinhar com fogo.",
    "MICROONDAS": "Aparelho que aquece comida rapidamente.",
    "LAVADORA": "Maquina que lava roupas.",
    "ASPIRADOR": "Aparelho que limpa o chao com sucao.",
    "CADEADO": "Trinco que tranca portas e cadeados.",
    "CHAVE": "Objeto que abre fechaduras.",
    "FECHADURA": "Mecanismo que trava portas.",
    "ESCRIANHO": "Mesa de trabalho com gavetas.",
    "LAPIZ": "Objeto de escrever e desenhar.",
    "CANETA": "Objeto de escrever com tinta.",
    "PAPEL": "Folha para escrever ou desenhar.",
    "BORRACHA": "Objeto para apagar erros de lapis.",
    "TESOURA": "Ferramenta com duas laminas para cortar.",
    "COLA": "Substancia para grudar materiais.",
    "FITA": "Largura estreita de material adesivo.",
    "SACOLA": "Saco para carregar compras.",
    "MALA": "Caixa grande para viajar.",
    "BOLSA": "Saco pequeno para carregar coisas.",
    "CARTEIRA": "Bolsa pequena para documentos e dinheiro.",
    "CINTO": "Tira de couro ou tecido para segurar calcas.",
    "CHAPEU": "Acessorio para cobrir a cabeca.",
    "OCULOS": "Acessorio para enxergar melhor.",
    "SAPATO": "Calçado para proteger os pes.",
    "SANDALIA": "Calçado aberto para o verao.",
    "MEIAS": "Tecido que cobre os pes dentro do sapato.",
    "CAMISA": "Roupa de cima com botoes.",
    "CALCA": "Roupa que cobre as pernas.",
    "VESTIDO": "Roupa longa para mulheres.",
    "SAIA": "Roupa que cobre apenas as pernas.",
    "JAQUETA": "Roupa quente para o frio.",
    "AGASALHO": "Roupa para se aquecer.",
    "PIJAMA": "Roupa para dormir.",
    "BANHO": "Roupa para ir a praia ou piscina.",
    "TOALHA": "Tecido para secar o corpo.",
    "COBERTOR": "Roupa de cama para se aquecer.",
    "TRAVESSEIRO": "Almofada para apoiar a cabeca na cama.",
    "COLCHAO": "Objeto mole onde dormimos.",
    "CAMA": "Move onde dormimos.",
    "ARMARIO": "Move para guardar roupas.",
    "GAVETA": "Compartimento dentro de um armario.",
    "ESTANTE": "Move para guardar livros.",
    "POLTRONA": "Assento estofado e confortavel.",
    "SOFA": "Assento comprido para varias pessoas.",
    "TAPETE": "Tecido que cobre o chao.",
    "PERFUME": "Liquido com cheiro bom para o corpo.",
    "SABONETE": "Produto para limpar o corpo.",
    "ESCOVA": "Ferramenta com cerdas para limpar.",
    "PENTE": "Ferramenta para arrumar o cabelo.",
    "ESPONJA": "Material poroso para limpar.",
    "DETERGENTE": "Produto para lavar louça.",
    "AMACIANTE": "Produto para amaciar roupas.",
    "INSETICIDA": "Produto para matar insetos.",
    "REMEDIO": "Produto para tratar doencas.",
    "VITAMINA": "Substancia para fortalecer o corpo.",
    "VACINA": "Medicamento para prevenir doencas.",
    "SERINGA": "Aparelho para injetar medicamentos.",
    "BANDAID": "Curativo para ferimentos pequenos.",
    "TERMOMETRO": "Aparelho para medir temperatura.",
    "ESTETOSCOPIO": "Aparelho que o medico usa para ouvir o coracao.",
    "AMBULANCIA": "Veiculo para transportar doentes.",
    "HOSPITAL": "Lugar onde tratam doencas.",
    "FARMACIA": "Lugar que vende remedios.",
    "IGREJA": "Templo de culto religioso.",
    "MUSEU": "Lugar com obras de arte e historia.",
    "BIBLIOTECA": "Lugar com muitos livros para emprestar.",
    "BANCO": "Instituicao financeira para guardar dinheiro.",
    "MERCADO": "Lugar para comprar comida e produtos.",
    "LOJA": "Lugar para comprar variedades de coisas.",
    "FEIRA": "Mercado ao ar livre com vendedores.",
    "RESTAURANTE": "Lugar para comer refeicoes prontas.",
    "LANCHONETE": "Lugar para lanches e refrigerantes.",
    "BAR": "Lugar para beber e socializar.",
    "HOTEL": "Lugar para hospedagem de viajantes.",
    "AEROPORTO": "Lugar onde avioes decolam e pousam.",
    "ESTACAO": "Lugar onde trens param.",
    "PORTO": "Lugar onde navios atracam.",
    "PONTE": "Estrutura que cruza rios ou vales.",
    "TUNEL": "Passagem subterranea.",
    "CASTELO": "Fortaleza antiga de reis.",
    "PRISAO": "Lugar onde ficam presos.",
    "QUARTEL": "Lugar onde soldados moram.",
    "TRIBUNAL": "Lugar onde julgam crimes.",
    "PREFEITURA": "Edificio do governo da cidade.",
    "UNIVERSIDADE": "Instituicao de ensino superior.",
    "FABRICA": "Lugar onde produzem produtos.",
    "OFICINA": "Lugar onde consertam maquinas.",
    "CAMPO": "Area aberta para plantar ou pastar.",
    "FLORESTA": "Grande quantidade de arvores.",
    "MONTANHA": "Elevacao grande da terra.",
    "COLINA": "Elevacao suave da terra.",
    "DESERTO": "Area seca e arenosa.",
    "PRAIA": "Area de areia junto ao mar.",
    "ILHA": "Terra cercada por agua.",
    "VULCAO": "Montanha que pode eruptar lava.",
    "TERREMOTO": "Abalo na terra que causa destruicao.",
    "SECA": "Falta de agua por muito tempo.",
    "NEVE": "Cristais de gelo que caem do ceu.",
    "CHUVA": "Agua que cai das nuvens.",
    "TROVOADA": "Fenomeno com relampagos e trovoes.",
    "NUVEM": "Massa de vapor dagua no ceu.",
    "VENTO": "Ar em movimento.",
    "FOGO": "Reacao quimica que gera calor e luz.",
    "RAIO": "Descarga eletrica durante tempestades.",
    "SOMBRA": "Area escura formada por bloqueio de luz.",
    "LUZ": "Claridade que permite enxergar.",
    "ESCURO": "Falta de luz.",
    "CLARO": "Com muita luz.",
    "QUENTE": "Temperatura alta.",
    "FRIO": "Temperatura baixa.",
    "MORNO": "Temperatura media agradavel.",
    "SECO": "Sem agua ou umidade.",
    "UMIDO": "Com umidade.",
    "DURO": "Dificil de quebrar ou cortar.",
    "MOLE": "Facil de comprimir.",
    "REDONDO": "Formato circular.",
    "QUADRADO": "Formato com quatro lados iguais.",
    "TRIANGULAR": "Formato com tres lados.",
    "RETO": "Em linha reta.",
    "CURVO": "Em formato de curva.",
    "ALTO": "Grande estatura ou altura.",
    "BAIXO": "Pequena estatura ou altura.",
    "GRANDE": "De tamanho consideravel.",
    "PEQUENO": "De tamanho reduzido.",
    "NOVO": "Que nao existe ha muito tempo.",
    "VELHO": "Que existe ha muito tempo.",
    "BONITO": "Agradavel de ver.",
    "FEIO": "Desagradavel de ver.",
    "FORTE": "Com muita força.",
    "FRACO": "Sem muita força.",
    "RAPIDO": "Que se move com velocidade.",
    "DEVAGAR": "Que se move sem pressa.",
    "FACIL": "Que nao exige dificuldade.",
    "DIFICIL": "Que exige muita esforco.",
    "LIMPO": "Sem sujeira.",
    "SUJO": "Com sujeira.",
    "CHEIO": "Sem espaco vazio.",
    "VAZIO": "Sem nada dentro.",
    "CERTO": "Correto ou verdadeiro.",
    "ERRADO": "Incorreto ou falso.",
    "VERDADE": "Algo que e real.",
    "MENTIRA": "Algo falso dito como verdade.",
    "AMOR": "Sentimento forte de afeto.",
    "ODIO": "Sentimento forte de aversao.",
    "ALEGRIA": "Sentimento de felicidade.",
    "TRISTEZA": "Sentimento de pesar.",
    "MEDO": "Sentimento de terror.",
    "CORAGEM": "Sentimento de bravura.",
    "PACIENCIA": "Capacidade de esperar.",
    "SABEDORIA": "Conhecimento e bom juizo.",
    "BELEZA": "Qualidade de ser bonito.",
    "SUCESSO": "Algo que foi alcancado.",
    "FRACASSO": "Algo que nao deu certo.",
    "TRABALHO": "Atividade para ganhar dinheiro.",
    "DINHEIRO": "Moeda usada para comprar.",
    "PRESENTE": "Coisa dada de graca.",
    "FUTURO": "O que ainda vai acontecer.",
    "PASSADO": "O que ja aconteceu.",
    "HOJE": "O dia atual.",
    "ONTEM": "O dia anterior.",
    "AMANHA": "O proximo dia.",
    "SEMPRE": "Em todos os momentos.",
    "NUNCA": "Em nenhum momento.",
    "MUITO": "Em grande quantidade.",
    "POUCO": "Em pequena quantidade.",
    "TUDO": "A totalidade das coisas.",
    "NADA": "Ausencia total de coisas.",
    "ALGO": "Uma coisa qualquer.",
    "CADA": "Um por um, todos.",
    "OUTRO": "Diferente deste.",
    "MESMO": "Identico ou igual.",
    "TODOS": "Todos juntos.",
    "NENHUM": "Nao existe nenhum.",
    "ALGUM": "Existe pelo menos um.",
}


def _ler_cache_dicas():
    if not DICA_CACHE.exists():
        return {}
    dicas = {}
    with open(DICA_CACHE) as f:
        for l in f:
            l = l.strip()
            if "\t" in l:
                k, v = l.split("\t", 1)
                dicas[k.upper()] = v
    return dicas


def _salvar_dica(palavra, dica):
    with open(DICA_CACHE, "a") as f:
        f.write(f"{palavra.upper()}\t{dica}\n")


def _ler_config():
    if not ARQ_CONFIG.exists():
        return {}
    config = {}
    with open(ARQ_CONFIG) as f:
        for l in f:
            l = l.strip()
            if "=" in l and not l.startswith("#"):
                k, v = l.split("=", 1)
                config[k.strip()] = v.strip()
    return config


def _salvar_config(config):
    with open(ARQ_CONFIG, "w") as f:
        f.write("# Configuracao do Jogo da Forca\n")
        f.write("# Chave de API do OpenRouter (gratuita)\n")
        for k, v in config.items():
            f.write(f"{k}={v}\n")


def _buscar_dica_openrouter(palavra, api_key, modelo=None):
    if not modelo:
        modelo = MODELOS_OPENROUTER[0]
    prompt = PROMPT_DICA.format(palavra=palavra)
    url = "https://openrouter.ai/api/v1/chat/completions"
    data = json.dumps({
        "model": modelo,
        "messages": [
            {"role": "system", "content": "Responda APENAS em portugues brasileiro. Nao mostre raciocinio, pensamentos ou explicacoes. Retorne SOMENTE a dica curta solicitada."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100,
        "reasoning": {"enabled": False}
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/jogodaforca",
        "X-Title": "Jogo da Forca",
        "User-Agent": "Mozilla/5.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            response = json.loads(f.read().decode())
        resultado = response["choices"][0]["message"]["content"].strip()
        _log(f"OpenRouter OK | modelo={modelo} | palavra={palavra}")
        return resultado
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:200]
        except Exception:
            pass
        erro = f"OpenRouter ERRO {e.code} | modelo={modelo} | palavra={palavra} | {e.reason} | {body}"
        _log(erro)
        raise
    except Exception as e:
        erro = f"OpenRouter FALHA | modelo={modelo} | palavra={palavra} | {type(e).__name__}: {e}"
        _log(erro)
        raise


def _buscar_dica_pollinations(palavra, modelo=None):
    if not modelo:
        modelo = "openai"
    prompt = PROMPT_DICA.format(palavra=palavra)
    url = "https://text.pollinations.ai/" + urllib.parse.quote(prompt) + f"?model={modelo}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            resultado = f.read().decode().strip()
        _log(f"Pollinations OK | modelo={modelo} | palavra={palavra}")
        return resultado
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:200]
        except Exception:
            pass
        erro = f"Pollinations ERRO {e.code} | modelo={modelo} | palavra={palavra} | {e.reason} | {body}"
        _log(erro)
        raise
    except Exception as e:
        erro = f"Pollinations FALHA | modelo={modelo} | palavra={palavra} | {type(e).__name__}: {e}"
        _log(erro)
        raise


def _buscar_dica_local(palavra):
    resultado = DICAS_LOCAIS.get(palavra.upper())
    if resultado:
        _log(f"Local OK | palavra={palavra}")
    else:
        _log(f"Local MISS | palavra={palavra} (sem dica no dicionario)")
    return resultado


def gerar_dica(palavra):
    dicas = _ler_cache_dicas()
    if palavra.upper() in dicas:
        _log(f"Cache HIT | palavra={palavra}")
        return dicas[palavra.upper()]
    
    _log(f"Inicio busca dica | palavra={palavra}")
    config = _ler_config()
    api_key = config.get("OPENROUTER_API_KEY")
    
    if api_key:
        for modelo in MODELOS_OPENROUTER:
            try:
                iniciar_animacao(f"Gerando dica (OpenRouter)")
                resultado = _buscar_dica_openrouter(palavra, api_key, modelo)
                _salvar_dica(palavra, resultado)
                return resultado
            except Exception:
                time.sleep(2)
            finally:
                parar_animacao()
    
    for modelo in MODELOS_POLLINATIONS:
        try:
            iniciar_animacao(f"Gerando dica (Pollinations)")
            resultado = _buscar_dica_pollinations(palavra, modelo)
            _salvar_dica(palavra, resultado)
            return resultado
        except Exception:
            time.sleep(2)
        finally:
            parar_animacao()
    
    local = _buscar_dica_local(palavra)
    if local:
        _salvar_dica(palavra, local)
        return local
    
    _log(f"FALHA TOTAL | palavra={palavra} (todos os mirrors falharam)")
    return None


def _prefetch_dicas_bg():
    _log("Prefetch iniciado")
    while not _prefetch_parar.is_set():
        palavras = list(_palavras_atuais)
        if not palavras:
            _prefetch_parar.wait(5)
            continue
        dicas = _ler_cache_dicas()
        pendentes = [p for p in palavras if p.upper() not in dicas]
        if not pendentes:
            _prefetch_parar.wait(30)
            continue
        random.shuffle(pendentes)
        total = len(pendentes)
        _log(f"Prefetch: {total} dicas pendentes")
        
        config = _ler_config()
        api_key = config.get("OPENROUTER_API_KEY")
        
        for i, palavra in enumerate(pendentes):
            if _prefetch_parar.is_set():
                _log("Prefetch interrompido")
                return
            
            if api_key:
                for modelo in MODELOS_OPENROUTER:
                    try:
                        resultado = _buscar_dica_openrouter(palavra, api_key, modelo)
                        _salvar_dica(palavra, resultado)
                        break
                    except Exception:
                        pass
            
            if _ler_cache_dicas().get(palavra.upper()) is None:
                for modelo in MODELOS_POLLINATIONS:
                    try:
                        resultado = _buscar_dica_pollinations(palavra, modelo)
                        _salvar_dica(palavra, resultado)
                        break
                    except urllib.error.HTTPError as e:
                        if e.code == 429:
                            _prefetch_parar.wait(15)
                            break
                    except Exception:
                        pass
            
            if _ler_cache_dicas().get(palavra.upper()) is None:
                local = _buscar_dica_local(palavra)
                if local:
                    _salvar_dica(palavra, local)
            
            if i < total - 1:
                _prefetch_parar.wait(10)


# ── Interface do jogo ───────────────────────────────────────────────

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_instrucoes_api_key():
    limpar_tela()
    print("=" * 50)
    print("   CONFIGURACAO OPCIONAL - MELHORES DICAS")
    print("=" * 50)
    print()
    print("Para dicas melhores, voce pode criar uma chave de API gratuita.")
    print("Eh rapido, gratuito e nao precisa de cartao de credito!")
    print()
    print("PASSO 1: Abra o navegador e va para:")
    print("         https://openrouter.ai")
    print()
    print("PASSO 2: Clique em 'Sign Up' (canto superior direito)")
    print("         - Voce pode usar Google ou GitHub para criar conta")
    print()
    print("PASSO 3: Apos entrar, clique no seu nome (canto superior)")
    print("         e va em 'Keys'")
    print()
    print("PASSO 4: Clique em 'Create Key' e copie a chave")
    print("         (comeca com sk-or-v1-...)")
    print()
    print("PASSO 5: Cole a chave abaixo quando pedido")
    print()
    print("Se nao quiser configurar, aperte ENTER e o jogo")
    print("continuara funcionando normalmente!")
    print()
    print("=" * 50)
    print()


def configurar_api_key():
    config = _ler_config()
    if config.get("OPENROUTER_API_KEY"):
        return True
    
    mostrar_instrucoes_api_key()
    
    while True:
        chave = input("Cole sua chave de API (ou ENTER para pular): ").strip()
        if not chave:
            print("OK! O jogo funcionara com dicas basicas.")
            time.sleep(2)
            return False
        if chave.startswith("sk-or-"):
            config["OPENROUTER_API_KEY"] = chave
            _salvar_config(config)
            print("Chave configurada com sucesso!")
            time.sleep(2)
            return True
        print("Chave invalida! Deve comecar com sk-or-v1-")
        print("Tente novamente ou aperte ENTER para pular.")


def mostrar_status(erros, progresso, letras_erradas, dica=None):
    limpar_tela()
    print("=" * 40)
    print("           JOGO DA FORCA")
    print("=" * 40)
    print(FORCAS[min(erros, MAX_ERROS)])
    if dica:
        print(f"DICA: {dica}")
    print(f"\n{' '.join(progresso)}")
    print(f"\nLetras erradas: {' '.join(letras_erradas)}")
    print(f"Erros: {erros}/{MAX_ERROS}")


def jogar():
    _log("=== NOVO JOGO INICIADO ===")
    _prefetch_parar.clear()
    t_prefetch = threading.Thread(target=_prefetch_dicas_bg, daemon=True)
    t_prefetch.start()

    iniciar_animacao("Buscando palavra")
    try:
        palavra = buscar_palavra()
    finally:
        parar_animacao()

    _log(f"Palavra sorteada: {palavra} ({len(palavra)} letras)")
    dica = gerar_dica(palavra)
    if dica is None:
        dica = "(dica indisponivel — sem conexao com a nuvem)"

    erros = 0
    letras_adivinhadas = set()
    letras_erradas = []
    progresso = ['_'] * len(palavra)
    inicio = time.time()

    while erros < MAX_ERROS and '_' in progresso:
        mostrar_status(erros, progresso, letras_erradas, dica)

        tentativa = input("\nDigite uma letra: ").strip().upper()

        if len(tentativa) != 1 or not tentativa.isalpha():
            print("Entrada invalida! Digite apenas uma letra.")
            input("Pressione ENTER para continuar...")
            continue

        if tentativa in letras_adivinhadas:
            print("Voce ja tentou essa letra!")
            input("Pressione ENTER para continuar...")
            continue

        letras_adivinhadas.add(tentativa)

        if tentativa in palavra:
            for i, letra in enumerate(palavra):
                if letra == tentativa:
                    progresso[i] = letra
        else:
            erros += 1
            letras_erradas.append(tentativa)

    tempo = time.time() - inicio
    venceu = '_' not in progresso
    mostrar_status(erros, progresso, letras_erradas, dica)

    if venceu:
        print(f"\nPARABENS! Voce venceu! Tempo: {_formatar_tempo(tempo)}")
        _log(f"Resultado: VITORIA | palavra={palavra} | erros={erros} | tempo={tempo:.1f}s")
    else:
        print(f"\nENFORCADO! A palavra era: {palavra} | Tempo: {_formatar_tempo(tempo)}")
        _log(f"Resultado: DERROTA | palavra={palavra} | erros={erros} | tempo={tempo:.1f}s")

    placar = _atualizar_placar(venceu, tempo)
    _mostrar_placar(placar)

    print("\nObrigado por jogar!")
    _prefetch_parar.set()

    resp = input("\nDeseja jogar novamente? (s/n): ").strip().lower()
    return resp in ("s", "sim", "y", "yes")


if __name__ == "__main__":
    configurar_api_key()
    while jogar():
        limpar_tela()
