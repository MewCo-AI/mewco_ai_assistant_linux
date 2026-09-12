import time
import psutil

last_net_io = {'sent': 0, 'recv': 0, 'time': 0}
last_disk_io = {'read_bytes': 0, 'write_bytes': 0, 'time': 0}


def get_system_load():
    try:
        load = psutil.getloadavg()
        return load[0], load[1], load[2]
    except:
        return 0, 0, 0


def get_process_count():
    try:
        return len(psutil.pids())
    except:
        return 0


def get_uptime():
    try:
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        if days > 0:
            return f"{days}天{hours}小时"
        elif hours > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{minutes}分钟"
    except:
        return "未知"


# open_source_project_address:https://github.com/MewCo-AI/mewco_ai_assistant_linux
def get_top_processes():
    processes = []
    cpu_count = psutil.cpu_count(logical=True)
    try:
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
                    'pid': info['pid'], 'name': info['name'][:30] if info['name'] else 'unknown',
                    'cpu': adjusted_cpu, 'memory': round(info['memory_percent'] or 0, 1),
                    'io_read': io_read, 'io_write': io_write})
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        cpu_top = sorted(processes, key=lambda x: x['cpu'], reverse=True)[:5]
        mem_top = sorted(processes, key=lambda x: x['memory'], reverse=True)[:5]
        disk_read_top = sorted(processes, key=lambda x: x['io_read'], reverse=True)[:5]
        disk_write_top = sorted(processes, key=lambda x: x['io_write'], reverse=True)[:5]
        return {'cpu_top': cpu_top, 'mem_top': mem_top, 'disk_read_top': disk_read_top,
                'disk_write_top': disk_write_top}
    except Exception as e:
        print(f"获取进程信息失败: {e}")
        return {'cpu_top': [], 'mem_top': [], 'disk_read_top': [], 'disk_write_top': []}


def get_network_io_speed():
    global last_net_io
    try:
        net_io = psutil.net_io_counters()
        now = time.time()
        if last_net_io['time'] == 0:
            last_net_io = {'sent': net_io.bytes_sent, 'recv': net_io.bytes_recv, 'time': now}
            return 0, 0
        delta_time = now - last_net_io['time']
        if delta_time <= 0:
            return 0, 0
        up_speed = (net_io.bytes_sent - last_net_io['sent']) / delta_time
        down_speed = (net_io.bytes_recv - last_net_io['recv']) / delta_time
        last_net_io = {'sent': net_io.bytes_sent, 'recv': net_io.bytes_recv, 'time': now}
        return max(0, up_speed), max(0, down_speed)
    except:
        return 0, 0


def get_disk_io_speed():
    global last_disk_io
    try:
        disk_io = psutil.disk_io_counters()
        now = time.time()
        if last_disk_io['time'] == 0:
            last_disk_io = {'read_bytes': disk_io.read_bytes, 'write_bytes': disk_io.write_bytes, 'time': now}
            return 0, 0
        delta_time = now - last_disk_io['time']
        if delta_time <= 0:
            return 0, 0
        read_speed = (disk_io.read_bytes - last_disk_io['read_bytes']) / delta_time
        write_speed = (disk_io.write_bytes - last_disk_io['write_bytes']) / delta_time
        last_disk_io = {'read_bytes': disk_io.read_bytes, 'write_bytes': disk_io.write_bytes, 'time': now}
        return max(0, read_speed), max(0, write_speed)
    except:
        return 0, 0
