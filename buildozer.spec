[app]

title = My AI
package.name = myai
package.domain = org.myai
version = 0.1.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,conf,bin,mdl,fst,txt

requirements = python3,kivy,pyjnius

android.permissions = RECORD_AUDIO

android.gradle_dependencies = net.java.dev.jna:jna:5.18.1@aar,com.alphacephei:vosk-android:0.3.75@aar
android.add_assets = model:model
android.enable_androidx = True
android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

orientation = portrait

android.api = 33
android.minapi = 24
android.accept_sdk_license = True

p4a.branch = develop