const
  ChromeAppRegKey = 'Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe';
  WindowsServiceName = 'InstaHappilyService';
  WindowsServiceFilePath = '\Run\InstaHappilyService.exe';



// FUNCTIONS
// #############################################################

function IsChromeInstalled: Boolean;
begin
  { check if there is the Chrome app registration entry under the HKCU, or }
  { HKLM root key, return the result }
  Result := RegKeyExists(HKEY_CURRENT_USER, ChromeAppRegKey) or
    RegKeyExists(HKEY_LOCAL_MACHINE, ChromeAppRegKey);
end;

function GetChromeFileName(): string;
var
  S: string;
begin
  // initialize returned value to an empty string
  Result := '';
  { first attempt to read the Chrome app file name from the HKCU root key; }
  { if that fails, try to read the same from HKLM; if any of that succeed, }
  { return the obtained registry value }
  if RegQueryStringValue(HKEY_CURRENT_USER, ChromeAppRegKey, '', S) or
    RegQueryStringValue(HKEY_LOCAL_MACHINE, ChromeAppRegKey, '', S)
  then
    Result := S;
end;

// PROCEDURES
// #############################################################
procedure _Log(const S: String);
begin
   Log(Format('===> %s', [S]));
end;

procedure UpdateProgressBar(Position: Integer);
begin
  WizardForm.ProgressGauge.Position := Position * WizardForm.ProgressGauge.Max div 100;
end;

procedure WindowsServiceManager(Action: string);
var
    ResultCode: integer;
    ServiceFile: string;
begin
  ServiceFile:= ExpandConstant('{app}') + WindowsServiceFilePath;
  _Log('[WindowsServiceManager] ServiceFile=' + ServiceFile + ', Action=' + Action);
  case (Action) of
    'stop':
        Exec('net.exe', 'STOP ' + WindowsServiceName, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    'install':
        Exec(ServiceFile, '--startup auto install', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  else
    Exec(ServiceFile, Action, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  _Log('[WindowsServiceManager] Done:' + Action)
end;

procedure ManageSetupLogs();
var
  ResultCode: integer;
  InstallLogSrc: string;
  InstallLogDest: string;
begin
  InstallLogSrc := ExpandConstant('{log}');
  InstallLogDest := ExpandConstant('{app}') + '\Install\install.log';
  _Log('Moving setup logs to install log');
  Exec('cmd.exe', '/C type "' + InstallLogSrc + '" >> "' + InstallLogDest + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure CreateAppRunLink();
var
  Filename: string;
  Description: string;
  ShortcutTo: string;
  Parameters: string;
  WorkingDir: string;
  IconFilename: string;
begin
  Filename := ExpandConstant('{app}\InstaHappily.lnk');
  Description := 'InstaHappily';
  ShortcutTo := GetChromeFileName();
  Parameters := '"http://localhost:5555"';
  WorkingDir := ExpandConstant('{app}');
  IconFilename := ExpandConstant('{app}') + '\logo.ico';

  CreateShellLink(Filename, Description, ShortcutTo, Parameters, WorkingDir, IconFilename, 0, SW_HIDE);
end;

procedure BeforeFilesSection();
begin
  WindowsServiceManager('stop');
end;

// Installer helper procedures
// #############################################################
procedure AfterRunStep();
begin
  WindowsServiceManager('install');
  UpdateProgressBar(95);
  WindowsServiceManager('start');
  UpdateProgressBar(100);
end;


// INSTALL EVENTS
// #############################################################
procedure InitializeWizard;
begin
  WizardForm.LicenseAcceptedRadio.Checked := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  case CurStep of
    // ssPostInstall:
    //     begin
    //
    //     end;
    ssDone:
      begin
        ManageSetupLogs();
      end;
  end;
end;

// UNINSTALL EVENTS
// #############################################################
function InitializeUninstall(): Boolean;
begin
  // Don't stop or remove Windows service here
  Result:=True
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  case CurUninstallStep of
    usUninstall:
      begin
        // Uninstall is about to start ...insert code to perform pre-uninstall tasks here...
        WindowsServiceManager('stop');
        WindowsServiceManager('remove');
      end;
    // usPostUninstall:
    //   begin
    //     // Uninstall just finished ...insert code to perform post-uninstall tasks here...
    //   end;
  end;
end;