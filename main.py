import tkinter as tk
import math
import random
import time
import pygame

pygame.mixer.init()

som_acerto = pygame.mixer.Sound("hit.wav")
som_great = pygame.mixer.Sound("great.wav")
som_erro = pygame.mixer.Sound("fail.wav")

class SkillCheck:
    def __init__(self, canvas, x, y, r):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.r = r
        self.active = False
        self.angle = 0
        self.speed = 6
        self.zone_size = 40
        self.great_size = 10
        self.zone_start = random.randint(0, 360)

    def start(self, speed=None, zone_size=None):
        self.angle = 0
        self.active = True
        if speed is not None:
            self.speed = speed
        if zone_size is not None:
            self.zone_size = zone_size
        self.zone_start = random.randint(0, 360)
        self.draw()

    def draw(self):
        self.canvas.delete("skillcheck")
        self.canvas.create_oval(self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r,
                                outline="white", width=2, tags="skillcheck")
        self.canvas.create_arc(self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r,
                               start=self.zone_start, extent=self.zone_size,
                               style=tk.ARC, width=8, outline="yellow", tags="skillcheck")
        great_start = self.zone_start + (self.zone_size - self.great_size) / 2
        self.canvas.create_arc(self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r,
                               start=great_start, extent=self.great_size,
                               style=tk.ARC, width=8, outline="orange", tags="skillcheck")
        rad = math.radians(self.angle)
        x2 = self.x + self.r * math.cos(rad)
        y2 = self.y - self.r * math.sin(rad)
        self.canvas.create_line(self.x, self.y, x2, y2, fill="cyan", width=3, tags="skillcheck")

    def update(self):
        if not self.active:
            return
        self.angle = (self.angle + self.speed) % 360
        self.draw()

    def check_hit(self):
        if not self.active:
            return False, False
        delta = (self.angle - self.zone_start) % 360
        if delta < self.zone_size:
            is_great = ((self.zone_size - self.great_size) / 2 < delta < (self.zone_size + self.great_size) / 2)
            return True, is_great
        return False, False

    def stop(self):
        self.active = False
        self.canvas.delete("skillcheck")

class GeneratorSim:
    def __init__(self, root):
        self.root = root
        self.root.title("DBD Skill Check Generator")
        self.root.geometry("600x600")
        self.root.configure(bg="black")
        self.total_time = 80000
        self.progress = 0
        self.progress_step = 0
        self.skillcheck_active = False
        self.skillcheck = None
        self.merciless = tk.BooleanVar()
        self.overcharge = tk.BooleanVar()
        self.sequence_active = False
        self.sequence_checks = 0
        self.paused = False
        self.pause_until = 0
        self.next_skillcheck_time = 0
        self.skillcheck_speed = 6
        self.skillcheck_zone = 40
        self.build_ui()
        self.root.bind("<space>", self.hit)
        self.progress_step = 100 / (self.total_time / 50)

    def build_ui(self):
        perks_frame = tk.Frame(self.root, bg="black")
        perks_frame.pack(pady=10)
        tk.Checkbutton(perks_frame, text="Merciless Storm", variable=self.merciless,
                       bg="black", fg="white", selectcolor="gray").pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(perks_frame, text="Overcharge", variable=self.overcharge,
                       bg="black", fg="white", selectcolor="gray").pack(side=tk.LEFT, padx=10)
        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="black", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.bg_bar = self.canvas.create_rectangle(50, 380, 350, 410, fill="gray20")
        self.fg_bar = self.canvas.create_rectangle(50, 380, 50, 410, fill="lime green")
        self.progress_text = self.canvas.create_text(200, 360, text="Progress: 0%", fill="white", font=("Arial", 16))
        self.feedback = tk.Label(self.root, text="", font=("Arial", 18), fg="white", bg="black")
        self.feedback.pack()
        self.start_btn = tk.Button(self.root, text="Start Generator", command=self.start)
        self.start_btn.pack(pady=10)

    def start(self):
        if self.skillcheck_active:
            return
        self.progress = 0
        self.paused = False
        self.pause_until = 0
        self.skillcheck_active = False
        self.feedback.config(text="")
        self.canvas.coords(self.fg_bar, 50, 380, 50, 410)
        self.start_btn.config(state=tk.DISABLED)
        self.sequence_active = False
        self.sequence_checks = 0
        self.schedule_next_skillcheck(initial=True)
        self.loop()

    def schedule_next_skillcheck(self, initial=False):
        now = time.time() * 1000
        if initial and self.overcharge.get():
            delay = random.randint(700, 1200)
            speed = 10
            zone_size = 25
        else:
            delay = random.randint(1500, 4000)
            speed = 6
            zone_size = 40
        if self.merciless.get() and self.progress >= 90 and not self.sequence_active:
            self.sequence_active = True
            self.sequence_checks = 3
            delay = 500
            speed = 8
            zone_size = 35
        self.next_skillcheck_time = now + delay
        self.skillcheck_speed = speed
        self.skillcheck_zone = zone_size

    def loop(self):
        now = time.time() * 1000
        if self.paused:
            if now >= self.pause_until:
                self.paused = False
                self.feedback.config(text="")
            else:
                self.root.after(50, self.loop)
                return
        if self.progress >= 100:
            self.feedback.config(text="🎉 Gerador Consertado! Parabéns!", fg="lime")
            self.start_btn.config(state=tk.NORMAL)
            self.skillcheck_active = False
            if self.skillcheck:
                self.skillcheck.stop()
            return
        if not self.skillcheck_active and now >= self.next_skillcheck_time:
            self.skillcheck_active = True
            self.skillcheck = SkillCheck(self.canvas, 200, 200, 120)
            self.skillcheck.start(speed=self.skillcheck_speed, zone_size=self.skillcheck_zone)
        if self.skillcheck_active:
            self.skillcheck.update()
        if not self.skillcheck_active:
            self.progress += self.progress_step
            self.progress = min(100, self.progress)
        width = 300 * (self.progress / 100)
        self.canvas.coords(self.fg_bar, 50, 380, 50 + width, 410)
        self.canvas.itemconfig(self.progress_text, text=f"Progress: {int(self.progress)}%")
        self.root.after(50, self.loop)

    def hit(self, event):
        if not self.skillcheck_active:
            return
        hit, great = self.skillcheck.check_hit()
        if hit:
            if great:
                self.feedback.config(text="🎯 GREAT SKILL CHECK!", fg="cyan")
                pygame.mixer.Sound.play(som_great)
                self.progress += 4
            else:
                self.feedback.config(text="✅ Skill Check Acertado!", fg="lime")
                pygame.mixer.Sound.play(som_acerto)
                self.progress += 2
            self.progress = min(100, self.progress)
            self.skillcheck_active = False
            self.skillcheck.stop()
            if self.sequence_active:
                self.sequence_checks -= 1
                if self.sequence_checks > 0:
                    self.next_skillcheck_time = time.time() * 1000 + 500
                else:
                    self.sequence_active = False
                    self.schedule_next_skillcheck()
            else:
                self.schedule_next_skillcheck()
        else:
            self.feedback.config(text="💥 Você errou!", fg="red")
            pygame.mixer.Sound.play(som_erro)
            self.skillcheck_active = False
            self.skillcheck.stop()
            self.progress -= 5
            if self.progress < 0:
                self.progress = 0
            self.paused = True
            self.pause_until = time.time() * 1000 + 1000
            self.schedule_next_skillcheck()

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneratorSim(root)
    root.mainloop()
