import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import random
import os
import time
import threading
import subprocess
import psutil
import ctypes
# import winshell
import winsound
import screen_brightness_control as sbc
import pyautogui as pg
from openai import OpenAI
from dotenv import load_dotenv
from wake_listener import wait_for_wake_word 
from megan_gui import MeganGUI
import threading
from utils.linkedin import linkedin_job_flow

# ---------- Load environment ----------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- GPT integration ----------
def ask_gpt(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("GPT ERROR:", e)
        return "I'm offline or something went wrong while contacting GPT."

# ---------- Text-to-speech ----------
def speak(text):
    print("Megan:", text)
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("TTS Error:", e)
    if 'gui' in globals():
        gui.display_message("Megan", text)

# Common apps mapped to their executable names or full paths
installed_apps = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vs code": rf"C:\Users\{os.getenv('USERNAME')}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "spotify": rf"C:\Users\{os.getenv('USERNAME')}\AppData\Roaming\Spotify\Spotify.exe",
    "notepad": "notepad",
    "calculator": "calc",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",

    # ✅ New Additions
    "power bi": rf"C:\Users\{os.getenv('USERNAME')}\AppData\Local\Microsoft\Power BI Desktop\bin\PBIDesktop.exe",
    "instagram": r"C:\Users\{os.getenv('USERNAME')}\AppData\Local\Microsoft\WindowsApps\Instagram.exe",
    "telegram": r"C:\Users\{os.getenv('USERNAME')}\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "whatsapp": r"C:\Users\{os.getenv('USERNAME')}\AppData\Local\WhatsApp\WhatsApp.exe",
    "paint": "mspaint",
    "snipping tool": "snippingtool",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
}


# ---------- Voice input ----------
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in').lower()
            print("You said:", query)
            return query
        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
            return ""

# ---------- Greeting ----------
def wish_user():
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        speak("Good morning!")
    elif hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak("I am Megan. How can I help you?")

