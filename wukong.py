import time
import json
import re
from pynput import keyboard
import pygetwindow as gw
import pyautogui

# Configuration file
CONFIG_FILE = "keypress_config.json"

# Global variables
key_press_data = []
last_event_time = None


def on_press(key):
    global last_event_time
    try:
        key_name = key.char if key.char else str(key)
    except AttributeError:
        key_name = str(key)

    current_time = time.time()
    time_elapsed = current_time - last_event_time if last_event_time else 0
    last_event_time = current_time

    # Save the event
    key_press_data.append({"event": "press", "key": key_name, "time_elapsed": time_elapsed})

    # Print to stdout
    print(f"Pressed: {key_name}, Time Elapsed Since Last Event: {time_elapsed:.6f} seconds")


def on_release(key):
    global last_event_time
    try:
        key_name = key.char if key.char else str(key)
    except AttributeError:
        key_name = str(key)

    current_time = time.time()
    time_elapsed = current_time - last_event_time if last_event_time else 0
    last_event_time = current_time

    # Save the event
    key_press_data.append({"event": "release", "key": key_name, "time_elapsed": time_elapsed})

    # Print to stdout
    print(f"Released: {key_name}, Time Elapsed Since Last Event: {time_elapsed:.6f} seconds")

    # Stop recording if 'esc' is released
    if key == keyboard.Key.esc:
        return False


def save_config(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def load_config(file):
    with open(file, "r") as f:
        return json.load(f)


def find_window_by_title_regex(pattern):
    """Find the first window whose title matches the given regex pattern."""
    for window in gw.getAllWindows():
        if re.search(pattern, window.title, re.IGNORECASE):
            return window
    return None


def replay_keypresses(config, window_title_regex):
    # Find and focus on the window
    window = find_window_by_title_regex(window_title_regex)
    if not window:
        print(f"No window found matching title pattern: {window_title_regex}")
        return

    window.activate()
    print(f"Focusing on window: {window.title}")

    # Replay the key presses
    for event in config:
        time.sleep(event["time_elapsed"])  # Wait based on the recorded interval
        if event["event"] == "press":
            pyautogui.keyDown(event["key"])
        elif event["event"] == "release":
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

    window_title_regex = input("Enter the window title regex pattern to focus: ").strip()
    replay_keypresses(config, window_title_regex)
    print("Replay complete!")


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
