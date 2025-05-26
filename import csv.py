import csv
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def wczytaj_kategorie(sciezka):
    kategorie = {}
    with open(sciezka, encoding='utf-8') as f:
        for linia in f:
            linia = linia.strip()
            if not linia or ':' not in linia:
                continue
            kat, slowa = linia.split(':', 1)
            slowa_lista = [s.strip().lower() for s in slowa.split(',')]
            kategorie[kat.strip()] = slowa_lista
    return kategorie

def zapisz_kategorie_do_pliku(kategorie, sciezka):
    try:
        with open(sciezka, 'w', encoding='utf-8') as f:
            for kat, slowa in kategorie.items():
                linia = kat + ':' + ','.join(slowa)
                f.write(linia + '\n')
    except Exception as e:
        messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać do pliku kategorii:\n{e}")

def zapytaj_uzytkownika(opis, kategorie):
    def zatwierdz():
        wybrana = entry_kat.get().strip()
        if wybrana:
            wybor.append(wybrana)
            win.destroy()

    win = tk.Toplevel()
    win.title("Nowa kategoria")
    win.grab_set()
    tk.Label(win, text=f"Nieznana kategoria dla opisu:\n„{opis}”").pack(padx=10, pady=10)
    tk.Label(win, text="Podaj nową kategorię lub wybierz istniejącą:").pack()

    entry_kat = tk.Entry(win, width=30)
    entry_kat.pack(padx=5, pady=5)

    wybor = []

    frame = tk.Frame(win)
    frame.pack(pady=5)
    for kat in kategorie.keys():
        btn = tk.Button(frame, text=kat, command=lambda k=kat: [entry_kat.delete(0, tk.END), entry_kat.insert(0, k)])
        btn.pack(side=tk.LEFT, padx=2)

    btn_ok = tk.Button(win, text="Zatwierdź", command=zatwierdz)
    btn_ok.pack(pady=10)
    win.wait_window()
    return wybor[0] if wybor else None

def kategoryzuj_wydatek(opis, kategorie, sciezka_kat):
    opis_lower = opis.lower()
    for kat, slowa in kategorie.items():
        for slowo in slowa:
            if slowo in opis_lower:
                return kat
    # Nie znaleziono — zapytaj użytkownika
    nowa_kat = zapytaj_uzytkownika(opis, kategorie)
    if nowa_kat:
        slowo_klucz = opis.split()[0].lower()
        if nowa_kat in kategorie:
            if slowo_klucz not in kategorie[nowa_kat]:
                kategorie[nowa_kat].append(slowo_klucz)
        else:
            kategorie[nowa_kat] = [slowo_klucz]
        zapisz_kategorie_do_pliku(kategorie, sciezka_kat)
        return nowa_kat
    return "Inne"

def wczytaj_wyciag(sciezka, kategorie, sciezka_kategorie):
    wydatki = {}
    with open(sciezka, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for wiersz in reader:
            opis = wiersz.get('Opis', '') or wiersz.get('description', '')
            kwota_str = wiersz.get('Kwota', wiersz.get('Amount', '0')).replace(',', '.')
            try:
                kwota = float(kwota_str)
            except:
                kwota = 0.0
            kat = kategoryzuj_wydatek(opis, kategorie, sciezka_kategorie)
            wydatki[kat] = wydatki.get(kat, 0) + kwota
    return wydatki

def wybierz_plik(entry_widget):
    sciezka = filedialog.askopenfilename()
    if sciezka:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, sciezka)

def wykonaj_analize():
    sciezka_wyciag = entry_wyciag.get()
    sciezka_kategorie = entry_kategorie.get()
    if not sciezka_wyciag or not sciezka_kategorie:
        messagebox.showerror("Błąd", "Proszę wybrać oba pliki: wyciąg i kategorie.")
        return
    try:
        kategorie = wczytaj_kategorie(sciezka_kategorie)
        wydatki = wczytaj_wyciag(sciezka_wyciag, kategorie, sciezka_kategorie)
    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił problem podczas wczytywania plików:\n{e}")
        return
    
    wynik_text.delete(1.0, tk.END)
    suma = 0
    for kat, kwota in wydatki.items():
        wynik_text.insert(tk.END, f"{kat}: {kwota:.2f} zł\n")
        suma += kwota
    wynik_text.insert(tk.END, f"\nŁącznie: {suma:.2f} zł")

def zapisz_wynik():
    wynik = wynik_text.get(1.0, tk.END)
    if not wynik.strip():
        messagebox.showinfo("Info", "Brak danych do zapisania.")
        return
    sciezka = filedialog.asksaveasfilename(defaultextension=".txt",
                                          filetypes=[("Pliki tekstowe", "*.txt")])
    if sciezka:
        with open(sciezka, 'w', encoding='utf-8') as f:
            f.write(wynik)
        messagebox.showinfo("Sukces", f"Wynik zapisano do:\n{sciezka}")

# --- GUI ---
root = tk.Tk()
root.title("Kategoryzator wydatków")

tk.Label(root, text="Plik wyciągu (CSV):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
entry_wyciag = tk.Entry(root, width=50)
entry_wyciag.grid(row=0, column=1, padx=5)
btn_wyciag = tk.Button(root, text="Wybierz...", command=lambda: wybierz_plik(entry_wyciag))
btn_wyciag.grid(row=0, column=2, padx=5)

tk.Label(root, text="Plik kategorii (TXT):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
entry_kategorie = tk.Entry(root, width=50)
entry_kategorie.grid(row=1, column=1, padx=5)
btn_kategorie = tk.Button(root, text="Wybierz...", command=lambda: wybierz_plik(entry_kategorie))
btn_kategorie.grid(row=1, column=2, padx=5)

btn_analiza = tk.Button(root, text="Przeanalizuj wydatki", command=wykonaj_analize)
btn_analiza.grid(row=2, column=0, columnspan=3, pady=10)

wynik_text = scrolledtext.ScrolledText(root, width=60, height=20)
wynik_text.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

btn_zapisz = tk.Button(root, text="Zapisz wynik do pliku", command=zapisz_wynik)
btn_zapisz.grid(row=4, column=0, columnspan=3, pady=10)

root.mainloop()
