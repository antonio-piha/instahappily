Filename: "{tmp}\{#VirtualEnvironmentPythonSetupScriptFileName}"; \
    WorkingDir: "{app}\App"; \
    Parameters: """{app}\App\"" ""{#InstallLogFile}"""; \
    StatusMsg: "Please wait... Setting up working environment. This may take a while."; \
    Flags: shellexec waituntilterminated runhidden; \
    BeforeInstall: UpdateProgressBar(70);

Filename: "{tmp}\db_migrate_installer.bat"; \
    WorkingDir: "{app}\Run"; \
    Parameters: """{app}\Run\"" ""{#InstallLogFile}"""; \
    StatusMsg: "Please wait... Applying database changes."; \
    Flags: shellexec waituntilterminated runhidden; \
    BeforeInstall: UpdateProgressBar(85); \
    AfterInstall: AfterRunStep();

;Filename: "{app}\Run\InstaHappilyService.exe"; \
;    Parameters: "--startup auto install"; \
;    StatusMsg: "Please wait... Finishing installation"; \
;    Flags: shellexec waituntilterminated runhidden; \
;    BeforeInstall: UpdateProgressBar(100);
;
;Filename: "{app}\Run\InstaHappilyService.exe"; \
;    Parameters: "start"; \
;    StatusMsg: "Please wait... Finishing installation"; \
;    Flags: shellexec waituntilterminated runhidden; \
;    BeforeInstall: UpdateProgressBar(100);


