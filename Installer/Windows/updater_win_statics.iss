#include "_variables.iss"
#define OutputBaseFilename OutputBaseFilename + "-statics-updater"

[Setup]
#include "_setup_updater.iss"

[Types]
Name: "full"; Description: "Full installation";

[Components]
Name: "mainapp"; \
    Description: "Automation software"; \
    Types: full; \
    Flags: fixed;

[Files]
#include "_files_statics.iss"

[Languages]
#include "_languages.iss"

[Code]
#include "_code.pas"