import psutil
import pynvml as nv


def get_first_sensor_temperature():
    try:
        try:
            temps = psutil.sensors_temperatures()
            temp = temps[next(iter(temps))][0].current
        except:
            nv.nvmlInit()
            handle = nv.nvmlDeviceGetHandleByIndex(0)
            temp = nv.nvmlDeviceGetTemperature(handle, nv.NVML_TEMPERATURE_GPU)
            nv.nvmlShutdown()
        print(f"温度:{temp}°C")
    except Exception as e:
        print(f"该设备不支持温度传感器，详情：{e}")


get_first_sensor_temperature()
