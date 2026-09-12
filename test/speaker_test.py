import pygame
import pygame._sdl2 as sdl2

try:
    pygame.mixer.init()
    try:
        output_devices = sdl2.audio.get_audio_device_names()
        print("可用的音频输出设备列表:")
        for i, device in enumerate(output_devices):
            print(f"{i}: {device}")
    except Exception as e:
        print(f"获取音频输出设备列表时出错: {e}")
except Exception as e:
    print(f"未检测到声卡输出设备，错误详情：{e}")
