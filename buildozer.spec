[app]

title = Verifica!
package.name = verifica
package.domain = org.mirkosomma

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,db

version = 1.0

requirements = python3,kivy==2.3.0,kivymd==1.2.0,reportlab==4.0.9,pillow==10.1.0

orientation = portrait
fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

android.archs = arm64-v8a,armeabi-v7a

icon.filename = icon.png

presplash.filename = icon.png

android.logcat_filters = *:S python:D

[buildozer]

log_level = 2
warn_on_root = 1