# ---------- Run shell commands ----------
def run(cmd, shell=True):
    subprocess.Popen(cmd, shell=shell, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---------- Main command execution ----------
def execute_command(cmd):
    cmd = cmd.lower()

    # ---- Time & date ----
    if "time" in cmd:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}")
    elif "date" in cmd:
        today = datetime.datetime.now().strftime("%A, %d %B %Y")
        speak(f"Today is {today}")

    # ---- Internet & browser ----
    elif "open youtube" in cmd:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif "open google" in cmd:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif "news" in cmd:
        speak("Opening Google News")
        webbrowser.open("https://news.google.com/")

    # ---- Media & folders ----
    elif "play music" in cmd:
        music_dir = r"C:\Users\Public\Music\Sample Music"
        if os.path.exists(music_dir):
            songs = [s for s in os.listdir(music_dir) if s.endswith(('.mp3', '.wav'))]
            if songs:
                speak("Playing music")
                os.startfile(os.path.join(music_dir, songs[0]))
            else:
                speak("No songs found")
        else:
            speak("Music directory not found")
    elif "open downloads" in cmd:
        os.startfile(os.path.join(os.path.expanduser("~"), "Downloads"))
        speak("Opening Downloads")
    elif "open documents" in cmd:
        os.startfile(os.path.join(os.path.expanduser("~"), "Documents"))
        speak("Opening Documents")

    # ---- Volume & brightness ----
    elif "volume up" in cmd or "increase volume" in cmd:
        for _ in range(10): pg.press("volumeup")
        speak("Volume increased")
    elif "volume down" in cmd or "decrease volume" in cmd:
        for _ in range(10): pg.press("volumedown")
        speak("Volume decreased")
    elif "mute" in cmd:
        pg.press("volumemute")
        speak("Muted")
    elif "brightness up" in cmd:
        sbc.set_brightness(min(sbc.get_brightness()[0] + 20, 100))
        speak("Brightness increased")
    elif "brightness down" in cmd:
        sbc.set_brightness(max(sbc.get_brightness()[0] - 20, 0))
        speak("Brightness decreased")

    # ---- System power ----
    elif "shutdown" in cmd and "cancel" not in cmd:
        speak("Shutting down in 10 seconds. Say cancel shutdown to stop.")
        run("shutdown /s /t 10")
    elif "restart" in cmd:
        speak("Restarting now")
        run("shutdown /r /t 5")
    elif "sleep" in cmd or "hibernate" in cmd:
        speak("Going to sleep")
        run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif "lock screen" in cmd or "lock" in cmd:
        speak("Locking screen")
        ctypes.windll.user32.LockWorkStation()
    elif "cancel shutdown" in cmd or "abort shutdown" in cmd:
        run("shutdown /a")
        speak("Shutdown aborted")

    # ---- Network ----
    elif any(w in cmd for w in ["disable wifi", "turn off wifi", "disable wi-fi", "turn off wi-fi"]):
        run("netsh interface set interface Wi-Fi admin=disable")
        speak("Wi-Fi turned off")
    elif any(w in cmd for w in ["enable wifi", "turn on wifi", "enable wi-fi", "turn on wi-fi"]):
        run("netsh interface set interface Wi-Fi admin=enable")
        speak("Wi-Fi turned on")
    elif "what is my ip" in cmd or "show ip" in cmd:
        try:
            ip = subprocess.check_output("nslookup myip.opendns.com resolver1.opendns.com", shell=True).decode().split()[-1]
            speak(f"Your public IP is {ip}")
        except:
            speak("Could not retrieve IP")

    # ---- System utilities ----
    elif "task manager" in cmd:
        speak("Opening task manager")
        run("taskmgr")
    elif "control panel" in cmd:
        speak("Opening control panel")
        run("control")
    elif "notepad" in cmd:
        speak("Opening notepad")
        run("notepad")
    elif "calculator" in cmd:
        speak("Opening calculator")
        run("calc")
    elif "camera" in cmd or "webcam" in cmd:
        speak("Opening camera")
        run("start microsoft.windows.camera:")
    elif "screenshot" in cmd:
        ts = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        path = os.path.join(os.path.expanduser("~"), "Pictures", f"screenshot_{ts}.png")
        pg.screenshot(path)
        speak("Screenshot saved in Pictures")
    # elif "clear recycle bin" in cmd:
    #     winshell.recycle_bin().empty(confirm=False, show_progress=False)
    #     speak("Recycle bin cleared")
    elif "disk usage" in cmd:
        du = psutil.disk_usage("C:\\")
        used = round(du.used / (1024**3), 1)
        total = round(du.total / (1024**3), 1)
        speak(f"Drive C has {used} GB used out of {total} GB")

    # ---- Open installed apps ----
    elif cmd.startswith("open "):
        app_name = cmd.replace("open ", "").strip()
        if app_name in installed_apps:
            speak(f"Opening {app_name}")
            run(installed_apps[app_name])
        else:
            speak(f"Sorry, I don't know how to open {app_name}")

    # ---- Clipboard and typing ----
    elif "clipboard" in cmd:
        try:
            clip = subprocess.check_output("powershell get-clipboard", shell=True).decode().strip()
            speak(clip if clip else "Clipboard is empty")
        except:
            speak("Cannot read clipboard")
    elif cmd.startswith("type "):
        text = cmd.replace("type ", "", 1)
        pg.typewrite(text, interval=0.02)
        speak("Typed")
    elif "select all" in cmd:
        pg.hotkey("ctrl", "a")
    elif "copy" in cmd:
        pg.hotkey("ctrl", "c")
        speak("Copied")
    elif "paste" in cmd:
        pg.hotkey("ctrl", "v")
        speak("Pasted")

    # ---- Alarms ----
    elif cmd.startswith("set alarm for "):
        alarm_time = cmd.replace("set alarm for ", "").strip()
        try:
            h, m = map(int, alarm_time.split())
            speak(f"Alarm set for {h}:{m:02d}")

            def alarm():
                while True:
                    now = datetime.datetime.now()
                    if now.hour == h and now.minute == m:
                        for _ in range(5):
                            winsound.Beep(1000, 1000)
                        break
                    time.sleep(20)
            threading.Thread(target=alarm, daemon=True).start()
        except:
            speak("Say set alarm for hour minute")

    # ---- Self intro ----
    elif "who are you" in cmd or "introduce yourself" in cmd:
        speak("I am Megan, your personal AI voice assistant. I can help with your system, answer questions, and keep you informed.")

    # ---- Exit ----
    elif any(w in cmd for w in ["exit", "stop", "bye"]):
        speak("Goodbye. Have a great day!")
        os._exit(0)

    # ---- LinkedIn ----
    elif "apply for" in cmd and "job" in cmd:
        speak("Scraping LinkedIn for matching jobs…")
        threading.Thread(target=linkedin_job_flow, args=(cmd,), daemon=True).start()

    # ---- GPT fallback ----
    else:
        gpt_response = ask_gpt(cmd)
        speak(gpt_response)

wake_responses = [ "I'm here!", "Yep, listening.", "Go ahead.", "What’s up?", "Yes boss?", 
                  "Okay, tell me.", "At your service.", "Let’s do this.", "All ears!", "tell me buddy"
]
def start_megan():
    wish_user()

    def megan_loop():
        global gui          # so the thread sees the gui instance created in __main__
        while True:
            gui.update_status("Waiting for wake word...")
            gui.set_listening(False)      # HUD: mic idle
            wait_for_wake_word()

            speak(random.choice(wake_responses))
            gui.update_status("Listening...")
            gui.set_listening(True)       # HUD: mic pulsing
            user_command = take_command()
            gui.set_listening(False)      # HUD: mic idle again

            if user_command:
                gui.display_message("You", user_command)
                gui.update_status("Responding...")
                execute_command(user_command)

            gui.update_status("Idle")

    threading.Thread(target=megan_loop, daemon=True).start()

# ----- GUI entry -----
if __name__ == "__main__":
    gui = MeganGUI(start_megan)
    gui.run()