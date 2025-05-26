import sys
import csv
from collections import defaultdict

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QLineEdit,
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import numpy as np


class Kategoryzator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kategoryzator wydatków")
        self.resize(900, 700)

        self.kategorie = {}
        self.wykres = WykresWidget()

        # UI - wybór plików i przyciski
        self.wyciag_edit = QLineEdit()
        self.wyciag_button = QPushButton("Wybierz plik wyciągu CSV")
        self.wyciag_button.clicked.connect(self.wybierz_wyciag)

        self.kategorie_edit = QLineEdit()
        self.kategorie_button = QPushButton("Wybierz plik kategorii TXT")
        self.kategorie_button.clicked.connect(self.wybierz_kategorie)

        self.combo_wykres = QComboBox()
        self.combo_wykres.addItems(["Słupkowy", "Heatmapa", "Waterfall"])

        self.analizuj_button = QPushButton("Przeanalizuj wydatki")
        self.analizuj_button.clicked.connect(self.analizuj)

        self.zapisz_button = QPushButton("Zapisz wynik do pliku")
        self.zapisz_button.clicked.connect(self.zapisz_wynik)

        self.wynik_edit = QTextEdit()
        self.wynik_edit.setReadOnly(True)

        # Layout
        pliki_layout = QHBoxLayout()
        pliki_layout.addWidget(self.wyciag_edit)
        pliki_layout.addWidget(self.wyciag_button)

        kat_layout = QHBoxLayout()
        kat_layout.addWidget(self.kategorie_edit)
        kat_layout.addWidget(self.kategorie_button)

        wykres_layout = QHBoxLayout()
        wykres_layout.addWidget(QLabel("Typ wykresu:"))
        wykres_layout.addWidget(self.combo_wykres)
        wykres_layout.addStretch()
        wykres_layout.addWidget(self.analizuj_button)
        wykres_layout.addWidget(self.zapisz_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(pliki_layout)
        main_layout.addLayout(kat_layout)
        main_layout.addLayout(wykres_layout)
        main_layout.addWidget(self.wynik_edit)
        main_layout.addWidget(self.wykres)

        self.setLayout(main_layout)

    def wybierz_wyciag(self):
        plik, _ = QFileDialog.getOpenFileName(self, "Wybierz plik wyciągu CSV", "", "CSV Files (*.csv);;All Files (*)")
        if plik:
            self.wyciag_edit.setText(plik)

    def wybierz_kategorie(self):
        plik, _ = QFileDialog.getOpenFileName(self, "Wybierz plik kategorii TXT", "", "Text Files (*.txt);;All Files (*)")
        if plik:
            self.kategorie_edit.setText(plik)

    def wczytaj_kategorie(self):
        plik = self.kategorie_edit.text()
        kategorie = {}
        try:
            with open(plik, encoding='utf-8') as f:
                for linia in f:
                    linia = linia.strip()
                    if not linia or ':' not in linia:
                        continue
                    kat, slowa = linia.split(':', 1)
                    kat = kat.strip()
                    slowa = [s.strip().lower() for s in slowa.split(',') if s.strip()]
                    kategorie[kat] = slowa
            return kategorie
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wczytać kategorii:\n{e}")
            return None

    def zapisz_kategorie(self):
        plik = self.kategorie_edit.text()
        try:
            with open(plik, 'w', encoding='utf-8') as f:
                for kat, slowa in self.kategorie.items():
                    f.write(f"{kat}: {', '.join(slowa)}\n")
        except Exception as e:
            QMessageBox.warning(self, "Uwaga", f"Nie udało się zapisać kategorii:\n{e}")

    def kategoryzuj(self, opis):
        opis_lower = opis.lower()
        for kat, slowa in self.kategorie.items():
            for slowo in slowa:
                if slowo in opis_lower:
                    return kat

        # Jeśli brak kategorii - wywołaj dialog do przypisania
        dialog = KategoriaDialog(self.kategorie.keys())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nowa_kat = dialog.wybrana_kategoria
            # Dodaj słowo kluczowe na podstawie opisu (pierwsze niepuste słowo)
            slowo_klucz = opis.split()[0].lower() if opis.split() else opis.lower()
            if nowa_kat in self.kategorie:
                if slowo_klucz not in self.kategorie[nowa_kat]:
                    self.kategorie[nowa_kat].append(slowo_klucz)
            else:
                self.kategorie[nowa_kat] = [slowo_klucz]
            self.zapisz_kategorie()
            return nowa_kat
        else:
            return "Nieznane"

    def analizuj(self):
        wyciag_plik = self.wyciag_edit.text()
        kategorie_plik = self.kategorie_edit.text()
        if not wyciag_plik or not kategorie_plik:
            QMessageBox.warning(self, "Uwaga", "Wybierz pliki wyciągu i kategorii.")
            return

        self.kategorie = self.wczytaj_kategorie()
        if self.kategorie is None:
            return

        suma_kategori = defaultdict(float)
        tekst_wynik = []

        try:
            with open(wyciag_plik, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for wiersz in reader:
                    opis = wiersz.get('Opis', '').strip()
                    kwota_str = wiersz.get('Kwota', '').replace(',', '.').strip()
                    try:
                        kwota = float(kwota_str)
                    except ValueError:
                        continue
                    kat = self.kategoryzuj(opis)
                    suma_kategori[kat] += kwota
                    tekst_wynik.append(f"{opis}: {kwota:.2f} zł => {kat}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd podczas przetwarzania pliku wyciągu:\n{e}")
            return

        self.wynik_edit.setPlainText('\n'.join(tekst_wynik))

        typ_wykresu = self.combo_wykres.currentText()
        self.wykres.rysuj_wykres(suma_kategori, typ_wykresu)

    def zapisz_wynik(self):
        sciezka, _ = QFileDialog.getSaveFileName(self, "Zapisz wyniki", "", "Pliki tekstowe (*.txt);;Wszystkie pliki (*)")
        if not sciezka:
            return
        try:
            with open(sciezka, 'w', encoding='utf-8') as f:
                f.write(self.wynik_edit.toPlainText())
            QMessageBox.information(self, "Sukces", f"Wyniki zapisane do pliku:\n{sciezka}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd zapisu", f"Nie udało się zapisać pliku:\n{e}")


class KategoriaDialog(QDialog):
    def __init__(self, istniejace_kategorie):
        super().__init__()
        self.setWindowTitle("Przypisz kategorię")

        self.wybrana_kategoria = None

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Nieznana kategoria. Wybierz istniejącą lub wpisz nową:"))

        self.radio_group = QButtonGroup(self)
        self.radio_group.setExclusive(True)

        # Radio buttony z istniejacymi kategoriami
        self.radio_buttons = []
        for kat in sorted(istniejace_kategorie):
            rb = QRadioButton(kat)
            self.radio_group.addButton(rb)
            self.radio_buttons.append(rb)
            layout.addWidget(rb)

        layout.addWidget(QLabel("Lub wpisz nową kategorię:"))
        self.nowa_kategoria_edit = QLineEdit()
        layout.addWidget(self.nowa_kategoria_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.acceptuj)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def acceptuj(self):
        # Sprawdz czy wybrano radio albo wpisano nową kategorię
        wybrane_rb = [rb for rb in self.radio_buttons if rb.isChecked()]
        nowa = self.nowa_kategoria_edit.text().strip()

        if wybrane_rb:
            self.wybrana_kategoria = wybrane_rb[0].text()
            self.accept()
        elif nowa:
            self.wybrana_kategoria = nowa
            self.accept()
        else:
            QMessageBox.warning(self, "Uwaga", "Wybierz kategorię lub wpisz nową.")
            # nie akceptuj dialogu


class WykresWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.figure, self.axes = plt.subplots(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.colorbar = None

    def rysuj_wykres(self, suma_kategori, typ_wykresu):
        self.axes.clear()

        kategorie = list(suma_kategori.keys())
        kwoty = np.array(list(suma_kategori.values()))

        # Usuń poprzedni colorbar, jeśli istnieje
        if self.colorbar is not None:
            try:
                if self.colorbar.ax is not None:
                    self.colorbar.remove()
            except Exception:
                pass
            self.colorbar = None

        if not kwoty.size:
            self.axes.text(0.5, 0.5, "Brak danych do wykresu", ha='center', va='center')
            self.canvas.draw()
            return

        if typ_wykresu == "Słupkowy":
            self.axes.bar(range(len(kategorie)), kwoty, color="#007ACC", edgecolor="#004C99")
            self.axes.set_title("Wydatki wg kategorii (Słupkowy)", fontsize=16, fontweight='bold')
            self.axes.set_ylabel("Kwota [zł]")
            self.axes.set_xticks(range(len(kategorie)))
            self.axes.set_xticklabels(kategorie, rotation=40, ha='right')

        elif typ_wykresu == "Waterfall":
            # Tworzymy wykres kaskadowy waterfall
            baseline = 0
            lefts = []
            heights = []
            colors = []
            for val in kwoty:
                lefts.append(baseline)
                heights.append(val)
                baseline += val
                # Kolory: ujemne czerwone, dodatnie zielone
                colors.append('#d62728' if val < 0 else '#2ca02c')

            self.axes.bar(range(len(kategorie)), heights, bottom=lefts, color=colors, edgecolor='black')
            self.axes.set_title("Wydatki wg kategorii (Waterfall)", fontsize=16, fontweight='bold')
            self.axes.set_ylabel("Kwota [zł]")
            self.axes.set_xticks(range(len(kategorie)))
            self.axes.set_xticklabels(kategorie, rotation=40, ha='right')

            # Dodajemy wartości nad słupkami
            for i, (left, height) in enumerate(zip(lefts, heights)):
                self.axes.text(i, left + height / 2, f"{height:.2f}", ha='center', va='center', color='white', fontweight='bold')

        elif typ_wykresu == "Heatmapa":
            range_ = np.ptp(kwoty)
            kwoty_norm = (kwoty - kwoty.min()) / (range_ if range_ > 0 else 1)
            data = kwoty_norm.reshape(1, -1)
            im = self.axes.imshow(data, aspect='auto', cmap='coolwarm')
            self.axes.set_yticks([])
            self.axes.set_xticks(range(len(kategorie)))
            self.axes.set_xticklabels(kategorie, rotation=40, ha='right')
            self.axes.set_title("Wydatki wg kategorii (Heatmapa)", fontsize=16, fontweight='bold')
            self.colorbar = self.figure.colorbar(im, ax=self.axes, orientation='vertical')
            self.colorbar.set_label('Wartość (znormalizowana)')
            self.figure.tight_layout()

        else:
            self.axes.text(0.5, 0.5, "Nieznany typ wykresu", ha='center', va='center')

        self.figure.tight_layout()
        self.canvas.draw()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Opcjonalny ciemny motyw z lekkim kontrastem
    dark_palette = app.palette()
    dark_palette.setColor(dark_palette.ColorRole.Window, Qt.GlobalColor.white)
    dark_palette.setColor(dark_palette.ColorRole.WindowText, Qt.GlobalColor.black)
    app.setPalette(dark_palette)

    window = Kategoryzator()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
