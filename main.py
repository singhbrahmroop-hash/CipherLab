import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText , ScrolledFrame
#Functions

ciphers = [
    {"name" : "Caesar Cipher", "function" : "caesar_cipher", "option" : "caesar_option", "info" : "Shift Based cipher"},
    {"name" : "Atbash Cipher", "function" : "atbash_cipher", "option" : "atbash_option", "info" : "Substitution cipher"},
    {"name" : "Vigenère Cipher", "function" : "vigenere_cipher", "option" : "vigenere_option", "info" : "Keyword cipher"},
    {"name" : "ROT13 Cipher", "function" : "rot13_cipher", "option" : "rot13_option", "info" : "Fixed 13 letter shift"},
    {"name" : "Reverse Cipher", "function" : "reverse_cipher", "option" : "reverse_option", "info" : "Reverses the text"},
]

buttons = []
fav_cards = []
favourites = []
max_favourites = 3

def show_options(option_name):
    for f in [caesar_option, vigenere_option, no_option]:
        f.pack_forget()
    frame = options.get(option_name)
    if frame is not None:
        frame.pack(anchor="w")

def create_sidebar_button(text,function):
    button = ttk.Button(sidebar , text = text , style = "Nav.TButton",command = function)
    button.pack(pady = 5, side = "top")
    buttons.append(button)
    return button

def page_active(button):
    for i in buttons:
        i.configure(style = "Nav.TButton")
    button.configure(style ="NavActive.TButton")

def show_page(page,button):
    for i in [lab_page, learn_page, challenges_page, progress_page, add_page]:
        i.pack_forget()
    page.pack(side="top", fill="both", expand=True)
    page_active(button)


cipher_card_window = None
current_cipher = None
count = 0
def select_cipher(cipher):
    global cipher_card_window, current_cipher
    current_cipher = cipher
    if cipher not in favourites:
        if len(favourites) == max_favourites:
            favourites.pop(0)
            fav_cards.pop(0).destroy()
        favourites.append(cipher)
        card = create_cipher_card(fav_row, cipher)
        card.pack(side="left", padx=(0, 15))
        fav_cards.append(card)
    name_label.configure(text=cipher["name"])
    desc_label.configure(text=cipher["info"])
    show_options(cipher["option"])
    if cipher_card_window is not None and cipher_card_window.winfo_exists():
        cipher_card_window.destroy()

def create_cipher_card(parent, cipher):
    card_border = ttk.Frame(parent, style="CardBorder.TFrame", padding=1)
    card = ttk.Frame(card_border, style="Card.TFrame", padding=(20, 12))
    card.pack(fill="both", expand=True)
    name = ttk.Label(card, text=cipher["name"], style="CardName.TLabel")
    name.pack(anchor="w")
    info_label = ttk.Label(card, text=cipher["info"], style="CardInfo.TLabel")
    info_label.pack(anchor="w")

    for w in [card_border, card, name, info_label]:
        w.bind("<Button-1>", lambda e: select_cipher(cipher))
        w.configure(cursor="hand2")
    return card_border

def fav_cipher():
    global cipher_card_window
    if cipher_card_window is not None and cipher_card_window.winfo_exists():
        cipher_card_window.lift()
        return
    cipher_card_window = ttk.Toplevel(title="Cipher's")
    cipher_card_window.geometry("800x600")
    cipher_card_window.configure(background="#0B1320")
    heading_label = ttk.Label(cipher_card_window, text="Select a Cipher", font=("Arial", 20, "bold"), background="#0B1320", foreground="#FFFFFF")
    heading_label.pack(pady=20)
    sep_2 = ttk.Frame(cipher_card_window, style="CardBorder.TFrame", height=1)
    sep_2.pack(side="top", fill="x", pady=(0, 20))
    cards_area = ScrolledFrame(cipher_card_window, autohide=True)
    cards_area.configure(style="Content.TFrame")
    cards_area.container.configure(style="Content.TFrame")
    cards_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    for i in ciphers:
        create_cipher_card(cards_area, i).pack(side="top", fill="x", padx=20, pady=10)

def caesar_cipher(text , shift):
    result= ''
    for i in text:
        if i.isalpha():
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

def show_result(text):
    result_text.text.delete("1.0", "end")
    result_text.text.insert("1.0", text)

