FileName: "{tmp}\{#PythonInstallerFileName}"; \
    Parameters: "/quiet InstallAllUsers=1 PrependPath=1 Include_tcltk=0"; \
    StatusMsg: "Please wait... Installing Python. This may take several minutes to finish."; \
    Components: python; \
    BeforeInstall: UpdateProgressBar(20); \
    AfterInstall: UpdateProgressBar(40);

FileName: "{tmp}\{#ChromeInstallerFileName}"; \
    StatusMsg: "Please wait... Installing Google Chrome."; \
    Components: chrome; \
    BeforeInstall: UpdateProgressBar(40); \
    AfterInstall: UpdateProgressBar(60);

