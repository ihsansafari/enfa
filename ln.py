import tkinter as tk
from tkinter import messagebox
import json
import os
import shutil
import threading
import time
import keyboard
import pyautogui
import pystray
from PIL import Image

# تنظیمات پیش‌فرض
default_settings = {
    "auto_start": False,
    "inactivity_interval": 10,  # فاصله زمانی عدم فعالیت (ثانیه)
    "enabled": True
}

# خوندن تنظیمات
settings = default_settings.copy()
if os.path.exists('settings.json'):
    try:
        with open('settings.json', 'r') as f:
            settings.update(json.load(f))
    except json.JSONDecodeError:
        print("خطا در خواندن تنظیمات. از پیش‌فرض استفاده می‌شه.")

# رابط کاربری
root = tk.Tk()
root.title("تنظیمات تغییر زبان")
root.geometry("300x250")

# متغیرها برای تنظیمات
auto_start_var = tk.BooleanVar(value=settings['auto_start'])
inactivity_interval_var = tk.StringVar(value=str(settings['inactivity_interval']))
enable_var = tk.BooleanVar(value=settings['enabled'])

# تابع تغییر زبان
def simulate_language_switch():
    print("تغییر زبان با Alt+Shift...")
    pyautogui.hotkey('alt', 'shift')
    time.sleep(0.2)

def is_english_text(text):
    return all(ord(char) < 128 for char in text)

# تابع اصلی تغییر زبان
def monitor_typing():
    typed_text = ""
    last_type_time = 0  # برای چک کردن از ابتدای اجرا
    checking = True     # از همون اول زبان رو چک کنه
    while True:
        if not enable_var.get():
            time.sleep(1)
            typed_text = ""
            continue
        
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            key = event.name
            print(f"کلید: {key}")
            
            current_time = time.time()
            inactivity_threshold = float(inactivity_interval_var.get())
            if current_time - last_type_time > inactivity_threshold:
                checking = True  # شروع تایپ جدید بعد از مکث
            last_type_time = current_time
            
            if len(key) == 1:
                typed_text += key
                print(f"متن: {typed_text}")
                
                if checking and len(typed_text) >= 3:
                    if is_english_text(typed_text):
                        print("متن انگلیسی. تغییر به انگلیسی...")
                        simulate_language_switch()
                    else:
                        print("متن فارسی. تغییر به فارسی...")
                        simulate_language_switch()
                    checking = False
                    typed_text = ""
            
            elif key in ['space', 'enter']:
                typed_text = ""
        
        time.sleep(0.01)

# تابع ذخیره تنظیمات
def save_settings():
    try:
        settings['auto_start'] = auto_start_var.get()
        settings['inactivity_interval'] = int(inactivity_interval_var.get())
        settings['enabled'] = enable_var.get()
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        update_startup()
        messagebox.showinfo("تنظیمات", "تنظیمات ذخیره شد!")
    except ValueError:
        messagebox.showerror("خطا", "فاصله زمانی رو عدد وارد کن!")

# تابع بوت خودکار
def update_startup():
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    exe_path = os.path.realpath(__file__.replace('.py', '.exe'))
    shortcut_path = os.path.join(startup_folder, 'LanguageChanger.exe')
    if auto_start_var.get():
        if not os.path.exists(shortcut_path) and os.path.exists(exe_path):
            shutil.copy(exe_path, shortcut_path)
    else:
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)

# سیستم تری
def minimize_to_tray():
    root.withdraw()
    image = Image.open("icon.png")
    menu = pystray.Menu(
        pystray.MenuItem("باز کردن", show_window),
        pystray.MenuItem("خروج", quit_program)
    )
    global icon
    icon = pystray.Icon("LanguageChanger", image, "تغییر زبان", menu)
    threading.Thread(target=icon.run, daemon=True).start()

def show_window():
    icon.stop()
    root.deiconify()

def quit_program():
    icon.stop()
    root.quit()

# رابط کاربری
tk.Label(root, text="تنظیمات تغییر زبان", font=("Arial", 14)).pack(pady=10)
tk.Checkbutton(root, text="فعال شدن هنگام بوت", variable=auto_start_var).pack(pady=5)
tk.Label(root, text="فاصله زمانی عدم فعالیت (ثانیه):").pack()
tk.Entry(root, textvariable=inactivity_interval_var).pack(pady=5)
tk.Checkbutton(root, text="روشن/خاموش کردن", variable=enable_var).pack(pady=5)
tk.Button(root, text="ذخیره تنظیمات", command=save_settings).pack(pady=10)

# اجرای ترد تغییر زبان
threading.Thread(target=monitor_typing, daemon=True).start()

# وقتی پنجره بسته می‌شه
root.protocol("WM_DELETE_WINDOW", minimize_to_tray)

# مدیریت Ctrl+C
try:
    root.mainloop()
except KeyboardInterrupt:
    print("برنامه با Ctrl+C بسته شد.")
    root.quit()