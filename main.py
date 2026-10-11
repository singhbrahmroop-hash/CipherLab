import json
import os
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText

# Runner mode: when the packaged exe is launched with --run-code it only runs
# the custom cipher code and exits. This must stay above any GUI code so no
# window is created in this mode.
if len(sys.argv) == 4 and sys.argv[1] == "--run-code":
    with open(sys.argv[2], "r", encoding="utf-8") as f:
        d = json.load(f)
    try:
        ns = {}
        exec(d["code"], ns)
        out = {"ok": True, "result": str(ns[d["function"]](d["text"]))}
    except Exception as error:
        out = {"ok": False, "result": str(error)}
    with open(sys.argv[3], "w", encoding="utf-8") as f:
        json.dump(out, f)
    sys.exit()

#Functions

def soft_style(widget, container=False):
    # Paints a Scrolled widget and every internal part of it with the app
    # background. Newer ttkbootstrap versions ignore style= on these widgets,
    # which leaves a gray area, so the parts are coloured directly instead.
    def paint(w):
        try:
            cls = w.winfo_class()
            if cls in ("Frame", "Canvas", "Labelframe"):
                w.configure(background="#0B1320", highlightthickness=0)
            elif cls == "TFrame":
                w.configure(style="Content.TFrame")
        except Exception:
            pass
        for child in w.winfo_children():
            paint(child)
    paint(widget)

scroll_areas = []
wheel_bound = False

def on_mousewheel(event):
    # Scrolls whichever scroll area the mouse pointer is over.
    try:
        widget = event.widget.winfo_containing(event.x_root, event.y_root)
    except Exception:
        return
    while widget is not None:
        for canvas, inner in scroll_areas:
            if widget is canvas:
                if inner.winfo_reqheight() > canvas.winfo_height():
                    canvas.yview_scroll(int(-event.delta / 120), "units")
                return
        widget = widget.master

def make_scroll_area(parent):
    # A simple vertical-only scroll area. Returns (outer, inner): pack the
    # outer frame, and put your widgets inside the inner frame.
    global wheel_bound
    outer = tk.Frame(parent, background="#0B1320", highlightthickness=0, borderwidth=0)
    canvas = tk.Canvas(outer, background="#0B1320", highlightthickness=0, borderwidth=0)
    bar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, background="#0B1320", highlightthickness=0, borderwidth=0)
    window_id = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=bar.set)
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))
    canvas.pack(side="left", fill="both", expand=True)
    bar.pack(side="right", fill="y")
    scroll_areas.append((canvas, inner))
    if not wheel_bound:
        outer.bind_all("<MouseWheel>", on_mousewheel)
        wheel_bound = True
    return outer, inner


a = [
    ("What is it?",
     "The Caesar cipher is one of the oldest and simplest encryption methods. Every letter in the "
     "message is replaced by the letter a fixed number of positions further along the alphabet. "
     "That fixed number is called the shift, and it is the secret key.",
     None),
    ("How it works",
     "Number the letters A = 0 to Z = 25, add the shift, and wrap around after Z. "
     "Only letters change. Spaces, numbers and punctuation stay as they are.",
     "Encrypt:  E(x) = (x + shift) mod 26\nDecrypt:  D(x) = (x - shift) mod 26"),
    ("Example  (shift = 3)",
     "H → K, E → H, L → O, L → O, O → R. To decrypt, shift every letter back by 3.",
     "Plain text   :  HELLO WORLD\nCipher text  :  KHOOR ZRUOG"),
]

b = [
    ("What is it?",
     "The Atbash cipher is a substitution cipher that flips the alphabet. The first letter becomes the last, "
     "the second becomes the second to last, and so on. A becomes Z, B becomes Y, C becomes X. "
     "There is no key, so the same text always gives the same result.",
     None),
    ("How it works",
     "Number the letters A = 0 to Z = 25 and subtract the number from 25. "
     "Only letters change. Spaces, numbers and punctuation stay as they are.",
     "Encrypt:  E(x) = 25 - x\nDecrypt:  D(x) = 25 - x"),
    ("Example",
     "H → S, E → V, L → O, L → O, O → L. Decrypting is the same process, because flipping the alphabet twice gives the original letter back.",
     "Plain text   :  HELLO WORLD\nCipher text  :  SVOOL DLIOW"),
]

c = [
    ("What is it?",
     "The Vigenère cipher uses a keyword instead of a single shift. Each letter of the keyword gives a different "
     "Caesar shift, and the keyword repeats along the message. The same plain letter can become different "
     "cipher letters depending on where it appears.",
     None),
    ("How it works",
     "Turn each keyword letter into a number (A = 0 to Z = 25) and use it as the shift for the matching message letter. "
     "The keyword only moves forward on letters, so spaces and punctuation are skipped.",
     "Encrypt:  E(x) = (x + k) mod 26\nDecrypt:  D(x) = (x - k) mod 26"),
    ("Example  (keyword = KEY)",
     "H shifts by K (10), E by E (4), L by Y (24), then the keyword starts again: L by K, O by E, and so on.",
     "Keyword      :  KEYKE YKEYK\nPlain text   :  HELLO WORLD\nCipher text  :  RIJVS UYVJN"),
]

d = [
    ("What is it?",
     "ROT13 is a Caesar cipher with the shift fixed at 13. It has no key, so it is used to hide text "
     "casually, such as spoilers, rather than to protect it.",
     None),
    ("How it works",
     "The alphabet has 26 letters, so shifting by 13 twice brings every letter back to where it started. "
     "That means encrypting and decrypting are the same operation.",
     "Encrypt:  E(x) = (x + 13) mod 26\nDecrypt:  D(x) = (x + 13) mod 26"),
    ("Example",
     "H → U, E → R, L → Y, L → Y, O → B. Running ROT13 on the cipher text gives the original message back.",
     "Plain text   :  HELLO WORLD\nCipher text  :  URYYB JBEYQ"),
]

e = [
    ("What is it?",
     "The Reverse cipher writes the message backwards. It has no key and no letter substitution, "
     "so it is the simplest transformation in CipherLab.",
     None),
    ("How it works",
     "Read the text from the last character to the first. Every character, including spaces and punctuation, "
     "just moves to the opposite position.",
     "Encrypt:  text[::-1]\nDecrypt:  text[::-1]"),
    ("Example",
     "The first letter becomes the last, the second becomes the second to last, and so on. Reversing the cipher text gives the original message back.",
     "Plain text   :  HELLO WORLD\nCipher text  :  DLROW OLLEH"),
]

