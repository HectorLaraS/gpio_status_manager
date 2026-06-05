import os
import time
import subprocess
import sys

import win32event
import win32service
import win32serviceutil
import servicemanager


PROJECT_ROOT = r"D:\PythonGeneral\proyectos\gpio_status_manager"
PYTHON_EXE = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")

LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
STDOUT_LOG = os.path.join(LOG_DIR, "web_service_stdout.log")
STDERR_LOG = os.path.join(LOG_DIR, "web_service_stderr.log")

APP_ARGS = [
    PYTHON_EXE,
    "-m",
    "src.main_web",
]


class GPIOStatusManagerWebService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GPIOStatusManagerWeb"
    _svc_display_name_ = "GPIO Status Manager - Web"
    _svc_description_ = "Runs GPIO Status Manager Flask web dashboard."

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.proc = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()

                for _ in range(20):
                    if self.proc.poll() is not None:
                        break
                    time.sleep(0.25)

                if self.proc.poll() is None:
                    self.proc.kill()

            except Exception:
                pass

    def SvcDoRun(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        os.chdir(PROJECT_ROOT)

        servicemanager.LogInfoMsg(
            "GPIOStatusManager-Web service starting..."
        )

        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        out = open(STDOUT_LOG, "a", encoding="utf-8")
        err = open(STDERR_LOG, "a", encoding="utf-8")

        try:
            self.proc = subprocess.Popen(
                APP_ARGS,
                cwd=PROJECT_ROOT,
                stdout=out,
                stderr=err,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            servicemanager.LogInfoMsg(
                "GPIOStatusManager-Web child process started."
            )

            while True:
                rc = win32event.WaitForSingleObject(
                    self.stop_event,
                    1000,
                )

                if rc == win32event.WAIT_OBJECT_0:
                    break

                if self.proc.poll() is not None:
                    servicemanager.LogErrorMsg(
                        "GPIOStatusManager-Web child exited "
                        f"with code {self.proc.returncode}. Restarting..."
                    )

                    time.sleep(3)

                    self.proc = subprocess.Popen(
                        APP_ARGS,
                        cwd=PROJECT_ROOT,
                        stdout=out,
                        stderr=err,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )

        finally:
            out.close()
            err.close()

        servicemanager.LogInfoMsg(
            "GPIOStatusManager-Web service stopped."
        )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(
            GPIOStatusManagerWebService
        )