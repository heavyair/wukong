import time
import json
from pynput import keyboard
import pygetwindow as gw
import pyautogui

# Configuration file
CONFIG_FILE = "keypress_config.json"

# Global variables
key_press_data = []
recording = True
last_event_time = None


def on_press(key):
    global last_event_time
    if not recording:
        return

    try:
        key_name = key.char if key.char else str(key)
    except AttributeError:
        key_name = str(key)

    current_time = time.time()
    time_duration = current_time - last_event_time if last_event_time else 0
    last_event_time = current_time

    # Save the event
    key_press_data.append({"event": "press", "key": key_name, "time": current_time})

    # Print to stdout
    print(f"Pressed: {key_name}, Saved Key: {key_name}, Time Since Last Event: {time_duration:.6f} seconds")


def on_release(key):
    global last_event_time
    if not recording:
        return

    try:
        key_name = key.char if key.char else str(key)
    except AttributeError:
        key_name = str(key)

    current_time = time.time()
    time_duration = current_time - last_event_time if last_event_time else 0
    last_event_time = current_time

    # Save the event
    key_press_data.append({"event": "release", "key": key_name, "time": current_time})

    # Print to stdout
    print(f"Released: {key_name}, Saved Key: {key_name}, Time Since Last Event: {time_duration:.6f} seconds")

    # Stop recording if 'esc' is released
    if key == keyboard.Key.esc:
        return False


def save_config(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def load_config(file):
    with open(file, "r") as f:
        return json.load(f)


def replay_keypresses(config, window_title):
    # Find and focus on the window
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"No window found with title: {window_title}")
        return

    window = windows[0]
    window.activate()
    print(f"Focusing on window: {window_title}")

    # Replay the key presses
    start_time = config[0]["time"]
    for event in config:
        time_to_wait = event["time"] - start_time
        time.sleep(time_to_wait)
        start_time = event["time"]

        if event["event"] == "press":
            pyautogui.keyDown(event["key"])
        elif event["event"] == "release":
            pyautogui.keyUp(event["key"])


def record_mode():
    global recording
    print("Recording mode: Press 'esc' to stop recording...")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    # Calculate intervals and save data
    if key_press_data:
        start_time = key_press_data[0]["time"]
        for event in key_press_data:
            event["time"] -= start_time  # Normalize time to start at 0
        save_config(key_press_data, CONFIG_FILE)
        print(f"Key presses saved to {CONFIG_FILE}")


def replay_mode():
    try:
        config = load_config(CONFIG_FILE)
    except FileNotFoundError:
        print(f"Configuration file '{CONFIG_FILE}' not found. Please record keypresses first.")
        return

    window_title = input("Enter the window title to focus: ").strip()
    replay_keypresses(config, window_title)
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