ciphers = [
    {"name" : "Caesar Cipher", "function" : "caesar_cipher", "option" : "caesar_option", "info" : "Shift Based cipher","learn_window":"caesar_learn","section":a},
    {"name" : "Atbash Cipher", "function" : "atbash_cipher", "option" : "atbash_option", "info" : "Substitution cipher","learn_window":"atbash_learn","section":b},
    {"name" : "Vigenère Cipher", "function" : "vigenere_cipher", "option" : "vigenere_option", "info" : "Keyword cipher","learn_window":"vigenere_learn","section":c},
    {"name" : "ROT13 Cipher", "function" : "rot13_cipher", "option" : "rot13_option", "info" : "Fixed 13 letter shift","learn_window":"rot13_learn","section":d},
    {"name" : "Reverse Cipher", "function" : "reverse_cipher", "option" : "reverse_option", "info" : "Reverses the text","learn_window":"reverse_learn","section":e},
]

buttons = []
fav_cards = []
favourites = []
max_favourites = 3
save_folder = os.path.join(os.path.expanduser("~"), ".cipherlab")
save_file = os.path.join(save_folder, "save.json")
loading_state = False

def save_state():
    if loading_state:
        return
    custom_list = []
    for item in ciphers:
        if item["function"] == "custom_cipher":
            custom_list.append({"name": item["name"], "info": item["info"], "data": item["custom"], "sample": item["sample"]})
    state = {"version": 1,
             "custom_ciphers": custom_list,
             "favourites": [item["name"] for item in favourites],
             "current": current_cipher["name"] if current_cipher is not None else None}
    try:
        os.makedirs(save_folder, exist_ok=True)
        temp_file = save_file + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        os.replace(temp_file, save_file)
    except OSError:
        pass

def load_state():
    global loading_state
    try:
        with open(save_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, ValueError):
        return
    if not isinstance(state, dict) or state.get("version") != 1:
        return
    loading_state = True
    for item in state.get("custom_ciphers", []):
        try:
            if not any(x["name"].lower() == item["name"].lower() for x in ciphers):
                add_custom_cipher(item["name"], item["info"], item["data"], item["sample"])
        except (KeyError, TypeError, ValueError):
            continue
    for name in state.get("favourites", []):
        for item in ciphers:
            if item["name"] == name:
                select_cipher(item)
    for item in ciphers:
        if item["name"] == state.get("current"):
            select_cipher(item)
    loading_state = False

def show_options(option_name):
    for f in [caesar_option, vigenere_option, no_option]:
        f.pack_forget()
    frame = options.get(option_name)
    if frame is not None:
        frame.pack(anchor="w")

def place_window(win, width, height):
    window.update_idletasks()
    x = window.winfo_rootx() + (window.winfo_width() - width) // 2
    y = window.winfo_rooty() + (window.winfo_height() - height) // 2
    win.geometry(str(width) + "x" + str(height) + "+" + str(max(x, 0)) + "+" + str(max(y, 0)))
    win.transient(window)
    win.bind("<Escape>", lambda e: win.destroy())

def create_sidebar_button(text,function):
    button = ttk.Button(sidebar , text = text , style = "Nav.TButton",command = function)
    button.pack(pady = 3, padx = 10, fill = "x", side = "top")
    buttons.append(button)
    return button

def page_active(button):
    for i in buttons:
        i.configure(style = "Nav.TButton")
    button.configure(style ="NavActive.TButton")

def show_page(page,button):
    for i in pages:
        i.pack_forget()
    page.pack(side="top", fill="both", expand=True)
    page_active(button)


cipher_card_window = None
current_cipher = None
def select_cipher(cipher):
    global cipher_card_window, current_cipher
    current_cipher = cipher
    if cipher not in favourites:
        if len(favourites) == max_favourites:
            favourites.pop(0)
            fav_cards.pop(0).destroy()
        favourites.append(cipher)
        card = create_cipher_card(fav_row, cipher,"fav")
        card.pack(side="left", padx=(0, 15))
        fav_cards.append(card)
    name_label.configure(text=cipher["name"])
    desc_label.configure(text=cipher["info"])
    show_options(cipher["option"])
    if cipher_card_window is not None and cipher_card_window.winfo_exists():
        cipher_card_window.destroy()
    save_state()

learn_window = None
def learn_content(cipher):
    global learn_window

    def create_learn_window(cipher):
        global learn_window
        learn_window = ttk.Toplevel(title=cipher["name"])
        place_window(learn_window, 800, 600)
        learn_window.configure(background="#0B1320")
        ttk.Label(learn_window, text=cipher["name"], style="LearnTitle.TLabel").pack(side="top", anchor="w", padx=20, pady=(20, 0))
        ttk.Label(learn_window, text=cipher["info"], style="LearnSub.TLabel").pack(side="top", anchor="w", padx=20, pady=(2, 10))
        ttk.Frame(learn_window, style="CardBorder.TFrame", height=1).pack(side="top", fill="x", pady=(0, 10))
        content_outer, content_area = make_scroll_area(learn_window)
        content_outer.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        for title_text, body_text, code_text in cipher["section"]:
            border = ttk.Frame(content_area, style="CardBorder.TFrame", padding=1)
            border.pack(side="top", fill="x", padx=(0, 15), pady=8)
            card = ttk.Frame(border, style="Card.TFrame", padding=20)
            card.pack(fill="both", expand=True)
            ttk.Label(card, text=title_text, style="LearnHead.TLabel").pack(anchor="w", pady=(0, 8))
            ttk.Label(card, text=body_text, style="LearnBody.TLabel", wraplength=660, justify="left").pack(anchor="w", pady=(0, 8))
            if code_text is not None:
                code_border = ttk.Frame(card, style="CardBorder.TFrame", padding=1)
                code_border.pack(anchor="w", pady=(0, 8))
                ttk.Label(code_border, text=code_text, style="Code.TLabel", justify="left").pack()
        if cipher["function"] == "custom_cipher":
            delete_button = ttk.Button(content_area, text="🗑  Delete this cipher", style="Del.TButton")
            delete_button.configure(command=lambda: confirm_delete(cipher, delete_button))
            delete_button.pack(anchor="w", pady=15)
        if cipher["learn_window"] == "caesar_learn":
            border = ttk.Frame(content_area, style="CardBorder.TFrame", padding=1)
            border.pack(side="top", fill="x", padx=(0, 15), pady=8)
            card = ttk.Frame(border, style="Card.TFrame", padding=20)
            card.pack(fill="both", expand=True)
            ttk.Label(card, text="The alphabet with shift 3", style="LearnHead.TLabel").pack(anchor="w", pady=(0, 8))
            grid_border = ttk.Frame(card, style="CardBorder.TFrame", padding=1)
            grid_border.pack(anchor="w")
            grid = ttk.Frame(grid_border, style="Content.TFrame", padding=8)
            grid.pack()
            ttk.Label(grid, text="Plain", style="AlphaCap.TLabel", width=6).grid(row=0, column=0)
            ttk.Label(grid, text="Cipher", style="AlphaCap.TLabel", width=6).grid(row=1, column=0)
            for i in range(26):
                ttk.Label(grid, text=chr(65 + i), style="AlphaPlain.TLabel", width=2).grid(row=0, column=i + 1)
                ttk.Label(grid, text=caesar_cipher(chr(65 + i), 3), style="AlphaCipher.TLabel", width=2).grid(row=1, column=i + 1)

    if learn_window is not None and learn_window.winfo_exists():
        learn_window.destroy()

    create_learn_window(cipher)

