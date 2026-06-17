"""
Módulo de constantes globais do jogo LateShift.
Contém todas as configurações e parâmetros compartilhados entre os módulos.
"""

# === Configurações de tela ===
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Tamanho do "pixel" para estética pixel art
PIXEL_SIZE = 3

# === Divisão da tela ===
TRACK_HEIGHT = 400
DASHBOARD_Y = TRACK_HEIGHT
DASHBOARD_HEIGHT = SCREEN_HEIGHT - TRACK_HEIGHT

# === Distância da corrida (em unidades do jogo) ===
RACE_DISTANCE = 1500.0

# === Estados do Jogo (Substituindo Enums por strings simples) ===
STATE_MAIN_MENU = "MAIN_MENU"
STATE_CAR_SELECT = "CAR_SELECT"
STATE_STAGE_SELECT = "STAGE_SELECT"
STATE_COUNTDOWN = "COUNTDOWN"
STATE_RACING = "RACING"
STATE_WIN = "WIN"
STATE_LOSE = "LOSE"

# === Marchas do Câmbio H-Pattern (Substituindo Enums por inteiros) ===
GEAR_NEUTRAL = 0
GEAR_FIRST = 1
GEAR_SECOND = 2
GEAR_THIRD = 3
GEAR_FOURTH = 4
GEAR_FIFTH = 5
GEAR_SIXTH = 6
GEAR_REVERSE = -1

# === Tipos de Carros (Substituindo Enums por strings) ===
CAR_BALANCED = "BALANCED"
CAR_HIGH_ACCEL = "HIGH_ACCEL"
CAR_TOP_SPEED = "TOP_SPEED"

# ========== PALETA DE CORES (pixel art) ==========
BLACK = (10, 10, 18)
WHITE = (240, 240, 235)
DARK_BG = (15, 15, 25)

# Cores neon de destaque
NEON_RED = (255, 60, 60)
NEON_GREEN = (60, 255, 120)
NEON_BLUE = (60, 120, 255)
NEON_ORANGE = (255, 165, 50)
NEON_YELLOW = (255, 230, 50)
NEON_CYAN = (50, 230, 255)
NEON_PINK = (255, 80, 180)
NEON_PURPLE = (180, 80, 255)

# Cores do dashboard
DASHBOARD_BG = (20, 20, 35)
DASHBOARD_BORDER = (50, 50, 80)
GAUGE_BG = (12, 12, 22)
GAUGE_RING = (60, 60, 90)
GAUGE_TEXT = (200, 200, 210)

# Cores por marcha (para indicadores visuais)
GEAR_COLORS = {
    GEAR_NEUTRAL: (120, 120, 140),
    GEAR_FIRST: (60, 255, 120),
    GEAR_SECOND: (180, 255, 50),
    GEAR_THIRD: (255, 230, 50),
    GEAR_FOURTH: (255, 165, 50),
    GEAR_FIFTH: (255, 100, 50),
    GEAR_SIXTH: (255, 60, 60),
    GEAR_REVERSE: (180, 80, 255),
}

# Cores dos pedais
PEDAL_IDLE = (50, 50, 70)
PEDAL_GAS_ACTIVE = (60, 220, 100)
PEDAL_CLUTCH_ACTIVE = (60, 140, 255)

# Tons de cinza
GRAY_LIGHT = (160, 160, 170)
GRAY_MED = (100, 100, 115)
GRAY_DARK = (50, 50, 65)

# ========== CONFIGURAÇÃO DOS CARROS ==========
CAR_CONFIGS = {
    CAR_BALANCED: {
        "name": "Skyline GT-R R34",
        "desc": "Equilibrado",
        "description": "Velocidade Média | Aceleração Média",
        "top_speed": 250.0,
        "acceleration": 1.0,
        "torque": 1.0,
        "body_color": (40, 120, 255),
        "accent_color": (80, 160, 255),
        "window_color": (100, 180, 255),
    },
    CAR_HIGH_ACCEL: {
        "name": "Dodge Charger 1970",
        "desc": "Arrancada Rápida",
        "description": "Alta Aceleração | Menor Velocidade Final",
        "top_speed": 200.0,
        "acceleration": 1.35,
        "torque": 1.25,
        "body_color": (255, 130, 30),
        "accent_color": (255, 180, 60),
        "window_color": (255, 210, 140),
    },
    CAR_TOP_SPEED: {
        "name": "Ferrari F40",
        "desc": "Top Speed",
        "description": "Baixa Aceleração | Alta Velocidade Final",
        "top_speed": 310.0,
        "acceleration": 0.72,
        "torque": 0.82,
        "body_color": (220, 40, 100),
        "accent_color": (255, 80, 140),
        "window_color": (255, 150, 190),
    },
}

