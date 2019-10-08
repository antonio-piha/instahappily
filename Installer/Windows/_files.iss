
; App
Source: "{#SourcePath}\App\*.py"; \
    DestDir: "{app}\App"; \
    BeforeInstall: BeforeFilesSection();
Source: "{#SourcePath}\App\database\*"; \
    DestDir: "{app}\App\database"; \
    Excludes: "__pycache__";
Source: "{#SourcePath}\App\database\migrations\*"; \
    DestDir: "{app}\App\database\migrations"; \
    Excludes: "__pycache__";
Source: "{#SourcePath}\App\database\migrations\versions\*"; \
    DestDir: "{app}\App\database\migrations\versions"; \
    Excludes: "__pycache__";
Source: "{#SourcePath}\App\forms\*"; \
    DestDir: "{app}\App\forms"; \
    Excludes: "__pycache__";
Source: "{#SourcePath}\App\service\*"; \
    DestDir: "{app}\App\service"; \
    Excludes: "__pycache__";
Source: "{#SourcePath}\App\follower_following_tool\*"; \
    DestDir: "{app}\App\follower_following_tool"; \
    Excludes: "__pycache__";
Source: "{#SourcePath}\App\session\*"; \
    DestDir: "{app}\App\session"; \
    Excludes: "__pycache__";
Source: "{#SourcePath}\App\templates\*"; \
    DestDir: "{app}\App\templates"; \
    Excludes: "__pycache__";
Source: "{#SourcePath}\App\utils\*"; \
    DestDir: "{app}\App\utils"; \
    Excludes: "__pycache__";
Source: "{#SourcePath}\App\view_model\*"; \
    DestDir: "{app}\App\view_model"; \
    Excludes: "__pycache__";
Source: "{#SourcePath}\App\requirements.txt"; \
    DestDir: "{app}\App";
#include "_files_statics.iss"

; InstaPy  - better to be specific to not accidentally ship something wrong
Source: "{#SourcePath}\InstaPy\instapy\*"; \
    DestDir: "{app}\InstaPy\instapy"; \
    Excludes: "*__pycache__*";
Source: "{#SourcePath}\InstaPy\proxy_extension.py"; \
    DestDir: "{app}\InstaPy";
Source: "{#SourcePath}\InstaPy\LICENSE"; \
    DestDir: "{app}\InstaPy";
Source: "{#InstallerAssetsSrcPath}\chromedriver.exe"; \
    DestDir: "{#AppAssetsDestPath}\InstaPy";

; Run - service
Source: "{#SourcePath}\Run\InstaHappilyService.exe"; \
    DestDir: "{app}\Run";
Source: "{#SourcePath}\Run\run.bat"; \
    DestDir: "{app}\Run";
Source: "{#SourcePath}\Run\db_migrate.bat"; \
    DestDir: "{app}\Run";

; Icons
Source: "{#InstallerAssetsSrcPath}\images\logo.ico"; \
    DestDir: "{app}";
; Source: "{#InstallerAssetsSrcPath}\images\*"; \
;     DestDir: "{tmp}"; \
;     Flags: deleteafterinstall;

; Tmp
Source: "{#InstallerAssetsSrcPath}\{#VirtualEnvironmentPythonSetupScriptFileName}"; \
    DestDir: "{tmp}"; \
    Flags: deleteafterinstall;
Source: "{#InstallerAssetsSrcPath}\db_migrate_installer.bat"; \
    DestDir: "{tmp}"; \
    Flags: deleteafterinstall;

; All Windows service related stuff is currently in Code, leaving for just in case
;Source: "{#InstallerAssetsSrcPath}\windows-service\*"; \
;    DestDir: "{tmp}"; \
;    Flags: deleteafterinstall;