def create_cipher_card(parent, cipher,mode):
    card_border = ttk.Frame(parent, style="CardBorder.TFrame", padding=1)
    card = ttk.Frame(card_border, style="Card.TFrame", padding=(20, 12))
    card.pack(fill="both", expand=True)
    name = ttk.Label(card, text=cipher["name"], style="CardName.TLabel")
    name.pack(anchor="w")
    info_label = ttk.Label(card, text=cipher["info"], style="CardInfo.TLabel")
    info_label.pack(anchor="w")
    if mode == "fav":
        for w in [card_border, card, name, info_label]:
            w.bind("<Button-1>", lambda e: select_cipher(cipher))
            w.configure(cursor="hand2")
    if mode == "lrn":
        for w in [card_border , card , name ,info_label]:
            w.bind("<Button-1>", lambda e: learn_content(cipher))
            w.configure(cursor="hand2")
    return card_border

def fav_cipher():
    global cipher_card_window
    if cipher_card_window is not None and cipher_card_window.winfo_exists():
        cipher_card_window.lift()
        return
    cipher_card_window = ttk.Toplevel(title="Cipher's")
    place_window(cipher_card_window, 800, 600)
    cipher_card_window.configure(background="#0B1320")
    heading_label = ttk.Label(cipher_card_window, text="Select a Cipher", font=("Arial", 20, "bold"), background="#0B1320", foreground="#FFFFFF")
    heading_label.pack(pady=20)
    sep_2 = ttk.Frame(cipher_card_window, style="CardBorder.TFrame", height=1)
    sep_2.pack(side="top", fill="x", pady=(0, 20))
    cards_outer, cards_area = make_scroll_area(cipher_card_window)
    cards_outer.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    for i in ciphers:
        create_cipher_card(cards_area, i,"fav").pack(side="top", fill="x", padx=20, pady=10)

def caesar_cipher(text , shift):
    result= ''
    for i in text:
        if i.isascii() and i.isalpha():
            shift_base = ord('A') if i.isupper() else ord('a')
            result += chr((ord(i) - shift_base + shift) % 26 + shift_base)
        else:
            result += i
    return result

def atbash_cipher(text):
    result = ''
    for i in text:
        if i.isascii() and i.isalpha():
            base = ord('A') if i.isupper() else ord('a')
            result += chr(base + 25 - (ord(i) - base))
        else:
            result += i
    return result

def vigenere_cipher(text , key , decrypt = False):
    key = [ord(k.lower()) - 97 for k in key if k.isascii() and k.isalpha()]
    result = ''
    index = 0
    for i in text:
        if i.isascii() and i.isalpha():
            shift = key[index % len(key)]
            if decrypt:
                shift = -shift
            result += caesar_cipher(i , shift)
            index += 1
        else:
            result += i
    return result

def rot13_cipher(text):
    return caesar_cipher(text , 13)

def reverse_cipher(text):
    return text[::-1]

def substitution_cipher(text , alphabet , decrypt = False):
    result = ''
    for i in text:
        if i.isascii() and i.isalpha():
            if decrypt:
                letter = chr(65 + alphabet.index(i.upper()))
            else:
                letter = alphabet[ord(i.upper()) - 65]
            result += letter if i.isupper() else letter.lower()
        else:
            result += i
    return result

