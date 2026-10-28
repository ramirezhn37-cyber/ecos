import json
import math
import random
import array
import shutil
import os
import sys
from pathlib import Path

import pygame

from fondos import FondoSubmarino

# ============================================================
# CONSTANTES
# ============================================================
ANCHO, ALTO = 800, 600
MAX_MUNDO = 3400  # ancho máximo para generar el fondo

GRAVEDAD = 1500.0
VELOCIDAD = 300.0
FUERZA_SALTO = -600.
COYOTE_TIME = 0.12
JUMP_BUFFER_TIME = 0.12
JUMP_CUT = 0.45

PERSONAJE_ANCHO = 56
PERSONAJE_ALTO = 77
RADIO_ECO = 11
VIDA_MAX = 3
INVUL_TIEMPO = 1.6

AZUL_NEON = (46, 224, 255)
BLANCO_AZUL = (224, 244, 255)
VERDE_ECO = (90, 255, 190)
ROJO_DANO = (255, 90, 110)

try:
    import android  # noqa: F401
    _ANDROID = True
except Exception:
    _ANDROID = os.environ.get("ANDROID_ARGUMENT") is not None or sys.platform.startswith("android")
RUTA_GUARDADO = Path(__file__).resolve().parent / "partida.json"
RUTA_BACKUP = Path(__file__).resolve().parent / "partida.bak.json"

# ============================================================
# INICIALIZACIÓN
# ============================================================
pygame.init()
flags = 0
if _ANDROID:
    flags = pygame.SCALED | pygame.FULLSCREEN
pantalla = pygame.display.set_mode((ANCHO, ALTO), flags)
pygame.display.set_caption("Ecos de la Memoria")
reloj = pygame.time.Clock()

fuente = pygame.font.SysFont("Arial", 17)
fuente_titulo = pygame.font.SysFont("Arial", 28, bold=True)
fuente_hud = pygame.font.SysFont("Arial", 21, bold=True)
fuente_pequena = pygame.font.SysFont("Arial", 14)

