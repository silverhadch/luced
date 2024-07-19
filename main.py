import curses
import pyperclip  # Dependency
import argparse
import os
import sys

def load_file(filename):
    """Load the content of the File, if it doesn't exist create one"""
    text = []
    new_file = False
    if not os.path.exists(filename):
        # File does not exist, create it and initialize with an empty line
        with open(filename, "w") as file:
            file.write("\n")
        new_file = True

    try:
        with open(filename, "r") as file:
            text = file.readlines()
            if not text:
                text = [""]  # Ensure one line because of this line bug
    except IOError as e:
        print(f"Error loading file: {e}")
        text = [""]

    return [line.rstrip() for line in text], new_file

def save_file(filename, text):
    """Save the text to the File"""
    try:
        with open(filename, "w") as file:
            for line in text:
                file.write(line + "\n")
        return True
    except IOError as e:
        print(f"Error saving file: {e}")
        return False

def signal_handler(signum, frame):
    """Handle the Interrupt-Signal (Ctrl-C) and exit."""
    raise KeyboardInterrupt  # Raise KeyboardInterrupt to exit

def draw_text(stdscr, text, cursor_y, cursor_x, message=None):
    """Draw the text on the screen with cursor position and display a message if needed."""
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()

    # Draw top and bottom bars
    top_bar = "Luced v.1.0 - Terminal Text Editor"
    bottom_bar = "Ctrl + V: Paste Clipboard Content  Ctrl + S: Save File  Ctrl + Q: Exit"

    # Center the top bar
    top_bar_x = (max_x - len(top_bar)) // 2
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(0, top_bar_x, top_bar[:max_x - top_bar_x], curses.A_REVERSE)

    # Center the bottom bar
    bottom_bar_x = (max_x - len(bottom_bar)) // 2
    stdscr.addstr(max_y - 1, bottom_bar_x, bottom_bar[:max_x - bottom_bar_x], curses.A_REVERSE)
    stdscr.attroff(curses.A_BOLD)

    # Display a message if needed
    if message:
        stdscr.addstr(max_y - 2, (max_x - len(message)) // 2, message, curses.A_BOLD | curses.A_REVERSE)

    # Ensure cursor_y and cursor_x don't go out of bounds
    cursor_y = min(max(cursor_y, 1), len(text) + 1)
    cursor_x = min(max(cursor_x, 0), max_x - 1)

    # Display text within the window
    start_y = max(1, cursor_y - (max_y - 2) // 2)
    end_y = min(len(text) + 1, start_y + (max_y - 2))

    for idx, line in enumerate(text[start_y - 1:end_y - 1]):
        line_y = 1 + idx
        # Wrap long lines to fit within the terminal width
        wrapped_lines = [line[i:i + max_x] for i in range(0, len(line), max_x)]

        for line_idx, wrapped_line in enumerate(wrapped_lines):
            if start_y - 1 + idx == cursor_y - 1 and line_idx == 0:
                # Draw the line with the cursor position highlighted
                if cursor_x < len(wrapped_line):
                    # Handle text before cursor
                    stdscr.addstr(line_y, 0, wrapped_line[:cursor_x])
                    # Handle cursor character
                    stdscr.addstr(line_y, cursor_x, wrapped_line[cursor_x], curses.A_REVERSE)
                    # Handle text after cursor
                    if cursor_x + 1 < len(wrapped_line):
                        stdscr.addstr(line_y, cursor_x + 1, wrapped_line[cursor_x + 1:])
                else:
                    stdscr.addstr(line_y, 0, wrapped_line)
            else:
                stdscr.addstr(line_y + line_idx, 0, wrapped_line[:max_x])

    # Move the cursor to the necessary position
    try:
        stdscr.move(cursor_y - start_y + 1, cursor_x)
    except curses.error:
        pass

    stdscr.refresh()

def move_cursor(stdscr, text, key, cursor_y, cursor_x):
    """Update cursor position based on key input."""
    max_y, max_x = stdscr.getmaxyx()
    num_lines = len(text)

    if key == curses.KEY_LEFT:
        if cursor_x > 0:
            cursor_x -= 1
        elif cursor_y > 1:
            cursor_y -= 1
            cursor_x = min(cursor_x, len(text[cursor_y - 1]))
    elif key == curses.KEY_RIGHT:
        if cursor_x < len(text[cursor_y - 1]):
            cursor_x += 1
        elif cursor_y < num_lines:
            cursor_y += 1
            cursor_x = min(cursor_x, len(text[cursor_y - 1]))
    elif key == curses.KEY_UP:
        if cursor_y > 1:
            cursor_y -= 1
            cursor_x = min(cursor_x, len(text[cursor_y - 1]))
    elif key == curses.KEY_DOWN:
        if cursor_y < num_lines:
            cursor_y += 1
            cursor_x = min(cursor_x, len(text[cursor_y - 1]))

    # Handle cursor wrapping to the next line if at the end of a line
    if cursor_x > max_x - 1:
        cursor_x = 0
        cursor_y += 1
        if cursor_y > len(text):
            text.append("")

    # Ensure cursor_x does not go out of bounds
    cursor_x = min(cursor_x, max_x - 1)

    return cursor_y, cursor_x

def main(stdscr, filename):
    # Check if running as root
    if os.geteuid() == 0:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        warning_message = "You are root! Proceed with caution!"
        stdscr.addstr(max_y // 2, (max_x - len(warning_message)) // 2, warning_message, curses.A_BLINK | curses.A_REVERSE)
        stdscr.refresh()
        stdscr.getch()  # Wait for user input before continuing

    # Initialize curses
    curses.curs_set(1)  # Show the cursor
    stdscr.clear()
    stdscr.refresh()

    # Enable raw mode to capture all key presses
    curses.raw()
    stdscr.keypad(True)

    # Load file content
    text, new_file = load_file(filename)

    # Initial values
    cursor_x = 0
    cursor_y = 1  # Start cursor at line 1 (below the top bar)

    while True:
        draw_text(stdscr, text, cursor_y, cursor_x)

        key = stdscr.getch()

        if key == 3:  # Ctrl-C to terminate
            break
        elif key == 22:  # Ctrl-V to paste
            clipboard_text = pyperclip.paste()
            if clipboard_text:  # Only paste if there's text in the clipboard
                clipboard_lines = clipboard_text.splitlines()
                for line in clipboard_lines:
                    if cursor_y > len(text):
                        text.append(line)
                    else:
                        text[cursor_y - 1] = text[cursor_y - 1][:cursor_x] + line + text[cursor_y - 1][cursor_x:]
                    cursor_y += 1
                cursor_y = min(cursor_y - 1, len(text))
                cursor_x = len(text[cursor_y - 1]) if cursor_y <= len(text) else 0
        elif key == 19:  # Ctrl-S to save
            if save_file(filename, text):
                draw_text(stdscr, text, cursor_y, cursor_x, "File saved successfully.")
            else:
                draw_text(stdscr, text, cursor_y, cursor_x, "Error saving file.")
            stdscr.getch()  # Wait for a key press before continuing
        elif key == 17:  # Ctrl-Q to quit
            break
        elif key == curses.KEY_BACKSPACE or key == 127:
            if cursor_x > 0:
                text[cursor_y - 1] = text[cursor_y - 1][:cursor_x - 1] + text[cursor_y - 1][cursor_x:]
                cursor_x -= 1
            elif cursor_y > 1:
                cursor_x = len(text[cursor_y - 2])
                text[cursor_y - 2] += text[cursor_y - 1]
                del text[cursor_y - 1]
                cursor_y -= 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if cursor_y > len(text):
                text.append("")
            else:
                text.insert(cursor_y, text[cursor_y - 1][cursor_x:])
                text[cursor_y - 1] = text[cursor_y - 1][:cursor_x]
            cursor_y += 1
            cursor_x = 0
        else:
            cursor_y, cursor_x = move_cursor(stdscr, text, key, cursor_y, cursor_x)
            if 32 <= key <= 126:
                if cursor_y <= len(text):
                    text[cursor_y - 1] = text[cursor_y - 1][:cursor_x] + chr(key) + text[cursor_y - 1][cursor_x:]
                else:
                    text.append(chr(key))
                cursor_x += 1

    # Reset terminal settings
    curses.noraw()
    stdscr.keypad(False)

if __name__ == "__main__":
    # Set up argument parsing for CLI
    parser = argparse.ArgumentParser(description='Luced v.1.0 - Terminal Text Editor')
    parser.add_argument('filename', nargs='?', default='Test.txt', help='File to open or create')
    args = parser.parse_args()

    # Run the curses application with the filename argument
    curses.wrapper(lambda stdscr: main(stdscr, args.filename))
