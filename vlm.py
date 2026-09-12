import os
import cv2
import requests as rq
import sys_init as cfg
from base64 import b64encode
from openai import OpenAI

vlm_prompt = cfg.prompt + "。你拥有图像识别能力"


def encode_image(image):  # 图片转base64
    _, buffer = cv2.imencode('.jpg', image)
    return b64encode(buffer).decode('utf-8')


def cap_picture():
    cap = cv2.VideoCapture(cfg.cam_num)
    if not cap.isOpened():
        return "无法打开摄像头"
    ret, frame = cap.read()
    cap.release()
    return frame


def vlm_preprocess(msg):
    vlm_handlers = {
        "OpenAI": openai_vlm_cam, "Ollama": ollama_vlm_cam, "LM Studio": lmstudio_vlm_cam,
        "KoboldCpp": kobold_vlm_cam, "llama.cpp": llamacpp_vlm_cam, "vLLM": vllm_vlm_cam}
    handler = vlm_handlers.get(cfg.prefer_vlm)
    if handler:
        return handler(msg)
    else:
        return "图像识别引擎未开启"


def ollama_vlm_cam(question):
    try:
        rq.get(cfg.ollama_url.replace("/v1", ""))
    except:
        os.system(f"ollama pull {cfg.ollama_vlm_model}")
    frame = cap_picture()
    base64_image = encode_image(frame)
    messages = [{"role": "system", "content": vlm_prompt},
                {"role": "user", "content": [{"type": "text", "text": question}, {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    vlm_client = OpenAI(base_url=cfg.ollama_url, api_key="ollama")
    completion = vlm_client.chat.completions.create(model=cfg.ollama_vlm_model, messages=messages)
    return completion.choices[0].message.content


# open_source_project_address:https://github.com/MewCo-AI/mewco_ai_assistant_linux
def lmstudio_vlm_cam(question):
    frame = cap_picture()
    base64_image = encode_image(frame)
    messages = [{"role": "system", "content": vlm_prompt},
                {"role": "user", "content": [{"type": "text", "text": question}, {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    vlm_client = OpenAI(base_url=cfg.lmstudio_url, api_key="lm-studio")
    completion = vlm_client.chat.completions.create(model="", messages=messages)
    return completion.choices[0].message.content


def openai_vlm_cam(question):
    frame = cap_picture()
    base64_image = encode_image(frame)
    messages = [{"role": "system", "content": vlm_prompt},
                {"role": "user", "content": [{"type": "text", "text": question}, {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    vlm_client = OpenAI(base_url=cfg.openai_url_vlm, api_key=cfg.openai_key_vlm)
    completion = vlm_client.chat.completions.create(model=cfg.openai_vlm_model, messages=messages)
    return completion.choices[0].message.content


def kobold_vlm_cam(question):
    frame = cap_picture()
    base64_image = encode_image(frame)
    messages = [{"role": "system", "content": vlm_prompt},
                {"role": "user", "content": [{"type": "text", "text": question}, {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    vlm_client = OpenAI(base_url=cfg.kobold_url, api_key="koboldcpp")
    completion = vlm_client.chat.completions.create(model="", messages=messages)
    return completion.choices[0].message.content


def llamacpp_vlm_cam(question):
    frame = cap_picture()
    base64_image = encode_image(frame)
    messages = [{"role": "system", "content": vlm_prompt},
                {"role": "user", "content": [{"type": "text", "text": question}, {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    vlm_client = OpenAI(base_url=cfg.llamacpp_url, api_key="llamacpp")
    completion = vlm_client.chat.completions.create(model="", messages=messages)
    return completion.choices[0].message.content


def vllm_vlm_cam(question):
    frame = cap_picture()
    base64_image = encode_image(frame)
    messages = [{"role": "system", "content": vlm_prompt},
                {"role": "user", "content": [{"type": "text", "text": question}, {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"}}]}]
    vlm_client = OpenAI(base_url=cfg.vllm_url, api_key="vllm")
    completion = vlm_client.chat.completions.create(model="", messages=messages)
    return completion.choices[0].message.content
