# Animated Heart (Simple)

A tiny Python program that shows a pulsing heart animation.

Quick overview !
- GUI mode (default): a colorful, pulsing heart using Tkinter.
- ASCII mode: a text-only heart animation that runs in your terminal.

Requirements !
- Python 3.6 or newer (3.8+ recommended).
- No extra Python packages needed.
- On Linux you may need to install tkinter:
  - Debian/Ubuntu: `sudo apt install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`

Files !
- `main.py` — the only program file. It contains both GUI and ASCII modes.

How to run !
- GUI (default):
  ```bash
  python main.py
  ```
- ASCII (terminal):
  ```bash
  python main.py --ascii
  ```

How to stop 1
- GUI: close the window.
- ASCII: press Ctrl+C in the terminal.

If something breaks :
- Error about `tkinter` — install the OS package (see above).
- If colors or clearing look odd in Windows terminal, try PowerShell or Windows Terminal.

Want more?
-in more we can add click effects, save frames as images/GIF, or add sound.
