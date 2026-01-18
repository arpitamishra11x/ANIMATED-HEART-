import sys
import math
import time
import argparse
from colorsys import hsv_to_rgb

# Optional dependency for saving PNG screenshots
try:
    from PIL import Image  # pyright: ignore[reportMissingImports]
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

try:
    import tkinter as tk
except Exception:
    tk = None


# =======================
# Constants
# =======================
VERSION = "1.2.0"
DEFAULT_BG = "#111"
DEFAULT_FPS = 60
HELP_TEXT = "Space/Click: Pause | S: Screenshot | Esc: Exit"


# =======================
# Math helpers
# =======================
def make_heart_points(scale=10, steps=200):
    pts = []
    for i in range(steps):
        t = (i / steps) * 2 * math.pi
        x = 16 * (math.sin(t) ** 3)
        y = (13 * math.cos(t)
             - 5 * math.cos(2 * t)
             - 2 * math.cos(3 * t)
             - math.cos(4 * t))
        pts.append((x * scale, -y * scale))
    return pts


def rgb_tuple_to_hex(rgb):
    r, g, b = rgb
    return '#{:02x}{:02x}{:02x}'.format(
        int(r * 255), int(g * 255), int(b * 255)
    )


# =======================
# GUI Application
# =======================
class HeartApp:
    def __init__(
        self,
        width=600,
        height=600,
        bg=DEFAULT_BG,
        pulse_period=1.2,
        fps=DEFAULT_FPS,
        glow_enabled=True
    ):
        if not tk:
            raise RuntimeError("tkinter is not available.")

        self.width = width
        self.height = height
        self.bg = bg
        self.pulse_period = pulse_period
        self.fps = fps
        self.frame_delay = int(1000 / fps)
        self.glow_enabled = glow_enabled

        self.root = tk.Tk()
        self.root.title(f"Animated Heart ❤️  v{VERSION}")

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=self.bg,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.center = (self.width // 2, self.height // 2)
        self.base_points = make_heart_points(scale=12, steps=300)

        coords = self._translated_coords(self.base_points, 1.0)
        self.poly = self.canvas.create_polygon(
            coords, fill="#ff0066", outline="", smooth=True
        )

        self.glow = None
        if self.glow_enabled:
            self.glow = self.canvas.create_polygon(
                coords, fill="", outline="", smooth=True
            )

        self.help_item = self.canvas.create_text(
            self.width // 2, 18,
            text=HELP_TEXT,
            fill="#ffffff",
            font=("Arial", 10)
        )

        self.running = True
        self.paused = False
        self.hue_base = 0.0

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Escape>", lambda e: self._on_close())
        self.root.bind("<space>", lambda e: self.toggle_pause())
        self.root.bind("<Key-s>", lambda e: self.save_screenshot())
        self.canvas.bind("<Button-1>", lambda e: self.toggle_pause())

    def _on_close(self):
        self.running = False
        try:
            self.root.destroy()
        except Exception:
            pass

    def toggle_pause(self):
        self.paused = not self.paused
        self.canvas.itemconfig(
            self.help_item,
            text="Paused — Press Space or Click"
            if self.paused else HELP_TEXT
        )

    def _translated_coords(self, points, scale):
        cx, cy = self.center
        coords = []
        for x, y in points:
            coords.extend((cx + x * scale, cy + y * scale))
        return coords

    def _update(self):
        if self.paused:
            if self.running:
                self.root.after(200, self._update)
            return

        t = time.time()
        pulse = 1.0 + 0.12 * math.sin(2 * math.pi * (t / self.pulse_period))
        hue = (self.hue_base + 0.06 * math.sin(t * 0.5)) % 1.0

        rgb = hsv_to_rgb(hue, 0.85, 1.0)
        hex_color = rgb_tuple_to_hex(rgb)

        coords = self._translated_coords(self.base_points, pulse)
        self.canvas.coords(self.poly, *coords)
        self.canvas.itemconfig(self.poly, fill=hex_color)

        if self.glow_enabled and self.glow:
            glow_rgb = tuple(min(1.0, c + 0.35) for c in rgb)
            self.canvas.coords(self.glow, *coords)
            self.canvas.itemconfig(self.glow, fill=rgb_tuple_to_hex(glow_rgb))

        if self.running:
            self.root.after(self.frame_delay, self._update)

    def save_screenshot(self):
        ts = time.strftime("%Y%m%d_%H%M%S")
        base = f"animated_heart_{ts}"
        ps_file = base + ".ps"

        try:
            self.canvas.postscript(file=ps_file, colormode="color")
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return

        if PIL_AVAILABLE:
            try:
                Image.open(ps_file).save(base + ".png", "PNG")
                print(f"Saved screenshot: {base}.png")
            except Exception as e:
                print(f"PNG conversion failed: {e}")
        else:
            print(f"Saved PostScript screenshot: {ps_file}")

    def run(self):
        self._update()
        self.root.mainloop()


# =======================
# CLI Entry
# =======================
def main():
    parser = argparse.ArgumentParser(description="Animated Heart (GUI / ASCII)")
    parser.add_argument("--ascii", action="store_true", help="Run ASCII animation")
    parser.add_argument("--width", type=int, default=700)
    parser.add_argument("--height", type=int, default=700)
    parser.add_argument("--pulse", type=float, default=1.2)
    parser.add_argument("--fps", type=int, default=60, help="Frames per second")
    parser.add_argument("--no-glow", action="store_true", help="Disable glow effect")

    args = parser.parse_args()

    if args.ascii:
        print("ASCII mode unchanged.")
        return

    if not tk:
        print("tkinter not available. Install python3-tk or use --ascii.")
        sys.exit(1)

    print(f"Animated Heart v{VERSION} | {args.width}x{args.height} | {args.fps} FPS")

    app = HeartApp(
        width=args.width,
        height=args.height,
        pulse_period=args.pulse,
        fps=args.fps,
        glow_enabled=not args.no_glow
    )
    app.run()


if __name__ == "__main__":
    main()