def open_text_file():
    path = filedialog.askopenfilename(title="Open a text file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if path == "":
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        show_result("Could not read that file. Use a plain text (.txt) file.")
        return
    if len(content) > 50000:
        show_result("That file is too big (the limit is 50,000 characters).")
        return
    message_text.text.delete("1.0", "end")
    message_text.text.insert("1.0", content)

def save_result_file():
    text = result_text.text.get("1.0", "end-1c")
    if text.strip() == "":
        show_result("Nothing to save yet. Encrypt or decrypt a message first.")
        return
    path = filedialog.asksaveasfilename(title="Save the result", defaultextension=".txt", filetypes=[("Text files", "*.txt")], initialfile="result.txt")
    if path == "":
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    except OSError:
        show_result("Could not save the file.")
        return
    save_button.configure(text="Saved!")
    window.after(1500, lambda: save_button.configure(text="Save"))

def show_result(text):
    result_text.text.delete("1.0", "end")
    result_text.text.insert("1.0", text)

def copy_result():
    window.clipboard_clear()
    window.clipboard_append(result_text.text.get("1.0", "end-1c"))
    copy_button.configure(text="Copied!")
    window.after(1500, lambda: copy_button.configure(text="Copy"))

runner_code = (
    "import sys, json\n"
    "d = json.load(sys.stdin)\n"
    "ns = {}\n"
    "exec(d['code'], ns)\n"
    "sys.stdout.write(json.dumps(str(ns[d['function']](d['text']))))\n"
)

def run_code_safely(code , function_name , text):
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    if getattr(sys, "frozen", False):
        # Packaged exe: relaunch ourselves in runner mode (see top of file).
        # Files are used instead of pipes because a windowed exe has no stdin/stdout.
        with tempfile.TemporaryDirectory() as folder:
            in_path = os.path.join(folder, "in.json")
            out_path = os.path.join(folder, "out.json")
            with open(in_path, "w", encoding="utf-8") as f:
                json.dump({"code": code, "function": function_name, "text": text}, f)
            try:
                subprocess.run([sys.executable, "--run-code", in_path, out_path],
                               timeout=10, creationflags=flags)
            except subprocess.TimeoutExpired:
                return "Error in your code: it ran for too long and was stopped."
            try:
                with open(out_path, "r", encoding="utf-8") as f:
                    out = json.load(f)
            except (OSError, ValueError):
                return "Error in your code: it crashed."
        if not out["ok"]:
            return "Error in your code: " + out["result"]
        return out["result"]
    payload = json.dumps({"code": code, "function": function_name, "text": text})
    try:
        done = subprocess.run([sys.executable, "-c", runner_code], input=payload, capture_output=True,
                              text=True, timeout=3, creationflags=flags)
    except subprocess.TimeoutExpired:
        return "Error in your code: it ran for more than 3 seconds and was stopped."
    if done.returncode != 0:
        lines = done.stderr.strip().splitlines()
        return "Error in your code: " + (lines[-1] if lines else "unknown error")
    return json.loads(done.stdout)

def run_custom(data , text , mode):
    if data["kind"] == "configure":
        if data["type"] == "Caesar":
            shift = data["shift"] if mode == "encrypt" else -data["shift"]
            return caesar_cipher(text , shift)
        if data["type"] == "Vigenère":
            return vigenere_cipher(text , data["keyword"] , mode == "decrypt")
        return substitution_cipher(text , data["alphabet"] , mode == "decrypt")
    code = data["encrypt"] if mode == "encrypt" else data["decrypt"]
    function_name = "encrypt" if mode == "encrypt" else "decrypt"
    return run_code_safely(code , function_name , text)

def clear_message():
    message_text.text.delete("1.0", "end")
    result_text.text.delete("1.0", "end")

def run_cipher(mode):
    if current_cipher is None:
        show_result("Select a cipher first.")
        return
    text = message_text.text.get("1.0", "end-1c")
    if text.strip() == "":
        show_result("Enter a message first.")
        return
    function = current_cipher["function"]
    if function == "caesar_cipher":
        shift = int(shift_box.get())
        if mode == "decrypt":
            shift = -shift
        result = caesar_cipher(text , shift)
    elif function == "vigenere_cipher":
        key = keyword_entry.get()
        if not any(k.isascii() and k.isalpha() for k in key):
            show_result("Enter a keyword (letters only) first.")
            return
        result = vigenere_cipher(text , key , mode == "decrypt")
    elif function == "atbash_cipher":
        result = atbash_cipher(text)
    elif function == "rot13_cipher":
        result = rot13_cipher(text)
    elif function == "reverse_cipher":
        result = reverse_cipher(text)
    elif function == "custom_cipher":
        result = run_custom(current_cipher["custom"] , text , mode)
    else:
        result = "This cipher is not available yet."
    show_result(result)

def change_form(num):
    add_cipher_form1.pack_forget()
    add_cipher_form2.pack_forget()
    if num == 1:
        add_cipher_form1.pack(side="top", fill="x", padx=20, pady=10)
    else:
        add_cipher_form2.pack(side="top", fill="x", padx=20, pady=10)

def show_settings(event=None):
    for f in [shift_frame, keyword_frame, alphabet_frame]:
        f.pack_forget()
    chosen = type_box.get()
    if chosen == "Caesar":
        shift_frame.pack(anchor="w", pady=(10, 0))
    elif chosen == "Vigenère":
        keyword_frame.pack(anchor="w", pady=(10, 0))
    else:
        alphabet_frame.pack(anchor="w", pady=(10, 0))

def run_page(cipher , mode , message_widget , result_widget):
    text = message_widget.text.get("1.0", "end-1c")
    result_widget.text.delete("1.0", "end")
    if text.strip() == "":
        result_widget.text.insert("1.0", "Enter a message first.")
        return
    result_widget.text.insert("1.0", run_custom(cipher["custom"] , text , mode))

def copy_page(result_widget , copy_btn):
    window.clipboard_clear()
    window.clipboard_append(result_widget.text.get("1.0", "end-1c"))
    copy_btn.configure(text="Copied!")
    window.after(1500, lambda: copy_btn.configure(text="Copy"))

def build_cipher_page(cipher):
    page = ttk.Frame(content, style="Content.TFrame")
    ttk.Label(page, text=cipher["name"], style="LearnTitle.TLabel").pack(side="top", anchor="w", padx=20, pady=(20, 0))
    ttk.Label(page, text=cipher["info"], style="LearnSub.TLabel").pack(side="top", anchor="w", padx=20, pady=(2, 10))
    ttk.Frame(page, style="CardBorder.TFrame", height=1).pack(side="top", fill="x", pady=(0, 10))

    page_message_box = ttk.Frame(page, style="Footer.TFrame", padding=15)
    page_message_box.pack(side="top", fill="x", padx=20, pady=(10, 10))
    ttk.Label(page_message_box, text="Message", font=("Arial", 13), background="#111827", foreground="#FFFFFF").pack(side="top", padx=20, anchor="w")
    page_message_border = ttk.Frame(page_message_box, style="CardBorder.TFrame", padding=1)
    page_message_border.pack(side="top", padx=20, pady=10, anchor="w")
    page_message = ScrolledText(page_message_border, padding=0, width=80, height=4, autohide=True, wrap="word")
    soft_style(page_message)
    page_message.pack()
    page_message.text.configure(font=("Arial", 13), background="#0B1320",
                                foreground="#FFFFFF", insertbackground="#FFFFFF",
                                borderwidth=0, highlightthickness=0, relief="flat",
                                padx=8, pady=8)

    page_buttons = ttk.Frame(page_message_box, style="Footer.TFrame")
    page_buttons.pack(side="top", anchor="w", padx=20, pady=(5, 0))
    ttk.Button(page_buttons, text="🔒  Encrypt", style="Enc.TButton", command=lambda: run_page(cipher, "encrypt", page_message, page_result)).pack(side="left", padx=(0, 10))
    ttk.Button(page_buttons, text="🔓  Decrypt", style="Dec.TButton", command=lambda: run_page(cipher, "decrypt", page_message, page_result)).pack(side="left")

    page_result_box = ttk.Frame(page, style="Footer.TFrame", padding=15)
    page_result_box.pack(side="top", fill="x", padx=20, pady=(0, 20))
    page_result_top = ttk.Frame(page_result_box, style="Footer.TFrame")
    page_result_top.pack(side="top", fill="x")
    ttk.Label(page_result_top, text="Result", font=("Arial", 13), background="#111827", foreground="#FFFFFF").pack(side="left", padx=20)
    page_copy = ttk.Button(page_result_top, text="Copy", style="Copy.TButton")
    page_copy.configure(command=lambda: copy_page(page_result, page_copy))
    page_copy.pack(side="right", padx=20)
    page_result_border = ttk.Frame(page_result_box, style="CardBorder.TFrame", padding=1)
    page_result_border.pack(side="top", padx=20, pady=10, anchor="w")
    page_result = ScrolledText(page_result_border, padding=0, width=80, height=3, autohide=True, wrap="word")
    soft_style(page_result)
    page_result.pack()
    page_result.text.configure(font=("Arial", 13), background="#0B1320",
                               foreground="#FFFFFF", insertbackground="#FFFFFF",
                               borderwidth=0, highlightthickness=0, relief="flat",
                               padx=8, pady=8)
    return page

def make_sections(info_text , data , sample):
    sections = [("What is it?", info_text, None)]
    if data["kind"] == "configure":
        if data["type"] == "Caesar":
            settings_text = "Type    :  Caesar\nShift   :  " + str(data["shift"])
        elif data["type"] == "Vigenère":
            settings_text = "Type    :  Vigenère\nKeyword :  " + data["keyword"].upper()
        else:
            settings_text = "Plain   :  ABCDEFGHIJKLMNOPQRSTUVWXYZ\nCipher  :  " + data["alphabet"]
        sections.append(("Settings", "The settings are saved with this cipher, so in the Lab you only type a message.", settings_text))
    else:
        sections.append(("Encryption code", "This runs when you press Encrypt.", data["encrypt"]))
        sections.append(("Decryption code", "This runs when you press Decrypt.", data["decrypt"]))
    sections.append(("Example", "A sample message encrypted with this cipher.", "Plain text   :  HELLO WORLD\nCipher text  :  " + sample))
    return sections

def add_custom_cipher(name , info_text , data , sample):
    new_cipher = {"name": name, "function": "custom_cipher", "option": "custom_option", "info": info_text,
                  "learn_window": "custom_learn", "section": make_sections(info_text, data, sample),
                  "custom": data, "sample": sample}
    ciphers.append(new_cipher)
    learn_card = create_cipher_card(learn_cards_area, new_cipher, "lrn")
    learn_card.pack(side="top", fill="x", padx=20, pady=10)
    page = build_cipher_page(new_cipher)
    pages.append(page)
    tab_button = create_sidebar_button("🔑 " + name, lambda: show_page(page, tab_button))
    new_cipher["learn_card"] = learn_card
    new_cipher["page"] = page
    new_cipher["tab_button"] = tab_button

def delete_custom_cipher(cipher):
    global current_cipher
    if learn_window is not None and learn_window.winfo_exists():
        learn_window.destroy()
    if cipher in favourites:
        index = favourites.index(cipher)
        favourites.pop(index)
        fav_cards.pop(index).destroy()
    if current_cipher is cipher:
        current_cipher = None
        name_label.configure(text="Select a cipher")
        desc_label.configure(text="Click Add Cipher above to pick one")
        show_options(None)
    was_open = cipher["page"].winfo_ismapped()
    pages.remove(cipher["page"])
    cipher["page"].destroy()
    buttons.remove(cipher["tab_button"])
    cipher["tab_button"].destroy()
    cipher["learn_card"].destroy()
    ciphers.remove(cipher)
    if was_open:
        show_page(lab_page, lab_button)
    save_state()

def confirm_delete(cipher , button):
    if button.cget("text") != "Click again to confirm":
        button.configure(text="Click again to confirm")
        window.after(3000, lambda: button.winfo_exists() and button.configure(text="🗑  Delete this cipher"))
        return
    delete_custom_cipher(cipher)

def save_cipher():
    name = new_name_entry.get().strip()
    info_text = new_info_entry.get().strip()
    if name == "" or info_text == "":
        save_status.configure(text="Enter a name and short information first.", foreground="#EF4444")
        return
    if len(name) > 24:
        save_status.configure(text="Name can be at most 24 characters.", foreground="#EF4444")
        return
    if len(info_text) > 70:
        save_status.configure(text="Short information can be at most 70 characters.", foreground="#EF4444")
        return
    if any(c["name"].lower() == name.lower() for c in ciphers):
        save_status.configure(text="A cipher with that name already exists.", foreground="#EF4444")
        return
    data = {}
    if mode.get() == "configure":
        data["kind"] = "configure"
        data["type"] = type_box.get()
        if data["type"] == "Caesar":
            data["shift"] = int(new_shift_box.get())
        elif data["type"] == "Vigenère":
            data["keyword"] = new_keyword_entry.get().strip()
            if not any(k.isascii() and k.isalpha() for k in data["keyword"]):
                save_status.configure(text="Enter a keyword (letters only).", foreground="#EF4444")
                return
        else:
            data["alphabet"] = new_alphabet_entry.get().strip().upper()
            if len(data["alphabet"]) != 26 or len(set(data["alphabet"])) != 26 or not (data["alphabet"].isascii() and data["alphabet"].isalpha()):
                save_status.configure(text="Alphabet needs 26 different letters.", foreground="#EF4444")
                return
    else:
        data["kind"] = "code"
        data["encrypt"] = encrypt_code.text.get("1.0", "end-1c")
        data["decrypt"] = decrypt_code.text.get("1.0", "end-1c")
        if "def encrypt" not in data["encrypt"] or "def decrypt" not in data["decrypt"]:
            save_status.configure(text="Define encrypt(text) and decrypt(text).", foreground="#EF4444")
            return
    sample = run_custom(data , "HELLO WORLD" , "encrypt")
    if sample.startswith("Error in your code"):
        save_status.configure(text=sample, foreground="#EF4444")
        return
    add_custom_cipher(name, info_text, data, sample)
    new_name_entry.delete(0, "end")
    new_info_entry.delete(0, "end")
    new_keyword_entry.delete(0, "end")
    new_alphabet_entry.delete(0, "end")
    save_status.configure(text="Cipher saved! Find it in the Lab and the sidebar.", foreground="#10B981")
    save_state()

# Main window

window = ttk.Window(themename="darkly")
window.title("CipherLab")
window.geometry("1200x750")
window.configure(background="#0B1320")
window.minsize(1200, 750)

window.option_add("*TCombobox*Listbox.background", "#0B1320")
window.option_add("*TCombobox*Listbox.foreground", "#FFFFFF")
window.option_add("*TCombobox*Listbox.selectBackground", "#1E3A6E")
window.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
window.option_add("*TCombobox*Listbox.highlightThickness", 0)
window.option_add("*TCombobox*Listbox.borderWidth", 0)

style = ttk.Style()
style.configure("TopBar.TFrame",background="#111827")
style.configure("TopBar.TLabel",background="#111827",foreground="#FFFFFF",font=("Arial", 16, "bold"))
style.configure("Content.TFrame",background="#0B1320")
style.configure("Nav.TButton", background="#111827", foreground="#E5E7EB",
                font=("Arial", 11), anchor="w", padding=(15,10),
                borderwidth=0, focuscolor="#111827")
style.map("Nav.TButton", background=[("active", "#1F2937")])
style.configure("NavActive.TButton", background="#1E3A6E", foreground="#FFFFFF",
                font=("Arial", 11, "bold"), anchor="w", padding=(15,10),
                borderwidth=0, focuscolor="#1E3A6E")
style.map("NavActive.TButton", background=[("active", "#1E3A6E")])

topbar = ttk.Frame(window,style="TopBar.TFrame",height=50)
topbar.pack(side="top", fill="x")
topbar.pack_propagate(False)
title = ttk.Label(topbar,text="🔐  CipherLab",   style="TopBar.TLabel")
title.pack(side="left", padx=20)
status = ttk.Label(topbar,text="● Ready",background="#111827",foreground="#10B981",font=("Arial", 10))
status.pack(side="right", padx=20)

# Footer

style.configure("Footer.TFrame",background="#111827")
style.configure("Footer.TLabel",background="#111827",foreground="#8B97AD",font=("Arial", 9))
footer = ttk.Frame(window,style="Footer.TFrame",height=30)
footer.pack(side="bottom", fill="x")
footer.pack_propagate(False)
version = ttk.Label(footer,text="CipherLab v1.0",style="Footer.TLabel")
version.pack(side="left", padx=20)
info = ttk.Label(footer,text="Classical Cryptography  •  Educational Tool",style="Footer.TLabel")
info.pack(side="right", padx=20)

# Sidebar

style.configure("Sidebar.TFrame",background="#111827")
sidebar = ttk.Frame(window,style="Sidebar.TFrame",width=200)
sidebar.pack(side="left",fill="y")
sidebar.pack_propagate(False)

#Content

content = ttk.Frame(window,style = "Content.TFrame")
content.pack(side="right",fill="both",expand = "True")

style.configure("CardBorder.TFrame", background="#1F2A44")
style.configure("Card.TFrame", background="#111827")
style.configure("CardPlus.TLabel", background="#111827", foreground="#FFFFFF", font=("Arial", 30))
style.configure("CardCaption.TLabel", background="#111827", foreground="#FFFFFF", font=("Arial", 13))
style.configure("CardName.TLabel", background="#111827", foreground="#FFFFFF", font=("Arial", 13, "bold"))
style.configure("CardInfo.TLabel", background="#111827", foreground="#8B97AD", font=("Arial", 10))

style.configure("LearnTitle.TLabel", background="#0B1320", foreground="#FFFFFF", font=("Arial", 20, "bold"))
style.configure("LearnSub.TLabel", background="#0B1320", foreground="#8B97AD", font=("Arial", 11))
style.configure("LearnHead.TLabel", background="#111827", foreground="#FFFFFF", font=("Arial", 14, "bold"))
style.configure("LearnBody.TLabel", background="#111827", foreground="#E5E7EB", font=("Arial", 11))
style.configure("Code.TLabel", background="#0B1320", foreground="#93C5FD", font=("Consolas", 12), padding=(12, 8))
style.configure("AlphaPlain.TLabel", background="#0B1320", foreground="#8B97AD", font=("Consolas", 11), anchor="center")
style.configure("AlphaCipher.TLabel", background="#0B1320", foreground="#60A5FA", font=("Consolas", 11, "bold"), anchor="center")
style.configure("AlphaCap.TLabel", background="#0B1320", foreground="#8B97AD", font=("Arial", 9))

lab_page = ttk.Frame(content, style="Content.TFrame")
lab_label = ttk.Label(lab_page, text="Cipher Lab", font=("Arial", 20, "bold"), background="#0B1320", foreground="#FFFFFF").pack(side="top", padx=20, pady=20, anchor="w")
cards_frame = ttk.Frame(lab_page, style="Content.TFrame")
cards_frame.pack(side="top", fill="x", padx=20)
fav_row = ttk.Frame(cards_frame, style="Content.TFrame")
fav_row.pack(side="left")
card_border = ttk.Frame(cards_frame, style="CardBorder.TFrame", padding=1)
card_border.pack(side="left", padx=(0, 15))
card = ttk.Frame(card_border, style="Card.TFrame", padding=(50, 10))
card.pack()
plus = ttk.Label(card, text="+", style="CardPlus.TLabel")
plus.pack(side="left", padx=(0, 20))
caption = ttk.Label(card, text="Add Cipher", style="CardCaption.TLabel")
caption.pack(side="left")

for w in [card_border, card, plus, caption]:
    w.bind("<Button-1>", lambda e: fav_cipher())
    w.configure(cursor="hand2")

message_box = ttk.Frame(lab_page, style="Footer.TFrame", padding=15, height=200)
message_box.pack(side="top", fill="x", padx=20, pady=20)

name_label = ttk.Label(message_box , text = "Select a cipher",font=("Arial", 20, "bold"),background="#111827", foreground="#FFFFFF")
name_label.pack(side="top", padx=20, pady=0, anchor="w")
desc_label = ttk.Label(message_box , text = "Click Add Cipher above to pick one",font=("Arial", 13),background="#111827", foreground="#FFFFFF")
desc_label.pack(side="top", padx=20, pady=10, anchor="w")
sep_1 = ttk.Frame(message_box, style="CardBorder.TFrame", height=1)
sep_1.pack(side="top", fill="x", pady=(0, 20))
message_label =ttk.Label(message_box , text = "Message",font=("Arial", 13),background="#111827", foreground="#FFFFFF")
message_label.pack(side="top", padx=20, pady=0, anchor="w")

boxframe = ttk.Frame(message_box , style="Footer.TFrame", padding=0)
boxframe.pack(side="top", fill="x", padx=1, pady=2, anchor="w")
entry_border = ttk.Frame(boxframe, style="CardBorder.TFrame", padding=1)
entry_border.pack(side="left", padx=20, pady=10, anchor="n")

message_text = ScrolledText(entry_border, padding=0, width=80, height=4, autohide=True, wrap="word")
soft_style(message_text)
message_text.pack()

message_text.text.configure(font=("Arial", 13), background="#0B1320",
                            foreground="#FFFFFF", insertbackground="#FFFFFF",
                            borderwidth=0, highlightthickness=0, relief="flat",
                            padx=8, pady=8)

options_frame = ttk.Frame(boxframe , style="Footer.TFrame", padding=0)
options_frame.pack(side="left", padx=20, pady=10, anchor="n")

style.configure("Form.TEntry", fieldbackground="#0B1320", foreground="#FFFFFF", insertcolor="#FFFFFF",
                bordercolor="#1F2A44", lightcolor="#1F2A44", darkcolor="#1F2A44", padding=6)
style.configure("Del.TButton", background="#7F1D1D", foreground="#FFFFFF", font=("Arial", 11, "bold"),
                padding=(18, 8), borderwidth=0, focuscolor="#7F1D1D")
style.map("Del.TButton", background=[("active", "#991B1B")])

style.configure("Drop.TCombobox", fieldbackground="#0B1320", background="#1F2A44", foreground="#FFFFFF",
                arrowcolor="#FFFFFF", bordercolor="#1F2A44", lightcolor="#1F2A44", darkcolor="#1F2A44")
style.map("Drop.TCombobox", fieldbackground=[("readonly", "#0B1320")], foreground=[("readonly", "#FFFFFF")],
          background=[("readonly", "#1F2A44")])

caesar_option = ttk.Frame(options_frame , style="Footer.TFrame")
shift_label = ttk.Label(caesar_option , text="Shift:", font=("Arial", 13), background="#111827", foreground="#FFFFFF")
shift_label.pack(anchor="w")
shift_box = ttk.Combobox(caesar_option, values=list(range(1, 26)), width=8, state="readonly", style="Drop.TCombobox")
shift_box.set(3)
shift_box.pack(anchor="w", pady=5)

popdown = shift_box.tk.eval("ttk::combobox::PopdownWindow " + str(shift_box))
shift_box.tk.call(popdown + ".f.l", "configure", "-background", "#0B1320", "-foreground", "#FFFFFF",
                  "-selectbackground", "#1E3A6E", "-selectforeground", "#FFFFFF",
                  "-highlightthickness", 0, "-borderwidth", 0)

vigenere_option = ttk.Frame(options_frame, style="Footer.TFrame")
keyword_label = ttk.Label(vigenere_option, text="Keyword", font=("Arial", 13), background="#111827", foreground="#FFFFFF")
keyword_label.pack(anchor="w")
keyword_entry = ttk.Entry(vigenere_option, width=20, style="Form.TEntry")
keyword_entry.pack(anchor="w", pady=5)

no_option = ttk.Frame(options_frame, style="Footer.TFrame")
no_option_label = ttk.Label(no_option, text="", font=("Arial", 13), background="#111827", foreground="#8B97AD")
no_option_label.pack(anchor="w")


options = {
    "caesar_option": caesar_option,
    "vigenere_option": vigenere_option,
    "atbash_option": no_option,
    "rot13_option": no_option,
    "reverse_option": no_option,
    "custom_option": no_option,
}

style.configure("Enc.TButton", background="#2563EB", foreground="#FFFFFF", font=("Arial", 12, "bold"),
                padding=(25, 8), borderwidth=0, focuscolor="#2563EB")
style.map("Enc.TButton", background=[("active", "#1D4ED8")])
style.configure("Dec.TButton", background="#111827", foreground="#E5E7EB", font=("Arial", 12),
                padding=(25, 8), borderwidth=1, bordercolor="#1F2A44", focuscolor="#111827")
style.map("Dec.TButton", background=[("active", "#1F2937")])
style.configure("Copy.TButton", background="#111827", foreground="#E5E7EB", font=("Arial", 10),
                padding=(12, 4), borderwidth=1, bordercolor="#1F2A44", focuscolor="#111827")
style.map("Copy.TButton", background=[("active", "#1F2937")])
style.configure("Clear.TButton", background="#111827", foreground="#8B97AD", font=("Arial", 12),
                padding=(25, 8), borderwidth=1, bordercolor="#1F2A44", focuscolor="#111827")
style.map("Clear.TButton", background=[("active", "#1F2937")], foreground=[("active", "#FFFFFF")])

button_row = ttk.Frame(message_box, style="Footer.TFrame")
button_row.pack(side="top", anchor="w", padx=20, pady=(5, 0))
encrypt_button = ttk.Button(button_row, text="🔒  Encrypt", style="Enc.TButton", command=lambda: run_cipher("encrypt"))
encrypt_button.pack(side="left", padx=(0, 10))
decrypt_button = ttk.Button(button_row, text="🔓  Decrypt", style="Dec.TButton", command=lambda: run_cipher("decrypt"))
decrypt_button.pack(side="left")
clear_button = ttk.Button(button_row ,text = "Clear", style = "Clear.TButton" ,command = lambda: clear_message())
clear_button.pack(side = "left" ,padx = (5 , 0))
open_button = ttk.Button(button_row, text="📂  Open file", style="Clear.TButton", command=open_text_file)
open_button.pack(side="left", padx=(5, 0))

result_box = ttk.Frame(lab_page, style="Footer.TFrame", padding=15)
result_box.pack(side="top", fill="x", padx=20, pady=(0, 20))
result_top = ttk.Frame(result_box, style="Footer.TFrame")
result_top.pack(side="top", fill="x")
result_label = ttk.Label(result_top, text="Result", font=("Arial", 13), background="#111827", foreground="#FFFFFF")
result_label.pack(side="left", padx=20)
copy_button = ttk.Button(result_top, text="Copy", style="Copy.TButton", command=copy_result)
copy_button.pack(side="right", padx=20)
save_button = ttk.Button(result_top, text="Save", style="Copy.TButton", command=save_result_file)
save_button.pack(side="right")
result_border = ttk.Frame(result_box, style="CardBorder.TFrame", padding=1)
result_border.pack(side="top", padx=20, pady=10, anchor="w")
result_text = ScrolledText(result_border, padding=0, width=80, height=3, autohide=True, wrap="word")
soft_style(result_text)
result_text.pack()
result_text.text.configure(font=("Arial", 13), background="#0B1320",
                           foreground="#FFFFFF", insertbackground="#FFFFFF",
                           borderwidth=0, highlightthickness=0, relief="flat",
                           padx=8, pady=8)

learn_page = ttk.Frame(content,style = "Content.TFrame")
add_page = ttk.Frame(content,style = "Content.TFrame")

pages = [lab_page, learn_page, add_page]

lab_button = create_sidebar_button("🏠 Lab", lambda: show_page(lab_page, lab_button))
learn_button = create_sidebar_button("📖 Learn", lambda: show_page(learn_page, learn_button))
add_button = create_sidebar_button("➕ Add Cipher", lambda: show_page(add_page, add_button))

learn_label = ttk.Label(learn_page, text="Learn", font=("Arial", 20, "bold"), background="#0B1320", foreground="#FFFFFF")
learn_label.pack(side="top", padx=20, pady=20, anchor="w")
learn_line = ttk.Frame(learn_page, style="CardBorder.TFrame", height=1)
learn_line.pack(side="top", fill="x", pady=(0, 20))

lesson_list = ttk.Frame(learn_page, style="Content.TFrame")
lesson_list.pack(side="left", padx=20, anchor="n")
lesson_box = ttk.Frame(learn_page, style="Footer.TFrame", padding=20)
lesson_box.pack(side="left", fill="both", expand=True, padx=(0, 20), pady=(0, 20))

learn_cards_outer, learn_cards_area = make_scroll_area(lesson_box)
learn_cards_outer.pack(fill="both", expand=True, padx=20, pady=(0, 20))
for i in ciphers:
    create_cipher_card(learn_cards_area, i,"lrn").pack(side="top", fill="x", padx=20, pady=10)

style.configure("Mode.TRadiobutton", background="#0B1320", foreground="#E5E7EB",
                font=("Arial", 13), focuscolor="#0B1320", padding=(0, 6))
style.map("Mode.TRadiobutton",
          background=[("active", "#0B1320"), ("selected", "#0B1320")],
          foreground=[("active", "#FFFFFF"), ("selected", "#FFFFFF")])
style.configure("FormLabel.TLabel", background="#111827", foreground="#FFFFFF", font=("Arial", 13))
style.configure("FormHint.TLabel", background="#111827", foreground="#8B97AD", font=("Arial", 10))
style.configure("Save.TButton", background="#2563EB", foreground="#FFFFFF", font=("Arial", 12, "bold"),
                padding=(25, 8), borderwidth=0, focuscolor="#2563EB")
style.map("Save.TButton", background=[("active", "#1D4ED8")])

add_label = ttk.Label(add_page, text="➕ Add New Cipher", font=("Arial", 20, "bold"), background="#0B1320", foreground="#FFFFFF").pack(side="top", padx=20, pady=20, anchor="w")

common_box = ttk.Frame(add_page, style="Footer.TFrame", padding=15)
common_box.pack(side="top", fill="x", padx=20, pady=(0, 10))
ttk.Label(common_box, text="Cipher Name", style="FormLabel.TLabel").pack(anchor="w")
new_name_entry = ttk.Entry(common_box, width=40, style="Form.TEntry")
new_name_entry.pack(anchor="w", pady=(5, 10))
ttk.Label(common_box, text="Short Information", style="FormLabel.TLabel").pack(anchor="w")
new_info_entry = ttk.Entry(common_box, width=80, style="Form.TEntry")
new_info_entry.pack(anchor="w", pady=5)

mode = ttk.StringVar(value="configure")
mode_row = ttk.Frame(add_page, style="Content.TFrame")
mode_row.pack(side="top", anchor="w", padx=20)
ttk.Radiobutton(mode_row, text="Configure a Cipher", variable=mode, value="configure", style="Mode.TRadiobutton", command=lambda: change_form(1)).pack(side="left", padx=(0, 30))
ttk.Radiobutton(mode_row, text="Write Custom Code", variable=mode, value="code", style="Mode.TRadiobutton", command=lambda: change_form(2)).pack(side="left")

form_area = ttk.Frame(add_page, style="Content.TFrame")
form_area.pack(side="top", fill="x")

add_cipher_form1 = ttk.Frame(form_area, style="Footer.TFrame", padding=20)
ttk.Label(add_cipher_form1, text="Cipher Type", style="FormLabel.TLabel").pack(anchor="w")
type_box = ttk.Combobox(add_cipher_form1, values=["Caesar", "Vigenère", "Substitution"], width=20, state="readonly", style="Drop.TCombobox")
type_box.set("Caesar")
type_box.pack(anchor="w", pady=5)
type_box.bind("<<ComboboxSelected>>", show_settings)

shift_frame = ttk.Frame(add_cipher_form1, style="Footer.TFrame")
ttk.Label(shift_frame, text="Shift", style="FormLabel.TLabel").pack(anchor="w")
new_shift_box = ttk.Combobox(shift_frame, values=list(range(1, 26)), width=8, state="readonly", style="Drop.TCombobox")
new_shift_box.set(3)
new_shift_box.pack(anchor="w", pady=5)

keyword_frame = ttk.Frame(add_cipher_form1, style="Footer.TFrame")
ttk.Label(keyword_frame, text="Keyword", style="FormLabel.TLabel").pack(anchor="w")
new_keyword_entry = ttk.Entry(keyword_frame, width=30, style="Form.TEntry")
new_keyword_entry.pack(anchor="w", pady=5)

alphabet_frame = ttk.Frame(add_cipher_form1, style="Footer.TFrame")
ttk.Label(alphabet_frame, text="Substitution Alphabet", style="FormLabel.TLabel").pack(anchor="w")
new_alphabet_entry = ttk.Entry(alphabet_frame, width=40, style="Form.TEntry")
new_alphabet_entry.pack(anchor="w", pady=5)
ttk.Label(alphabet_frame, text="26 different letters. A becomes the 1st letter, B the 2nd, and so on.", style="FormHint.TLabel").pack(anchor="w")

add_cipher_form2 = ttk.Frame(form_area, style="Footer.TFrame", padding=20)
encrypt_col = ttk.Frame(add_cipher_form2, style="Footer.TFrame")
encrypt_col.pack(side="left", anchor="n")
decrypt_col = ttk.Frame(add_cipher_form2, style="Footer.TFrame")
decrypt_col.pack(side="left", anchor="n", padx=(20, 0))

ttk.Label(encrypt_col, text="Encryption Function", style="FormLabel.TLabel").pack(anchor="w")
encrypt_border = ttk.Frame(encrypt_col, style="CardBorder.TFrame", padding=1)
encrypt_border.pack(anchor="w", pady=5)
encrypt_code = ScrolledText(encrypt_border, padding=0, width=45, height=8, autohide=True, wrap="none")
soft_style(encrypt_code)
encrypt_code.pack()
encrypt_code.text.configure(font=("Consolas", 12), background="#0B1320", foreground="#93C5FD",
                            insertbackground="#FFFFFF", borderwidth=0, highlightthickness=0,
                            relief="flat", padx=8, pady=8)
encrypt_code.text.insert("1.0", "def encrypt(text):\n    return text")

ttk.Label(decrypt_col, text="Decryption Function", style="FormLabel.TLabel").pack(anchor="w")
decrypt_border = ttk.Frame(decrypt_col, style="CardBorder.TFrame", padding=1)
decrypt_border.pack(anchor="w", pady=5)
decrypt_code = ScrolledText(decrypt_border, padding=0, width=45, height=8, autohide=True, wrap="none")
soft_style(decrypt_code)
decrypt_code.pack()
decrypt_code.text.configure(font=("Consolas", 12), background="#0B1320", foreground="#93C5FD",
                            insertbackground="#FFFFFF", borderwidth=0, highlightthickness=0,
                            relief="flat", padx=8, pady=8)
decrypt_code.text.insert("1.0", "def decrypt(text):\n    return text")

save_row = ttk.Frame(add_page, style="Content.TFrame")
save_row.pack(side="top", anchor="w", padx=20, pady=(5, 20))
ttk.Button(save_row, text="💾  Save Cipher", style="Save.TButton", command=save_cipher).pack(side="left")
save_status = ttk.Label(save_row, text="", background="#0B1320", foreground="#10B981", font=("Arial", 11))
save_status.pack(side="left", padx=15)

change_form(1)
show_settings()

def on_close():
    save_state()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_close)

load_state()
show_page(lab_page, lab_button)

window.mainloop()