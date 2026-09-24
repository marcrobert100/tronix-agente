[app]
title = Portaria Facial
package.name = portariafacial
package.domain = com.tronix
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
version = 1.0.0
requirements = python3,kivy,opencv-python,numpy,pyttsx3,torch,torchvision,torchaudio,facenet-pytorch,sqlite3
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0
android.permissions = CAMERA,INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECORD_AUDIO
android.features = android.hardware.camera,android.hardware.camera.autofocus
android.api = 31
android.minapi = 24
android.ndk = 25c
android.archs = arm64-v8a,armeabi-v7a
p4a.branch = master
p4a.bootstrap = sdl2
android.gradle_dependencies = 
android.add_activities = 
android.add_services = 
android.copy_libs = 1
android.allow_backup = True
android.use_androidx = True
android.enable_jetifier = True
android.debuggable = True

[buildozer]
log_level = 2
warn_on_root = 1

[presplash]
presplash.filename = %(source.dir)s/assets/presplash.png

[icon]
icon.filename = %(source.dir)s/assets/icon.png