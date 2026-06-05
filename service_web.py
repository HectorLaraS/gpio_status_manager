import os
import sys
import time
import subprocess
import servicemanager
import win32event
import win32service
import win32serviceutil


class GPIOStatusManagerWebService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GPIOStatusManager-Web"
    _svc_display_name_ = "GPIO Status Manager - Web"
    _svc_description_ = "Runs GPIO Status Manager Flask web dashboard."

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False

        if self.process:
            self.process.terminate()

        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("GPIOStatusManager-Web service started.")

        project_root = os.path.dirname(os.path.abspath(__file__))
        python_exe = sys.executable

        os.chdir(project_root)

        while self.running:
            self.process = subprocess.Popen(
                [
                    python_exe,
                    "-m",
                    "src.main_web",
                ],
                cwd=project_root,
            )

            self.process.wait()

            if self.running:
                servicemanager.LogWarningMsg(
                    "GPIOStatusManager-Web stopped unexpectedly. Restarting in 10 seconds."
                )
                time.sleep(10)

        servicemanager.LogInfoMsg("GPIOStatusManager-Web service stopped.")


if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(GPIOStatusManagerWebService)