# ============================================================
# DATOS DE NIVELES (5 niveles)
# ============================================================
NIVELES = [
    {  # --- Nivel 1: El Barrio Anegado ---
        "nombre": "I · El Barrio Anegado",
        "ancho": 2400,
        "inicio": (40.0, 423.0),
        "plataformas": [
            pygame.Rect(0, 500, 240, 100),
            pygame.Rect(300, 450, 170, 24),
            pygame.Rect(530, 410, 170, 24),
            pygame.Rect(760, 455, 165, 24),
            pygame.Rect(985, 415, 175, 24),
            pygame.Rect(1215, 460, 180, 24),
            pygame.Rect(1455, 420, 170, 24),
            pygame.Rect(1690, 465, 160, 24),
            pygame.Rect(1905, 500, 495, 100),
        ],
        "ecos": ((120, 500), (385, 450), (615, 410), (842, 455), (1072, 415)),
        "zombies": ((150, 500, 80, "errante"), (620, 410, 60, "errante"),
                    (1300, 460, 70, "corrupto")),
        "vel_zombie": 55.0,
        "npcs": [
            {
                "x": 150, "y": 500, "sprite": "adventurer",
                "nombre": "Tomás · Archivista", "color": (255, 200, 120),
                "lineas": [
                    ("Tomás", (255, 200, 120),
                     "¿Otro caminante entre ruinas? Yo soy Tomás, archivista de este barrio."),
                    ("Tomás", (255, 200, 120),
                     "La inundación se llevó las voces, pero los ecos quedaron grabados en la piedra."),
                    ("Kael", AZUL_NEON,
                     "Entonces los recogeré todos. Cada voz importa."),
                    ("Tomás", (255, 200, 120),
                     "Cuidado con las sombras: son recuerdos que el agua corrompió. Repiten su dolor y no piensan."),
                    ("Tomás", (255, 200, 120),
                     "Salta sobre ellas para dispersarlas. Sus saltos son torpes, pero letales."),
                    ("Tomás", (255, 200, 120),
                     "Recupera los fragmentos y el ascensor del fondo te llevará más abajo."),
                ],
            },
            {
                "x": 1975, "y": 500, "sprite": "female",
                "nombre": "Vera · Niña de Papel", "color": (255, 160, 200),
                "lineas": [
                    ("Vera", (255, 160, 200),
                     "Shhh. Si haces ruido, las sombras corriendo vendrán a por ti."),
                    ("Kael", AZUL_NEON, "¿Corren? Las he oído arrastrándose."),
                    ("Vera", (255, 160, 200),
                     "Corren. Pero trotan. Es mejor que las congeladas, esas no se cansan nunca."),
                    ("Vera", (255, 160, 200),
                     "Yo contaré los Ecos para ti. Cinco, ¿verdad? Dije cinco."),
                ],
            },
        ],
        "ascensor": pygame.Rect(2280, 420, 60, 80),
        "terminal": None,
    },
    {  # --- Nivel 2: El Refugio Hundido ---
        "nombre": "II · El Refugio Hundido",
        "ancho": 2800,
        "inicio": (40.0, 423.0),
        "plataformas": [
            pygame.Rect(0, 500, 200, 100),
            pygame.Rect(270, 445, 160, 24),
            pygame.Rect(490, 390, 160, 24),
            pygame.Rect(715, 440, 150, 24),
            pygame.Rect(940, 400, 170, 24),
            pygame.Rect(1180, 455, 175, 24),
            pygame.Rect(1420, 405, 160, 24),
            pygame.Rect(1650, 460, 150, 24),
            pygame.Rect(1865, 415, 165, 24),
            pygame.Rect(2095, 460, 155, 24),
            pygame.Rect(2320, 500, 480, 100),
        ],
        "ecos": ((95, 500), (350, 445), (570, 390), (790, 440),
                 (1025, 400), (1500, 405)),
        "zombies": ((140, 500, 70, "errante"), (570, 390, 55, "errante"),
                    (1260, 455, 70, "corrupto"), (1500, 405, 60, "errante"),
                    (2160, 460, 60, "coloso")),
        "vel_zombie": 65.0,
        "npcs": [
            {
                "x": 120, "y": 500, "sprite": "soldier",
                "nombre": "Iris · Guardiana", "color": (240, 200, 110),
                "lineas": [
                    ("Iris", (240, 200, 110),
                     "Alto. Soy Iris, guardiana del refugio... o de lo que queda de ella."),
                    ("Kael", AZUL_NEON,
                     "El refugio seguía en pie en mis sueños. Bajé por eso."),
                    ("Iris", (240, 200, 110),
                     "Las sombras —los no-muertos de la memoria— rondan las plataformas. No las destruyes, solo las esquivas."),
                    ("Iris", (240, 200, 110),
                     "Si te tocan, respira. El eco te devuelve al inicio, pero nunca te quita lo que ya recuerdas."),
                    ("Kael", AZUL_NEON, "¿Y qué hay más abajo?"),
                    ("Iris", (240, 200, 110),
                     "El Archivo. Donde Elena registró todo antes de la inundación. Dicen que ella aún «está» allí."),
                ],
            },
            {
                "x": 2440, "y": 500, "sprite": "adventurer",
                "nombre": "Nilo · Explorador", "color": (140, 230, 170),
                "lineas": [
                    ("Nilo", (140, 230, 170),
                     "Tres pisos de andamios y ni una sola escalera. Built for giants, I guess."),
                    ("Kael", AZUL_NEON, "¿Y cómo bajaste tú?"),
                    ("Nilo", (140, 230, 170),
                     "Cayendo. Aprendí a caer mejor que a caminar. El truco es no mirar abajo."),
                    ("Nilo", (140, 230, 170),
                     "Oye, los que pesan más, los Colosos, no se mueven. Casi. Espera a que se cansen."),
                ],
            },
        ],
        "ascensor": pygame.Rect(2680, 420, 60, 80),
        "terminal": None,
    },
    {  # --- Nivel 3: El Corazón del Archivo ---
        "nombre": "III · El Corazón del Archivo",
        "ancho": 3000,
        "inicio": (40.0, 423.0),
        "plataformas": [
            pygame.Rect(0, 500, 220, 100),
            pygame.Rect(290, 440, 160, 24),
            pygame.Rect(510, 385, 160, 24),
            pygame.Rect(730, 435, 165, 24),
            pygame.Rect(960, 395, 160, 24),
            pygame.Rect(1185, 450, 170, 24),
            pygame.Rect(1420, 400, 165, 24),
            pygame.Rect(1650, 450, 160, 24),
            pygame.Rect(1875, 405, 170, 24),
            pygame.Rect(2110, 455, 165, 24),
            pygame.Rect(2345, 415, 160, 24),
            pygame.Rect(2570, 500, 430, 100),
        ],
        "ecos": ((110, 500), (370, 440), (590, 385), (812, 435),
                 (1040, 395), (1270, 450)),
        "zombies": ((150, 500, 70, "errante"), (590, 385, 55, "errante"),
                    (800, 435, 60, "corrupto"), (1490, 400, 60, "corrupto"),
                    (2180, 455, 65, "errante"), (2400, 415, 70, "coloso")),
        "vel_zombie": 80.0,
        "npcs": [
            {
                "x": 180, "y": 500, "sprite": "female",
                "nombre": "Elena · Cartógrafa", "color": (160, 210, 255),
                "lineas": [
                    ("Elena", (160, 210, 255),
                     "Soy Elena. Dibujé los mapas de la ciudad antes de que el agua la borrara."),
                    ("Elena", (160, 210, 255),
                     "Kael... sabía que vendrías. Eres el último eco que envié al mundo de arriba."),
                    ("Kael", AZUL_NEON, "¿Yo soy... un recuerdo?"),
                    ("Elena", (160, 210, 255),
                     "Eres la pregunta que Nova Tellus se hizo al hundirse. El terminal guarda la respuesta."),
                    ("Elena", (160, 210, 255),
                     "Recupera todos los ecos y elige. Lo que elijas se convertirá en la nueva verdad."),
                ],
            },
            {
                "x": 2680, "y": 500, "sprite": "soldier",
                "nombre": "Soto · El Último Guardia", "color": (255, 120, 120),
                "lineas": [
                    ("Soto", (255, 120, 120),
                     "No te acerques al terminal del fondo. Yo también firmé el decreto, ¿sabes?"),
                    ("Kael", AZUL_NEON, "¿Qué decreto?"),
                    ("Soto", (255, 120, 120),
                     "El de la inundación. La Fundadora quería empezar de cero. Firmamos todos."),
                    ("Soto", (255, 120, 120),
                     "He cargado con eso desde que el agua me dejó sin aire."),
                    ("Kael", AZUL_NEON, "Sin aire. Lo sé. El agua también me dejó sin."),
                    ("Soto", (255, 120, 120),
                     "Entonces ya sabes por qué te aviso: el terminal no juzga, pero los vivos sí."),
                    ("Soto", (255, 120, 120),
                     "Baja. Hay dos pisos más de archivo, y en el último está la respuesta."),
                ],
            },
        ],
        "ascensor": pygame.Rect(2830, 420, 60, 80),
        "terminal": None,
    },
    {  # --- Nivel 4: La Cisterna Rota ---
        "nombre": "IV · La Cisterna Rota",
        "ancho": 3200,
        "inicio": (40.0, 423.0),
        "plataformas": [
            pygame.Rect(0, 500, 210, 100),
            pygame.Rect(280, 445, 150, 24),
            pygame.Rect(500, 395, 150, 24),
            pygame.Rect(720, 345, 150, 24),
            pygame.Rect(940, 395, 150, 24),
            pygame.Rect(1160, 445, 150, 24),
            pygame.Rect(1380, 395, 160, 24),
            pygame.Rect(1610, 345, 150, 24),
            pygame.Rect(1830, 400, 160, 24),
            pygame.Rect(2060, 450, 150, 24),
            pygame.Rect(2280, 400, 150, 24),
            pygame.Rect(2500, 345, 150, 24),
            pygame.Rect(2720, 400, 160, 24),
            pygame.Rect(2950, 500, 250, 100),
        ],
        "ecos": ((100, 500), (355, 445), (575, 395), (795, 345),
                 (1015, 395), (1235, 445), (1460, 395), (1685, 345),
                 (1910, 400), (2135, 450)),
        "zombies": ((140, 500, 70, "errante"), (575, 395, 60, "errante"),
                    (795, 345, 55, "corrupto"), (1235, 445, 65, "corrupto"),
                    (1460, 395, 70, "errante"), (1685, 345, 60, "errante"),
                    (2135, 450, 70, "coloso"), (2575, 345, 65, "corrupto"),
                    (2800, 400, 70, "errante")),
        "vel_zombie": 90.0,
        "npcs": [
            {
                "x": 120, "y": 500, "sprite": "soldier",
                "nombre": "Bram · Guardamuros", "color": (200, 200, 120),
                "lineas": [
                    ("Bram", (200, 200, 120),
                     "Aquí el techo se vino abajo. Por eso las cisternas están tan profundas."),
                    ("Kael", AZUL_NEON, "Alguien abrió las compuertas."),
                    ("Bram", (200, 200, 120),
                     "Todos las abrimos. Fue lo primero que firmamos, antes incluso del decreto."),
                    ("Bram", (200, 200, 120),
                     "Hay diez ecos en esta cisterna. En el plano de Elena hay más, si puedes leerla."),
                    ("Kael", AZUL_NEON, "Elena tenía un mapa de todo esto."),
                    ("Bram", (200, 200, 120),
                     "De todo. Por eso la rascaron. Por eso su memoria sigue ahí, doliendo."),
                ],
            },
            {
                "x": 3020, "y": 500, "sprite": "female",
                "nombre": "Nara · La Escriba", "color": (190, 170, 255),
                "lineas": [
                    ("Nara", (190, 170, 255),
                     "No escribas. Escribir fija el recuerdo, y lo fijado no se puede cambiar."),
                    ("Kael", AZUL_NEON, "Entonces, ¿cómo se cambia algo?"),
                    ("Nara", (190, 170, 255),
                     "Escuchando. Escucha lo que la gente intenta decir y no lo que dice."),
                    ("Nara", (190, 170, 255),
                     "Cuando llegues al Archivo, no leas la última página. Esa es la trampa."),
                ],
            },
        ],
        "ascensor": pygame.Rect(3080, 420, 60, 80),
        "terminal": None,
    },
    {  # --- Nivel 5: El Archivo Sumergido ---
        "nombre": "V · El Archivo Sumergido",
        "ancho": 3400,
        "inicio": (40.0, 423.0),
        "plataformas": [
            pygame.Rect(0, 500, 200, 100),
            pygame.Rect(260, 450, 150, 24),
            pygame.Rect(470, 400, 150, 24),
            pygame.Rect(680, 350, 150, 24),
            pygame.Rect(890, 400, 150, 24),
            pygame.Rect(1100, 450, 150, 24),
            pygame.Rect(1310, 395, 150, 24),
            pygame.Rect(1520, 340, 150, 24),
            pygame.Rect(1730, 390, 150, 24),
            pygame.Rect(1940, 440, 150, 24),
            pygame.Rect(2150, 385, 150, 24),
            pygame.Rect(2360, 335, 150, 24),
            pygame.Rect(2570, 390, 150, 24),
            pygame.Rect(2780, 445, 150, 24),
            pygame.Rect(2990, 395, 160, 24),
            pygame.Rect(3200, 500, 200, 100),
        ],
        "ecos": ((90, 500), (335, 450), (545, 400), (755, 350),
                 (965, 400), (1175, 450), (1385, 395), (1595, 340),
                 (1805, 390), (2015, 440), (2225, 385), (2435, 335),
                 (2645, 390)),
        "zombies": ((130, 500, 65, "errante"), (545, 400, 60, "errante"),
                    (755, 350, 55, "corrupto"), (965, 400, 60, "corrupto"),
                    (1385, 395, 65, "errante"), (1595, 340, 55, "coloso"),
                    (1805, 390, 60, "errante"), (2015, 440, 65, "corrupto"),
                    (2225, 385, 60, "errante"), (2435, 335, 60, "coloso"),
                    (2645, 390, 65, "corrupto"), (3070, 395, 70, "errante")),
        "vel_zombie": 105.0,
        "npcs": [
            {
                "x": 110, "y": 500, "sprite": "adventurer",
                "nombre": "Orin · El Escriba Ciego", "color": (255, 210, 140),
                "lineas": [
                    ("Orin", (255, 210, 140),
                     "Escribí las últimas páginas con los ojos cerrados. Ya no me servían."),
                    ("Kael", AZUL_NEON, "¿Qué dice la última página?"),
                    ("Orin", (255, 210, 140),
                     "Por eso te lo digo a ti, que aún ves: no la leas. Es una orden de la Fundadora."),
                    ("Orin", (255, 210, 140),
                     "Aquí abajo hay trece Ecos. Ni uno menos. Yo los conté durante mucho tiempo."),
                ],
            },
            {
                "x": 3345, "y": 500, "sprite": "soldier",
                "nombre": "Vega · La Última Soldado", "color": (120, 220, 255),
                "lineas": [
                    ("Vega", (120, 220, 255),
                     "Trece. Nunca llegué a trece. Siempre me faltaba uno."),
                    ("Kael", AZUL_NEON, "¿Cuál te faltaba?"),
                    ("Vega", (120, 220, 255),
                     "El primero. El de la Fundadora. Ese nunca estuvo en ningún sitio."),
                    ("Vega", (120, 220, 255),
                     "El terminal está al fondo. Ya sabes lo que te va a preguntar."),
                    ("Kael", AZUL_NEON, "Voy a responder con la verdad."),
                    ("Vega", (120, 220, 255),
                     "La verdad también se pudre bajo el agua, Kael. Lleva una antorcha."),
                ],
            },
        ],
        "ascensor": None,
        "terminal": pygame.Rect(3260, 398, 48, 102),
    },
]

