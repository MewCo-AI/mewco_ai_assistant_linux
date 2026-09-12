import pyaudio
import wave

FORMAT = pyaudio.paInt16  # 16位深度
CHANNELS = 1  # 单声道
RATE = 16000  # 采样率
CHUNK = 1024  # 每个缓冲区的帧数
RECORD_SECONDS = 3  # 录制时长
OUTPUT_FILENAME = "cache.wav"  # 输出文件名
audio = pyaudio.PyAudio()


def list_audio_devices():  # 获取所有可用的音频设备信息
    print("可用的音频设备：")
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        print(f"设备索引 {i}: {device_info['name']} (输入通道: {device_info['maxInputChannels']})")


list_audio_devices()
device_index = int(input("请输入要使用的麦克风设备索引: "))
device_info = audio.get_device_info_by_index(device_index)
if device_info['maxInputChannels'] < 1:
    print("错误：选择的设备不支持输入！")
    exit()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=device_index,
                    frames_per_buffer=CHUNK)
print("开始录音...")
frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
print("录音结束...")
stream.stop_stream()
stream.close()
audio.terminate()
with wave.open(OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
print(f"录音已保存到 {OUTPUT_FILENAME}")
