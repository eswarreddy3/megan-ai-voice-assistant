import tkinter as tk
from tkinter import font
from math import sin, cos, pi, fmod
import colorsys
import threading
import time
from PIL import Image, ImageTk   # only for fast colour → hex

# ---------- helpers ----------
def hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

class MeganGUI:
    def __init__(self, start_callback):
        self.start_callback = start_callback

        self.root = tk.Tk()
        self.root.configure(bg='black')
        self.root.attributes('-fullscreen', True)
        # Inside __init__:
        self.fullscreen = True
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)

        # Full-screen canvas
        self.c = tk.Canvas(self.root, highlightthickness=0, bg='black')
        self.c.pack(fill='both', expand=True)

        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.cx, self.cy = w // 2, h // 2

        # ---------- HUD layers ----------
        self.ring_ids = []
        for r in range(50, 250, 40):
            self.ring_ids.append(
                self.c.create_oval(self.cx-r, self.cy-r,
                                   self.cx+r, self.cy+r,
                                   outline='', width=3))

        # ---------- chat area ----------
        pad = 70
        self.chat_bg = self.c.create_rectangle(
            pad, h-250-pad, w-pad, h-pad,
            fill='#000011', outline='', width=0)
        self.chat_txt = self.c.create_text(
            pad+20, h-250-pad+20, anchor='nw',
            font=('Consolas', 14), fill='#00ffcc', width=w-2*pad-40)

        # ---------- status ----------
        self.status_id = self.c.create_text(
            w//2, 60, text='Status: Idle', font=('Orbitron', 18),
            fill='#ffffff')

        # ---------- start button ----------
        self.btn = tk.Button(
            self.root, text='► START MEGAN',
            font=('Orbitron', 12), fg='white', bg='#00ffcc',
            activebackground='#00ff99', bd=0,
            command=self.on_start_click)
        self.btn.place(relx=1, rely=1, x=-120, y=-50, anchor='se')

        # ---------- animation variables ----------
        self.phase = 0
        self.is_listening = False
        self.animate()

    # ---------- public API  ----------
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
    def on_start_click(self):
        self.btn.config(state='disabled', text='INITIALISING…')
        self.start_callback()

    def update_status(self, txt):
        self.c.itemconfig(self.status_id, text=f'Status: {txt}')

    def display_message(self, sender, msg):
        full = f"{sender}: {msg}"
        threading.Thread(target=self._typewriter, args=(full,), daemon=True).start()

    def run(self):
        self.root.mainloop()

    # ---------- internal ----------
    def _typewriter(self, text):
        def worker():
            for i in range(1, len(text)+1):
                self.c.itemconfig(self.chat_txt, text=text[:i])
                time.sleep(0.03)
            self.c.itemconfig(self.chat_txt, text=text+"\n")
        worker()

    def animate(self):
        self.phase = (self.phase + 2) % 360
        p = self.phase / 180 * pi

        # Rainbow crawling border
        for i, rid in enumerate(self.ring_ids):
            angle = (p + i * 0.5) % (2*pi)
            col = hsv(angle / (2*pi), 1, 1)
            self.c.itemconfig(rid, outline=col)

            # Pulse size when listening
            if self.is_listening:
                pulse = 1 + 0.05 * sin(p*4 + i)
                r = (50 + i*40) * pulse
                self.c.coords(rid,
                              self.cx-r, self.cy-r,
                              self.cx+r, self.cy+r)
        self.root.after(50, self.animate)

    # ---------- extra helpers ----------
    def set_listening(self, flag):
        """Call from main.py while waiting for command"""
        self.is_listening = flag