# ============================================================
# SPRITES (con fallback si faltan archivos)
# ============================================================
CARPETA_SPRITES = (
    Path(__file__).resolve().parent
    / "kenney_platformer-characters" / "PNG"
)


def _placeholder(color):
    surf = pygame.Surface((PERSONAJE_ANCHO, PERSONAJE_ALTO), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (4, 4, PERSONAJE_ANCHO - 8, PERSONAJE_ALTO - 8),
                     border_radius=8)
    pygame.draw.rect(surf, (255, 255, 255, 120),
                     (4, 4, PERSONAJE_ANCHO - 8, PERSONAJE_ALTO - 8), 2,
                     border_radius=8)
    return surf


def cargar_sprite(personaje, nombre, color=(60, 140, 220)):
    try:
        imagen = pygame.image.load(
            str(CARPETA_SPRITES / personaje / "Poses" / nombre)).convert_alpha()
        return pygame.transform.scale(imagen, (PERSONAJE_ANCHO, PERSONAJE_ALTO))
    except (pygame.error, FileNotFoundError) as e:
        print(f"[WARN] Sprite no encontrado: {personaje}/Poses/{nombre} ({e})")
        return _placeholder(color)


SPRITES_JUGADOR = {
    "quieto": cargar_sprite("Player", "player_idle.png"),
    "salto": cargar_sprite("Player", "player_jump.png", (90, 180, 255)),
    "caminar": [
        cargar_sprite("Player", "player_walk1.png"),
        cargar_sprite("Player", "player_walk2.png", (70, 160, 230)),
    ],
}

# Fragmentos corrompidos de la memoria (enemigos)
# Tres variantes de zombie usan las poses de la carpeta "Zombie".
SPRITES_ZOMBIE = {
    "errante": {
        "quieto": cargar_sprite("Zombie", "zombie_idle.png", (96, 158, 84)),
        "caminar": [
            cargar_sprite("Zombie", "zombie_walk1.png", (96, 158, 84)),
            cargar_sprite("Zombie", "zombie_walk2.png", (84, 140, 74)),
        ],
    },
    "corrupto": {
        "quieto": cargar_sprite("Zombie", "zombie_action1.png", (120, 96, 160)),
        "caminar": [
            cargar_sprite("Zombie", "zombie_action1.png", (120, 96, 160)),
            cargar_sprite("Zombie", "zombie_action2.png", (104, 84, 144)),
        ],
    },
    "coloso": {
        "quieto": cargar_sprite("Zombie", "zombie_stand.png", (168, 120, 70)),
        "caminar": [
            cargar_sprite("Zombie", "zombie_walk1.png", (168, 120, 70)),
            cargar_sprite("Zombie", "zombie_walk2.png", (150, 106, 62)),
        ],
    },
}

# Habitantes del recuerdo (NPC con diálogos)
SPRITES_NPC = {
    "adventurer": {
        "quieto": cargar_sprite("Adventurer", "adventurer_idle.png", (170, 150, 120)),
        "caminar": [
            cargar_sprite("Adventurer", "adventurer_walk1.png", (170, 150, 120)),
            cargar_sprite("Adventurer", "adventurer_walk2.png", (160, 140, 110)),
        ],
    },
    "soldier": {
        "quieto": cargar_sprite("Soldier", "soldier_idle.png", (186, 158, 96)),
        "caminar": [
            cargar_sprite("Soldier", "soldier_walk1.png", (186, 158, 96)),
            cargar_sprite("Soldier", "soldier_walk2.png", (170, 144, 88)),
        ],
    },
    "female": {
        "quieto": cargar_sprite("Female", "female_idle.png", (130, 160, 205)),
        "caminar": [
            cargar_sprite("Female", "female_walk1.png", (130, 160, 205)),
            cargar_sprite("Female", "female_walk2.png", (120, 148, 190)),
        ],
    },
}

