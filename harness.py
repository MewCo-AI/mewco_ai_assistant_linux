import json
import requests as rq
import sys_init as cfg
from openai import OpenAI


def chat_openclaw(msg):
    try:
        client = OpenAI(api_key=cfg.openclaw_api_key, base_url=f"{cfg.openclaw_gateway}/v1")
        messages = [{"role": "system", "content": cfg.openclaw_prompt}, {"role": "user", "content": msg}]
        completion = client.chat.completions.create(model=cfg.openclaw_model, messages=messages, stream=False)
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenClaw龙虾调用异常，错误详情：{e}")
        return "OpenClaw龙虾调用异常"


def chat_hermes(msg):
    try:
        client = OpenAI(base_url=f"{cfg.hermes_gateway}/v1", api_key=cfg.hermes_api_key)
        message = [{"role": "system", "content": cfg.hermes_prompt}, {"role": "user", "content": msg}]
        response = client.chat.completions.create(model=cfg.hermes_model, messages=message, stream=False)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Hermes调用异常，错误详情：{e}")
        return "Hermes调用异常"


# open_source_project_address:https://github.com/MewCo-AI/mewco_ai_assistant_linux
def chat_qwenpaw(msg):
    headers = {"Content-Type": "application/json", "X-Agent-Id": cfg.qwenpaw_agent_id}
    data = {
        "input": [{"role": "user", "content": [{"type": "text", "text": msg}]}],
        "session_id": "my-session", "user_id": "user", "channel": "console"}
    result_text = ""
    current_msg_type = None
    try:
        with rq.post(cfg.qwenpaw_url, headers=headers, json=data, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        event_data = json.loads(line[6:])
                        if not event_data:
                            continue
                        obj_type = event_data.get('object')
                        msg_type = event_data.get('type')
                        status = event_data.get('status')
                        if obj_type == 'message' and status == 'in_progress':
                            current_msg_type = msg_type
                        if obj_type == 'message' and status == 'completed':
                            current_msg_type = None
                        if obj_type == 'content' and current_msg_type == 'message':
                            text = event_data.get('text', '')
                            if event_data.get('delta', True):
                                result_text += text
        return result_text.split("</think>")[-1].strip()
    except Exception as e:
        print(f"QwenPaw调用异常，错误详情：{e}")
        return "QwenPaw调用异常"
