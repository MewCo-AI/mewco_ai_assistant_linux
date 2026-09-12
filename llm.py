import json
import os
import random
import tts
import vlm
import requests as rq
import agent as agt
import function as funct
import harness as harn
import sys_init as cfg
from datetime import datetime
from openai import OpenAI

with open('data/db/memory.db', 'r', encoding='utf-8') as memory_file:
    try:
        openai_history = json.load(memory_file)
    except:
        openai_history = []


def current_time():  # 当前时间
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def chat_llm(msg):  # 与大语言模型对话
    if cfg.prefer_llm == "OpenAI":
        client = OpenAI(base_url=cfg.openai_url_llm, api_key=cfg.openai_key_llm)
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": cfg.prompt}]
        messages.extend(openai_history)
        completion = client.chat.completions.create(model=cfg.openai_llm_model, messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content.strip()
    elif cfg.prefer_llm == "Ollama":
        try:
            rq.get(cfg.ollama_url.replace("/v1", ""))
        except:
            os.system(f"ollama pull {cfg.ollama_llm_model}")
        client = OpenAI(base_url=cfg.ollama_url, api_key="ollama")
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": cfg.prompt}]
        messages.extend(openai_history)
        completion = client.chat.completions.create(model=cfg.ollama_llm_model, messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content.strip()
    elif cfg.prefer_llm == "LM Studio":
        client = OpenAI(base_url=cfg.lmstudio_url, api_key="lm-studio")
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": cfg.prompt}]
        messages.extend(openai_history)
        completion = client.chat.completions.create(model="", messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content.strip()
    elif cfg.prefer_llm == "KoboldCpp":
        client = OpenAI(base_url=cfg.kobold_url, api_key="koboldcpp")
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": cfg.prompt}]
        messages.extend(openai_history)
        completion = client.chat.completions.create(model="", messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content.strip()
    elif cfg.prefer_llm == "llama.cpp":
        client = OpenAI(base_url=cfg.llamacpp_url, api_key="llamacpp")
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": cfg.prompt}]
        messages.extend(openai_history)
        completion = client.chat.completions.create(model="", messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content.strip()
    elif cfg.prefer_llm == "vLLM":
        client = OpenAI(base_url=cfg.vllm_url, api_key="vllm")
        openai_history.append({"role": "user", "content": msg})
        messages = [{"role": "system", "content": cfg.prompt}]
        messages.extend(openai_history)
        completion = client.chat.completions.create(model="", messages=messages)
        openai_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content.strip()
    elif cfg.prefer_llm == "AnythingLLM":
        res = chat_anything_llm(msg)
        return res
    elif cfg.prefer_llm == "Dify":
        res = chat_dify(msg)
        return res
    elif cfg.prefer_llm == "RKLLM":
        res = chat_rkllm(msg)
        return res
    else:
        return "对话语言模型选择错误，请检查配置"


# open_source_project_address:https://github.com/MewCo-AI/mewco_ai_assistant_linux
def chat_preprocess(msg, play=True):  # 对话预处理
    if play:
        tts.stop_tts()
    try:
        if "几点" in msg or "多少点" in msg or "时间" in msg or "时候" in msg or "日期" in msg or "多少号" in msg or "几号" in msg:
            msg = f"[当前时间:{current_time()}]{msg}"
        if cfg.run_mode == "多智能体助手":
            user_task = agt.user_intent_recognition(msg)
            print(f"[系统]{cfg.asst_name}调用了[{user_task}]智能体")
            intent_handler_map = {
                "音乐播放": funct.play_music, "摄像头场景问答": vlm.vlm_preprocess, "天气查询": agt.get_weather, "热搜新闻": agt.get_news,
                "联网搜索": agt.ol_search, "IP地址查询": funct.get_lan_url, "状态查询": agt.get_state,
                "灯类智能家居控制": funct.control_ha_lamp, "风扇类智能家居控制": funct.control_ha_fan,
                "插座类智能家居控制": funct.control_ha_plug, "切换语音模式": funct.switch_asr_mode, "切换主动对话": funct.switch_ase_mode,
                "系统命令执行": agt.nl2linux_ask, "确认删除记忆": clear_chat, "确认退出": funct.exit_app, "确认重新启动": funct.reboot,
                "确认关机": funct.shutdown}
            handler = None
            for intent, func in intent_handler_map.items():
                if intent in user_task:
                    handler = func
                    break
            if handler:
                if handler in [funct.play_music, vlm.vlm_preprocess, agt.get_weather, agt.get_news, agt.ol_search, agt.nl2linux_ask, agt.get_state]:
                    res = handler(msg)
                else:
                    res = handler()
            else:
                res = chat_llm(msg)
        elif cfg.run_mode == "OpenClaw龙虾":
            res = harn.chat_openclaw(msg)
        elif cfg.run_mode == "QwenPaw":
            res = harn.chat_qwenpaw(msg)
        elif cfg.run_mode == "Hermes Agent":
            res = harn.chat_hermes(msg)
        else:
            res = chat_llm(msg)
        MEMORY_ROUNDS_MAP = {"超长记忆": 200, "长期记忆": 100, "中期记忆": 50, "短期记忆": 25}
        limit_rounds = MEMORY_ROUNDS_MAP.get(cfg.memory_mode, 10)
        current_rounds = len(openai_history) // 2
        while current_rounds > limit_rounds:
            round_to_remove = random.randint(0, current_rounds - 1) * 2
            del openai_history[round_to_remove:round_to_remove + 2]
            current_rounds = len(openai_history) // 2  # 更新当前轮数
        with open('data/db/memory.db', 'w', encoding='utf-8') as f:
            json.dump(openai_history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        res = f"服务异常：{e}"
    res = res.replace("#", "").replace("*", "")
    print(f"{cfg.asst_name}：{res}")
    if play:
        tts.play_tts(res)
    return res


def chat_dify(msg):  # Dify知识库
    headers = {"Authorization": f"Bearer {cfg.dify_key}", "Content-Type": "application/json"}
    data = {"query": msg, "inputs": {}, "response_mode": "blocking", "user": cfg.username, "conversation_id": None}
    res = rq.post(f"{cfg.dify_ip}/v1/chat-messages", headers=headers, data=json.dumps(data))
    res = res.json()['answer'].strip()
    return res


def chat_anything_llm(msg):  # AnythingLLM知识库
    url = f"{cfg.anything_llm_ip}/api/v1/workspace/{cfg.anything_llm_ws}/chat"
    headers = {"Authorization": f"Bearer {cfg.anything_llm_key}", "Content-Type": "application/json"}
    data = {"message": msg, "mode": "chat"}
    res = rq.post(url, json=data, headers=headers)
    return res.json().get("textResponse")


def chat_rkllm(msg):  # RKLLM
    res = rq.get(f"{cfg.rkllm_url}/rkllm?msg={msg}")
    res = res.json()['answer'].strip()
    return res


def clear_chat():  # 删除记忆
    global openai_history
    openai_history = []
    with open('data/db/memory.db', 'w', encoding='utf-8') as f:
        f.write("")
    return "记忆已清空"
