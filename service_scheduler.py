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
STDOUT_LOG = os.path.join(LOG_DIR, "scheduler_service_stdout.log")
STDERR_LOG = os.path.join(LOG_DIR, "scheduler_service_stderr.log")

APP_ARGS = [
    PYTHON_EXE,
    "-m",
    "src.main_scheduler",
]


class GPIOStatusManagerSchedulerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GPIOStatusManagerScheduler"
    _svc_display_name_ = "GPIO Status Manager - Scheduler"
    _svc_description_ = (
        "Runs GPIO Status Manager scheduler for inventory, "
        "status polling and alert engine."
    )

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

        servicemanager.LogInfoMsg("GPIOStatusManager-Scheduler service starting...")
        
        # AVISO CRUCIAL A WINDOWS: Ya estamos corriendo. No lances el error de tiempo de espera.
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        # Abrimos los logs en modo "a" (append). 
        # Al no usar el "with" envolviendo el bucle eterno, evitamos bloqueos de descriptores de archivos.
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

            servicemanager.LogInfoMsg("GPIOStatusManager-Scheduler child process started.")

            while True:
                # Espera 1 segundo a ver si se solicita detener el servicio
                rc = win32event.WaitForSingleObject(self.stop_event, 1000)

                if rc == win32event.WAIT_OBJECT_0:
                    break

                # Si el proceso hijo muere, lo revivimos
                if self.proc.poll() is not None:
                    servicemanager.LogErrorMsg(
                        "GPIOStatusManager-Scheduler child exited "
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
            # Nos aseguramos de cerrar los archivos al salir
            out.close()
            err.close()

        servicemanager.LogInfoMsg("GPIOStatusManager-Scheduler service stopped.")


if __name__ == "__main__":
    # Esta estructura es obligatoria para evitar que falle al ejecutar como servicio real
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(GPIOStatusManagerSchedulerService)