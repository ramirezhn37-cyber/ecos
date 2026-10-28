import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((800, 600))

import main as M

fallos = []


def check(cond, msg):
    if cond:
        print(f"  OK   {msg}")
    else:
        print(f"  FAIL {msg}")
        fallos.append(msg)


print("== ESTRUCTURA DE NIVELES ==")
check(len(M.NIVELES) == 5, f"5 niveles definidos (hay {len(M.NIVELES)})")

TIPOS = {"errante", "corrupto", "coloso"}
for i, d in enumerate(M.NIVELES):
    n = d["nombre"]
    check(len(d["npcs"]) == 2, f"N{i+1} '{n}': 2 NPCs (hay {len(d['npcs'])})")
    check(len(d["zombies"]) >= 3, f"N{i+1}: >=3 zombies (hay {len(d['zombies'])})")
    for z in d["zombies"]:
        check(len(z) == 4 and z[3] in TIPOS,
              f"N{i+1}: tupla zombie de 4 campos, tipo valido -> {z}")
    for npc in d["npcs"]:
        check(len(npc["lineas"]) >= 3, f"N{i+1} NPC {npc['nombre']}: >=3 lineas")
        check(npc["x"] < d["ancho"], f"N{i+1} NPC {npc['nombre']}: x dentro del mundo")
    asc = d["ascensor"]
    term = d["terminal"]
    check((asc is not None) != (term is not None), f"N{i+1}: ascensor XOR terminal")
    if i < 4:
        check(asc is not None, f"N{i+1}: tiene ascensor (necesario para avanzar)")
    else:
        check(term is not None, f"N{i+1}: nivel final tiene terminal")
    if asc is not None:
        for npc in d["npcs"]:
            r = pygame.Rect(npc["x"] - 24, npc["y"] - 70, 48, 70)
            check(not asc.colliderect(r),
                  f"N{i+1}: ascensor no solapa al NPC {npc['nombre']}")

print("== ANCHOS, PLATAFORMAS E INICIO ==")
for i, d in enumerate(M.NIVELES):
    check(d["ancho"] >= 2400, f"N{i+1}: ancho {d['ancho']} suficiente")
    last = d["plataformas"][-1]
    check(last.x + last.width >= d["ancho"] - 400,
          f"N{i+1}: la ultima plataforma cubre el final del mundo")
    check(d["plataformas"][0].x == 0, f"N{i+1}: plataforma inicial en x=0")
    ix, iy = d["inicio"]
    ok = any(p.x <= ix <= p.x + p.width and abs(p.y - iy) < 120
             for p in d["plataformas"])
    check(ok, f"N{i+1}: inicio ({ix},{iy}) apoyado en una plataforma")
    fin = d["ascensor"] or d["terminal"]
    check(fin.x > d["ancho"] - 400, f"N{i+1}: ascensor/terminal cerca del final")
    check(max(e[0] for e in d["ecos"]) < d["ancho"],
          f"N{i+1}: todos los ecos dentro del mundo")

print("== INSTANCIACION DE NIVELES ==")
j = M.Juego()
for i in range(len(M.NIVELES)):
    j.cargar_nivel(i)
    check(len(j.npcs) == 2, f"N{i+1}: 2 NPCs instanciados")
    check(len(j.zombies) == len(M.NIVELES[i]["zombies"]),
          f"N{i+1}: {len(M.NIVELES[i]['zombies'])} zombies instanciados")
    check(j.ancho_mundo == M.NIVELES[i]["ancho"], f"N{i+1}: ancho_mundo correcto")
    check(j.terminal == M.NIVELES[i]["terminal"], f"N{i+1}: terminal correcto")
    check(j.ascensor == M.NIVELES[i]["ascensor"], f"N{i+1}: ascensor correcto")
    check(len(j.ecos) == len(M.NIVELES[i]["ecos"]), f"N{i+1}: ecos instanciados")

