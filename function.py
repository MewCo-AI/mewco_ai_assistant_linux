import base64
import io
import os
import random
import tts
import pygame as pg
import sys_init as cfg
from pathlib import Path
from homeassistant_api import Client as hClient
from ping3 import ping
from PIL import Image
from qrcode.main import QRCode


def get_lan_info():  # 外部网络延迟查询
    try:
        net_delay = ping(cfg.router_ip, timeout=3, unit="ms")
        return f"延迟{int(net_delay)}毫秒"
    except:
        return "延迟-毫秒"


def get_wan_info():  # 外部网络延迟查询
    try:
        net_delay = ping("223.5.5.5", timeout=3, unit="ms")
        return f"延迟{int(net_delay)}毫秒"
    except:
        return "外部网络未连接"


def get_lan_url():  # 局域网地址查询
    lan_url = f"访问网址为{cfg.get_local_ip()}冒号{cfg.web_port}"
    return lan_url


def control_ha_lamp():  # Home Assistant控制灯
    try:
        client = hClient(f"{cfg.ha_api}/api/", cfg.ha_key)
        button = client.get_domain("button")
    except Exception as e:
        return f"Home Assistant配置错误，详情：{e}"
    try:
        result = button.press(entity_id=cfg.entity_id_lamp)
        if len(result) == 0:
            return "灯不在线"
    except:
        return "灯不在线"
    return "操作灯成功"


def control_ha_fan():  # Home Assistant控制风扇
    try:
        client = hClient(f"{cfg.ha_api}/api/", cfg.ha_key)
        button = client.get_domain("button")
    except Exception as e:
        return f"Home Assistant配置错误，详情：{e}"
    try:
        result = button.press(entity_id=cfg.entity_id_fan)
        if len(result) == 0:
            return "风扇不在线"
    except:
        return "风扇不在线"
    return "操作风扇成功"


def control_ha_plug():  # Home Assistant控制插座
    try:
        client = hClient(f"{cfg.ha_api}/api/", cfg.ha_key)
        button = client.get_domain("button")
    except Exception as e:
        return f"Home Assistant配置错误，详情：{e}"
    try:
        result = button.press(entity_id=cfg.entity_id_plug)
        if len(result) == 0:
            return "插座不在线"
    except:
        return "插座不在线"
    return "操作插座成功"


# open_source_project_address:https://github.com/MewCo-AI/mewco_ai_assistant_linux
def exit_app():  # 退出程序
    res = f"{cfg.asst_name}即将退出，再见"
    print(f"{cfg.asst_name}：{res}")
    tts.play_tts(res)
    os.kill(os.getpid(), 15)


def reboot():  # 重启
    res = f"{cfg.asst_name}即将重启，等会见"
    print(f"{cfg.asst_name}：{res}")
    tts.play_tts(res)
    try:
        os.system("reboot -h now")
        return "重启指令已执行"
    except:
        print("重启失败，该操作需要root权限")
        return "重启失败，该操作需要root权限"


def shutdown():  # 关机
    res = f"{cfg.asst_name}即将关机，再见"
    print(f"{cfg.asst_name}：{res}")
    tts.play_tts(res)
    try:
        os.system("shutdown -h now")
        return "关机指令已执行"
    except:
        print("关机失败，该操作需要root权限")
        return "关机失败，该操作需要root权限"


def switch_asr_mode():  # 切换语音模式
    with open("data/db/current_asr.txt", "r", encoding="utf-8") as f:
        current_asr = f.read()
    if current_asr == "RealTime":
        with open("data/db/current_asr.txt", "w", encoding="utf-8") as f:
            f.write("WakeWord")
        return "已切换为唤醒词模式"
    elif current_asr == "WakeWord":
        with open("data/db/current_asr.txt", "w", encoding="utf-8") as f:
            f.write("RealTime")
        return "已切换为实时语音模式"
    else:
        return "语音识别模式设置错误，请前往软件设置修改"


def switch_ase_mode():  # 切换主动对话模式
    with open("data/db/current_ase.txt", "r", encoding="utf-8") as f:
        current_ase = f.read()
    if current_ase == "on":
        with open("data/db/current_ase.txt", "w", encoding="utf-8") as f:
            f.write("off")
        return "已关闭主动感知对话"
    elif current_ase == "off":
        with open("data/db/current_ase.txt", "w", encoding="utf-8") as f:
            f.write("on")
        return "已开启主动感知对话"
    else:
        return "主动感知对话设置错误，请前往软件设置修改"


def play_music(msg):  # 音乐播放
    music_folder = "data/music"
    try:
        mp3_files = [f for f in os.listdir(music_folder) if f.endswith('.mp3')]
        for character in msg:
            matched_songs = [song for song in mp3_files if character in song]
            if matched_songs:
                selected_song = random.choice(matched_songs)
                song_name = selected_song.replace(".mp3", "").replace("data/music\\", "")
                break
        else:
            selected_song = random.choice(mp3_files)
            song_name = selected_song.replace(".mp3", "").replace("data/music\\", "")
        tts.play_tts(f"请欣赏我唱跳{song_name}")
        audio_path = os.path.join(music_folder, selected_song)
        pg.mixer.music.load(audio_path)
        pg.mixer.music.set_volume(0.25)
        pg.mixer.music.play()
        while pg.mixer.music.get_busy():
            pg.time.Clock().tick(1)
    except Exception as e:
        print(f"音乐播放服务出错，错误详情：{e}")
    return "音乐播放完成"


def gen_qr_code(url):
    logo_path = Path("data/image/logo.png")
    try:
        qr = QRCode(version=10, error_correction=2, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#1e293b", back_color="#ffffff").convert('RGB')
        try:
            logo = Image.open(logo_path)
            qr_width, qr_height = qr_img.size
            logo_size = qr_width // 4
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            if logo.mode == 'RGBA':
                logo = logo.convert('RGB')
            pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            qr_img.paste(logo, pos)
        except Exception as e:
            print(f"加载Logo失败: {e}")
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{base64_str}"
    except Exception as e:
        print(f"生成二维码失败: {e}")
        return None


with open("data/db/current_asr.txt", "w", encoding="utf-8") as file:
    file.write(cfg.prefer_asr)
with open("data/db/current_ase.txt", "w", encoding="utf-8") as file:
    file.write(cfg.prefer_ase)
