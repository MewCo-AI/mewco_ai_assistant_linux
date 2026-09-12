import json
import logging
import os
import random
import time
import psutil
import llm
import tts
import pynvml as nv
import pygame as pg
import function as funct
import function_web as funcw
import sys_init as cfg
from collections import deque
from functools import wraps
from threading import Thread
from flask import Flask, send_file, render_template_string, jsonify, request, send_from_directory, session, redirect

app = Flask(__name__, static_folder='dist')
app.secret_key = 'mewco_ai_secret_key'
logging.getLogger('werkzeug').setLevel(logging.ERROR)
history_data = {
    'cpu': deque(maxlen=360), 'memory': deque(maxlen=360), 'temp': deque(maxlen=360),
    'process': deque(maxlen=360), 'net_up': deque(maxlen=360), 'net_down': deque(maxlen=360),
    'load1': deque(maxlen=360), 'load5': deque(maxlen=360), 'load15': deque(maxlen=360),
    'disk_read': deque(maxlen=360), 'disk_write': deque(maxlen=360)}


def update_history():
    while True:
        try:
            try:
                temps = psutil.sensors_temperatures()
                temp = int(temps[next(iter(temps))][0].current)
            except:
                nv.nvmlInit()
                handle = nv.nvmlDeviceGetHandleByIndex(0)
                temp = nv.nvmlDeviceGetTemperature(handle, nv.NVML_TEMPERATURE_GPU)
                nv.nvmlShutdown()
        except:
            temp = 0
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory_percent = psutil.virtual_memory().percent
        process_cnt = funcw.get_process_count()
        load1, load5, load15 = funcw.get_system_load()
        up_speed, down_speed = funcw.get_network_io_speed()
        read_speed, write_speed = funcw.get_disk_io_speed()
        history_data['cpu'].append(cpu_percent)
        history_data['memory'].append(memory_percent)
        history_data['temp'].append(temp)
        history_data['process'].append(process_cnt)
        history_data['net_up'].append(up_speed / 1024.0)
        history_data['net_down'].append(down_speed / 1024.0)
        history_data['load1'].append(load1)
        history_data['load5'].append(load5)
        history_data['load15'].append(load15)
        history_data['disk_read'].append(read_speed / 1024.0)
        history_data['disk_write'].append(write_speed / 1024.0)
        time.sleep(2)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):  # 沿用我们已有的键名
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if str(request.form.get('password')) == str(cfg.password):
            session['logged_in'] = True
            return redirect('/')
        with open("dist/web_login.html", 'r', encoding='utf-8') as f:
            html_login = f.read()
        return render_template_string(html_login, error='密码错误')
    if session.get('logged_in'):
        return redirect('/')
    with open("dist/web_login.html", 'r', encoding='utf-8') as f:
        html_login = f.read()
    return render_template_string(html_login, error=None)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')


@app.route('/')
@login_required
def index_state():
    with open("dist/web_state.html", 'r', encoding='utf-8') as f:
        html_state = f.read()
    return render_template_string(html_state, asst_name=cfg.asst_name, username=cfg.username)


@app.route('/chat')
@login_required
def index_chat():
    with open("dist/web_chat.html", 'r', encoding='utf-8') as f:
        html_chat = f.read()
    return render_template_string(html_chat, asst_name=cfg.asst_name, username=cfg.username)


@app.route('/settings')
@login_required
def index_settings():
    with open("dist/web_settings.html", 'r', encoding='utf-8') as f:
        html_settings = f.read()
    return render_template_string(html_settings)


@app.route('/get_config')
def get_config():
    config = cfg.load_config()
    return jsonify(config)


