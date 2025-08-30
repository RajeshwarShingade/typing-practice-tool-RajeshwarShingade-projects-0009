"""
Typing Practice & Analysis Dashboard (clean, minimal-bug)
- Dark modern UI using CustomTkinter
- Matplotlib charts for WPM / Accuracy history
- Difficulty levels (Beginner, Intermediate, Advanced)
- Saves history to typing_history.csv
- Uses header/icon image if found at IMAGE_PATH
"""

import os
import time
import random
import csv
from datetime import datetime
import math

import customtkinter as ctk
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import tkinter.messagebox as messagebox

# ---------- Config ----------
IMAGE_PATH = "/mnt/data/354e585e-05f9-4f26-9f8a-a8cea97a5dba.png"
HISTORY_CSV = "typing_history.csv"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Simple sentence pools
BEGINNER_TEXTS = [
    "Type these simple words quickly",
    "Practice makes perfect",
    "Keep your fingers on the home row"
]
INTERMEDIATE_TEXTS = [
    "A quick brown fox jumps over the lazy dog",
    "Typing improves speed and accuracy with daily practice",
    "Focus on rhythm and minimize corrections"
]
ADVANCED_TEXTS = [
    "Artificial intelligence is transforming modern software engineering rapidly",
    "Punctuation, capitalization and special characters increase challenge for accuracy",
    "Consistent small sessions are better than irregular long practice sessions"
]

TIPS = [
    "Keep your eyes on the screen, not the keyboard.",
    "Use the home row position (ASDF / JKL;).",
    "Start slow: accuracy first, speed will follow.",
    "Practice daily in short sessions (10-20 minutes).",
    "Try timed sprints: 1 minute focusing on accuracy."
]

# ---------- Utility ----------
def ensure_history():
    if not os.path.exists(HISTORY_CSV):
        with open(HISTORY_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "wpm", "accuracy", "errors", "difficulty"])

def append_history(wpm, accuracy, errors, difficulty):
    ensure_history()
    with open(HISTORY_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), wpm, accuracy, errors, difficulty])

def load_history_df():
    ensure_history()
    try:
        df = pd.read_csv(HISTORY_CSV, parse_dates=["timestamp"])
        return df
    except Exception:
        return pd.DataFrame(columns=["timestamp", "wpm", "accuracy", "errors", "difficulty"])

