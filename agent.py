import platform
import subprocess
import psutil
import pynvml as nv
import requests as rq
import function as funct
import sys_init as cfg
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
from openai import OpenAI

all_task = "音乐播放、摄像头场景问答、灯类智能家居控制、风扇类智能家居控制、插座类智能家居控制、天气查询、热搜新闻、状态查询、联网搜索、IP地址查询、系统命令执行、日常闲聊"


def user_intent_recognition(msg):
    if "确认删除记忆" in msg or "确定删除记忆" in msg:
        return "确认删除记忆"
    elif "确定退出" in msg or "确认退出" in msg:
        return "确认退出"
    elif "确认重新启动" in msg or "确定重新启动" in msg:
        return "确认重新启动"
    elif "确认关机" in msg or "确定关机" in msg:
        return "确认关机"
    elif "切换" in msg and "语音" in msg:
        return "切换语音模式"
    elif "切换" in msg and "主动" in msg:
        return "切换主动对话"
    else:
        return function_llm(
            """1、你是一个严格的意图匹配器，必须完全遵守以下约束：
       - 仅从提供的意图清单中选择输出
       - 禁止添加任何解释、说明或额外文本
       - 禁止修改或扩展意图清单内容
       - 若用户意图不在清单中则输出"日常闲聊"
       2、处理流程：
       - 步骤1：将用户输入与清单进行精确匹配
       - 步骤2：找到最接近的意图项（必须完全匹配）
       - 步骤3：输出且仅输出匹配到的意图词汇""",
            f"{all_task}。上面是可以使用的意图清单，你只能在上面的意图清单中的内容进行选择输出。下面是用户的消息，请你对其中的意图进行提取：{msg}。仅需输出提取后的意图，不要输出其他内容")


def function_llm(fc_prompt, msg):  # 函数大语言模型
    messages = [{"role": "system", "content": fc_prompt}, {"role": "user", "content": msg}]
    if cfg.prefer_llm == "OpenAI":
        client = OpenAI(base_url=cfg.openai_url_llm, api_key=cfg.openai_key_llm)
        completion = client.chat.completions.create(model=cfg.openai_llm_model, messages=messages)
    elif cfg.prefer_llm == "LM Studio":
        client = OpenAI(base_url=cfg.lmstudio_url, api_key="lm-studio")
        completion = client.chat.completions.create(model="", messages=messages)
    elif cfg.prefer_llm == "KoboldCpp":
        client = OpenAI(base_url=cfg.kobold_url, api_key="koboldcpp")
        completion = client.chat.completions.create(model="", messages=messages)
    elif cfg.prefer_llm == "llama.cpp":
        client = OpenAI(base_url=cfg.llamacpp_url, api_key="llamacpp")
        completion = client.chat.completions.create(model="", messages=messages)
    elif cfg.prefer_llm == "vLLM":
        client = OpenAI(base_url=cfg.vllm_url, api_key="vllm")
        completion = client.chat.completions.create(model="", messages=messages)
    elif cfg.prefer_llm == "Ollama":
        client = OpenAI(base_url=cfg.ollama_url, api_key="ollama")
        completion = client.chat.completions.create(model=cfg.ollama_llm_model, messages=messages)
    else:
        return f"[{cfg.prefer_llm}未适配FC函数，可选择其他对话模型]"
    res = completion.choices[0].message.content
    res = res.split("</think>")[-1].strip()
    return res.replace("#", "").replace("*", "").strip()


