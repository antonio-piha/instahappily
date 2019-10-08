; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{520BD62C-1FC0-4035-BE53-52EB92944076}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppVerName}

AppUpdatesURL={#AppURL}

; Allows
AllowCancelDuringInstall=no
AllowNetworkDrive=no
AllowUNCPath=no

; Show - Hide
AlwaysShowComponentsList=no
AlwaysShowDirOnReadyPage=yes

; Install related
SourceDir="{#SourcePath}"
DefaultGroupName={#AppName}
OutputBaseFilename={#OutputBaseFilename}
OutputDir="{#InstallerSrcDir}\Output"
;SetupIconFile={#file InstallerAssetsSrcPath + "\as-above-so-below.ico"}
Compression=lzma2/ultra64
InternalCompressLevel=ultra64
SolidCompression=yes

; "Support" dialog of the Add/Remove Programs Control Panel applet
AppComments="In case of any problems with uninstallation, please contact support."
AppContact={#AppURL}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}


; Environment
ChangesEnvironment=yes
DefaultDirName="{pf}\{#AppName}"
; ExtraDiskSpaceRequired set to 100 MB in bytes
ExtraDiskSpaceRequired=104857600
;InfoAfterFile={#file InstallerAssetsSrcPath + "\infoafter.rtf"}
;InfoBeforeFile={#file InstallerAssetsSrcPath + "\infobefore.rtf"}
LicenseFile={#file InstallerAssetsSrcPath + "\license.rtf"}
RestartApplications=no
SetupLogging=yes
RestartIfNeededByRun=no

; Uninstall
Uninstallable=yes
UninstallFilesDir="{#UninstallFilesDir}"

; Cosmetic
AppCopyright="Copyright (C) 2019 Happily Ever Digital, LTD"
WizardSmallImageFile="{#InstallerImagesSrcPath}\logo_140x140.bmp"