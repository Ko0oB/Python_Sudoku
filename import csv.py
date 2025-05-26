import csv
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

aktualne_kategorie = {}
sciezka_kategorie_glob = ""
pending_opis = None
pending_callback = None

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

def pokaz_formularz_kategorii(opis, callback):
    global pending_opis, pending_callback
    pending_opis = opis
    pending_callback = callback

    entry_nowy_opis.config(state='normal')
    entry_nowy_opis.delete(0, tk.END)
    entry_nowy_opis.insert(0, opis)

    entry_nowa_kategoria.delete(0, tk.END)
    frame_formularz.pack(padx=10, pady=10, fill='x')

def zatwierdz_kategorie():
    global pending_opis, pending_callback
    nowa_kat = entry_nowa_kategoria.get().strip()
    slowo_klucz = pending_opis.split()[0].lower()
    if nowa_kat:
        if nowa_kat in aktualne_kategorie:
            if slowo_klucz not in aktualne_kategorie[nowa_kat]:
                aktualne_kategorie[nowa_kat].append(slowo_klucz)
        else:
            aktualne_kategorie[nowa_kat] = [slowo_klucz]
        zapisz_kategorie_do_pliku(aktualne_kategorie, sciezka_kategorie_glob)
        frame_formularz.pack_forget()
        if pending_callback:
            pending_callback(nowa_kat)

def kategoryzuj_wydatek(opis, callback):
    opis_lower = opis.lower()
    for kat, slowa in aktualne_kategorie.items():
        for slowo in slowa:
            if slowo in opis_lower:
                return callback(kat)
    pokaz_formularz_kategorii(opis, callback)

def przetworz_wyciag(sciezka, on_done):
    wydatki = {}

    def kontynuuj(opis, kwota, iterator):
        def przypisz_kategorie(kat):
            wydatki[kat] = wydatki.get(kat, 0) + kwota
            przetworz_nastepny(iterator)
        kategoryzuj_wydatek(opis, przypisz_kategorie)

    def przetworz_nastepny(iterator):
        try:
            wiersz = next(iterator)
            opis = wiersz.get('Opis', '') or wiersz.get('description', '')
            kwota_str = wiersz.get('Kwota', wiersz.get('Amount', '0')).replace(',', '.')
            kwota = float(kwota_str)
            kontynuuj(opis, kwota, iterator)
        except StopIteration:
            on_done(wydatki)
        except Exception as e:
            messagebox.showerror("Błąd", f"Problem przy przetwarzaniu:\n{e}")

    try:
        with open(sciezka, encoding='utf-8') as f:
            reader = list(csv.DictReader(f))  # Wczytaj dane do listy
        przetworz_nastepny(iter(reader))
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się otworzyć pliku:\n{e}")

def wybierz_plik(entry_widget):
    sciezka = filedialog.askopenfilename()
    if sciezka:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, sciezka)

def wykonaj_analize():
    global aktualne_kategorie, sciezka_kategorie_glob
    sciezka_wyciag = entry_wyciag.get()
    sciezka_kategorie = entry_kategorie.get()
    if not sciezka_wyciag or not sciezka_kategorie:
        messagebox.showerror("Błąd", "Wybierz plik wyciągu i kategorii.")
        return

    try:
        aktualne_kategorie = wczytaj_kategorie(sciezka_kategorie)
        sciezka_kategorie_glob = sciezka_kategorie
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się wczytać pliku kategorii:\n{e}")
        return

    def wyswietl_wynik(wydatki):
        wynik_text.delete(1.0, tk.END)
        suma = 0
        for kat, kwota in wydatki.items():
            wynik_text.insert(tk.END, f"{kat}: {kwota:.2f} zł\n")
            suma += kwota
        wynik_text.insert(tk.END, f"\nŁącznie: {suma:.2f} zł")

    przetworz_wyciag(sciezka_wyciag, wyswietl_wynik)

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
        messagebox.showinfo("Zapisano", f"Wynik zapisano do:\n{sciezka}")

# --- GUI ---
root = tk.Tk()
root.title("Kategoryzator wydatków")

# Główna ramka z grid
frame_glowny = tk.Frame(root)
frame_glowny.pack(padx=10, pady=10)

tk.Label(frame_glowny, text="Plik wyciągu (CSV):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
entry_wyciag = tk.Entry(frame_glowny, width=50)
entry_wyciag.grid(row=0, column=1, padx=5)
btn_wyciag = tk.Button(frame_glowny, text="Wybierz...", command=lambda: wybierz_plik(entry_wyciag))
btn_wyciag.grid(row=0, column=2, padx=5)

tk.Label(frame_glowny, text="Plik kategorii (TXT):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
entry_kategorie = tk.Entry(frame_glowny, width=50)
entry_kategorie.grid(row=1, column=1, padx=5)
btn_kategorie = tk.Button(frame_glowny, text="Wybierz...", command=lambda: wybierz_plik(entry_kategorie))
btn_kategorie.grid(row=1, column=2, padx=5)

btn_analiza = tk.Button(frame_glowny, text="Przeanalizuj wydatki", command=wykonaj_analize)
btn_analiza.grid(row=2, column=0, columnspan=3, pady=10)

wynik_text = scrolledtext.ScrolledText(frame_glowny, width=60, height=20)
wynik_text.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

btn_zapisz = tk.Button(frame_glowny, text="Zapisz wynik do pliku", command=zapisz_wynik)
btn_zapisz.grid(row=4, column=0, columnspan=3, pady=10)

# Formularz kategorii (pack)
frame_formularz = tk.Frame(root, bd=2, relief='groove')
tk.Label(frame_formularz, text="Nowa kategoria dla opisu:").pack(padx=5, pady=(5, 0))
entry_nowy_opis = tk.Entry(frame_formularz, state='readonly', width=60)
entry_nowy_opis.pack(pady=2)
entry_nowa_kategoria = tk.Entry(frame_formularz, width=40)
entry_nowa_kategoria.pack(pady=2)
btn_dodaj_kategorie = tk.Button(frame_formularz, text="Dodaj kategorię", command=zatwierdz_kategorie)
btn_dodaj_kategorie.pack(pady=5)

root.mainloop()
