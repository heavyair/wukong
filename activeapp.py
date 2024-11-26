import win32gui

def find_window_and_activate(window_title_search):
    """Finds a window matching the search string and activates it.

    Args:
        window_title_search (str): The search string to match in the window title.
    """

    def callback(hwnd, lParam):
        window_text = win32gui.GetWindowText(hwnd)
        if window_title_search.lower() in window_text.lower():  # Case-insensitive match
            try:
                print(f"Activating window: {window_text} (HWND: {hwnd})")
                win32gui.SetForegroundWindow(hwnd)
            except Exception as e:
                print(f"Failed to activate window: {e}")
            return False  # Stop enumeration
        return True

    win32gui.EnumWindows(callback, None)

# Example usage:
search_string = "Chiaki | Stream"  # Replace with your desired search string
find_window_and_activate(search_string)
