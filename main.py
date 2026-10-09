import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText
#Functions

style = ttk.Style()
style.configure("CardName.TLabel", background="#111827", foreground="#FFFFFF", font=("Arial", 13, "bold"))
style.configure("CardInfo.TLabel", background="#111827", foreground="#8B97AD", font=("Arial", 10))
ciphers = [{"name" : "Caesar Cipher", "function" : "caesar_cipher", "option" : "caesar_option", "info" : "Shift Based cipher"}]

def select_cipher(cipher):
    print(cipher["name"])

def show_cipher_cards(parent):
    for index, cipher in enumerate(ciphers):
        card = create_cipher_card(parent, cipher)
        card.grid(row=index // 3, column=index % 3, padx=10, pady=10, sticky="nsew")

def create_cipher_card(parent , cipher):
    card_border = ttk.Frame(parent , style ="CardBorder.TFrame")
    card = ttk.Frame(card_border , style = "Card.TFrame" , padding=(20,5))
    card.pack(fill="both", expand = "true")

    name = ttk.Label(card, text=cipher["name"], style="CardName.TLabel")
    name.pack(anchor="w")
    info = ttk.Label(card, text=cipher["info"], style="CardInfo.TLabel")
    info.pack(anchor="w")
    for w in [card_border, card, name, info]:
        w.bind("<Button-1>", lambda e: select_cipher(cipher))
        w.configure(cursor="hand2")
    return card_border


buttons = []
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


def fav_cipher():
    cipher_card_window = ttk.Toplevel(title="Cipher's")
    cipher_card_window.geometry("800x600")
    cipher_card_window.configure(background="#0B1320")

def caesar_cipher(text , shift):
    result= ''
    for i in text:
        if i.isalpha():
            shift_base = ord('A') if i.isupper() else ord('a')
            result += chr((ord(i) - shift_base + shift) % 26 + shift_base)
        else:
            result += i
    return result

# Main window

window = ttk.Window()
window.title("CipherLab")
window.geometry("1200x750")
window.configure(background="#0B1320")

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

lab_page = ttk.Frame(content, style="Content.TFrame")
lab_label = ttk.Label(lab_page, text="Cipher Lab", font=("Arial", 20, "bold"), background="#0B1320", foreground="#FFFFFF").pack(side="top", padx=20, pady=20, anchor="w")
cards_frame = ttk.Frame(lab_page, style="Content.TFrame")
cards_frame.pack(side="top", fill="x", padx=20)
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

name = ttk.Label(message_box , text = "Select a cipher",font=("Arial", 20, "bold"),background="#111827", foreground="#FFFFFF").pack(side="top", padx=20, pady=0, anchor="w")
desc = ttk.Label(message_box , text = "Select Cipher",font=("Arial", 13),background="#111827", foreground="#FFFFFF").pack(side="top", padx=20, pady=10, anchor="w")
sep_1 = ttk.Frame(message_box, style="CardBorder.TFrame", height=1)
sep_1.pack(side="top", fill="x", pady=(0, 20))
message_label =ttk.Label(message_box , text = "Message",font=("Arial", 13),background="#111827", foreground="#FFFFFF").pack(side="top", padx=20, pady=0, anchor="w")

boxframe = ttk.Frame(message_box , style="Footer.TFrame", padding=0)
boxframe.pack(side="top", fill="x", padx=1, pady=2, anchor="w")
entry_border = ttk.Frame(boxframe, style="CardBorder.TFrame", padding=1)
entry_border.pack(side="top", padx=20, pady=10, anchor="w")

message_text = ScrolledText(entry_border, padding=0, width=80, height=6, autohide=True, wrap="word")
message_text.configure(style="Content.TFrame")
message_text.pack()

message_text.text.configure(font=("Arial", 13), background="#0B1320",
                            foreground="#FFFFFF", insertbackground="#FFFFFF",
                            borderwidth=0, highlightthickness=0, relief="flat",
                            padx=8, pady=8)

options_frame = ttk.Frame(boxframe , style="Footer.TFrame", padding=0)
options_frame.pack(side="top", fill="x", padx=20, pady=10, anchor="w")



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