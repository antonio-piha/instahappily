; =====================================================================
#include "_variables_win32bit.iss"
; =====================================================================

[Setup]
#include "_setup.iss"

[Types]
#include "_types.iss"

[Components]
#include "_components.iss"

[Dirs]
#include "_dirs.iss"

[Files]
#include "_files.iss"
#include "_files_third_parties.iss"

[Run]
#include "_run_third_parties.iss"
#include "_run.iss"

[InstallDelete]
#include "_installdelete.iss"

[Languages]
#include "_languages.iss"

[Tasks]
#include "_tasks.iss"

[Icons]
#include "_icons.iss"

[UninstallRun]
#include "_uninstallrun.iss"

[UninstallDelete]
#include "_uninstalldelete.iss"

[Code]
#include "_code.pas"