# ============================================================
# CLASES DE EFECTOS
# ============================================================
class Particula:
    __slots__ = ("x", "y", "vx", "vy", "vida", "vida_max", "color", "radio")

    def __init__(self, x, y, color, velocidad=150.0, vida=0.7):
        angulo = random.uniform(0, math.tau)
        rapidez = velocidad * random.uniform(0.4, 1.2)
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angulo) * rapidez
        self.vy = math.sin(angulo) * rapidez - 80
        self.vida = vida
        self.vida_max = vida
        self.color = color
        self.radio = random.randint(2, 4)

    def actualizar(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 380 * dt
        self.vida -= dt

    def viva(self):
        return self.vida > 0

    def dibujar(self, superficie, camara_x):
        if self.vida <= 0:
            return
        t = self.vida / self.vida_max
        r, g, b = self.color
        pygame.draw.circle(superficie, (int(r * t), int(g * t), int(b * t)),
                           (int(self.x - camara_x), int(self.y)), self.radio)


class TextoFlotante:
    __slots__ = ("x", "y", "texto", "color", "vida", "vida_max")

    def __init__(self, x, y, texto, color, vida=1.2):
        self.x = float(x)
        self.y = float(y)
        self.texto = texto
        self.color = color
        self.vida = vida
        self.vida_max = vida

    def actualizar(self, dt):
        self.y -= 45 * dt
        self.vida -= dt

    def viva(self):
        return self.vida > 0

    def dibujar(self, superficie, camara_x):
        if self.vida <= 0:
            return
        alpha = int(255 * min(1.0, self.vida / (self.vida_max * 0.5)))
        img = fuente_pequena.render(self.texto, True, self.color)
        img.set_alpha(alpha)
        superficie.blit(img, (int(self.x - camara_x), int(self.y)))


# ============================================================
# JUGADOR
# ============================================================
class Jugador:
    W = PERSONAJE_ANCHO
    H = PERSONAJE_ALTO

    def __init__(self, x, y):
        self.x = 0.0
        self.y = 0.0
        self.vel_y = 0.0
        self.en_suelo = True
        self.direccion = 1
        self.coyote = COYOTE_TIME
        self.jump_buffer = 0.0
        self.caminando = False
        self.anim_time = 0.0
        self.anim_idx = 0
        self.vida = VIDA_MAX
        self.vida_max = VIDA_MAX
        self.invul = 0.0
        self.reset(x, y)

    def reset(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vel_y = 0.0
        self.en_suelo = True
        self.direccion = 1
        self.coyote = COYOTE_TIME
        self.jump_buffer = 0.0
        self.caminando = False
        self.anim_time = 0.0
        self.anim_idx = 0

    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.W, self.H)

    def pedir_salto(self):
        self.jump_buffer = JUMP_BUFFER_TIME

    def soltar_salto(self):
        if self.vel_y < -200:
            self.vel_y *= JUMP_CUT

    def recibir_daño(self, desde_x, cantidad=1):
        """Aplica daño si no está invulnerable. Devuelve True si tocó."""
        if self.invul > 0:
            return False
        self.vida -= cantidad
        self.invul = INVUL_TIEMPO
        self.vel_y = -330.0
        self.x += 38.0 if self.x >= desde_x else -38.0
        self.x = max(0.0, self.x)
        return True

    def actualizar(self, dt, teclas, plataformas, ancho_mundo, touch=None):
        self.invul = max(0.0, self.invul - dt)
        # --- Horizontal ---
        self.caminando = False
        izq = teclas[pygame.K_LEFT] or teclas[pygame.K_a] or (touch is not None and "left" in touch)
        der = teclas[pygame.K_RIGHT] or teclas[pygame.K_d] or (touch is not None and "right" in touch)
        if izq:
            self.x -= VELOCIDAD * dt
            self.caminando = True
            self.direccion = -1
        if der:
            self.x += VELOCIDAD * dt
            self.caminando = True
            self.direccion = 1
        self.x = max(0.0, min(self.x, ancho_mundo - self.W))

        # --- Salto con coyote + buffer ---
        if self.jump_buffer > 0 and (self.en_suelo or self.coyote > 0):
            self.vel_y = FUERZA_SALTO
            Audio.play("salto")
            self.en_suelo = False
            self.coyote = 0.0
            self.jump_buffer = 0.0

        # --- Física vertical ---
        rect_prev = self.rect()
        self.vel_y += GRAVEDAD * dt
        self.y += self.vel_y * dt
        rect_actual = self.rect()

        # --- Detección de aterrizaje ---
        self.en_suelo = False
        if self.vel_y >= 0:
            for p in plataformas:
                if (rect_prev.bottom <= p.top + 1
                        and rect_actual.bottom >= p.top
                        and rect_actual.right > p.left + 3
                        and rect_actual.left < p.right - 3):
                    self.y = float(p.top - self.H)
                    self.vel_y = 0.0
                    self.en_suelo = True
                    break

        # --- Timers ---
        if self.en_suelo:
            self.coyote = COYOTE_TIME
        else:
            self.coyote = max(0.0, self.coyote - dt)
        self.jump_buffer = max(0.0, self.jump_buffer - dt)

        # --- Animación ---
        if self.caminando and self.en_suelo:
            self.anim_time += dt
            if self.anim_time >= 0.13:
                self.anim_time = 0.0
                self.anim_idx = 1 - self.anim_idx
        else:
            self.anim_time = 0.0
            self.anim_idx = 0

    def dibujar(self, superficie, camara_x, tiempo):
        if self.invul > 0 and int(self.invul * 12) % 2 == 0:
            return  # parpadeo al recibir daño
        if not self.en_suelo:
            base = SPRITES_JUGADOR["salto"]
        elif self.caminando:
            base = SPRITES_JUGADOR["caminar"][self.anim_idx]
        else:
            base = SPRITES_JUGADOR["quieto"]
        if self.direccion < 0:
            base = pygame.transform.flip(base, True, False)
        bob = int(math.sin(tiempo * 0.004) * 2) if (self.en_suelo and not self.caminando) else 0
        superficie.blit(base, (int(self.x - camara_x), int(self.y + bob)))


# ============================================================
# ENEMIGOS Y NPCS
# ============================================================
class Zombie:
    """Fragmento corrompido de la memoria: patrulla su plataforma.

    Tipos:
      errante  -> rápido y frágil
      corrupto -> mediano, más resistente
      coloso   -> lento, golpe fuerte, ocupa más espacio
    """
    H = PERSONAJE_ALTO

    TIPOS = {
        "errante": {"vida": 1, "vel": 1.0, "dano": 1,
                    "ancho": PERSONAJE_ANCHO, "alto": PERSONAJE_ALTO},
        "corrupto": {"vida": 2, "vel": 0.72, "dano": 1,
                     "ancho": PERSONAJE_ANCHO, "alto": PERSONAJE_ALTO},
        "coloso": {"vida": 4, "vel": 0.45, "dano": 2,
                   "ancho": PERSONAJE_ANCHO + 36, "alto": PERSONAJE_ALTO + 40},
    }

    def __init__(self, x, y_suelo, rango, velocidad, tipo="errante"):
        cfg = self.TIPOS[tipo]
        self.tipo = tipo
        self.x = float(x)
        self.y_suelo = int(y_suelo)
        self.rango_a = float(x - rango)
        self.rango_b = float(x + rango)
        self.vel = float(velocidad) * cfg["vel"]
        self.ancho = cfg["ancho"]
        self.alto = cfg["alto"]
        self.dano = cfg["dano"]
        self.vida = cfg["vida"]
        self.vida_max = cfg["vida"]
        self.dir = -1
        self.anim_time = 0.0
        self.anim_idx = 0
        self.muerto = False
        self.sprites = SPRITES_ZOMBIE[tipo]
        # Escala propia para el coloso
        if (self.ancho, self.alto) != (PERSONAJE_ANCHO, PERSONAJE_ALTO):
            self.sprites = {
                "quieto": pygame.transform.scale(self.sprites["quieto"],
                                                (self.ancho, self.alto)),
                "caminar": [pygame.transform.scale(s, (self.ancho, self.alto))
                            for s in self.sprites["caminar"]],
            }

    def rect(self):
        """Caja de daño (un poco más estrecha que el sprite)."""
        return pygame.Rect(round(self.x) + 10, self.y_suelo - self.alto + 10,
                           self.ancho - 20, self.alto - 10)

    def actualizar(self, dt):
        if self.muerto:
            return
        self.x += self.vel * self.dir * dt
        if self.x <= self.rango_a:
            self.x = self.rango_a
            self.dir = 1
        elif self.x >= self.rango_b:
            self.x = self.rango_b
            self.dir = -1
        self.anim_time += dt
        if self.anim_time >= 0.22:
            self.anim_time = 0.0
            self.anim_idx = 1 - self.anim_idx

    def recibir_daño(self):
        """Devuelve True si este golpe lo destruye."""
        self.vida -= 1
        if self.vida <= 0:
            self.vida = 0
            self.muerto = True
            return True
        return False

    def dibujar(self, superficie, camara_x):
        if self.muerto:
            return
        base = self.sprites["caminar"][self.anim_idx]
        if self.dir < 0:
            base = pygame.transform.flip(base, True, False)
        superficie.blit(base, (int(self.x - camara_x), self.y_suelo - self.alto))
        # Barra de vida para los enemigos resistentes
        if self.vida_max > 1:
            barra_w = self.ancho - 16
            bx = int(self.x - camara_x) + 8
            by = self.y_suelo - self.alto - 10
            pygame.draw.rect(superficie, (30, 20, 30), (bx, by, barra_w, 4))
            pygame.draw.rect(superficie, ROJO_DANO,
                             (bx, by, int(barra_w * self.vida / self.vida_max), 4))


class NPC:
    """Habitante del recuerdo con el que Kael puede conversar."""

    def __init__(self, x, y_suelo, sprite, nombre, color, lineas, hablado=False):
        self.x = float(x)
        self.y_suelo = int(y_suelo)
        self.sprites = SPRITES_NPC[sprite]
        self.nombre = nombre
        self.color = color
        self.lineas = lineas
        self.hablado = hablado
        self.fase = random.uniform(0, math.tau)

    def rect(self):
        return pygame.Rect(round(self.x) - 8, self.y_suelo - PERSONAJE_ALTO,
                           PERSONAJE_ANCHO + 16, PERSONAJE_ALTO)

    def dibujar(self, superficie, camara_x, tiempo):
        bob = int(math.sin(tiempo * 0.003 + self.fase) * 2)
        superficie.blit(self.sprites["quieto"],
                        (int(self.x - camara_x), self.y_suelo - PERSONAJE_ALTO + bob))
        # Burbuja "!" (sin hablar) / "?" (ya hablado)
        marca = "!" if not self.hablado else "?"
        bx = int(self.x - camara_x) + PERSONAJE_ANCHO // 2
        by = self.y_suelo - PERSONAJE_ALTO - 15 + bob
        pygame.draw.circle(superficie, (10, 30, 50), (bx, by), 11)
        pygame.draw.circle(superficie, self.color, (bx, by), 11, 2)
        img = fuente_pequena.render(marca, True, self.color)
        superficie.blit(img, (bx - img.get_width() // 2, by - img.get_height() // 2))


# ============================================================
# DIBUJO DE ESCENARIO
# ============================================================
def dibujar_texto(texto, x, y, fuente_usada=fuente, color=BLANCO_AZUL, superficie=None):
    if superficie is None:
        superficie = pantalla
    superficie.blit(fuente_usada.render(texto, True, color), (x, y))


def envolver_texto(texto, font, max_ancho):
    """Divide texto en líneas que caben en max_ancho píxeles."""
    lineas = []
    actual = ""
    for palabra in texto.split(" "):
        prueba = (actual + " " + palabra).strip()
        if font.size(prueba)[0] <= max_ancho or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def dibujar_plataforma(rect, indice, camara_x, tiempo):
    vx = int(rect.x - camara_x)
    if vx + rect.width < 0 or vx > ANCHO:
        return
    # Piedra hundida con musgo
    pygame.draw.rect(pantalla, (12, 34, 48), (vx, rect.y, rect.width, rect.height))
    pygame.draw.rect(pantalla, (20, 55, 70),
                     (vx, rect.y + 6, rect.width, rect.height - 6))
    pygame.draw.line(pantalla, (34, 130, 140),
                     (vx, rect.y + 2), (vx + rect.width, rect.y + 2), 3)
    pygame.draw.line(pantalla, (70, 190, 190),
                     (vx + 6, rect.y + 7), (vx + rect.width - 6, rect.y + 7), 1)

    # Grietas en la piedra
    for px in range(vx + 20, vx + rect.width - 15, 45):
        pygame.draw.line(pantalla, (8, 26, 38),
                         (px, rect.y + 10), (px + 6, rect.bottom - 4), 1)

    # Algas balanceándose en el borde superior (en todas las plataformas)
    for px in range(vx + 8, vx + rect.width - 8, 22):
        sway = int(math.sin(tiempo * 0.002 + px * 0.3) * 2)
        altura = 6 + (px // 11) % 7
        pygame.draw.line(pantalla, (40, 120, 90),
                         (px, rect.y), (px + sway, rect.y - altura), 2)

    # Colonias de percebes/barnacles en la cara inferior
    if rect.height < 40:
        for px in (vx + 24, vx + rect.width - 26):
            pygame.draw.line(pantalla, (29, 81, 136),
                             (px, rect.bottom), (px, rect.bottom + 13), 3)
            pygame.draw.circle(pantalla, (50, 110, 120), (px, rect.bottom + 14), 3)


def dibujar_eco(rect, tiempo, camara_x):
    centro = (round(rect.centerx - camara_x), rect.centery)
    pulso = 2 + int((math.sin(tiempo * 0.006 + rect.x) + 1) * 2)
    pygame.draw.circle(pantalla, (29, 142, 255), centro, 19 + pulso, 1)
    pygame.draw.circle(pantalla, (25, 208, 255), centro, 12)
    pygame.draw.circle(pantalla, (207, 255, 255), centro, 5)


def dibujar_ascensor(rect, camara_x, tiempo, listo):
    """Cápsula de ascensor que baja al siguiente nivel."""
    vx = int(rect.x - camara_x)
    if vx + rect.width < 0 or vx > ANCHO:
        return
    # Rieles
    pygame.draw.line(pantalla, (22, 60, 92), (vx + 6, rect.bottom),
                     (vx + 6, rect.bottom + 90), 3)
    pygame.draw.line(pantalla, (22, 60, 92), (vx + rect.width - 6, rect.bottom),
                     (vx + rect.width - 6, rect.bottom + 90), 3)
    # Carcasa
    pygame.draw.rect(pantalla, (11, 30, 58), (vx, rect.y, rect.width, rect.height),
                     border_radius=6)
    color_borde = AZUL_NEON if listo else (58, 92, 130)
    pygame.draw.rect(pantalla, color_borde, (vx, rect.y, rect.width, rect.height),
                     3, border_radius=6)
    # Ventana iluminada
    color_v = (24, 151, 212) if listo else (38, 64, 95)
    if listo:
        pulso = int(18 * (1 + math.sin(tiempo * 0.005)))
        color_v = tuple(min(255, c + pulso) for c in color_v)
    pygame.draw.rect(pantalla, color_v, (vx + 9, rect.y + 12, rect.width - 18, 34),
                     border_radius=3)
    pygame.draw.line(pantalla, (207, 255, 255), (vx + 12, rect.y + 56),
                     (vx + rect.width - 12, rect.y + 56), 2)
    # Flecha hacia abajo
    cy = rect.y + rect.height + 22 + int(math.sin(tiempo * 0.004) * 4)
    pygame.draw.polygon(pantalla, color_borde, [
        (vx + rect.width // 2 - 9, cy - 8),
        (vx + rect.width // 2 + 9, cy - 8),
        (vx + rect.width // 2, cy + 6)])
    if listo:
        etiqueta = fuente_pequena.render("E", True, AZUL_NEON)
        pantalla.blit(etiqueta, (vx + rect.width // 2 - etiqueta.get_width() // 2,
                                 rect.y - 22))


def dibujar_terminal(rect, camara_x, tiempo, listo):
    """Terminal del Archivo: guarda la respuesta de la Fundadora."""
    vx = int(rect.x - camara_x)
    if vx + rect.width < 0 or vx > ANCHO:
        return
    pygame.draw.rect(pantalla, (9, 27, 61), (vx, rect.y, rect.width, rect.height),
                     border_radius=5)
    color_borde = AZUL_NEON if listo else (62, 97, 143)
    pygame.draw.rect(pantalla, color_borde, (vx, rect.y, rect.width, rect.height),
                     3, border_radius=5)
    color_p = (24, 151, 212) if listo else (40, 68, 99)
    if listo:
        pulso = int(20 * (1 + math.sin(tiempo * 0.005)))
        color_p = tuple(min(255, c + pulso) for c in color_p)
    pygame.draw.rect(pantalla, color_p, (vx + 8, rect.y + 12,
                                          rect.width - 16, 48), border_radius=3)
    pygame.draw.line(pantalla, (207, 255, 255), (vx + 12, rect.y + 75),
                     (vx + rect.width - 12, rect.y + 75), 2)
    if listo:
        etiqueta = fuente_pequena.render("E", True, AZUL_NEON)
        pantalla.blit(etiqueta, (vx + rect.width // 2 - etiqueta.get_width() // 2,
                                 rect.y - 22))

def dibujar_dialogo(npc, idx, tiempo):
    """Caja de diálogo inferior con el texto actual del NPC."""
    _, color, texto = npc.lineas[idx]
    lineas = envolver_texto(texto, fuente, ANCHO - 90)
    alto_caja = 52 + len(lineas) * 24
    y0 = ALTO - alto_caja - 26

    pygame.draw.rect(pantalla, (3, 9, 26), (26, y0, ANCHO - 52, alto_caja),
                     border_radius=10)
    pygame.draw.rect(pantalla, AZUL_NEON, (26, y0, ANCHO - 52, alto_caja), 2,
                     border_radius=10)
    # Retrato del interlocutor
    pygame.draw.rect(pantalla, (10, 24, 52), (36, y0 + 10, 54, 54), border_radius=8)
    pygame.draw.rect(pantalla, color, (36, y0 + 10, 54, 54), 2, border_radius=8)
    pantalla.blit(pygame.transform.scale(npc.sprites["quieto"], (50, 50)),
                  (38, y0 + 12))
    # Nombre
    pantalla.blit(fuente_hud.render(npc.nombre, True, color), (102, y0 + 12))
    # Texto
    for i, ln in enumerate(lineas):
        pantalla.blit(fuente.render(ln, True, BLANCO_AZUL), (102, y0 + 42 + i * 24))
    # Indicador de continuar
    if int(tiempo / 500) % 2 == 0:
        pygame.draw.polygon(pantalla, AZUL_NEON, [
            (ANCHO - 62, ALTO - 48), (ANCHO - 44, ALTO - 48), (ANCHO - 53, ALTO - 38)])
    pantalla.blit(fuente_pequena.render("E / Enter: continuar   Esc: salir",
                                        True, (110, 150, 180)),
                  (102, y0 + alto_caja - 22))


# ============================================================
# PANTALLAS
# ============================================================
def mostrar_pantalla_decision():
    capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    capa.fill((3, 8, 24, 210))
    pantalla.blit(capa, (0, 0))
    pygame.draw.rect(pantalla, (10, 23, 55), (75, 165, 650, 270), border_radius=12)
    pygame.draw.rect(pantalla, AZUL_NEON, (75, 165, 650, 270), 2, border_radius=12)
    dibujar_texto("EL ECO REVELA LA VERDAD", 105, 190, fuente_titulo, AZUL_NEON)
    dibujar_texto("La Fundadora provocó la inundación para reiniciar la humanidad.", 105, 238)
    dibujar_texto("¿Qué hará Kael con el recuerdo?", 105, 276, fuente_hud)
    dibujar_texto("[1] Revelarlo y arriesgar el caos", 125, 320)
    dibujar_texto("[2] Destruirlo y perpetuar la mentira", 125, 354)
    dibujar_texto("[3] Alterarlo para crear otra historia", 125, 388)


def mostrar_pantalla_final(texto, fade):
    if fade <= 0:
        return
    capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    capa.fill((3, 8, 24, 210))
    pygame.draw.rect(capa, (10, 23, 55), (75, 205, 650, 160), border_radius=12)
    pygame.draw.rect(capa, AZUL_NEON, (75, 205, 650, 160), 2, border_radius=12)
    capa.blit(fuente_titulo.render("ECO REGISTRADO", True, AZUL_NEON), (105, 230))
    capa.blit(fuente.render(texto, True, BLANCO_AZUL), (105, 286))
    capa.blit(fuente_pequena.render("Pulsa R para volver al menú.",
                                    True, (120, 200, 255)), (105, 330))
    capa.set_alpha(int(255 * min(1.0, fade)))
    pantalla.blit(capa, (0, 0))


def mostrar_pausa():
    capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    capa.fill((3, 8, 24, 170))
    pantalla.blit(capa, (0, 0))
    pygame.draw.rect(pantalla, (10, 23, 55), (230, 200, 340, 200), border_radius=12)
    pygame.draw.rect(pantalla, AZUL_NEON, (230, 200, 340, 200), 2, border_radius=12)
    dibujar_texto("PAUSA", 230 + 340 // 2 - 40, 225, fuente_titulo, AZUL_NEON)
    dibujar_texto("[P / Esc] Reanudar", 260, 275)
    dibujar_texto("[R] Reiniciar nivel", 260, 305)
    dibujar_texto("[M] Volver al menu", 260, 335)


def mostrar_menu(opcion, tiene_guardado, tiempo):
    if fondo_menu is not None:
        fondo_menu.draw(pantalla, 0.0)

    titulo = fuente_titulo.render("ECOS DE LA MEMORIA", True, AZUL_NEON)
    pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 140))
    sub = fuente.render("Nova Tellus  //  Recuerdo fragmentado", True, (120, 200, 230))
    pantalla.blit(sub, (ANCHO // 2 - sub.get_width() // 2, 185))

    opciones = ["Nueva Partida", "Continuar", "Salir"]
    for i, texto_op in enumerate(opciones):
        y = 280 + i * 50
        activo = (i == opcion)
        color = AZUL_NEON if activo else (140, 180, 210)
        if i == 1 and not tiene_guardado:
            color = (70, 90, 110)
        prefijo = "> " if activo else "  "
        img = fuente_hud.render(prefijo + texto_op, True, color)
        pantalla.blit(img, (ANCHO // 2 - img.get_width() // 2, y))

    if opcion == 1 and not tiene_guardado:
        aviso = fuente_pequena.render("No hay partida guardada.", True, (120, 140, 160))
        pantalla.blit(aviso, (ANCHO // 2 - aviso.get_width() // 2, 450))

    dibujar_texto("Arriba/Abajo: navegar   Enter/E: seleccionar   Esc: salir",
                  ANCHO // 2 - 190, 540, fuente_pequena, (120, 180, 210))


# ============================================================
# GUARDADO / CARGA (1 slot automático)
# ============================================================
def guardar_partida(juego):
    datos = {
        "version": 1,
        "nivel": juego.nivel,
        "x": juego.jugador.x,
        "y": juego.jugador.y,
        "direccion": juego.jugador.direccion,
        "vida": juego.jugador.vida,
        "ecos": [[eco.centerx, eco.centery + 36] for eco in juego.ecos],
        "ecos_recuperados": juego.ecos_recuperados,
        "ecos_recuperados_nivel": juego.ecos_recuperados_nivel,
        "npcs_hablados": sorted(juego.npcs_hablados),
        "final_elegido": juego.final_elegido,
    }
    # Backup del slot anterior
    try:
        if RUTA_GUARDADO.exists():
            shutil.copyfile(RUTA_GUARDADO, RUTA_BACKUP)
    except OSError:
        pass
    try:
        with open(RUTA_GUARDADO, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def cargar_partida(juego):
    datos = None
    for ruta in (RUTA_GUARDADO, RUTA_BACKUP):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
            break
        except (OSError, json.JSONDecodeError, ValueError):
            datos = None
            continue
    if not isinstance(datos, dict):
        return False
    try:
        nivel = int(datos.get("nivel", 0))
        if not 0 <= nivel < len(NIVELES):
            nivel = 0
        juego.npcs_hablados = set(datos.get("npcs_hablados", []))
        juego.cargar_nivel(nivel)
        juego.jugador.reset(datos["x"], datos["y"])
        juego.jugador.direccion = datos.get("direccion", 1)
        juego.jugador.vida = max(1, int(datos.get("vida", VIDA_MAX)))
        juego.ecos = [
            pygame.Rect(x - RADIO_ECO, y - 36 - RADIO_ECO,
                        RADIO_ECO * 2, RADIO_ECO * 2)
            for x, y in datos["ecos"]
        ]
        juego.ecos_recuperados = datos.get("ecos_recuperados", 0)
        juego.ecos_recuperados_nivel = datos.get(
            "ecos_recuperados_nivel", len(NIVELES[nivel]["ecos"]) - len(juego.ecos))
        juego.nivel_listo = (len(juego.ecos) == 0)
        juego.final_elegido = datos.get("final_elegido")
        if juego.final_elegido not in (None, "decidir"):
            juego.fade_final = 1.0
    except (KeyError, TypeError, ValueError):
        return False
    return True


# ============================================================
# ============================================================
# AUDIO (sintetizado, sin archivos externos; fallback silencioso)
# ============================================================
class Audio:
    _ok = False
    _sounds = {}

    @classmethod
    def init(cls):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            cls._ok = True
        except pygame.error:
            cls._ok = False
            return
        # Genera beeps simples
        def beep(freq, dur, vol=0.35):
            if not cls._ok:
                return None
            n = int(22050 * dur)
            buf = array.array("h")
            import math as _m
            for i in range(n):
                v = int(32767 * vol * _m.sin(2 * _m.pi * freq * i / 22050))
                # fade out corto para evitar clic
                if i > n - 200:
                    v = int(v * (n - i) / 200)
                buf.append(v)
            try:
                return pygame.mixer.Sound(buffer=buf.tobytes())
            except pygame.error:
                return None
        cls._sounds = {
            "salto": beep(660, 0.08),
            "eco": beep(880, 0.12),
            "dano": beep(220, 0.18),
            "dispersar": beep(440, 0.1),
            "nivel": beep(523, 0.18),
            "menu": beep(740, 0.06),
            "ascensor": beep(330, 0.2),
            "terminal": beep(988, 0.15),
            "pausa": beep(494, 0.07),
        }

    @classmethod
    def play(cls, nombre):
        if not cls._ok:
            return
        s = cls._sounds.get(nombre)
        if s is not None:
            try:
                s.play()
            except pygame.error:
                pass


Audio.init()

# ============================================================
# CONTROLES TACTILES (movil)
# ============================================================
TOUCH_BUTTONS = [
    {"name": "left", "rect": pygame.Rect(40, ALTO - 110, 70, 70), "label": "<"},
    {"name": "right", "rect": pygame.Rect(120, ALTO - 110, 70, 70), "label": ">"},
    {"name": "jump", "rect": pygame.Rect(ANCHO - 110, ALTO - 110, 90, 90), "label": "SALTO"},
    {"name": "interact", "rect": pygame.Rect(ANCHO - 210, ALTO - 100, 80, 70), "label": "E"},
    {"name": "pause", "rect": pygame.Rect(ANCHO - 70, 15, 55, 40), "label": "||"},
]
touch_state = set()
_touch_map = {}  # touch_id -> button name

def _touch_button_at(x, y):
    for b in TOUCH_BUTTONS:
        if b["rect"].collidepoint(x, y):
            return b["name"]
    return None

def dibujar_touch_controls():
    if os.environ.get("ANDROID_ARGUMENT") or sys.platform.startswith("android"):
        pass
    # Siempre dibujar en pantallas tactiles; en desktop solo si se desea (oculto por defecto)
    if not _ANDROID:
        return
    for b in TOUCH_BUTTONS:
        r = b["rect"]
        activo = b["name"] in touch_state
        color = (46, 224, 255, 120) if activo else (20, 60, 90, 90)
        surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        surf.fill(color)
        pantalla.blit(surf, r.topleft)
        pygame.draw.rect(pantalla, (120, 200, 230), r, 2, border_radius=10)
        img = fuente_pequena.render(b["label"], True, (220, 240, 255))
        pantalla.blit(img, (r.centerx - img.get_width() // 2,
                            r.centery - img.get_height() // 2))

# ESTADO DEL JUEGO
# ============================================================
fondo_menu = None


class Juego:
    def __init__(self):
        self.estado = "menu"
        self.opcion_menu = 0
        self.tiene_guardado = RUTA_GUARDADO.exists()
        self.banner_nivel = 0.0
        self.fondo = None
        self.reiniciar()

    def reiniciar(self):
        self.nivel = 0
        self.ecos_recuperados = 0
        self.ecos_recuperados_nivel = 0
        self.npcs_hablados = set()
        self.camara_x = 0.0
        self.particulas = []
        self.textos = []
        self.final_elegido = None
        self.fade_final = 0.0
        self.flash = 0.0
        self.dialogo = None
        self.jugador = Jugador(40.0, 423.0)
        self.cargar_nivel(0)

    def cargar_nivel(self, indice):
        """Construye el nivel desde NIVELES y coloca al jugador."""
        datos = NIVELES[indice]
        self.nivel = indice
        self.ancho_mundo = datos["ancho"]
        self.plataformas = datos["plataformas"]
        self.ascensor = datos["ascensor"]
        self.terminal = datos["terminal"]
        self.ecos = [
            pygame.Rect(x - RADIO_ECO, y - 36 - RADIO_ECO,
                        RADIO_ECO * 2, RADIO_ECO * 2)
            for x, y in datos["ecos"]
        ]
        self.ecos_recuperados_nivel = 0
        self.nivel_listo = (len(self.ecos) == 0)
        self.zombies = self._crear_zombies(datos)
        self.npcs = [
            NPC(d["x"], d["y"], d["sprite"], d["nombre"], d["color"], d["lineas"],
                d["nombre"] in self.npcs_hablados)
            for d in datos["npcs"]
        ]
        ix, iy = datos["inicio"]
        self.jugador.reset(ix, iy)
        self.camara_x = max(0.0, min(ix, self.ancho_mundo - ANCHO))
        self.dialogo = None
        self.banner_nivel = 3.0
        self.fondo = FondoSubmarino(ANCHO, ALTO, indice + 1, semilla=indice + 1)
        self.fondo = FondoSubmarino(ANCHO, ALTO, indice + 1, semilla=indice + 1)

    @staticmethod
    def _crear_zombies(datos):
        """Instancia los enemigos del nivel con su tipo (errante/corrupto/coloso)."""
        return [
            Zombie(x, y, rango, datos["vel_zombie"], tipo)
            for x, y, rango, tipo in datos["zombies"]
        ]

    def _npc_cercano(self):
        """Devuelve el NPC con el que Kael puede hablar (el más cercano)."""
        rj = self.jugador.rect()
        candidatos = [n for n in self.npcs if rj.colliderect(n.rect())]
        if not candidatos:
            return None
        return min(candidatos, key=lambda n: abs(n.x - self.jugador.x))

    def _reaparecer(self):
        """Vuelve al inicio del nivel conservando ecos ya recogidos."""
        datos = NIVELES[self.nivel]
        self.zombies = self._crear_zombies(datos)
        ix, iy = datos["inicio"]
        self.jugador.reset(ix, iy)
        self.camara_x = max(0.0, min(ix, self.ancho_mundo - ANCHO))

    # --- Eventos ---
    def manejar(self, ev):
        if ev.type == pygame.QUIT:
            return False

        # --- Eventos tactiles (movil) ---
        if ev.type in (pygame.FINGERDOWN, pygame.MOUSEBUTTONDOWN):
            if ev.type == pygame.FINGERDOWN:
                x = int(ev.x * ANCHO)
                y = int(ev.y * ALTO)
                tid = ev.touch_id
            else:
                x, y = ev.pos
                tid = -1
            # Menu: tocar opcion
            if self.estado == "menu":
                # zonas aproximadas de las 3 opciones
                for i, yy in enumerate((280, 330, 380)):
                    if pygame.Rect(260, yy, 280, 40).collidepoint(x, y):
                        self.opcion_menu = i
                        # activar
                        if i == 0:
                            self.reiniciar()
                            self.estado = "jugando"
                            guardar_partida(self)
                        elif i == 1 and self.tiene_guardado:
                            if cargar_partida(self):
                                self.estado = "jugando"
                        elif i == 2:
                            return False
            btn = _touch_button_at(x, y)
            if btn is not None:
                _touch_map[tid] = btn
                touch_state.add(btn)
                if btn == "jump" and self.estado == "jugando" and self.final_elegido is None:
                    self.jugador.pedir_salto()
                if btn == "interact" and self.estado == "jugando" and self.final_elegido is None:
                    rj = self.jugador.rect()
                    npc = self._npc_cercano()
                    if npc is not None:
                        self.dialogo = {"npc": npc, "idx": 0}
                        self.estado = "dialogo"
                    elif (self.ascensor is not None and self.nivel_listo
                            and self.nivel + 1 < len(NIVELES)
                            and rj.colliderect(self.ascensor.inflate(20, 10))):
                        self.flash = 120.0
                        self.cargar_nivel(self.nivel + 1)
                        Audio.play("nivel")
                        guardar_partida(self)
                    elif (self.terminal is not None and not self.ecos
                            and rj.colliderect(self.terminal.inflate(45, 10))):
                        self.final_elegido = "decidir"
                        guardar_partida(self)
                if btn == "pause":
                    if self.estado == "jugando":
                        Audio.play("pausa")
                        self.estado = "pausa"
                    elif self.estado == "pausa":
                        self.estado = "jugando"
                        Audio.play("pausa")

        if ev.type in (pygame.FINGERUP, pygame.MOUSEBUTTONUP):
            if ev.type == pygame.FINGERUP:
                tid = ev.touch_id
            else:
                tid = -1
            btn = _touch_map.pop(tid, None)
            if btn is not None and tid not in _touch_map.values():
                # remove only if no other finger holds it
                if btn not in _touch_map.values():
                    touch_state.discard(btn)

        if ev.type == pygame.FINGERMOTION:
            tid = ev.touch_id
            x = int(ev.x * ANCHO)
            y = int(ev.y * ALTO)
            old = _touch_map.get(tid)
            new = _touch_button_at(x, y)
            if old is not None and old != new:
                _touch_map.pop(tid, None)
                if old not in _touch_map.values():
                    touch_state.discard(old)
            if new is not None:
                _touch_map[tid] = new
                touch_state.add(new)

        if self.estado == "menu":
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w):
                    self.opcion_menu = (self.opcion_menu - 1) % 3
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    self.opcion_menu = (self.opcion_menu + 1) % 3
                elif ev.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                    if self.opcion_menu == 0:
                        self.reiniciar()
                        self.estado = "jugando"
                        guardar_partida(self)
                    elif self.opcion_menu == 1 and self.tiene_guardado:
                        if cargar_partida(self):
                            self.estado = "jugando"
                    elif self.opcion_menu == 2:
                        return False
                elif ev.key == pygame.K_ESCAPE:
                    return False
            return True

        if self.estado == "dialogo":
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
                    self.dialogo["idx"] += 1
                    if self.dialogo["idx"] >= len(self.dialogo["npc"].lineas):
                        npc = self.dialogo["npc"]
                        npc.hablado = True
                        self.npcs_hablados.add(npc.nombre)
                        self.dialogo = None
                        self.estado = "jugando"
                        guardar_partida(self)
                elif ev.key == pygame.K_ESCAPE:
                    self.dialogo = None
                    self.estado = "jugando"
            return True

        if self.estado == "pausa":
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_RETURN):
                    self.estado = "jugando"
                    Audio.play("pausa")
                elif ev.key == pygame.K_r:
                    self.reiniciar()
                    self.estado = "jugando"
                    guardar_partida(self)
                elif ev.key == pygame.K_m:
                    self.estado = "menu"
                    self.tiene_guardado = RUTA_GUARDADO.exists()
            return True

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                Audio.play("pausa")
                self.estado = "pausa"
                return True
            if ev.key == pygame.K_r and self.final_elegido is not None:
                self.estado = "menu"
                self.tiene_guardado = RUTA_GUARDADO.exists()
                return True
            if self.final_elegido is None:
                if ev.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.jugador.pedir_salto()
                if ev.key == pygame.K_e:
                    rj = self.jugador.rect()
                    npc = self._npc_cercano()
                    if npc is not None:
                        self.dialogo = {"npc": npc, "idx": 0}
                        self.estado = "dialogo"
                    elif (self.ascensor is not None and self.nivel_listo
                            and self.nivel + 1 < len(NIVELES)
                            and rj.colliderect(self.ascensor.inflate(20, 10))):
                        self.flash = 120.0
                        self.cargar_nivel(self.nivel + 1)
                        Audio.play("nivel")
                        self.textos.append(TextoFlotante(
                            self.jugador.x + 40, self.jugador.y - 40,
                            NIVELES[self.nivel]["nombre"], AZUL_NEON, 2.0))
                        guardar_partida(self)
                    elif (self.terminal is not None and not self.ecos
                            and rj.colliderect(self.terminal.inflate(45, 10))):
                        self.final_elegido = "decidir"
                        guardar_partida(self)
            elif self.final_elegido == "decidir" and ev.key in (
                    pygame.K_1, pygame.K_2, pygame.K_3):
                finales = {
                    pygame.K_1: "Revelaste la verdad. Nova Tellus ya no puede ocultar su origen.",
                    pygame.K_2: "Destruiste el eco. La ciudad conserva la paz y también la mentira.",
                    pygame.K_3: "Alteraste el recuerdo. Una nueva historia empieza a propagarse.",
                }
                self.final_elegido = finales[ev.key]
                Audio.play("terminal")
                guardar_partida(self)
        if ev.type == pygame.KEYUP and ev.key in (
                pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.jugador.soltar_salto()
        return True

    # --- Actualización ---
    def actualizar(self, dt, tiempo):
        if self.fondo is not None:
            self.fondo.update(dt)
        if self.estado != "jugando":
            return

        if self.final_elegido is None:
            self.jugador.actualizar(dt, pygame.key.get_pressed(),
                                    self.plataformas, self.ancho_mundo, touch_state)

            # Caída al vacío
            if self.jugador.y > ALTO + 80:
                self._reaparecer()

            # Zombies: fragmentos corrompidos de la memoria
            rj = self.jugador.rect()
            for z in self.zombies[:]:
                if z.muerto:
                    continue
                z.actualizar(dt)
                rz = z.rect()
                if not rj.colliderect(rz):
                    continue
                # Si Kael cae encima (stomp), dispersa al fragmento
                if self.jugador.vel_y > 60 and self.jugador.y + self.jugador.H <= rz.top + 18:
                    self.jugador.vel_y = FUERZA_SALTO * 0.62
                    self.jugador.y = rz.top - self.jugador.H
                    if z.recibir_daño():
                        self._estallido(rz)
                        Audio.play("dispersar")
                        self.textos.append(TextoFlotante(
                            rz.centerx, rz.top - 10, "DISPERSADO", VERDE_ECO))
                    else:
                        self.textos.append(TextoFlotante(
                            rz.centerx, rz.top - 10, f"x{z.vida}", (255, 220, 120)))
                    self.flash = 50.0
                elif self.jugador.recibir_daño(z.x, z.dano):
                    Audio.play("dano")
                    self.flash = 90.0
                    self.textos.append(TextoFlotante(
                        self.jugador.x + 20, self.jugador.y - 15,
                        f"-{z.dano} VIDA", ROJO_DANO))
            self.zombies = [z for z in self.zombies if not z.muerto]
            if self.jugador.vida <= 0:
                self.jugador.vida = self.jugador.vida_max
                self.textos.append(TextoFlotante(
                    self.jugador.x + 20, self.jugador.y - 15,
                    "¡EL LAGO TE RECLAMA!", ROJO_DANO, 1.6))
                self._reaparecer()

            # Recoger ecos
            for eco in self.ecos[:]:
                if rj.colliderect(eco):
                    self.ecos.remove(eco)
                    self.ecos_recuperados += 1
                    self.ecos_recuperados_nivel += 1
                    self._estallido(eco)
                    Audio.play("eco")
                    self.textos.append(TextoFlotante(
                        eco.centerx, eco.centery - 15, "+1 ECO", (120, 240, 255)))
                    self.flash = 80.0
                    guardar_partida(self)

            # Todos los ecos del nivel recuperados
            if not self.ecos and not self.nivel_listo:
                self.nivel_listo = True
                destino = "ASCENSOR" if self.ascensor is not None else "TERMINAL"
                self.textos.append(TextoFlotante(
                    self.jugador.x + 20, self.jugador.y - 40,
                    f"¡ECOS COMPLETOS! → {destino}", VERDE_ECO, 2.0))
                guardar_partida(self)

            # Ascensor: se usa pulsando E (ver manejar)

        # Partículas
        for p in self.particulas:
            p.actualizar(dt)
        self.particulas = [p for p in self.particulas if p.viva()]
        for t in self.textos:
            t.actualizar(dt)
        self.textos = [t for t in self.textos if t.viva()]

        self.flash = max(0.0, self.flash - 400 * dt)
        self.banner_nivel = max(0.0, self.banner_nivel - dt)

        # Cámara (lerp exponencial)
        objetivo = max(0, min(self.jugador.x - ANCHO * 0.38,
                              self.ancho_mundo - ANCHO))
        factor = 1 - math.exp(-14 * dt)
        self.camara_x += (objetivo - self.camara_x) * factor

        if self.final_elegido not in (None, "decidir"):
            self.fade_final = min(1.0, self.fade_final + dt * 2)

    def _estallido(self, eco):
        for _ in range(18):
            color = random.choice([(120, 240, 255), (46, 224, 255), (200, 255, 255)])
            self.particulas.append(Particula(eco.centerx, eco.centery, color))

    # --- Dibujo ---
    def dibujar(self, tiempo):
        if self.estado == "menu":
            mostrar_menu(self.opcion_menu, self.tiene_guardado, tiempo)
            return

        if self.fondo is not None:
            self.fondo.draw(pantalla, self.camara_x)
        for idx, p in enumerate(self.plataformas):
            dibujar_plataforma(p, idx, self.camara_x, tiempo)

        # Láser decorativo (barrera de energía del Archivo)
        li = int(1740 - self.camara_x)
        lf = int(1885 - self.camara_x)
        if lf > 0 and li < ANCHO:
            pygame.draw.line(pantalla, (255, 39, 102), (li, 465), (lf, 465), 3)
            pygame.draw.line(pantalla, (255, 135, 168), (li, 465), (lf, 465), 1)

        # Ascensor hacia el siguiente nivel
        if self.ascensor is not None:
            dibujar_ascensor(self.ascensor, self.camara_x, tiempo, self.nivel_listo)

        # Terminal del Archivo
        if self.terminal is not None:
            dibujar_terminal(self.terminal, self.camara_x, tiempo, self.nivel_listo)

        for eco in self.ecos:
            dibujar_eco(eco, tiempo, self.camara_x)

        # Zombies (fragmentos corrompidos de la memoria)
        for z in self.zombies:
            z.dibujar(pantalla, self.camara_x)

        # Habitantes del recuerdo con los que Kael puede hablar
        for n in self.npcs:
            n.dibujar(pantalla, self.camara_x, tiempo)

        for p in self.particulas:
            p.dibujar(pantalla, self.camara_x)

        self.jugador.dibujar(pantalla, self.camara_x, tiempo)

        for t in self.textos:
            t.dibujar(pantalla, self.camara_x)

        # Flash
        if self.flash > 0:
            flash = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            flash.fill((80, 200, 255, int(self.flash)))
            pantalla.blit(flash, (0, 0))

        # HUD
        self._hud()

        # Controles tactiles (movil)
        dibujar_touch_controls()

        # Banner de nivel
        if self.banner_nivel > 0:
            alpha = int(255 * min(1.0, self.banner_nivel))
            capa = pygame.Surface((ANCHO, 120), pygame.SRCALPHA)
            capa.fill((3, 9, 26, alpha))
            pantalla.blit(capa, (0, (ALTO - 120) // 2))
            nombre = NIVELES[self.nivel]["nombre"]
            img = fuente_titulo.render(nombre, True, AZUL_NEON)
            img.set_alpha(alpha)
            pantalla.blit(img, (ANCHO // 2 - img.get_width() // 2,
                                (ALTO - 120) // 2 + 28))
            sub = fuente_pequena.render(
                f"{len(NIVELES[self.nivel]['ecos'])} fragmentos de memoria · "
                f"{len(NIVELES[self.nivel]['npcs'])} habitantes del recuerdo",
                True, (140, 200, 230))
            sub.set_alpha(alpha)
            pantalla.blit(sub, (ANCHO // 2 - sub.get_width() // 2,
                                (ALTO - 120) // 2 + 70))

# Pausa
        if self.estado == "pausa":
            mostrar_pausa()

        # Caja de diálogo
        if self.estado == "dialogo" and self.dialogo is not None:
            dibujar_dialogo(self.dialogo["npc"], self.dialogo["idx"], tiempo)

        # Pantallas finales
        if self.final_elegido == "decidir":
            mostrar_pantalla_decision()
        elif self.final_elegido is not None:
            mostrar_pantalla_final(self.final_elegido, self.fade_final)

    def _hud(self):
        capa = pygame.Surface((ANCHO, 112), pygame.SRCALPHA)
        capa.fill((4, 10, 32, 230))
        pantalla.blit(capa, (0, 0))
        pygame.draw.line(pantalla, (33, 139, 211), (18, 108), (ANCHO - 18, 108), 1)

        dibujar_texto("ECOS DE LA MEMORIA", 18, 10, fuente_titulo, AZUL_NEON)
        dibujar_texto(f"{NIVELES[self.nivel]['nombre']}   ({self.nivel + 1}/{len(NIVELES)})",
                      20, 46, fuente, AZUL_NEON)
        total_ecos = len(NIVELES[self.nivel]["ecos"])
        restantes = total_ecos - self.ecos_recuperados_nivel
        dibujar_texto("✦", 20, 75, fuente_hud, (46, 238, 220))
        dibujar_texto(f"Ecos: {restantes}/{total_ecos}", 44, 76, fuente_hud)
        # Vidas
        for i in range(self.jugador.vida_max):
            cx = 150 + i * 22
            col = ROJO_DANO if i < self.jugador.vida else (52, 70, 96)
            pygame.draw.circle(pantalla, col, (cx, 87), 8)
            pygame.draw.circle(pantalla, (255, 255, 255, 0), (cx, 87), 8, 1)
        dibujar_texto(f"x{self.jugador.vida}", 150 + self.jugador.vida_max * 22 + 6,
                      78, fuente_hud, ROJO_DANO)

        dibujar_texto("A/D o flechas: mover   Espacio: saltar   "
                      "E: interactuar   R/Esc: menú",
                      18, 578, fuente_pequena)

        if self.final_elegido is None:
            rj = self.jugador.rect()
            npc = self._npc_cercano()
            if npc is not None:
                dibujar_texto(f"Pulsa E para hablar con {npc.nombre}.",
                              210, 529, fuente_pequena, (86, 231, 255))
            elif self.terminal is not None and rj.colliderect(
                    self.terminal.inflate(45, 10)):
                dibujar_texto("Pulsa E para sincronizar con el terminal.",
                              210, 529, fuente_pequena, (86, 231, 255))
            elif self.ascensor is not None and rj.colliderect(
                    self.ascensor.inflate(20, 10)):
                dibujar_texto("Pulsa E para tomar el ascensor." if self.nivel_listo
                              else "Recupera todos los ecos para activar el ascensor.",
                              210, 529, fuente_pequena, (86, 231, 255))
            elif self.ecos:
                dibujar_texto(
                    "Recupera los fragmentos del recuerdo de la Fundadora.",
                    210, 529, fuente_pequena, (86, 231, 255))


# ============================================================
# BUCLE PRINCIPAL
# ============================================================
def main():
    global fondo_menu
    juego = Juego()
    fondo_menu = FondoSubmarino(ANCHO, ALTO, 1, semilla=1)
    while True:
        dt = min(reloj.tick(60) / 1000.0, 0.05)
        tiempo = float(pygame.time.get_ticks())
        if fondo_menu is not None:
            fondo_menu.update(dt)
        for ev in pygame.event.get():
            if not juego.manejar(ev):
                pygame.quit()
                sys.exit()

        juego.actualizar(dt, tiempo)
        juego.dibujar(tiempo)
        pygame.display.flip()


if __name__ == "__main__":
    main()