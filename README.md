# Ecos de la Memoria

Juego de plataformas 2D en Python (pygame-ce): Kael recorre 5 niveles hundidos
de Nova Tellus recuperando "ecos" de memoria mientras evita fragmentos corrompidos.

## Requisitos
- Python 3.11+ (probado con 3.14)
- pygame-ce

## Instalación
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar
```bash
python main.py
```

## Controles
- A/D o flechas: mover
- Espacio: saltar
- E: interactuar (NPCs, ascensor, terminal)
- Esc: volver al menú
- R: reiniciar tras el final

## Estructura
- `main.py` — juego completo (niveles, entidades, HUD, guardado).
- `fondos.py` — fondos procedurales (`FondoSubmarino`) para los 5 niveles.
- `kenney_platformer-characters/` — sprites (CC0, Kenney).
- `partida.json` — guardado automático (1 slot).

## Tests
```bash
python _test_harness.py
```
Usa el driver de video dummy de SDL, no abre ventana.

## Compilar APK (Android)

El proyecto incluye `buildozer.spec` y un workflow de GitHub Actions (`.github/workflows/build-apk.yml`).

### Opción A — GitHub Actions (recomendado, sin Linux local)
1. Sube el repositorio a GitHub.
2. Ve a **Actions → Build Android APK → Run workflow**.
3. Descarga el artifact `ecos-apk` (archivo `.apk`).

### Opción B — Buildozer en Linux / WSL
```bash
sudo apt-get install -y git zip unzip openjdk-17-jdk autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip install buildozer cython
buildozer android debug
# El APK queda en bin/
```

Controles en móvil: botones en pantalla (izquierda/derecha/salto/E/pausa). El juego fuerza orientación horizontal.
## Licencia de assets
Sprites de Kenney (CC0). Código del proyecto sin licencia explícita.