[app]

title = Ecos de la Memoria
package.name = ecosdelamemoria
package.domain = org.ecos

source.dir = .
source.include_exts = py,png,json,ttf,ogg,wav
source.exclude_dirs = tests,bin,.venv,.git,__pycache__

version = 1.0

requirements = python3,pygame

orientation = landscape
fullscreen = 1

osx.python_version = 3
osx.kivy_version = 1.9.1

[buildozer]
log_level = 2
warn_on_root = 1

[p4a]
bootstrap = sdl2

[android]
api = 33
minapi = 21
ndk = 25b
sdk = 33
arch = armeabi-v7a,arm64-v8a
allow_backup = True