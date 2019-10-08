; This is because uninstaller won't remove them if they're not empty
Type: filesandordirs; Name: "{app}\App"
Type: filesandordirs; Name: "{app}\Install"
Type: filesandordirs; Name: "{app}\InstaPy"
Type: filesandordirs; Name: "{app}\Run"
Type: files; Name: "{app}\{#AppName}.lnk"

; Two additional files were created, but let's not remove them, in case they were put there before
; drive:\WINDOWS\system32\pythoncom36.dll
; drive:\WINDOWS\system32\pywintypes36.dll