# ---------- Main Application ----------
class TypingDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Typing Practice — Dashboard")
        self.geometry("1150x700")
        self.minsize(1000, 650)

        # State
        self.difficulty = ctk.StringVar(value="Beginner")
        self.current_text = ""
        self.start_time = None
        self.history_df = load_history_df()

        # Load header image if available
        self.header_imgtk = None
        if os.path.exists(IMAGE_PATH):
            try:
                img = Image.open(IMAGE_PATH).convert("RGBA")
                img = img.resize((200, 80), Image.LANCZOS)
                self.header_imgtk = ImageTk.PhotoImage(img)
            except Exception as e:
                print("Header image load error:", e)

        # Layout: 3 columns (left nav, center content, right stats)
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=2, uniform="col")
        self.grid_columnconfigure(2, weight=1, uniform="col")
        self.grid_rowconfigure(1, weight=1)

        self._create_header()
        self._create_left_nav()
        self._create_center()
        self._create_right()

        ensure_history()

    def _create_header(self):
        header = ctk.CTkFrame(self, height=110, corner_radius=0)
        header.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=12, pady=12)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=2)
        header.grid_columnconfigure(2, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=12)
        if self.header_imgtk:
            ctk.CTkLabel(left, image=self.header_imgtk, text="").pack(anchor="w")
        else:
            ctk.CTkLabel(left, text="Typing Practice", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w")

        center = ctk.CTkFrame(header, fg_color="transparent")
        center.grid(row=0, column=1)
        ctk.CTkLabel(center, text="Improve your typing — track speed & accuracy", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=8)

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=2, sticky="e", padx=12)
        self.header_snap_wpm = ctk.CTkLabel(right, text="WPM: -", font=ctk.CTkFont(size=14, weight="bold"))
        self.header_snap_wpm.pack(anchor="e")
        self.header_snap_acc = ctk.CTkLabel(right, text="Accuracy: -", font=ctk.CTkFont(size=12))
        self.header_snap_acc.pack(anchor="e")

    def _create_left_nav(self):
        nav = ctk.CTkFrame(self, corner_radius=8)
        nav.grid(row=1, column=0, sticky="nsew", padx=(12,6), pady=(0,12))
        nav.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(nav, text="Menu", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=8, padx=12, sticky="w")
        ctk.CTkButton(nav, text="Practice", command=lambda: None).grid(row=1, column=0, padx=12, pady=6, sticky="ew")
        ctk.CTkButton(nav, text="Reports", command=self.show_history_window).grid(row=2, column=0, padx=12, pady=6, sticky="ew")
        ctk.CTkButton(nav, text="Settings", command=lambda: None).grid(row=3, column=0, padx=12, pady=6, sticky="ew")

        ctk.CTkLabel(nav, text="Difficulty", font=ctk.CTkFont(size=13, weight="bold")).grid(row=4, column=0, pady=(18,6), padx=12, sticky="w")
        ctk.CTkOptionMenu(nav, values=["Beginner", "Intermediate", "Advanced"], variable=self.difficulty).grid(row=5, column=0, padx=12, sticky="ew")

        ctk.CTkLabel(nav, text="Quick Tips", font=ctk.CTkFont(size=13, weight="bold")).grid(row=6, column=0, pady=(20,6), padx=12, sticky="w")
        tips_text = "\n".join(["• " + t for t in TIPS[:4]])
        ctk.CTkLabel(nav, text=tips_text, wraplength=220, justify="left").grid(row=7, column=0, padx=12, pady=6, sticky="w")

    def _create_center(self):
        center = ctk.CTkFrame(self, corner_radius=8)
        center.grid(row=1, column=1, sticky="nsew", padx=6, pady=(0,12))
        center.grid_rowconfigure(2, weight=1)

        # Text card
        self.text_card = ctk.CTkFrame(center, corner_radius=8)
        self.text_card.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.lbl_text = ctk.CTkLabel(self.text_card, text="Click Start to begin a typing test", font=ctk.CTkFont(size=16), wraplength=700, justify="left")
        self.lbl_text.pack(padx=12, pady=12)

        # Input box
        self.input_box = ctk.CTkTextbox(center, height=140, font=ctk.CTkFont(size=14))
        self.input_box.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0,8))
        self.input_box.bind("<KeyRelease>", self._on_key_release)

        # Controls
        controls = ctk.CTkFrame(center, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="nsew", padx=12, pady=8)
        controls.grid_columnconfigure((0,1,2,3), weight=1)

        self.btn_start = ctk.CTkButton(controls, text="Start Test", command=self.start_test, fg_color="#6a5cff")
        self.btn_start.grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.btn_finish = ctk.CTkButton(controls, text="Finish Test", command=self.finish_test)
        self.btn_finish.grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self.btn_reset = ctk.CTkButton(controls, text="Reset", command=self.reset_input)
        self.btn_reset.grid(row=0, column=2, padx=6, pady=6, sticky="ew")
        self.btn_tip = ctk.CTkButton(controls, text="Get Tip", command=self.show_random_tip)
        self.btn_tip.grid(row=0, column=3, padx=6, pady=6, sticky="ew")

    def _create_right(self):
        right = ctk.CTkFrame(self, corner_radius=8)
        right.grid(row=1, column=2, sticky="nsew", padx=(6,12), pady=(0,12))
        right.grid_rowconfigure(3, weight=1)

        # Summary cards
        self.lbl_wpm = ctk.CTkLabel(right, text="WPM\n-", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_wpm.grid(row=0, column=0, padx=12, pady=(12,6), sticky="n")
        self.lbl_acc = ctk.CTkLabel(right, text="Accuracy\n-", font=ctk.CTkFont(size=16))
        self.lbl_acc.grid(row=1, column=0, padx=12, pady=6, sticky="n")
        self.lbl_err = ctk.CTkLabel(right, text="Errors\n-", font=ctk.CTkFont(size=14))
        self.lbl_err.grid(row=2, column=0, padx=12, pady=6, sticky="n")

        # Chart area
        chart_card = ctk.CTkFrame(right)
        chart_card.grid(row=3, column=0, padx=12, pady=8, sticky="nsew")
        ctk.CTkLabel(chart_card, text="Performance (Last sessions)", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=8, pady=(8,0))
        self.fig = Figure(figsize=(3.5,2.2), dpi=90)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#23232b")
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        self._plot_history()

    # ---------- Interactions ----------
    def start_test(self):
        level = self.difficulty.get()
        if level == "Beginner":
            self.current_text = random.choice(BEGINNER_TEXTS)
        elif level == "Intermediate":
            self.current_text = random.choice(INTERMEDIATE_TEXTS)
        else:
            self.current_text = random.choice(ADVANCED_TEXTS)

        self.lbl_text.configure(text=self.current_text)
        self.input_box.delete("1.0", "end")
        self.input_box.focus()
        self.start_time = time.time()

        # Reset live displays
        self.lbl_wpm.configure(text="WPM\n-")
        self.lbl_acc.configure(text="Accuracy\n-")
        self.lbl_err.configure(text="Errors\n-")

    def _on_key_release(self, event):
        # provide live feedback (non-blocking, safe)
        if not self.start_time:
            return
        text = self.input_box.get("1.0", "end").rstrip("\n")
        elapsed = max(0.001, time.time() - self.start_time)
        words = len(text.split())
        wpm_live = int(words / (elapsed / 60.0)) if words > 0 else 0

        correct_chars = sum(1 for i, ch in enumerate(text) if i < len(self.current_text) and ch == self.current_text[i])
        accuracy_live = int((correct_chars / max(1, len(self.current_text))) * 100)
        errors_live = max(0, len(text) - correct_chars) + max(0, len(self.current_text) - correct_chars)

        # Update small header snapshot
        self.header_snap_wpm.configure(text=f"WPM: {wpm_live}")
        self.header_snap_acc.configure(text=f"Accuracy: {accuracy_live}%")

    def finish_test(self):
        if not self.start_time:
            messagebox.showwarning("No Test", "Click 'Start Test' first.")
            return

        typed = self.input_box.get("1.0", "end").strip()
        elapsed = max(0.001, time.time() - self.start_time)
        words = len(typed.split())
        wpm = round(words / (elapsed / 60.0), 2)

        correct_chars = sum(1 for i, ch in enumerate(typed) if i < len(self.current_text) and ch == self.current_text[i])
        accuracy = int((correct_chars / max(1, len(self.current_text))) * 100)
        # errors computed as mismatches + missing/extra
        errors = max(0, len(self.current_text) - correct_chars) + max(0, len(typed) - correct_chars)

        # update UI
        self.lbl_wpm.configure(text=f"WPM\n{wpm}")
        self.lbl_acc.configure(text=f"Accuracy\n{accuracy}%")
        self.lbl_err.configure(text=f"Errors\n{errors}")
        self.header_snap_wpm.configure(text=f"WPM: {wpm}")
        self.header_snap_acc.configure(text=f"Accuracy: {accuracy}%")

        # Save history
        append_history(wpm, accuracy, errors, self.difficulty.get())
        self.history_df = load_history_df()
        self._plot_history()

        # Give a short tip
        tip = self._generate_tip(wpm, accuracy)
        messagebox.showinfo("Tip", tip)

        # lock until user starts a new test
        self.start_time = None

    def reset_input(self):
        self.input_box.delete("1.0", "end")
        self.start_time = None
        self.lbl_wpm.configure(text="WPM\n-")
        self.lbl_acc.configure(text="Accuracy\n-")
        self.lbl_err.configure(text="Errors\n-")
        self.header_snap_wpm.configure(text="WPM: -")
        self.header_snap_acc.configure(text="Accuracy: -")

    def show_random_tip(self):
        messagebox.showinfo("Tip", random.choice(TIPS))

    def _generate_tip(self, wpm, accuracy):
        if accuracy < 70:
            return "Work on accuracy first: slow down, focus on correct keystrokes, and aim for >80%."
        if wpm < 30:
            return "Beginner: practice home-row drills and keep sessions short but daily."
        if 30 <= wpm < 50:
            return "Intermediate: try timed 1-minute sprints and reduce corrections."
        return "Advanced: practice punctuation & mixed-case passages to push precision."

    # ---------- Charts ----------
    def _plot_history(self):
        self.ax.clear()
        self.ax.set_facecolor("#23232b")
        df = self.history_df
        if df.shape[0] == 0:
            self.ax.text(0.5, 0.5, "No history", color="white", ha="center", va="center")
        else:
            sub = df.tail(12)
            x = sub['timestamp'].apply(lambda t: pd.to_datetime(t).strftime("%m-%d\n%H:%M"))
            y = sub['wpm'].astype(float)
            self.ax.plot(x, y, marker='o', linewidth=2)
            self.ax.set_ylim(0, max(60, math.ceil(y.max() / 10.0) * 10))
            for label in self.ax.get_xticklabels():
                label.set_rotation(25)
                label.set_color("white")
            self.ax.set_ylabel("WPM", color="white")
        self.fig.tight_layout()
        self.canvas.draw()

    # ---------- History window ----------
    def show_history_window(self):
        df = load_history_df()
        win = ctk.CTkToplevel(self)
        win.title("Typing History")
        win.geometry("720x480")
        txt = ctk.CTkTextbox(win, width=700, height=420)
        txt.pack(padx=8, pady=8, fill="both", expand=True)
        if df.shape[0] == 0:
            txt.insert("0.0", "No history yet.")
        else:
            txt.insert("0.0", df.sort_values("timestamp", ascending=False).to_string(index=False))
        txt.configure(state="disabled")

# ---------- Run ----------
if __name__ == "__main__":
    ensure_history()
    app = TypingDashboard()
    app.mainloop()
    self.grid_columnconfigure(0, weight=0)
    self.grid_columnconfigure(1, weight=1)
    self.grid_rowconfigure(0, weight=1) 



    


#created by Mr.Rajeshwar Shingade
#GitHub : https://github.com/RajeshwarShingade
#LinkedIn : https://www.linkedin.com/in/rajeshwarshingade
#telegram : https://t.me/rajeshwarshingade



#Happy Coding
#© All Rights Reserved