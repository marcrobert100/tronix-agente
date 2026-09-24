@echo off 
C:\xampp\htdocs\agente\scrcpy\scrcpy-win64-v3.2\adb.exe shell screencap -p /sdcard/screen.png 
C:\xampp\htdocs\agente\scrcpy\scrcpy-win64-v3.2\adb.exe pull /sdcard/screen.png "C:\Users\CHCONTE RECP€ÇO\Desktop\screenshot.png" 
C:\xampp\htdocs\agente\scrcpy\scrcpy-win64-v3.2\adb.exe shell rm /sdcard/screen.png 
echo Screenshot salva no Desktop! 
pause 
