"""Fondos procedurales para los cinco niveles de Ecos de la Memoria.
Requiere pygame o pygame-ce. No utiliza recursos externos.
"""
import math
import random
import pygame


class FondoSubmarino:
    PALETAS = {
        "profundo": ((20, 112, 151), (7, 52, 84), (2, 16, 32), (80, 170, 181), (12, 87, 115), (5, 44, 67), (3, 28, 46), (107, 211, 198)),
        "verdoso": ((17, 91, 91), (9, 56, 66), (3, 18, 28), (69, 132, 110), (13, 75, 75), (7, 44, 51), (4, 27, 36), (127, 228, 165)),
        "violeta": ((52, 47, 112), (27, 22, 72), (8, 7, 27), (96, 76, 145), (36, 29, 83), (20, 16, 52), (12, 10, 36), (189, 123, 255)),
        "abisal": ((10, 46, 58), (5, 26, 38), (1, 8, 17), (25, 70, 76), (7, 37, 48), (4, 23, 34), (2, 14, 23), (69, 238, 205)),
        "terminal": ((79, 35, 55), (40, 15, 32), (10, 4, 15), (120, 43, 64), (57, 24, 43), (32, 13, 29), (19, 7, 19), (255, 92, 119)),
    }
    NIVELES = ("profundo", "verdoso", "violeta", "abisal", "terminal")

    def __init__(self, ancho, alto, paleta="profundo", semilla=0):
        self.ancho, self.alto = max(1, int(ancho)), max(2, int(alto))
        if isinstance(paleta, int):
            paleta = self.NIVELES[max(0, min(4, paleta - 1))]
        self.nombre = paleta if paleta in self.PALETAS else "profundo"
        self.col = self.PALETAS[self.nombre]
        self.rnd = random.Random(semilla)
        self.tiempo = 0.0
        self._crear_base()
        self._crear_capas()
        self._crear_decoracion()
        self._crear_particulas()

    @staticmethod
    def _mezclar(a, b, t):
        return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

    def _crear_base(self):
        self.base = pygame.Surface((self.ancho, self.alto)).convert()
        top, mid, bottom = self.col[:3]
        for y in range(self.alto):
            f = y / max(1, self.alto - 1)
            color = self._mezclar(top, mid, f / .48) if f < .48 else self._mezclar(mid, bottom, (f - .48) / .52)
            pygame.draw.line(self.base, color, (0, y), (self.ancho, y))
        self.luz = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        if self.nombre in ("profundo", "verdoso"):
            for i in range(8):
                x = self.rnd.randint(-self.ancho // 2, self.ancho)
                w = self.rnd.randint(35, 125)
                pygame.draw.polygon(self.luz, (*self.col[7], 7),
                                    [(x, 0), (x + w, 0), (x + w * 2, self.alto), (x + w // 2, self.alto)])

    def _montana(self, altura, amplitud, frecuencia, color):
        s = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        fase = self.rnd.random() * math.tau
        puntos = [(0, self.alto)]
        for x in range(0, self.ancho + 9, 8):
            y = altura + math.sin(x * frecuencia + fase) * amplitud
            y += math.sin(x * frecuencia * 2.7 + fase * 1.8) * amplitud * .32
            puntos.append((x, round(y)))
        puntos.append((self.ancho, self.alto))
        pygame.draw.polygon(s, color, puntos)
        return s

    def _crear_capas(self):
        self.capas = [
            (self._montana(self.alto * .58, 32, .006, self.col[4]), .035),
            (self._montana(self.alto * .72, 42, .009, self.col[5]), .10),
            (self._montana(self.alto * .88, 27, .014, self.col[6]), .19),
        ]

    def _crear_decoracion(self):
        self.decoraciones = []
        for indice, (capa, factor) in enumerate(self.capas):
            s = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
            if self.nombre in ("profundo", "verdoso"):
                for _ in range(24 if indice == 2 else 12):
                    x = self.rnd.randrange(self.ancho)
                    base_y = self.rnd.randrange(int(self.alto * .83), self.alto + 30)
                    h = self.rnd.randint(30, 115)
                    color = self.col[7] if indice == 0 else self.col[3]
                    puntos = []
                    for k in range(9):
                        t = k / 8
                        puntos.append((x + math.sin(t * 4 + x) * 11 * t, base_y - h * t))
                    pygame.draw.lines(s, color, False, puntos, 2 if indice == 0 else 4)
                if self.nombre == "verdoso" and indice > 0:
                    for _ in range(8):
                        x = self.rnd.randrange(self.ancho)
                        y = self.rnd.randrange(int(self.alto * .57), int(self.alto * .87))
                        pygame.draw.rect(s, self.col[3], (x, y, 13, self.alto - y))
                        pygame.draw.rect(s, self.col[4], (x - 8, y - 7, 29, 9))
            elif self.nombre == "violeta":
                for _ in range(24):
                    x = self.rnd.randrange(self.ancho)
                    y = self.rnd.randrange(int(self.alto * .58), self.alto)
                    h = self.rnd.randint(14, 70)
                    pygame.draw.polygon(s, (*self.col[7], 105 if indice == 0 else 175),
                                        [(x - 9, y), (x, y - h), (x + 11, y), (x + 2, y + 8)])
            elif self.nombre == "abisal":
                for _ in range(12):
                    x = self.rnd.randrange(self.ancho)
                    y = self.rnd.randrange(int(self.alto * .75), self.alto)
                    pygame.draw.line(s, self.col[3], (x, self.alto), (x, y), 8)
                    pygame.draw.circle(s, (*self.col[7], 155), (x, y), self.rnd.randint(3, 8))
            else:
                for _ in range(13):
                    x = self.rnd.randrange(self.ancho)
                    y = self.rnd.randrange(int(self.alto * .55), self.alto)
                    w = self.rnd.randint(20, 65)
                    pygame.draw.rect(s, self.col[3], (x, y, w, self.alto - y))
                    pygame.draw.line(s, self.col[7], (x + 5, y + 9), (x + w - 5, y + 9), 2)
                    pygame.draw.circle(s, self.col[7], (x + w // 2, y + 22), 3)
            self.decoraciones.append((s, factor))

    def _crear_particulas(self):
        self.burbujas = []
        for _ in range(35):
            self.burbujas.append([self.rnd.uniform(0, self.ancho),
                                  self.rnd.uniform(0, self.alto),
                                  self.rnd.uniform(1.5, 5),
                                  self.rnd.uniform(12, 36), self.rnd.uniform(0, math.tau)])
        self.peces = []
        if self.nombre in ("profundo", "verdoso", "violeta"):
            for _ in range(6 if self.nombre == "profundo" else 3):
                self.peces.append([self.rnd.uniform(0, self.ancho),
                                   self.rnd.uniform(self.alto * .16, self.alto * .62),
                                   self.rnd.choice((-1, 1)) * self.rnd.uniform(12, 33),
                                   self.rnd.randint(4, 9)])
        self.polvo = [(self.rnd.randrange(self.ancho), self.rnd.randrange(self.alto),
                       self.rnd.choice((1, 1, 2))) for _ in range(90)]

    def update(self, dt):
        dt = max(0, min(float(dt), .1))
        self.tiempo += dt
        for b in self.burbujas:
            b[1] -= b[3] * dt
            if b[1] < -12:
                b[1] = self.alto + 12
                b[0] = self.rnd.uniform(0, self.ancho)
        for p in self.peces:
            p[0] += p[2] * dt
            if p[0] < -35:
                p[0] = self.ancho + 35
            elif p[0] > self.ancho + 35:
                p[0] = -35

    def _repetir(self, pantalla, surf, cam_x, factor):
        x = (-round(cam_x * factor)) % self.ancho
        pantalla.blit(surf, (x, 0))
        if x:
            pantalla.blit(surf, (x - self.ancho, 0))

    def draw(self, pantalla, cam_x=0):
        pantalla.blit(self.base, (0, 0))
        pantalla.blit(self.luz, (0, 0))
        for (capa, factor), (decoracion, _) in zip(self.capas, self.decoraciones):
            self._repetir(pantalla, capa, cam_x, factor)
            self._repetir(pantalla, decoracion, cam_x, factor)
        brillo = self.col[7]
        for x, y, radio in self.polvo:
            intensidad = .5 + .5 * math.sin(self.tiempo * 1.4 + x * .13)
            color = self._mezclar(self.col[1], brillo, .22 + intensidad * .35)
            pygame.draw.circle(pantalla, color, (x, y), radio)
        for pez in self.peces:
            x, y, vx, tam = pez
            x, y = int(x), int(y + math.sin(self.tiempo * 1.7 + x * .03) * 3)
            color = self.col[2]
            pygame.draw.ellipse(pantalla, color, (x - tam * 2, y - tam, tam * 4, tam * 2))
            direccion = 1 if vx > 0 else -1
            pygame.draw.polygon(pantalla, color, [(x - direccion * tam * 2, y),
                                                  (x - direccion * tam * 4, y - tam),
                                                  (x - direccion * tam * 4, y + tam)])
        for x, y, radio, velocidad, fase in self.burbujas:
            bx = int(x + math.sin(self.tiempo * 2 + fase) * 7)
            pygame.draw.circle(pantalla, brillo, (bx, int(y)), int(radio), 1)
        if self.nombre in ("violeta", "abisal", "terminal"):
            pulso = .5 + .5 * math.sin(self.tiempo * (2.2 if self.nombre == "terminal" else 1.2))
            x = int(self.ancho * .78)
            y = int(self.alto * .38)
            radio = int(7 + pulso * 6)
            pygame.draw.circle(pantalla, brillo, (x, y), radio, 1)
            pygame.draw.circle(pantalla, brillo, (x, y), 3)


if __name__ == "__main__":
    pygame.init()
    ANCHO, ALTO = 960, 540
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Ecos de la Memoria - Fondos (1 a 5)")
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 30)
    nivel = 1
    fondo = FondoSubmarino(ANCHO, ALTO, nivel, semilla=nivel)
    cam_x = 0
    activo = True
    while activo:
        dt = reloj.tick(60) / 1000
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                activo = False
            elif evento.type == pygame.KEYDOWN:
                if pygame.K_1 <= evento.key <= pygame.K_5:
                    nivel = evento.key - pygame.K_0
                    fondo = FondoSubmarino(ANCHO, ALTO, nivel, semilla=nivel)
        teclas = pygame.key.get_pressed()
        cam_x += (int(teclas[pygame.K_RIGHT]) - int(teclas[pygame.K_LEFT])) * 230 * dt
        fondo.update(dt)
        fondo.draw(pantalla, cam_x)
        etiqueta = fuente.render(f"Nivel {nivel} - {fondo.nombre} | 1-5 cambiar | flechas mover camara", True, (235, 245, 255))
        pantalla.blit(etiqueta, (16, 16))
        pygame.display.flip()
    pygame.quit()
