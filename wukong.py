import time
import json
import re
import win32gui
from pynput import keyboard
import pyautogui

# Configuration file
CONFIG_FILE = "keypress_config.json"

# Global variables
key_press_data = []
last_event_time = None

# To match key names with pyautogui.KEYBOARD_KEYS
VALID_KEYS = pyautogui.KEYBOARD_KEYS


def on_press(key):
    global last_event_time
    try:
        key_name = key.char if key.char in VALID_KEYS else str(key).replace("Key.", "")
    except AttributeError:
        key_name = str(key).replace("Key.", "")

    if key_name not in VALID_KEYS:
        print(f"Ignoring invalid key: {key_name}")
        return

    current_time = time.time()
    time_elapsed = current_time - last_event_time if last_event_time else 0
    last_event_time = current_time

    # Add sleep event for time elapsed
    if time_elapsed > 0:
        key_press_data.append({"event": "sleep", "duration": time_elapsed})

    # Add press event
    key_press_data.append({"event": "press", "key": key_name})
    print(f"Recorded press: {key_name}, Time Elapsed Since Last Event: {time_elapsed:.6f} seconds")


def on_release(key):
    global last_event_time
    try:
        key_name = key.char if key.char in VALID_KEYS else str(key).replace("Key.", "")
    except AttributeError:
        key_name = str(key).replace("Key.", "")

    if key_name not in VALID_KEYS:
        print(f"Ignoring invalid key: {key_name}")
        return

    current_time = time.time()
    time_elapsed = current_time - last_event_time if last_event_time else 0
    last_event_time = current_time

    # Add sleep event for time elapsed
    if time_elapsed > 0:
        key_press_data.append({"event": "sleep", "duration": time_elapsed})

    # Add release event
    key_press_data.append({"event": "release", "key": key_name})
    print(f"Recorded release: {key_name}, Time Elapsed Since Last Event: {time_elapsed:.6f} seconds")

    # Stop recording if 'esc' is released
    if key == keyboard.Key.esc:
        return False


def save_config(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def load_config(file):
    with open(file, "r") as f:
        return json.load(f)


def find_window_and_activate(window_title_search):
    """Finds a window matching the search string and activates it."""
    def callback(hwnd, _):
        window_text = win32gui.GetWindowText(hwnd)
        if re.search(window_title_search, window_text, re.IGNORECASE):  # Case-insensitive regex match
            try:
                print(f"Activating window: {window_text} (HWND: {hwnd})")
                win32gui.SetForegroundWindow(hwnd)
            except Exception as e:
                print(f"Failed to activate window: {e}")
            return False  # Stop enumeration
        return True

    win32gui.EnumWindows(callback, None)


def replay_keypresses(config, window_title_regex):
    # Find and focus on the window
    find_window_and_activate(window_title_regex)

    # Replay the key presses
    for event in config:
        if event["event"] == "sleep":
            print(f"Sleeping for {event['duration']} seconds...")
            time.sleep(event["duration"])
        elif event["event"] == "press":
            print(f"Pressing key '{event['key']}'...")
            pyautogui.keyDown(event["key"])
        elif event["event"] == "release":
            print(f"Releasing key '{event['key']}'...")
            pyautogui.keyUp(event["key"])


def record_mode():
    global last_event_time
    last_event_time = None  # Reset timing
    print("Recording mode: Press 'esc' to stop recording...")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    # Save data
    if key_press_data:
        save_config(key_press_data, CONFIG_FILE)
        print(f"Key presses saved to {CONFIG_FILE}")

def replay_mode():
    try:
        config = load_config(CONFIG_FILE)
    except FileNotFoundError:
        print(f"Configuration file '{CONFIG_FILE}' not found. Please record keypresses first.")
        return

    window_title_regex = "Chiaki | Stream"  # Replace this with your desired window title
    print("Starting replay loop. Press Ctrl+C to stop.")
    
    try:
        while True:
            replay_keypresses(config, window_title_regex)
            print("Replay cycle complete. Restarting...")
    except KeyboardInterrupt:
        print("\nReplay loop interrupted by user. Exiting.")



def main():
    print("Select an operation mode:")
    print("1: Record keypresses")
    print("2: Replay keypresses")
    mode = input("Enter mode (1 or 2): ").strip()

    if mode == "1":
        record_mode()
    elif mode == "2":
        replay_mode()
    else:
        print("Invalid mode selected. Exiting.")


if __name__ == "__main__":
    main()
