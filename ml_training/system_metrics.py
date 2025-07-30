import psutil
import mlflow
import time

try:
    import pynvml
    pynvml.nvmlInit()
    gpu_available = True
    gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
except (ImportError, pynvml.NVMLError):
    print("[WARN] pynvml not available or GPU inaccessible — GPU metrics will be skipped.")
    gpu_available = False

def log_system_metrics(stop_event, interval=10):
    while not stop_event.is_set():
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().used / 1e9  # GB
        mlflow.log_metric("cpu_percent", cpu)
        mlflow.log_metric("ram_used_gb", ram)

        if gpu_available:
            try:
                gpu_util = pynvml.nvmlDeviceGetUtilizationRates(gpu_handle).gpu
                gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle).used / 1e6  # MB
                mlflow.log_metric("gpu_util_percent", gpu_util)
                mlflow.log_metric("gpu_mem_used_mb", gpu_mem)
            except pynvml.NVMLError:
                print("[WARN] Failed to read GPU metrics this interval.")

        stop_event.wait(interval)