# ========== FÍSICA ==========
RPM_IDLE = 800.0
RPM_REDLINE = 6000.0
RPM_MAX = 7000.0
RPM_EXPLODE_TIME = 2.0  # Segundos no redline antes do motor explodir

# Relação de transmissão por marcha
GEAR_RATIOS = {
    GEAR_NEUTRAL: 0.0,
    GEAR_FIRST: 3.50,
    GEAR_SECOND: 2.33,
    GEAR_THIRD: 1.67,
    GEAR_FOURTH: 1.25,
    GEAR_FIFTH: 0.98,
    GEAR_SIXTH: 0.80,
    GEAR_REVERSE: 3.0,
}

# Fração da velocidade máxima atingível em cada marcha
GEAR_SPEED_LIMITS = {
    GEAR_NEUTRAL: 0.0,
    GEAR_FIRST: 0.19,
    GEAR_SECOND: 0.36,
    GEAR_THIRD: 0.52,
    GEAR_FOURTH: 0.69,
    GEAR_FIFTH: 0.86,
    GEAR_SIXTH: 1.0,
    GEAR_REVERSE: 0.15,
}

# ========== H-PATTERN ==========
# Posições do knob no diagrama H (coordenadas relativas em grade)
# Layout: R(-3,-1) 1(-1,-1) 3(1,-1) 5(3,-1)
#         Neutro(0,0) na barra central
#                2(-1,1)  4(1,1)  6(3,1)
H_PATTERN_POSITIONS = {
    GEAR_NEUTRAL: (1, 0),
    GEAR_REVERSE: (-3, -1),
    GEAR_FIRST:   (-1, -1),
    GEAR_SECOND:  (-1, 1),
    GEAR_THIRD:   (1, -1),
    GEAR_FOURTH:  (1, 1),
    GEAR_FIFTH:   (3, -1),
    GEAR_SIXTH:   (3, 1),
}

# Caminho visual de uma marcha para a próxima (pontos intermediários do knob)
H_PATTERN_PATHS = {
    (GEAR_NEUTRAL, GEAR_FIRST):   [(-1, 0), (-1, -1)],
    (GEAR_FIRST, GEAR_SECOND):    [(-1, 0), (-1, 1)],
    (GEAR_SECOND, GEAR_THIRD):    [(-1, 0), (1, 0), (1, -1)],
    (GEAR_THIRD, GEAR_FOURTH):    [(1, 0), (1, 1)],
    (GEAR_FOURTH, GEAR_FIFTH):    [(1, 0), (3, 0), (3, -1)],
    (GEAR_FIFTH, GEAR_SIXTH):     [(3, 0), (3, 1)],
    (GEAR_NEUTRAL, GEAR_REVERSE): [(-1, 0), (-3, 0), (-3, -1)],
}

# Mapa de adjacência do knob na grade física do câmbio.
# Cada posição define quais direções de seta são válidas e para onde levam.
KNOB_ADJACENCY = {
    # Posições das marchas (linha superior — só desce para a barra)
    (-3, -1): {"DOWN": (-3, 0)},
    (-1, -1): {"DOWN": (-1, 0)},
    (1, -1):  {"DOWN": (1, 0)},
    (3, -1):  {"DOWN": (3, 0)},
    # Posições das marchas (linha inferior — só sobe para a barra)
    (-1, 1):  {"UP": (-1, 0)},
    (1, 1):   {"UP": (1, 0)},
    (3, 1):   {"UP": (3, 0)},
    # Posições na barra horizontal (crossbar / neutro)
    # Nota: não existe nó (0,0) — a barra vai direto de (-1,0) para (1,0)
    (-3, 0):  {"UP": (-3, -1), "RIGHT": (-1, 0)},
    (-1, 0):  {"UP": (-1, -1), "DOWN": (-1, 1), "LEFT": (-3, 0), "RIGHT": (1, 0)},
    (1, 0):   {"UP": (1, -1), "DOWN": (1, 1), "LEFT": (-1, 0), "RIGHT": (3, 0)},
    (3, 0):   {"UP": (3, -1), "DOWN": (3, 1), "LEFT": (1, 0)},
}

