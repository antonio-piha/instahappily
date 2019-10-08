import os
import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import traceback
from time import sleep

## We can't use psutil here because we must not rely on
## installing it in global python environment

class Service(win32serviceutil.ServiceFramework):
    _svc_name_ = "InstaHappilyService"
    _svc_display_name_ = "InstaHappily Service"
    _svc_description_ = "InstaHappily Service is responsible for running InstaHappily."
    def __init__(self, *args):
        super().__init__(*args)
        #self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
    def SvcDoRun(self):
        self.start()
        #win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
    def start(self):
        while True:
            # Keep alive and skip if it's alive
            if self.process is not None:
                # poll return - None value indicates that the process hasn’t terminated yet
                if self.process.poll() is None:
                    self.nap()
                    continue

            # Create process
            try:
                if getattr(sys, 'frozen', False):
                    # If the application is run as a bundle, the pyInstaller bootloader
                    # extends the sys module by a flag frozen=True and sets the app
                    working_directory = os.path.dirname(sys.executable)
                else:
                    working_directory = os.path.dirname(os.path.abspath(__file__))
                # Move to working dir
                os.chdir(working_directory)
                program_to_run=os.path.join(working_directory, 'run.bat')
                with open("run.log","wb") as out:
                    self.process = subprocess.Popen(
                        program_to_run,
                        cwd=working_directory,
                        stdin=subprocess.DEVNULL,
                        stdout=out,
                        stderr=out)
                servicemanager.LogInfoMsg('{} started from {} by running {}'.format(
                    self._svc_name_,
                    working_directory,
                    program_to_run
                ))
            except Exception as exc:
                error_msg = repr(exc) + traceback.format_exc() + program_to_run
                servicemanager.LogErrorMsg(error_msg)
                self.clean_process_properly()
                # Safety mechanism for slow down, but will try again
                self.nap()
                continue
    def stop(self):
        self.clean_process_properly()
        #win32event.SetEvent(self.hWaitStop)
    def clean_process_properly(self):
        if self.process is not None:
            # self.process.terminate() wouldn't kill all the child processes
            # Taskkill will bring down the entire tree
            # /F - we need to force it, otherwise error: Reason: One or more child processes of this process were still running.
            subprocess.run('TASKKILL /T /F /PID {}'.format(self.process.pid))
            # Important - to not kill somethig else
        self.process = None
    def nap(self):
        sleep(600) # 10 minutes

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(Service)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(Service)