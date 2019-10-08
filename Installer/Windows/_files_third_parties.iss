; Tmp
Source: "{#InstallerAssetsSrcPath}\{#PythonInstallerFileName}"; \
    DestDir: "{tmp}"; \
    Components: python; \
    Flags: deleteafterinstall;
Source: "{#InstallerAssetsSrcPath}\{#ChromeInstallerFileName}"; \
    DestDir: "{tmp}"; \
    Components: chrome; \
    Flags: deleteafterinstall;
