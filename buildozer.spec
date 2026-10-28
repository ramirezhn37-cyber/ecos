[app]

title = Ecos de la Memoria
package.name = ecosdelamemoria
package.domain = org.ecos

source.dir = .
source.include_exts = py,png,jpg,jpeg,json,ttf,ogg,wav
source.exclude_dirs = tests,bin,.venv,.git,__pycache__,.buildozer

version = 1.0

requirements = python3,pygame==2.5.2

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
api = 31
minapi = 21
ndk = 25b
sdk = 33
arch = arm64-v8a
allow_backup = True
android.permissions = INTERNET