def get_news(msg):
    def get_news_from_rss(news_url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        res = rq.get(news_url, headers=headers, timeout=5)
        xml_content = res.content.decode("utf-8")
        root1 = ET.fromstring(xml_content)
        titles = []
        for item in root1.findall(".//item"):
            title_elem = item.find("title")
            if title_elem is not None and title_elem.text:
                titles.append(title_elem.text.strip())
        result = "\n".join(titles)
        return result
    try:
        if "世界" in msg or "国际" in msg:
            news_result = get_news_from_rss("https://www.chinanews.com.cn/rss/world.xml")
        elif "财经" in msg or "经济" in msg:
            news_result = get_news_from_rss("https://www.chinanews.com.cn/rss/finance.xml")
        elif "科技" in msg or "数码" in msg:
            news_result = get_news_from_rss("https://www.ithome.com/rss")
        elif "AI" in msg or "ai" in msg or "人工智能" in msg:
            news_result = get_news_from_rss("https://www.qbitai.com/feed")
        else:
            news_result = get_news_from_rss("https://www.chinanews.com.cn/rss/society.xml")
        return function_llm(
            "请你扮演一名专业的新闻评论员和我对话，完整阅读我给你的新闻热搜，并简要地回答我的问题，输出为一段话，不要分段，不要用MarkDown格式",
            f"{news_result}。上面是完整的新闻热搜，请你根据这些热搜，分析并发表你的观点见解并回答我的问题，我的问题是：{msg}？回答不要超过100个字")
    except Exception as e:
        return f"新闻服务维护中，请一段时间后再试，错误详情：{e}"


def get_weather(msg):
    def extract_weather_city_name():  # 提取题天气城市名称
        return function_llm(
            "你是一个专业的城市名称提取器，需要把用户输入信息中想查询的城市名称提取出来。仅需输出提取后的城市名称，不要输出其他内容",
            f"下面是用户的消息，请你对其中的城市名称进行提取：{msg}。仅需输出提取后的城市名称，不要输出其他内容。如果用户输入不包含城市名称，则输出{cfg.weather_city}")

    try:
        input_city = extract_weather_city_name()
        api = f"https://wttr.in/{input_city}?format=j1&lang=zh"
        res = rq.get(api).json()["current_condition"][0]
        wind_scale = int(int(res["windspeedKmph"]) / 5)
        wind_direction = res["winddir16Point"]
        wind_map = {"SW": "西南", "NW": "西北", "SE": "东南", "NE": "东北", "N": "北", "S": "南", "E": "东",
                    "W": "西"}
        for key, value in wind_map.items():
            if key in wind_direction:
                wind_direction = value
                break
        uv_index = int(res["uvIndex"])
        uv_level_map = {3: "弱", 6: "中等", 8: "强", 11: "很强"}
        uv_index = next((level for bound, level in uv_level_map.items() if uv_index < bound), "极强")
        try:
            weather_result = f"{input_city}{res['lang_zh'][0]['value']}，气温{res['temp_C']}℃，湿度{res['humidity']}%，{wind_direction}风{wind_scale}级，紫外线{uv_index}"
        except Exception as e:
            weather_result = f"气象第三方服务异常，请检查城市名或一段时间后试，错误详情：{e}"
        return function_llm(
            "请你扮演一名专业的天气观察员和我对话，阅读我给你的天气信息，并简要地回答我的问题，输出为一句话，不要分段，不要用MarkDown格式",
            f"{weather_result}。上面是天气信息，请你根据天气信息，回答我的问题，我的问题是：{msg}？回答不要超过100个字")
    except Exception as e:
        return f"气象第三方服务异常，请检查城市名或一段时间后试，错误详情：{e}"


def ol_search(msg):  # 联网搜索
    def web_search(query):
        try:
            resp = rq.get(f"https://bing.com/search?q={query}", timeout=5)
            soup = BeautifulSoup(resp.text, "html.parser")
            snippet_list = []
            items = soup.select("li.b_algo")
            for item in items:
                try:
                    snippet_tag = item.select_one(".b_caption p")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                    snippet_list.append(snippet)
                except:
                    continue
            return "\n".join(snippet_list)
        except Exception as e1:
            print(f"搜索异常：{e1}")
            return "未获取到搜索结果"

    def extract_keyword():  # 提取搜索关键词
        return function_llm(
            "你是一个专业的搜索关键词提取器，需要把用户输入信息中想查询的重要的关键词提取出来。仅需输出提取后的重要关键词，忽略不重要的词语，不要输出其他内容，用空格分隔",
            f"下面是用户的消息，请你对其中的重要的关键词进行提取：{msg}。仅需输出提取后的重要关键词，忽略不重要的词语，不要输出其他内容，用空格分隔。")

    try:
        search_content = extract_keyword()
        print(f"搜索关键词：{search_content}")
        search_result = web_search(search_content)
        answer = function_llm(
            "你是一个专业的搜索总结助手，我输入我的问题和杂乱的内容，你输出整理好的内容为详细的一段话，不要分段，回答不要超过200个字",
            f"{search_result}。上面是完整的搜索结果，请你根据这些搜索结果，分析并回答我的问题，我的问题是：{msg}？")
        return answer
    except Exception as e:
        return f"联网搜索服务维护中，请一段时间后再试，详情：{e}"


# open_source_project_address:https://github.com/MewCo-AI/mewco_ai_assistant_linux
def nl2linux_ask(question):
    def get_system_info():
        info = {"os_name": platform.system(), "os_version": platform.release(),
                "kernel": platform.release(), "architecture": platform.machine()}
        return (f"当前系统信息：\n"
                f"- 操作系统：{info['os_name']}\n"
                f"- 系统版本：{info['os_version']}\n"
                f"- 内核版本：{info['kernel']}\n"
                f"- 架构：{info['architecture']}\n")
    DANGER_KEYWORDS = {"rm -rf", "mkfs", "dd", "shred", "passwd", "useradd", "reboot", "halt", "shutdown", "poweroff",
                       ">/dev/sd", "fdisk", "parted", "format", "init"}
    system_info = get_system_info()
    system_prompt = f"""
    你是专业Linux命令生成助手。
    {system_info}
    规则：
    1. 只能生成安全的命令，禁止任何提权、关机、格式化等风险操作
    2. 禁止使用以下危险命令或关键词：{', '.join(DANGER_KEYWORDS)}
    3. 只返回最终命令，不要任何解释、文字、符号
    4. 无法安全回答则返回：SAFE_BLOCK
    """.strip()
    try:
        cmd = function_llm(system_prompt, question)
        print(f"生成的命令：{cmd}")
    except Exception as e:
        return f"命令生成失败，错误详情：{e}"
    if cmd == "SAFE_BLOCK":
        return "🛡️ 安全拦截：该问题无法用安全命令完成"
    lower_cmd = cmd.lower()
    for kw in DANGER_KEYWORDS:
        if kw in lower_cmd:
            return f"🛡️ 安全拦截：命令包含危险关键词「{kw}」"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5, executable="/bin/bash")
        stdout = result.stdout
        print(f"命令执行输出：{stdout}")
        stderr = result.stderr
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        return "⌛ 命令执行超时"
    except Exception as e:
        return f"命令执行异常，错误详情：{e}"
    analysis_prompt = f"""
    {system_info}
    执行命令：{cmd}
    退出码：{exit_code}
    输出：
    {stdout}
    错误：
    {stderr}
    请用简洁中文回答用户问题。
    """
    try:
        answer = function_llm(analysis_prompt, question)
    except Exception as e:
        return f"命令结果分析失败，错误详情：{e}"
    return answer