@app.route('/save_config', methods=['POST'])
def save_config_route():
    try:
        new_config_data = request.json
        config = cfg.load_config()
        config.update(new_config_data)
        if cfg.save_config(config):
            return jsonify({"success": True, "message": "保存成功，重启软件生效"})
        else:
            return jsonify({"success": False, "message": "保存设置失败"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/live2d')
@login_required
def index_live2d():
    with open("dist/web_live2d.html", 'r', encoding='utf-8') as f:
        html_live2d = f.read()
    return render_template_string(html_live2d)


@app.route('/api/get_mouth_y')
def check_play_state():
    is_playing = pg.mixer.music.get_busy() if pg.mixer.get_init() else False
    if is_playing:
        return json.dumps({"y": random.uniform(0.1, 0.9)})
    else:
        return json.dumps({"y": 0})


@app.route('/mmd')
@login_required
def index_mmd():
    with open("dist/web_mmd.html", 'r', encoding='utf-8') as f:
        html_mmd = f.read()
    return render_template_string(html_mmd)


@app.route('/vmd')
@login_required
def index_vmd():
    with open("dist/web_mmd_vmd.html", 'r', encoding='utf-8') as f:
        html_vmd = f.read()
    return render_template_string(html_vmd)


@app.route('/vrm')
@login_required
def index_vrm():
    with open("dist/web_vrm.html", 'r', encoding='utf-8') as f:
        html_vrm = f.read()
    return render_template_string(html_vrm, model_name=cfg.vrm_model_name)


@app.route('/is_audio_playing')
def is_audio_playing():
    try:
        is_playing = pg.mixer.music.get_busy() if pg.mixer.get_init() else False
        return jsonify({'is_playing': is_playing})
    except:
        return jsonify({'is_playing': False})


@app.route('/link')
@login_required
def index_link():
    with open("dist/web_link.html", 'r', encoding='utf-8') as f:
        html_link = f.read()
    return render_template_string(html_link)


# open_source_project_address:https://github.com/MewCo-AI/mewco_ai_assistant_linux
@app.route('/focus_mode')
@login_required
def index_focus_mode():
    with open("dist/web_focus_mode.html", 'r', encoding='utf-8') as f:
        html_focus_mode = f.read()
    return render_template_string(html_focus_mode)


@app.route('/relax_mode')
@login_required
def index_relax_mode():
    with open("dist/web_relax_mode.html", 'r', encoding='utf-8') as f:
        html_relax_mode = f.read()
    return render_template_string(html_relax_mode)


@app.route('/relax_audio/<path:filename>')
def serve_relax_audio(filename):
    safe_name = os.path.basename(filename)
    audio_dir = os.path.join('data', 'audio', 'relax_mode')
    file_path = os.path.join(audio_dir, safe_name)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='audio/mpeg')
    else:
        print(f"音频文件不存在: {file_path}")
        return '', 404


@app.route('/focus_audio/<path:filename>')
def serve_focus_audio(filename):
    safe_name = os.path.basename(filename)
    audio_dir = os.path.join('data', 'audio', 'focus_mode')
    file_path = os.path.join(audio_dir, safe_name)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='audio/mpeg')
    else:
        print(f"音频文件不存在: {file_path}")
        return '', 404


@app.route('/relax_image/<path:filename>')
def serve_relax_image(filename):
    safe_name = os.path.basename(filename)
    image_dir = os.path.join('data', 'image', 'relax_mode')
    file_path = os.path.join(image_dir, safe_name)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/jpeg')
    else:
        print(f"图片文件不存在: {file_path}")
        return '', 404


@app.route('/api/link-info')
def api_link_info():
    try:
        url = f"http://{cfg.lan_ip}:{cfg.web_port}"
        qr_code = funct.gen_qr_code(url)
        return jsonify({'url': url, 'qr_code': qr_code, 'status': 'success'})
    except Exception as e:
        print(f"生成跨端信息失败: {e}")
        return jsonify({'url': '获取失败', 'qr_code': None, 'status': 'error', 'error': str(e)})


