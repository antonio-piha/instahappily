; Create icons for opening the app
Name: "{group}\{#AppName}"; \
    Filename: "{app}\{#AppName}.lnk"; \
    BeforeInstall: CreateAppRunLink();
; Restart icon
Name: "{group}\Restart {#AppName}"; \
    Filename: "{app}\Run\InstaHappilyService.exe"; \
    Parameters: " restart"; \
    IconFilename: "{app}\logo.ico"; \
    Flags: preventpinning runminimized;
Name: "{commondesktop}\{#AppName}"; \
    Filename: "{app}\{#AppName}.lnk"; \
    Tasks: desktopicon;


; Don't create uninstall icon in start menu
;Name: "{group}\{cm:UninstallProgram,{#AppName}}"; \
;    Filename: "{uninstallexe}";