def get_state(msg):  # 系统状态查询
    def get_top_info():
        cpu_count = psutil.cpu_count(logical=True)
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if info['name'] and 'System Idle Process' in info['name']:
                    continue
                if info['cpu_percent'] == 0 and info['memory_percent'] == 0:
                    continue
                try:
                    io_counters = proc.io_counters()
                    io_read = io_counters.read_bytes if io_counters else 0
                    io_write = io_counters.write_bytes if io_counters else 0
                except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError, Exception):
                    io_read = 0
                    io_write = 0
                adjusted_cpu = round((info['cpu_percent'] or 0) / cpu_count, 1)
                processes.append({
                    'name': info['name'][:20] if info['name'] else 'unknown','cpu': adjusted_cpu,
                    'mem': round(info['memory_percent'] or 0, 1), 'io_read': io_read, 'io_write': io_write})
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        cpu_top = sorted(processes, key=lambda x: x['cpu'], reverse=True)[:5]
        mem_top = sorted(processes, key=lambda x: x['mem'], reverse=True)[:5]
        io_top = sorted(processes, key=lambda x: x['io_read'] + x['io_write'], reverse=True)[:5]
        cpu_str = "、".join([f"{p['name']}({p['cpu']}%)" for p in cpu_top]) if cpu_top else "无"
        mem_str = "、".join([f"{p['name']}({p['mem']}%)" for p in mem_top]) if mem_top else "无"
        io_str = "、".join([f"{p['name']}" for p in io_top]) if io_top else "无"
        return f"CPU占用前5：{cpu_str}。内存占用前5：{mem_str}。磁盘IO前5：{io_str}"

    try:
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
        disk_io = psutil.disk_io_counters()
        disk_read_mb = disk_io.read_bytes / (1024 * 1024)
        disk_write_mb = disk_io.write_bytes / (1024 * 1024)
        disk_io_info = f"磁盘总读取{disk_read_mb:.1f}MB，总写入{disk_write_mb:.1f}MB"
        system_state = (f"温度{temp}度，处理器使用率{psutil.cpu_percent(interval=1)}%，"
                        f"内存使用率{psutil.virtual_memory().percent}%，{disk_io_info}，"
                        f"外部网络{funct.get_wan_info()}，内部网络{funct.get_lan_info()}。{get_top_info()}")
        return function_llm(
            "请你扮演一名专业的系统状态分析员和我对话，阅读我给你的系统状态信息，并简要地回答我的问题，输出为一句话，不要分段，不要用MarkDown格式",
            f"{system_state}。上面是系统状态，请你根据系统状态，回答我的问题，我的问题是：{msg}？回答不要超过150个字")
    except Exception as e:
        return f"获取系统状态失败，请稍后重试，错误详情：{e}"