def copy_result():
    window.clipboard_clear()
    window.clipboard_append(result_text.text.get("1.0", "end-1c"))
    copy_button.configure(text="Copied!")
    window.after(1500, lambda: copy_button.configure(text="Copy"))

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
    else:
        result = "This cipher is not available yet."
    show_result(result)

# Main window

window = ttk.Window(themename="darkly")
window.title("CipherLab")
window.geometry("1200x750")
window.configure(background="#0B1320")

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
desc_label = ttk.Label(message_box , text = "Select Cipher",font=("Arial", 13),background="#111827", foreground="#FFFFFF")
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
message_text.configure(style="Content.TFrame")
message_text.pack()

message_text.text.configure(font=("Arial", 13), background="#0B1320",
                            foreground="#FFFFFF", insertbackground="#FFFFFF",
                            borderwidth=0, highlightthickness=0, relief="flat",
                            padx=8, pady=8)

options_frame = ttk.Frame(boxframe , style="Footer.TFrame", padding=0)
options_frame.pack(side="left", padx=20, pady=10, anchor="n")

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
keyword_entry = ttk.Entry(vigenere_option, width=20)
keyword_entry.pack(anchor="w", pady=5)

no_option = ttk.Frame(options_frame, style="Footer.TFrame")
no_option_label = ttk.Label(no_option, text="No settings for this cipher", font=("Arial", 13), background="#111827", foreground="#8B97AD")
no_option_label.pack(anchor="w")


options = {
    "caesar_option": caesar_option,
    "vigenere_option": vigenere_option,
    "atbash_option": no_option,
    "rot13_option": no_option,
    "reverse_option": no_option,
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

button_row = ttk.Frame(message_box, style="Footer.TFrame")
button_row.pack(side="top", anchor="w", padx=20, pady=(5, 0))
encrypt_button = ttk.Button(button_row, text="🔒  Encrypt", style="Enc.TButton", command=lambda: run_cipher("encrypt"))
encrypt_button.pack(side="left", padx=(0, 10))
decrypt_button = ttk.Button(button_row, text="🔓  Decrypt", style="Dec.TButton", command=lambda: run_cipher("decrypt"))
decrypt_button.pack(side="left")

result_box = ttk.Frame(lab_page, style="Footer.TFrame", padding=15)
result_box.pack(side="top", fill="x", padx=20, pady=(0, 20))
result_top = ttk.Frame(result_box, style="Footer.TFrame")
result_top.pack(side="top", fill="x")
result_label = ttk.Label(result_top, text="Result", font=("Arial", 13), background="#111827", foreground="#FFFFFF")
result_label.pack(side="left", padx=20)
copy_button = ttk.Button(result_top, text="Copy", style="Copy.TButton", command=copy_result)
copy_button.pack(side="right", padx=20)
result_border = ttk.Frame(result_box, style="CardBorder.TFrame", padding=1)
result_border.pack(side="top", padx=20, pady=10, anchor="w")
result_text = ScrolledText(result_border, padding=0, width=80, height=3, autohide=True, wrap="word")
result_text.configure(style="Content.TFrame")
result_text.pack()
result_text.text.configure(font=("Arial", 13), background="#0B1320",
                           foreground="#FFFFFF", insertbackground="#FFFFFF",
                           borderwidth=0, highlightthickness=0, relief="flat",
                           padx=8, pady=8)

learn_page = ttk.Frame(content,style = "Content.TFrame")
learn_label = ttk.Label(learn_page,text="Learn").pack()
add_page = ttk.Frame(content,style = "Content.TFrame")
add_label = ttk.Label(add_page,text="Add Cipher").pack()
challenges_page = ttk.Frame(content,style = "Content.TFrame")
challenges_label = ttk.Label(challenges_page,text="Challenges").pack()
progress_page = ttk.Frame(content,style = "Content.TFrame")
progress_label = ttk.Label(progress_page,text="Progress").pack()

lab_button = create_sidebar_button("🏠 Lab", lambda: show_page(lab_page, lab_button))
learn_button = create_sidebar_button("📖 Learn", lambda: show_page(learn_page, learn_button))
add_button = create_sidebar_button("➕ Add Cipher", lambda: show_page(add_page, add_button))
challenges_button = create_sidebar_button("🎯 Challenges", lambda: show_page(challenges_page, challenges_button))
progress_button = create_sidebar_button("📊 Progress", lambda: show_page(progress_page, progress_button))


window.mainloop()