# Mapa de posição do knob para a marcha correspondente.
KNOB_GEAR_MAP = {
    (-3, -1): GEAR_REVERSE,
    (-1, -1): GEAR_FIRST,
    (-1, 1):  GEAR_SECOND,
    (1, -1):  GEAR_THIRD,
    (1, 1):   GEAR_FOURTH,
    (3, -1):  GEAR_FIFTH,
    (3, 1):   GEAR_SIXTH,
    (-3, 0):  GEAR_NEUTRAL,
    (-1, 0):  GEAR_NEUTRAL,
    (1, 0):   GEAR_NEUTRAL,
    (3, 0):   GEAR_NEUTRAL,
}

# Dica textual da próxima marcha (teclas que o jogador deve pressionar)
NEXT_GEAR_HINTS = {
    GEAR_NEUTRAL: (GEAR_FIRST, "<- ^"),
    GEAR_FIRST:   (GEAR_SECOND, "v v"),
    GEAR_SECOND:  (GEAR_THIRD, "^ -> ^"),
    GEAR_THIRD:   (GEAR_FOURTH, "v v"),
    GEAR_FOURTH:  (GEAR_FIFTH, "^ -> ^"),
    GEAR_FIFTH:   (GEAR_SIXTH, "v v"),
    GEAR_SIXTH:   (None, "MAX"),
    GEAR_REVERSE: (None, "REV"),
}

# ========== FASES ==========
STAGE_CONFIGS = [
    {
        "name": "Silicon Expressway",
        "desc": "Via expressa da cidade",
        "ai_multiplier": 0.6,
        "ai_car_type": CAR_HIGH_ACCEL,
        "distance": 2000.0,
        "sky_top": (80, 40, 120),
        "sky_bottom": (255, 140, 60),
        "ground_color": (60, 60, 70),
        "road_color": (45, 45, 55),
        "road_line": (200, 200, 180)
    },
    {
        "name": "Industrial Dawn",
        "desc": "Ruas da zona industrial",
        "ai_multiplier": 0.7,
        "ai_car_type": CAR_HIGH_ACCEL,
        "distance": 2200.0,
        "sky_top": (100, 160, 220),
        "sky_bottom": (200, 180, 140),
        "ground_color": (180, 150, 100),
        "road_color": (70, 60, 50),
        "road_line": (220, 200, 160)
    },
    {
        "name": "Outrun Boulevard",
        "desc": "Cartão-postal mais bonito da cidade",
        "ai_multiplier": 0.7,
        "ai_car_type": CAR_BALANCED,
        "distance": 2400.0,
        "sky_top": (60, 120, 180),
        "sky_bottom": (140, 200, 160),
        "ground_color": (60, 100, 50),
        "road_color": (50, 50, 45),
        "road_line": (200, 200, 180)
    },
    {
        "name": "Shaded Metropolis",
        "desc": "Sombras dos imensos arranha-céus corporativos.",
        "ai_multiplier": 0.75,
        "ai_car_type": CAR_BALANCED,
        "distance": 2600.0,
        "sky_top": (10, 10, 30),
        "sky_bottom": (20, 20, 50),
        "ground_color": (30, 30, 45),
        "road_color": (35, 35, 50),
        "road_line": (150, 150, 170)
    },
    {
        "name": "Cyber Sunset",
        "desc": "O céu mais vibrante da cidade alta",
        "ai_multiplier": 0.8,
        "ai_car_type": CAR_TOP_SPEED,
        "distance": 2800.0,
        "sky_top": (80, 180, 240),
        "sky_bottom": (160, 220, 240),
        "ground_color": (200, 180, 140),
        "road_color": (55, 55, 60),
        "road_line": (220, 220, 200)
    },
    {
        "name": "Midnight Club",
        "desc": "Corrida de rua ilegal na rota Bayshore",
        "ai_multiplier": 0.85,
        "ai_car_type": CAR_TOP_SPEED,
        "distance": 3000.0,
        "sky_top": (15, 5, 30),
        "sky_bottom": (40, 10, 60),
        "ground_color": (25, 15, 40),
        "road_color": (30, 20, 45),
        "road_line": (180, 60, 255)
    },
]

# === Configuração de áudio ===
SAMPLE_RATE = 22050
