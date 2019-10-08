#include "_variables.iss"
#define OutputBaseFilename OutputBaseFilename + "-updater"

[Setup]
#include "_setup_updater.iss"

[Types]
Name: "full"; Description: "Full installation";

[Components]
Name: "mainapp"; \
    Description: "Automation software"; \
    Types: full; \
    Flags: fixed;

[Dirs]
#include "_dirs.iss"

[Files]
#include "_files.iss"

[Run]
#include "_run.iss"

[Languages]
#include "_languages.iss"

[UninstallDelete]
#include "_uninstalldelete.iss"

[Code]
#include "_code.pas"