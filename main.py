import sys
import math
import time
import argparse
from colorsys import hsv_to_rgb  # used to convert hue->RGB for vivid colors

# tkinter may not be available on some systems (e.g., minimal Linux containers).
# We import it inside a try/except and set tk=None if unavailable; the CLI will
# fall back to ASCII mode or print a helpful message.
try:
    # Python 3 uses 'tkinter' (lowercase)
    import tkinter as tk
except Exception:
    tk = None


def make_heart_points(scale=10, steps=200):
    """
    Generate points for a heart shape using a classic parametric formula.

    scale: multiplier to make the heart larger or smaller
    steps: number of points around the parametric curve (higher => smoother)
    Returns: list of (x, y) tuples
    """
    pts = []
    for i in range(steps):
        # t goes from 0 to 2*pi
        t = (i / steps) * 2 * math.pi
        # parametric heart formula
        x = 16 * (math.sin(t) ** 3)
        y = (13 * math.cos(t)
             - 5 * math.cos(2 * t)
             - 2 * math.cos(3 * t)
             - math.cos(4 * t))
        # Multiply by scale and invert y so the heart is upright in screen coords
        pts.append((x * scale, -y * scale))
    return pts


def rgb_tuple_to_hex(rgb):
    """
    Convert an (r,g,b) tuple with values in [0,1] to a Tk-compatible hex color string.
    Example: (1.0, 0.5, 0.0) -> '#ff7f00'
    """
    r, g, b = rgb
    return '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))


