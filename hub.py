# by Noxmain
# -*- coding: utf-8 -*-
# v2.5.0
from getch import getch
from time import time
import json
import os

format_left = lambda string, length: f"{string:<{length}}"
format_center = lambda string, length: f"{string:^{length}}"
format_right = lambda string, length: f"{string:>{length}}"
move = lambda x, y: print(f"\033[{y};{x}H", end="", flush=True)
clear = lambda: print("\033[H\033[0J", end="", flush=True)
style = lambda string, color, bold = False: STYLE[color] + (STYLE[0] if bold else "") + string + "\033[0m"

FIRST = True
NOTFIRST = lambda: exec("global FIRST\nFIRST = False")

STYLES = [
    # [highlight, primary color, secondary color, autocomplete color]
    ["\033[1m", "", "", ""],  # nocolor
    ["\033[1m", "\033[31m", "\033[34m", "\033[90m"],  # basic for light
    ["\033[1m", "\033[91m", "\033[94m", "\033[37m"],  # basic for dark
    ["\033[1m", "\033[34m", "\033[31m", "\033[90m"],  # anti for light
    ["\033[1m", "\033[94m", "\033[91m", "\033[37m"],  # anti for dark
    ["\033[1m", "\033[92m", "\033[92m", "\033[93m"],  # green
]
STYLE = STYLES[1]


def load():
    if os.path.isfile(".hub"):
        f = open(".hub", "r")
        loaded = json.load(f)
        f.close()
        return map(list, zip(*loaded))
    else:
        return list(), list()


def save():
    f = open(".hub", "w")
    json.dump(list(zip(recent_paths, recent_names)), f)
    f.close()


def run():
    save()
    clear()
    t = time()
    os.system("cd " + recent_paths[0].replace(" ", "\\ ") + "; python3 " + recent_names[0].replace(" ", "\\ "))
    input(style("Process finished in " + str(time() - t) + " seconds", 1, True))
    print("\n" * (height - 3))


def print_window():
    NOTFIRST() if FIRST else move(0, 0)
    print("┌" + "─" * (width - 2) + "┐")
    print("│" + style(format_center("PYTHON HUB", width - 2), 1, True) + "│")
    print("├" + "─" * (width - 2) + "┤")
    print("│" + style(format_left("Recent files", width - 2), 1, True) + "│")
    for i in range(height - 8, -1, -1):
        try:
            print("│" + style(format_left(recent_names[i], width - 2), 1) + "│")
        except IndexError:
            print("│" + " " * (width - 2) + "│")
    print("├" + "─" * (width - len(in_info) - 2) + style(in_info, 1, True) + "┤")
    s = format_left(" > " + in_input[:width - 6] + STYLE[3] + in_suggestion[len(in_input):], width - 2) + " " * len(STYLE[3])
    print("│" + style(s[:width + len(STYLE[3]) - 2], 2) + "│")
    print("└" + "─" * (width - 2) + "┘", end="", flush=True)
    move(in_x, height - 1)


if __name__ == '__main__':
    recent_paths, recent_names = load()
    in_input = ""
    in_save = ""
    in_suggestion = ""
    in_info = ""
    in_x = 5
    in_y = -1
    while True:
        width = os.get_terminal_size().columns
        height = os.get_terminal_size().lines
        print_window()
        ch = getch()
        if ch in ["\x1b"]:
            ch = getch() + getch()
            if ch in ["[A"]:  # up
                in_save = in_input if in_y == -1 else in_save
                in_y = min(in_y + 1, len(recent_names) - 1)
                in_input = recent_names
            if ch in ["[B"]:  # down
                in_y = max(in_y - 1, -1)
                in_input = recent_names + [in_save]
            if ch in ["[A", "[B"]:
                in_input = in_input[in_y]
                in_suggestion = ""
                in_x = 5 + len(in_input)
            if ch in ["[C"]:  # right
                in_x = min(in_x + 1, 5 + len(in_input), width - 2)
            if ch in ["[D"]:  # left
                in_x = max(in_x - 1, 5)
            in_info = ""
        elif ch in ["\n", "\r", ""]:
            if in_input.lower() in ["\n", "\r", " ", "", "exit", "quit"]:
                save()
                clear()
                exit()
            in_input = in_input[:-1] if in_input[-1] == " " else in_input
            in_input = in_input.replace("\\ ", " ")
            if (in_input in recent_names) or (in_suggestion in recent_names):
                index = recent_names.index(in_input if in_input in recent_names else in_suggestion)
                if os.path.isfile(os.path.join(recent_paths[index], recent_names[index])):
                    recent_names = [recent_names.pop(index)] + recent_names
                    recent_paths = [recent_paths.pop(index)] + recent_paths
                    run()
                else:
                    in_info = " file does not exist anymore "
            elif os.path.isfile(in_input):
                in_input = os.path.abspath(in_input)
                tmp = lambda x: os.path.join(x[0], x[1]) == in_input
                tmp = list(map(tmp, zip(recent_paths, recent_names)))
                if True in tmp:
                    index = tmp.index(True)
                    recent_names = [recent_names.pop(index)] + recent_names
                    recent_paths = [recent_paths.pop(index)] + recent_paths
                else:
                    recent_names = [os.path.basename(in_input)] + recent_names
                    recent_paths = [os.path.dirname(in_input)] + recent_paths
                run()
            else:
                in_info = " invalid path "
            in_input = ""
            in_save = ""
            in_suggestion = ""
            in_x = 5
            in_y = -1
        elif ch in ["\x7f"]:
            in_input = in_input if in_x == 5 else (in_input[:in_x - 6] + in_input[in_x - 5:])
            in_x = max(in_x - 1, 5)
            if len(in_input) > 0:
                in_suggestion = list(filter(lambda x: x.startswith(in_input), recent_names))
                in_suggestion = in_suggestion[0] if len(in_suggestion) > 0 else ""
            else:
                in_suggestion = ""
        else:
            if in_x == width - 2:
                in_input = in_input + ch
            else:
                in_input = in_input[:in_x - 5] + ch + in_input[in_x - 5:]
            in_suggestion = list(filter(lambda x: x.startswith(in_input), recent_names))
            in_suggestion = in_suggestion[0] if len(in_suggestion) > 0 else ""
            in_x = min(in_x + 1, 5 + len(in_input), width - 2)
            in_info = ""
