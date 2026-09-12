import random
import time
import llm
import tts
import pygame as pg
import function as funct
import im_bot as imb
import sys_init as cfg
import web_server as wser
from datetime import datetime
from threading import Thread


def sense_voice_main():  # 语音交互主线程
    from asr import recognize_audio, record_audio
    while True:
        try:
            with open("data/db/current_asr.txt", "r", encoding="utf-8") as f:
                current_asr = f.read()
            if current_asr == "RealTime" or current_asr == "WakeWord":
                say_text = recognize_audio(record_audio())
                if len(say_text) > 1 and current_asr == "RealTime":
                    if pg.mixer.music.get_busy():
                        time.sleep(0.1)
                    else:
                        print(f"{cfg.username}：{say_text}")
                        llm.chat_preprocess(say_text)
                elif len(say_text) > 2 and current_asr == "WakeWord" and cfg.wake_word in say_text:
                    if pg.mixer.music.get_busy():
                        time.sleep(0.1)
                    else:
                        say_text = say_text.replace(cfg.wake_word + "，", "").replace(cfg.wake_word, "")
                        print(f"{cfg.username}：{say_text}")
                        llm.chat_preprocess(say_text)
            else:
                time.sleep(0.1)
        except:
            time.sleep(0.1)


# open_source_project_address:https://github.com/MewCo-AI/mewco_ai_assistant_linux
def run_ase():  # 主动感知对话线程
    def ase_chat(msg):
        print(f"{cfg.asst_name}主动感知并发起了聊天")
        llm.chat_preprocess(msg)

    def ase_hello():
        current_hour = datetime.now().time().hour
        time_area = {(0, 6): "夜深了睡不着，你来发起聊天话题吧。", (6, 9): "早上好呀，你来发起聊天话题吧。",
                     (9, 11): "上午好呀，你来发起聊天话题吧。", (11, 13): "中午好呀，你来发起聊天话题吧。",
                     (13, 17): "下午好呀，你来发起聊天话题吧。", (17, 19): "傍晚好呀，你来发起聊天话题吧。",
                     (19, 24): "晚上好呀，你来发起聊天话题吧。"}
        for (start, end), hello_msg in time_area.items():
            if start <= current_hour < end:
                ase_chat(hello_msg)
                break

    def ase_news():
        ase_chat("请你完整阅读这些新闻，然后选感兴趣的和我聊聊天，不能选择明星类、负面或令人感到不安的新闻。")

    def ase_weather():
        ase_chat(f"请你结合天气信息，和我发起话题聊聊天，例如提出生活或出行建议")

    def ase_vlm_cam():
        ase_chat("请你读取你看到的摄像头内容，务必根据其中的内容和我聊聊天。")

    def ase_context():
        ase_chat("你是我的全能助手，请你结合上下文和提示词，主动向我发起聊天话题。")

    while True:
        time.sleep(random.randint(180, 600))
        with open("data/db/current_ase.txt", "r", encoding="utf-8") as f:
            current_ase = f.read()
        if current_ase == "on":
            if cfg.run_mode == "多智能体助手":
                ase_function = random.choice([ase_hello, ase_news, ase_weather, ase_vlm_cam, ase_context])
            else:
                ase_function = random.choice([ase_hello, ase_context])
            print(ase_function)
            ase_function()


def play_welcome():
    try:
        pg.mixer.Sound("data/audio/welcome.mp3").play()
        if cfg.welcome_voice_switch == "on":
            time.sleep(2)
            tts.play_tts(f"哈喽！{cfg.username}，我是{cfg.asst_name}，{funct.get_lan_url()}")
    except Exception as e:
        print(f"未检测到声卡输出设备，错误详情：{e}")


Thread(target=wser.run_web_server).start()
Thread(target=sense_voice_main).start()
Thread(target=run_ase).start()
Thread(target=play_welcome).start()
if cfg.dingding_switch == "on":
    Thread(target=imb.run_dingding).start()
if cfg.feishu_switch == "on":
    Thread(target=imb.run_feishu).start()
if cfg.qq_switch == "on":
    Thread(target=imb.run_qqbot).start()
while True:
    time.sleep(1)