print("== VARIANTES DE ZOMBIE ==")
ESPERADO = {
    "errante": (1, 1, M.PERSONAJE_ANCHO, M.PERSONAJE_ALTO),
    "corrupto": (2, 1, M.PERSONAJE_ANCHO, M.PERSONAJE_ALTO),
    "coloso": (4, 2, M.PERSONAJE_ANCHO + 26, M.PERSONAJE_ALTO + 30),
}
for nivel_n in range(5):
    j.cargar_nivel(nivel_n)
    for z in j.zombies:
        hp, dmg, ancho, alto = ESPERADO[z.tipo]
        check(z.vida_max == hp, f"N{nivel_n+1} {z.tipo}: vida_max {hp}")
        check(z.dano == dmg, f"N{nivel_n+1} {z.tipo}: dano {dmg}")
        check(z.ancho == ancho and z.alto == alto,
              f"N{nivel_n+1} {z.tipo}: hitbox {ancho}x{alto}")
        check(z.sprites["quieto"].get_size() == (ancho, alto),
              f"N{nivel_n+1} {z.tipo}: sprite escalado a {ancho}x{alto}")

j.cargar_nivel(0)
err = next((z for z in j.zombies if z.tipo == "errante"), None)
col = next((z for z in j.zombies if z.tipo == "coloso"), None)
if not (err and col):
    for i in range(5):
        j.cargar_nivel(i)
        e = [z for z in j.zombies if z.tipo == "errante"]
        c = [z for z in j.zombies if z.tipo == "coloso"]
        if e and c:
            err, col = e[0], c[0]
            break
check(err is not None and col is not None, "hay errante y coloso para comparar")
if err and col:
    check(col.rect().width > err.rect().width, "el coloso es mas ancho que el errante")
    check(col.rect().height > err.rect().height, "el coloso es mas alto que el errante")
    check(col.vel < err.vel, "el coloso es mas lento que el errante")
    check(col.dano > err.dano, "el coloso golpea mas fuerte que el errante")

print("== STOMP Y DAÑO AL ZOMBIE ==")
for tipo, stomps in (("errante", 1), ("corrupto", 2), ("coloso", 4)):
    z = None
    for i in range(5):
        j.cargar_nivel(i)
        z = next((x for x in j.zombies if x.tipo == tipo), None)
        if z:
            break
    check(z is not None, f"existe un zombie {tipo}")
    if not z:
        continue
    for n in range(stomps - 1):
        destruido = z.recibir_daño()
        check(not destruido, f"{tipo} sobrevive al stomp {n + 1}")
        check(not z.muerto, f"{tipo} no muerto tras {n + 1} stomps")
    destruido = z.recibir_daño()
    check(destruido, f"{tipo} muere en el stomp {stomps}")
    check(z.muerto, f"{tipo} marcado como muerto")
    check(z.vida == 0, f"{tipo} con vida 0")

print("== DAÑO AL JUGADOR ==")
j.cargar_nivel(0)
jug = j.jugador
jug.reset(40, 423)
vida0 = jug.vida
tocó = jug.recibir_daño(200, 1)
check(tocó, "el jugador recibe dano")
check(jug.vida == vida0 - 1, f"pierde 1 vida ({vida0} -> {jug.vida})")
check(jug.invul > 0, "queda invulnerable tras el golpe")
tocó = jug.recibir_daño(200, 1)
check(not tocó, "el segundo golpe se ignora por invulnerabilidad")
check(jug.vida == vida0 - 1, "la vida no baja dos veces seguidas")
jug.invul = 0.0
jug.recibir_daño(200, 2)
check(jug.vida == vida0 - 3, f"el coloso quita 2 vidas (vida {jug.vida})")

print("== FONDOS (FondoSubmarino) ==")
for i in range(1, 6):
    f = M.FondoSubmarino(800, 600, i, semilla=i)
    f.update(0.016)
    surf = pygame.Surface((800, 600))
    f.draw(surf, 100.0)
    check(True, f"paleta {i}: instancia/update/draw OK ({f.nombre})")

# @@APPEND@@
