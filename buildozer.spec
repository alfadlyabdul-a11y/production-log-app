[app]
title = Production Log Dashboard
package.name = prodlogapp
package.domain = org.production
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.3.0,opencv4android,requests
orientation = portrait
fullscreen = 1
android.permissions = INTERNET, CAMERA
android.api = 34
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
p4a.branch = stable
android.ndk = 25b
