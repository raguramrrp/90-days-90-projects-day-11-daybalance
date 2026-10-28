"""
DayBalance — Offline Desktop Local Application Launcher
Runs DayBalance as a standalone desktop application window without browser chrome,
tabs, or address bar. Shuts down the background server cleanly on window close.
"""

import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


APP_PORT = 8501
APP_URL = f"http://127.0.0.1:{APP_PORT}"
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 920


def find_browser_app_runner() -> str:
    """Finds Edge or Chrome executable capable of --app mode on Windows."""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p

    for name in ["msedge", "chrome"]:
        which_path = shutil.which(name)
        if which_path:
            return which_path

    return ""


def is_server_ready(url: str) -> bool:
    """Checks if the local DayBalance server is responding."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DayBalanceDesktop/1.0"})
        with urllib.request.urlopen(req, timeout=1.0) as response:
            return response.status in (200, 304)
    except Exception:
        return False


def main() -> None:
    workspace_dir = Path(__file__).resolve().parent
    os.chdir(workspace_dir)

    print("=====================================================================")
    print("  DayBalance - Offline Local Desktop Application")
    print("  Personal Behavioral Habit Analytics & Health Tracker")
    print("=====================================================================")

    server_process = None
    started_server = False

    if not is_server_ready(APP_URL):
        print(f"Starting local DayBalance offline engine on port {APP_PORT}...")
        streamlit_cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            f"--server.port={APP_PORT}",
            "--server.address=127.0.0.1",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ]
        server_process = subprocess.Popen(
            streamlit_cmd,
            cwd=str(workspace_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        started_server = True

        # Wait up to 15 seconds for server to start
        max_wait = 15.0
        start_time = time.time()
        print("Initializing local database and interface...", end="", flush=True)
        while time.time() - start_time < max_wait:
            time.sleep(0.4)
            print(".", end="", flush=True)
            if is_server_ready(APP_URL):
                print(" Ready!")
                break
        else:
            print("\nServer startup took longer than expected; attempting launch anyway...")

    runner = find_browser_app_runner()
    if runner:
        print(f"Launching DayBalance native application window ({Path(runner).name})...")
        app_args = [
            runner,
            f"--app={APP_URL}",
            f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}",
            "--app-id=DayBalancePersonalTracker"
        ]
        try:
            # Run the standalone window and wait for the user to close it
            subprocess.run(app_args, check=False)
        except Exception as e:
            print(f"Application window error: {e}")
    else:
        import webbrowser
        print(f"Launching DayBalance at {APP_URL}...")
        webbrowser.open(APP_URL)
        print("DayBalance is running. Press CTRL+C to terminate.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    # Clean shutdown of background server if we launched it
    if started_server and server_process:
        print("\nClosing DayBalance local engine...")
        try:
            server_process.terminate()
            server_process.wait(timeout=3)
        except Exception:
            try:
                server_process.kill()
            except Exception:
                pass

    print("DayBalance application closed successfully.")


if __name__ == "__main__":
    main()
