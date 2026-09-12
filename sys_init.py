import json
import socket

CONFIG_FILE = 'data/db/config.json'
DEFAULT_CONFIG_FILE = 'data/db/config_default.json'
#model_root_path = "data/model"
model_root_path = "E:/model"


def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置失败，将使用默认配置文件，错误详情: {e}")
        with open(DEFAULT_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)


def save_config(config_data):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存设置失败，错误详情: {e}")
        return False


# open_source_project_address:https://github.com/MewCo-AI/mewco_ai_assistant_linux
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('223.5.5.5', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    return ip


lan_ip = get_local_ip()
config = load_config()
prefer_asr = config["prefer_asr"]
prefer_llm = config["prefer_llm"]
prefer_tts = config["prefer_tts"]
prefer_vlm = config["prefer_vlm"]
prefer_ase = config["prefer_ase"]
username = config["username"]
asst_name = config["asst_name"]
prompt = config["prompt"]
vrm_model_name = config["vrm_model_name"]
speech_end_wait_time = config["speech_end_wait_time"]
wake_word = config["wake_word"]
mic_num = config["mic_num"]
sound_sense_switch = config["sound_sense_switch"]
sound_sense_threshold = config["sound_sense_threshold"]
voiceprint_switch = config["voiceprint_switch"]
voiceprint_threshold = config["voiceprint_threshold"]
myvoice_path = config["myvoice_path"]
openai_url_llm = config["openai_url_llm"]
openai_key_llm = config["openai_key_llm"]
openai_llm_model = config["openai_llm_model"]
openai_url_vlm = config["openai_url_vlm"]
openai_key_vlm = config["openai_key_vlm"]
openai_vlm_model = config["openai_vlm_model"]
ollama_url = config["ollama_url"]
ollama_llm_model = config["ollama_llm_model"]
ollama_vlm_model = config["ollama_vlm_model"]
lmstudio_url = config["lmstudio_url"]
anything_llm_ip = config["anything_llm_ip"]
anything_llm_ws = config["anything_llm_ws"]
anything_llm_key = config["anything_llm_key"]
dify_ip = config["dify_ip"]
dify_key = config["dify_key"]
stream_tts_switch = config["stream_tts_switch"]
edge_speaker = config["edge_speaker"]
edge_rate = config["edge_rate"]
edge_pitch = config["edge_pitch"]
vits_model_name = config["vits_model_name"]
gsv_api = config["gsv_api"]
tts_prompt = config["tts_prompt"]
ref_audio_path = config["ref_audio_path"]
tts_prompt_lang = config["tts_prompt_lang"]
gsv_lang = config["gsv_lang"]
qwentts_api = config["qwentts_api"]
voxcpm_api = config["voxcpm_api"]
index_api = config["index_api"]
custom_tts_url = config["custom_tts_url"]
custom_tts_model = config["custom_tts_model"]
custom_tts_voice = config["custom_tts_voice"]
custom_tts_key = config["custom_tts_key"]
cam_num = config["cam_num"]
ha_api = config["ha_api"]
ha_key = config["ha_key"]
entity_id_lamp = config["entity_id_lamp"]
entity_id_fan = config["entity_id_fan"]
entity_id_plug = config["entity_id_plug"]
router_ip = config["router_ip"]
weather_city = config["weather_city"]
rkllm_url = config["rkllm_url"]
welcome_voice_switch = config["welcome_voice_switch"]
web_port = config["web_port"]
run_mode = config["run_mode"]
memory_mode = config["memory_mode"]
kobold_url = config["kobold_url"]
llamacpp_url = config["llamacpp_url"]
vllm_url = config["vllm_url"]
tts_input_mode = config["tts_input_mode"]
omnivoice_api = config["omnivoice_api"]
omnivoice_design_text = config["omnivoice_design_text"]
voxcpm_design_text = config["voxcpm_design_text"]
feishu_switch = config["feishu_switch"]
feishu_app_id = config["feishu_app_id"]
feishu_app_secret = config["feishu_app_secret"]
dingding_switch = config["dingding_switch"]
dingding_client_id = config["dingding_client_id"]
dingding_client_secret = config["dingding_client_secret"]
qq_switch = config["qq_switch"]
qq_app_id = str(config["qq_app_id"])
qq_app_secret = config["qq_app_secret"]
openclaw_gateway = config["openclaw_gateway"]
openclaw_api_key = config["openclaw_api_key"]
openclaw_model = config["openclaw_model"]
openclaw_prompt = config["openclaw_prompt"]
qwenpaw_url = config["qwenpaw_url"]
qwenpaw_agent_id = config["qwenpaw_agent_id"]
hermes_gateway = config["hermes_gateway"]
hermes_api_key = config["hermes_api_key"]
hermes_prompt = config["hermes_prompt"]
hermes_model = config["hermes_model"]
password = config["password"]