@app.route('/api/info')
def get_info():
    try:
        try:
            temps = psutil.sensors_temperatures()
            temp = int(temps[next(iter(temps))][0].current)
        except:
            nv.nvmlInit()
            handle = nv.nvmlDeviceGetHandleByIndex(0)
            temp = nv.nvmlDeviceGetTemperature(handle, nv.NVML_TEMPERATURE_GPU)
            nv.nvmlShutdown()
    except:
        temp = 0
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory_percent = psutil.virtual_memory().percent
    process_cnt = funcw.get_process_count()
    load1, load5, load15 = funcw.get_system_load()
    uptime_str = funcw.get_uptime()
    wan_info = funct.get_wan_info()
    lan_info = funct.get_lan_info()
    up_now, down_now = funcw.get_network_io_speed()
    read_now, write_now = funcw.get_disk_io_speed()
    top_processes = funcw.get_top_processes()
    cpu_history = list(history_data['cpu'])
    memory_history = list(history_data['memory'])
    temp_history = list(history_data['temp'])
    process_history = list(history_data['process'])
    net_up_history = list(history_data['net_up'])
    net_down_history = list(history_data['net_down'])
    load_history = {'load1': list(history_data['load1']), 'load5': list(history_data['load5']),
                    'load15': list(history_data['load15'])}
    disk_read_history = list(history_data['disk_read'])
    disk_write_history = list(history_data['disk_write'])
    return jsonify({
        'cpu_percent': cpu_percent, 'memory_percent': memory_percent, 'temp': temp, 'process_count': process_cnt,
        'uptime': uptime_str, 'wan_info': wan_info, 'lan_info': lan_info, 'load1': round(load1, 2),
        'load5': round(load5, 2), 'load15': round(load15, 2), 'net_speed': {'up_speed': up_now, 'down_speed': down_now},
        'disk_speed': {'read_speed': read_now, 'write_speed': write_now}, 'cpu_history': cpu_history,
        'memory_history': memory_history, 'temp_history': temp_history, 'process_history': process_history,
        'net_up_history': net_up_history, 'net_down_history': net_down_history, 'load_history': load_history,
        'disk_read_history': disk_read_history, 'disk_write_history': disk_write_history,
        'top_processes': top_processes})


@app.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.json
    message = data.get('message')
    if message:
        try:
            print(f"{cfg.username}：{message}")
            res = llm.chat_preprocess(message)
            return jsonify({'status': 'success', 'response': res})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return jsonify({'status': 'error', 'message': '消息未提供'}), 400


@app.route('/assets/<path:path>')
def serve_static(path):
    if path.endswith(".js"):
        return send_from_directory('./dist/assets', path, mimetype='application/javascript')
    return send_from_directory('./dist/assets', path)


@app.route('/data/image/ch/<path:filename>')
def serve_avatar(filename):
    return send_from_directory('./data/image/ch', filename)


@app.route('/data/image/icon/<path:filename>')
def serve_icon(filename):
    return send_from_directory('./data/image/icon', filename)


@app.route('/data/cache/cache_voice')
def serve_voice_cache():
    try:
        if os.path.exists(tts.voice_path):
            return send_file(tts.voice_path, mimetype='audio/mpeg', as_attachment=False)
        else:
            return '', 204
    except Exception as e:
        print(f"语音文件服务错误: {e}")
        return '', 404


@app.route('/assets/vrm_model/<path:filename>')
def serve_vrm_model(filename):
    return send_from_directory('dist/assets/vrm_model', filename)


@app.route('/assets/vrm_core/<path:filename>')
def serve_vrm_core(filename):
    return send_from_directory('dist/assets/vrm_core', filename)


def run_web_server():
    print(f"枫云AI助手Linux版访问网址：http://{cfg.lan_ip}:{str(cfg.web_port)}\n全部功能，请点击网页右上角功能菜单")
    if cfg.password == "mewco168":
        print("当前使用默认密码 mewco168，建议前往网页右上角功能菜单→软件设置→基本信息，修改为其他密码")
    app.run(port=cfg.web_port, host="0.0.0.0")


Thread(target=update_history, daemon=True).start()