class HeartApp:
    """
    GUI application that draws and animates a heart on a tkinter Canvas.
    """

    def __init__(self, width=600, height=600, bg="#111"):
        # Ensure tkinter is available before proceeding
        if not tk:
            raise RuntimeError("tkinter is not available on this system.")

        # Save configuration
        self.width = width
        self.height = height
        self.bg = bg

        # Create main window
        self.root = tk.Tk()
        self.root.title("Animated Heart ❤️")

        # Create canvas for drawing; highlightthickness=0 removes focus border
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height,
                                bg=self.bg, highlightthickness=0)
        # Pack canvas to fill the window
        self.canvas.pack(fill="both", expand=True)

        # Calculate center of canvas for translating parametric points
        self.center = (self.width // 2, self.height // 2)

        # Precompute base heart points once (more efficient than recalculating each frame)
        self.base_points = make_heart_points(scale=12, steps=300)

        # Translate points to screen coordinates and create a polygon item
        coords = self._translated_coords(self.base_points, self.center, 1.0)
        # main heart polygon (filled)
        self.poly = self.canvas.create_polygon(coords, fill="#ff0066", outline="", smooth=True)
        # glow polygon underneath (we will update its fill color to simulate glow)
        self.glow = self.canvas.create_polygon(coords, fill="", outline="", smooth=True)

        # Animation parameters
        self.current_scale = 1.0
        self.pulse_period = 1.2   # seconds for a full pulse cycle
        self.hue_base = 0.00      # base hue (0.0 == red)
        self.running = True       # flag used to stop animation loop cleanly

        # Bind close (window manager 'X' button) to a cleanup handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        """
        Called when the window is requested to close. Stop the animation loop and
        destroy the root window to exit cleanly.
        """
        self.running = False
        self.root.destroy()

    def _translated_coords(self, points, center, scale):
        """
        Helper: given a list of (x,y) points relative to origin, translate them
        to canvas coordinates around 'center' and apply a scale factor.
        Returns a flat list suitable for Canvas.create_polygon or coords().
        """
        cx, cy = center
        coords = []
        for x, y in points:
            coords.append(cx + x * scale)
            coords.append(cy + y * scale)
        return coords

    def _update(self):
        """
        Animation step: compute current pulse scale and color, update polygon coords
        and fill colors, then schedule the next frame using tkinter's after() (approx 60 FPS).
        """
        # current time used for smooth periodic animation
        t = time.time()

        # Pulse smoothly oscillates. Amplitude chosen to make a subtle pulse.
        pulse = 1.0 + 0.12 * math.sin(2 * math.pi * (t / self.pulse_period))

        # Slowly shift hue for a color-cycling effect
        hue = (self.hue_base + 0.06 * math.sin(t * 0.5)) % 1.0

        # Convert hue to RGB (saturation=0.85, value=1.0 for vivid color)
        rgb = hsv_to_rgb(hue, 0.85, 1.0)
        hex_color = rgb_tuple_to_hex(rgb)

        # Update polygon coordinates to scale shape around center (pulse effect)
        coords = self._translated_coords(self.base_points, self.center, pulse)
        self.canvas.coords(self.poly, *coords)

        # Create a brighter "glow" color by boosting channel values (clamped at 1.0)
        glow_rgb = tuple(min(1.0, c + 0.35) for c in rgb)
        glow_hex = rgb_tuple_to_hex(glow_rgb)

        # Update glow polygon coordinates and fills
        self.canvas.coords(self.glow, *coords)
        self.canvas.itemconfig(self.glow, fill=glow_hex)
        self.canvas.itemconfig(self.poly, fill=hex_color)

        # Note: tkinter canvas doesn't support alpha channel for fills. To simulate
        # transparency/glow you could draw multiple semi-opaque shapes or use PIL images.
        # For simplicity, we just change fill colors.

        # Schedule next frame at ~16ms (about 60 FPS) if still running
        if self.running:
            self.root.after(16, self._update)

    def run(self):
        """
        Start the animation loop and enter the tkinter main event loop.
        """
        self._update()   # start the first update
        self.root.mainloop()


def ascii_heart_loop(width=40, height=24, cycles=9999, speed=0.08):
    """
    Terminal-based ASCII heart animation. Uses an implicit heart inequality:
    (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0

    width, height: terminal character grid size (increase for larger hearts)
    cycles: how many internal cycles to run (ignored since outer while True)
    speed: time between frames in seconds
    """
    try:
        while True:
            for phase in range(cycles):
                t = time.time()

                # pulse factor to make the ASCII heart appear to breathe
                pulse = 1.0 + 0.12 * math.sin(2 * math.pi * (t / 1.2))

                out_lines = []
                # Iterate rows (j) and columns (i) to build the ASCII frame
                for j in range(height):
                    row_chars = []
                    for i in range(width):
                        # Map terminal coordinates to a roughly -1.5..1.5 x range and
                        # -1.0..1.2 y range, adjusted by pulse.
                        x = (i - width / 2) / (width / 4) / pulse
                        y = (j - height / 2) / (height / 4) * 1.2 / pulse

                        # Evaluate the heart implicit equation
                        value = (x * x + y * y - 1) ** 3 - (x * x) * (y ** 3)

                        if value <= 0:
                            # Determine a character for shading based on distance from center
                            d = math.hypot(x, y)
                            if d < 0.5:
                                ch = "@"
                            elif d < 0.9:
                                ch = "O"
                            else:
                                ch = "*"
                        else:
                            ch = " "
                        row_chars.append(ch)
                    out_lines.append("".join(row_chars))

                # Clear the terminal screen (ANSI escape sequences) and print frame
                # Note: On some Windows terminals you may need to enable ANSI support or use PowerShell/Windows Terminal.
                print("\x1b[H\x1b[2J", end="")
                print("\n".join(out_lines))
                print("\nPress Ctrl+C to exit.")
                time.sleep(speed)
    except KeyboardInterrupt:
        # Graceful exit on user interrupt
        print("\nGoodbye!")


def main():
    """
    CLI entry point. Parses args and either runs the ASCII version or launches the GUI.
    """
    parser = argparse.ArgumentParser(description="Animated heart (GUI and ASCII)")
    parser.add_argument("--ascii", action="store_true", help="Run terminal ASCII animation")
    parser.add_argument("--gui", action="store_true", help="Run GUI animation (default)")
    args = parser.parse_args()

    # ASCII mode requested -> run it and exit
    if args.ascii:
        ascii_heart_loop()
        return

    # GUI mode: ensure tkinter is available; otherwise instruct the user how to install it
    if not tk:
        print("tkinter is not available on this system. Install it or run with --ascii mode.")
        print("On Debian/Ubuntu: sudo apt install python3-tk")
        sys.exit(1)

    # Create and run the GUI app with a default size (can be adjusted)
    app = HeartApp(width=700, height=700)
    app.run()


if __name__ == "__main__":
    main()