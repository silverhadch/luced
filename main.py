import curses
import signal
import pyperclip  # Install with `pip install pyperclip`
import argparse
import os

def load_file(filename):
    """Load the content of a file into a list of lines. Create the file if it doesn't exist."""
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
                text = [""]  # Ensure at least one line if the file is empty
    except IOError as e:
        print(f"Error loading file: {e}")
        text = [""]

    return [line.rstrip() for line in text], new_file

def save_file(filename, text):
    """Save the text content to a file."""
    try:
        with open(filename, "w") as file:
            for line in text:
                file.write(line + "\n")
        return True
    except IOError as e:
        print(f"Error saving file: {e}")
        return False

def draw_text(stdscr, text, cursor_y, cursor_x, message=None):
    """Draw the text on the screen with cursor position highlighted and display a message if provided."""
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()

    # Draw top and bottom bars
    top_bar = "Luced v.1.0 - Terminal Text Editor"
    bottom_bar = "Ctrl + V Paste Clipboard Content  Ctrl + S Save File  Ctrl + Q Exit"

    # Center the top bar
    top_bar_x = (max_x - len(top_bar)) // 2
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(0, top_bar_x, top_bar[:max_x - top_bar_x], curses.A_REVERSE)

    # Center the bottom bar
    bottom_bar_x = (max_x - len(bottom_bar)) // 2
    stdscr.addstr(max_y - 1, bottom_bar_x, bottom_bar[:max_x - bottom_bar_x], curses.A_REVERSE)
    stdscr.attroff(curses.A_BOLD)

    # Display a message if provided
    if message:
        stdscr.addstr(max_y - 2, (max_x - len(message)) // 2, message, curses.A_BOLD | curses.A_REVERSE)

    # Ensure cursor_y and cursor_x are within bounds
    cursor_y = min(max(cursor_y, 1), len(text) + 1)
    cursor_x = min(max(cursor_x, 0), max_x - 1)

    # Display text within visible area
    start_y = max(1, cursor_y - (max_y - 2) // 2)
    end_y = min(len(text) + 1, start_y + (max_y - 2))

    for idx, line in enumerate(text[start_y - 1:end_y - 1]):
        line_y = 1 + idx
        if start_y - 1 + idx == cursor_y - 1:
            # Draw the line with the cursor position highlighted
            if cursor_x < len(line):
                stdscr.addstr(line_y, 0, line[:cursor_x])  # Part before cursor
                stdscr.addstr(line_y, cursor_x, line[cursor_x], curses.A_REVERSE)  # Cursor character
                stdscr.addstr(line_y, cursor_x + 1, line[cursor_x + 1:])  # Part after cursor
            else:
                stdscr.addstr(line_y, 0, line)  # Full line if cursor is at the end
        else:
            stdscr.addstr(line_y, 0, line)

    # Move the cursor to the current position
    try:
        stdscr.move(cursor_y - start_y + 1, cursor_x)
    except curses.error:
        pass

    stdscr.refresh()

def signal_handler(signum, frame):
    """Handle the interrupt signal (Ctrl-C) and exit."""
    raise KeyboardInterrupt  # Raise KeyboardInterrupt to exit the program

def main(stdscr, filename):
    # Set up signal handling for Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)

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

    if new_file:
        draw_text(stdscr, text, cursor_y, cursor_x, "New File Created")
        stdscr.getch()  # Wait for a key press before continuing

    while True:
        draw_text(stdscr, text, cursor_y, cursor_x)

        key = stdscr.getch()

        if key == 3:  # Ctrl-C to terminate the editor
            raise KeyboardInterrupt  # Exit the editor
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
            stdscr.refresh()
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
        elif key == curses.KEY_LEFT:
            if cursor_x > 0:
                cursor_x -= 1
            elif cursor_y > 1:
                cursor_y -= 1
                cursor_x = len(text[cursor_y - 1])
        elif key == curses.KEY_RIGHT:
            if cursor_x < len(text[cursor_y - 1]):
                cursor_x += 1
            elif cursor_y < len(text):
                cursor_y += 1
                cursor_x = 0
        elif key == curses.KEY_UP:
            if cursor_y > 1:
                cursor_y -= 1
                cursor_x = min(cursor_x, len(text[cursor_y - 1]))
        elif key == curses.KEY_DOWN:
            if cursor_y < len(text):
                cursor_y += 1
                cursor_x = min(cursor_x, len(text[cursor_y - 1]))
        else:
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
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Luced v.1.0 - Terminal Text Editor')
    parser.add_argument('filename', nargs='?', default='Test.txt', help='File to open or create')
    args = parser.parse_args()

    # Run the curses application with the filename argument
    curses.wrapper(lambda stdscr: main(stdscr, args.filename))
