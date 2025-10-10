import json
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLineEdit, QLabel, QPushButton,
    QMessageBox, QDialog, QFileDialog, QTableWidget,
    QTableWidgetItem, QMenuBar, QMenu
)
from PyQt6.QtGui import QAction, QCursor, QImage



# =========================================================
# 1. CLASELE POO (LOGICA DATELOR)
# =========================================================

class CorpulCeresc:
    """Clasa de bază pentru toate corpurile cerești."""

    def __init__(self, nume, masa_solara, varsta_milioane):
        self.nume = nume
        self.masa_solara = masa_solara
        self.varsta = varsta_milioane

    def to_dict(self):
        return {
            "Nume": self.nume,  # Folosim majuscule pentru a se potrivi cu Antetul Tabelului
            "Masa Solara": self.masa_solara,
            "Varsta Milioane": self.varsta,
            "Tip Obiect": self.__class__.__name__
        }


class Planeta(CorpulCeresc):
    def __init__(self, nume, masa_solara, varsta_milioane, numar_sateliti, tip_atmosfera):
        super().__init__(nume, masa_solara, varsta_milioane)
        self.numar_sateliti = numar_sateliti
        self.tip_atmosfera = tip_atmosfera

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "Nr. Sateliti": self.numar_sateliti,
            "Tip Atmosfera": self.tip_atmosfera
        })
        return data


class Stea(CorpulCeresc):
    def __init__(self, nume, masa_solara, varsta_milioane, tip_spectral, luminozitate, nume_constelatie):
        super().__init__(nume, masa_solara, varsta_milioane)
        self.tip_spectral = tip_spectral
        self.luminozitate = luminozitate
        self.nume_constelatie = nume_constelatie

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "Tip Spectral": self.tip_spectral,
            "Luminozitate": self.luminozitate,
            "Constelatie": self.nume_constelatie
        })
        return data


class Constelatie:
    def __init__(self, nume, nume_latin, zona_vizibilitate):
        self.nume = nume
        self.nume_latin = nume_latin
        self.zona_vizibilitate = zona_vizibilitate
        self.stele_principale = []

    def to_dict(self):
        return {
            "Nume": self.nume,
            "Nume Latin": self.nume_latin,
            "Zona Vizibilitate": self.zona_vizibilitate,
            "Stele Asociate": self.stele_principale  # O listă de nume
        }


class DataManager:
    """Manager central pentru stocarea tuturor obiectelor POO."""

    def __init__(self):
        self.obiecte_univers = []

    def adauga_obiect(self, obiect):
        self.obiecte_univers.append(obiect)


# =========================================================
# 2. DIALOGURI PENTRU ADAUGARE (QDialogs)
# =========================================================

# (Clasele AddPlanetDialog, AddStarDialog, AddConstellationDialog rămân la fel,
# folosind DataManager pentru a adăuga obiectele)

class AddPlanetDialog(QDialog):
    def __init__(self, data_manager):
        super().__init__();
        self.setWindowTitle("Adaugă Planetă");
        self.data_manager = data_manager;
        self.fields = {};
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout();
        fields_data = [("Nume:", QLineEdit), ("Masa Solara (float):", QLineEdit),
                       ("Varsta Milioane (float):", QLineEdit), ("Nr. Sateliti (int):", QLineEdit),
                       ("Tip Atmosfera:", QLineEdit)]
        for label_text, widget_class in fields_data:
            h_layout = QHBoxLayout();
            h_layout.addWidget(QLabel(label_text));
            input_field = widget_class();
            h_layout.addWidget(input_field);
            layout.addLayout(h_layout);
            self.fields[label_text] = input_field
        save_button = QPushButton("SALVEAZĂ");
        save_button.clicked.connect(self.salveaza_planeta);
        layout.addWidget(save_button);
        self.setLayout(layout)

    def salveaza_planeta(self):
        try:
            nume = self.fields["Nume:"].text();
            masa = float(self.fields["Masa Solara (float):"].text());
            varsta = float(self.fields["Varsta Milioane (float):"].text());
            sateliti = int(self.fields["Nr. Sateliti (int):"].text());
            atmosfera = self.fields["Tip Atmosfera:"].text()
            if not nume or not atmosfera: raise ValueError("Numele și Atmosfera nu pot fi goale.")
            noua_planeta = Planeta(nume, masa, varsta, sateliti, atmosfera);
            self.data_manager.adauga_obiect(noua_planeta)
            QMessageBox.information(self, "Succes", f"Planeta '{nume}' a fost adăugată.");
            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Eroare", f"Date invalide: {e}\nAsigurați-vă că numerele sunt corecte!")


class AddStarDialog(QDialog):
    def __init__(self, data_manager):
        super().__init__();
        self.setWindowTitle("Adaugă Stea");
        self.data_manager = data_manager;
        self.fields = {};
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout();
        fields_data = [("Nume:", QLineEdit), ("Masa Solara (float):", QLineEdit),
                       ("Varsta Milioane (float):", QLineEdit), ("Tip Spectral (ex: G2V):", QLineEdit),
                       ("Luminozitate (solara, float):", QLineEdit), ("Constelatie Asociată:", QLineEdit)]
        for label_text, widget_class in fields_data:
            h_layout = QHBoxLayout();
            h_layout.addWidget(QLabel(label_text));
            input_field = widget_class();
            h_layout.addWidget(input_field);
            layout.addLayout(h_layout);
            self.fields[label_text] = input_field
        save_button = QPushButton("SALVEAZĂ STEAUA");
        save_button.clicked.connect(self.salveaza_stea);
        layout.addWidget(save_button);
        self.setLayout(layout)

    def salveaza_stea(self):
        try:
            nume = self.fields["Nume:"].text();
            masa = float(self.fields["Masa Solara (float):"].text());
            varsta = float(self.fields["Varsta Milioane (float):"].text());
            tip_spectral = self.fields["Tip Spectral (ex: G2V):"].text();
            luminozitate = float(self.fields["Luminozitate (solara, float):"].text());
            constelatie = self.fields["Constelatie Asociată:"].text()
            if not nume or not tip_spectral: raise ValueError("Numele și Tipul Spectral nu pot fi goale.")
            noua_stea = Stea(nume, masa, varsta, tip_spectral, luminozitate, constelatie);
            self.data_manager.adauga_obiect(noua_stea)
            QMessageBox.information(self, "Succes", f"Steaua '{nume}' a fost adăugată.");
            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Eroare", f"Date invalide: {e}\nVerifică tipurile numerice.")


class AddConstellationDialog(QDialog):
    def __init__(self, data_manager):
        super().__init__();
        self.setWindowTitle("Adaugă Constelație");
        self.data_manager = data_manager;
        self.fields = {};
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout();
        fields_data = [("Nume Constelatie:", QLineEdit), ("Nume Latin (Genitiv):", QLineEdit),
                       ("Zona Vizibilitate:", QLineEdit), ("Stele (separate prin virgulă):", QLineEdit)]
        for label_text, widget_class in fields_data:
            h_layout = QHBoxLayout();
            h_layout.addWidget(QLabel(label_text));
            input_field = widget_class();
            h_layout.addWidget(input_field);
            layout.addLayout(h_layout);
            self.fields[label_text] = input_field
        save_button = QPushButton("SALVEAZĂ CONSTELAȚIA");
        save_button.clicked.connect(self.salveaza_constelatie);
        layout.addWidget(save_button);
        self.setLayout(layout)

    def salveaza_constelatie(self):
        try:
            nume = self.fields["Nume Constelatie:"].text();
            nume_latin = self.fields["Nume Latin (Genitiv):"].text();
            zona = self.fields["Zona Vizibilitate:"].text();
            stele_text = self.fields["Stele (separate prin virgulă):"].text()
            if not nume or not nume_latin: raise ValueError("Numele nu pot fi goale.")
            noua_constelatie = Constelatie(nume, nume_latin, zona)
            if stele_text:
                nume_stele = [s.strip() for s in stele_text.split(',')];
                noua_constelatie.stele_principale.extend(nume_stele)
            self.data_manager.adauga_obiect(noua_constelatie);
            QMessageBox.information(self, "Succes", f"Constelația '{nume}' a fost adăugată.");
            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Eroare", f"Date invalide: {e}")


# =========================================================
# 3. FEREASTRA PRINCIPALĂ (QMainWindow)
# =========================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proiect Univers POO (PyQt6)")
        self.setGeometry(100, 100, 1000, 700)  # Lățime mărită pentru tabel

        self.setStyleSheet("""
                    QMainWindow {
                        background-color: #050510; 
                        color: #E0E0FF;

                        /* CORECTAT: FOLOSEȘTE ':' ÎN LOC DE '=' */
                        background-image: url("assets/galaxy_sky2.jpg"); 

                        background-repeat: no-repeat;
                        background-position: center;
                        background-size: cover; /* Ajustează imaginea */
                    }
                """)
        self.data_manager = DataManager()

        self.setup_ui()
        self.setup_menu_bar()

    def lanseaza_vizualizare_ursina(self):
        """Rulează scriptul Ursina într-un proces separat."""

        # Aici presupunem că fișierul tău Ursina se numește 'sistem_solar_ursina.py'
        try:
            # Rulează fișierul Python separat. Shell=True este mai simplu dar mai puțin sigur.
            # Alternativ, folosește: subprocess.Popen(['python', 'sistem_solar_ursina.py'])
            subprocess.Popen("python Test_sistem_solar.py", shell=True)

        except FileNotFoundError:
            QMessageBox.critical(self, "Eroare Lansare",
                                 "Fișierul 'sistem_solar_ursina.py' nu a fost găsit. "
                                 "Asigură-te că este în același director.")
        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"Eroare la pornirea Ursina: {e}")

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        #background-image: url("assets/galaxy_sky.jpg");

        # ---------------------------------
        # Panel Stânga: Vizualizare Tabel & Buton
        # ---------------------------------

        self.table_widget = QTableWidget()  # <-- NOU: QTableWidget
        self.table_widget.setStyleSheet(
            "background-color: #1A1A2E; color: #E0E0FF; border: 1px solid #4A4A6E; gridline-color: #4A4A6E;")

        # Meniu Vizualizare (Vizualizeaza Planete, Stele, Constelatii)
        self.view_menu = QMenu()

        action_planets = self.view_menu.addAction("Vizualizează Planete")
        action_planets.triggered.connect(lambda: self.vizualizeaza_tip_obiect(Planeta))

        action_stars = self.view_menu.addAction("Vizualizează Stele")
        action_stars.triggered.connect(lambda: self.vizualizeaza_tip_obiect(Stea))

        action_constellations = self.view_menu.addAction("Vizualizează Constelații")
        action_constellations.triggered.connect(lambda: self.vizualizeaza_tip_obiect(Constelatie))

        view_button = QPushButton("VIZUALIZEAZĂ TIP...")
        view_button.setMenu(self.view_menu)  # Atașează meniul la buton
        view_button.setStyleSheet("background-color: #4A4A6E; color: white; padding: 10px; border-radius: 5px;")

        view_layout = QVBoxLayout()
        view_layout.addWidget(view_button)
        view_layout.addWidget(self.table_widget)

        main_layout.addLayout(view_layout, 70)  # 70% din spațiu pentru tabel

        # ---------------------------------
        # Panel Dreapta: Acțiuni (Buton Adăugare)
        # ---------------------------------
        action_layout = QVBoxLayout()
        launch_ursina_button = QPushButton("SISTEMUL SOLAR (3D)")
        launch_ursina_button.setStyleSheet(
            "background-color: #A349A4; color: white; padding: 15px; border-radius: 5px; font-weight: bold;")
        launch_ursina_button.clicked.connect(self.lanseaza_vizualizare_ursina)
        action_layout.addWidget(launch_ursina_button)

        add_menu_button = QPushButton("ADAUGA CORP CERESC")
        add_menu_button.setStyleSheet(
            "background-color: #0077B6; color: white; padding: 15px; border-radius: 5px; font-weight: bold;")
        add_menu_button.clicked.connect(self.show_add_menu)
        action_layout.addWidget(add_menu_button)

        refresh_button = QPushButton("ACTUALIZEAZĂ TABELUL")
        refresh_button.clicked.connect(lambda: self.vizualizeaza_tip_obiect(self.clasa_curenta or Planeta))
        action_layout.addWidget(refresh_button)

        action_layout.addStretch(1)
        main_layout.addLayout(action_layout, 30)  # 30% din spațiu pentru butoane

        self.clasa_curenta = Planeta  # Variabilă pentru a ști ce tip de date se afișează
        self.vizualizeaza_tip_obiect(Planeta)  # Setează vizualizarea inițială

    def setup_menu_bar(self):
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("&Fișier")

        save_action = QAction("&Salvează Date (JSON)", self)
        save_action.triggered.connect(self.salveaza_date_in_json)
        file_menu.addAction(save_action)

        exit_action = QAction("&Ieșire", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    # --- METODE DE VIZUALIZARE ȘI GESTIONARE ---

    def vizualizeaza_tip_obiect(self, tip_clasa):
        """Filtrează și afișează obiectele de tipul specificat într-un QTableWidget."""

        self.clasa_curenta = tip_clasa  # Actualizează clasa curentă
        obiecte_filtrate = [obj for obj in self.data_manager.obiecte_univers if isinstance(obj, tip_clasa)]
        self.table_widget.setRowCount(0)

        if not obiecte_filtrate:
            self.table_widget.setColumnCount(1)
            self.table_widget.setHorizontalHeaderLabels([f"Nicio dată de afișat pentru {tip_clasa.__name__}."])
            return

        # Obținerea anteturilor (coloanelor)
        coloane = list(obiecte_filtrate[0].to_dict().keys())

        self.table_widget.setColumnCount(len(coloane))
        self.table_widget.setHorizontalHeaderLabels(coloane)
        self.table_widget.setRowCount(len(obiecte_filtrate))

        # Umplerea tabelului
        for row, obiect_poo in enumerate(obiecte_filtrate):
            data_dict = obiect_poo.to_dict()
            for col, cheie in enumerate(coloane):
                valoare = data_dict.get(cheie, "")

                # Formatare specifică pentru liste (ex: Stele Asociate)
                if isinstance(valoare, list):
                    valoare_text = f"{len(valoare)} Stele"
                else:
                    valoare_text = str(valoare)

                item = QTableWidgetItem(valoare_text)
                self.table_widget.setItem(row, col, item)

        self.table_widget.resizeColumnsToContents()

    def show_add_menu(self):
        """Afișează meniul pop-up cu opțiunile de adăugare."""
        menu = QMenu(self)

        action_planet = QAction("Adaugă Planetă", self)
        action_planet.triggered.connect(self.open_add_planet_dialog)
        menu.addAction(action_planet)

        action_star = QAction("Adaugă Stea", self)
        action_star.triggered.connect(self.open_add_star_dialog)
        menu.addAction(action_star)

        action_constellation = QAction("Adaugă Constelație", self)
        action_constellation.triggered.connect(self.open_add_constellation_dialog)
        menu.addAction(action_constellation)

        menu.exec(QCursor.pos())  # Afișează meniul la poziția mouse-ului

    def open_add_planet_dialog(self):
        dialog = AddPlanetDialog(self.data_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.vizualizeaza_tip_obiect(Planeta)  # Reafișează automat planetele

    def open_add_star_dialog(self):
        dialog = AddStarDialog(self.data_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.vizualizeaza_tip_obiect(Stea)  # Reafișează automat stelele

    def open_add_constellation_dialog(self):
        dialog = AddConstellationDialog(self.data_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.vizualizeaza_tip_obiect(Constelatie)  # Reafișează automat constelațiile

    def salveaza_date_in_json(self):
        """Salvează toate obiectele din DataManager în JSON."""
        nume_fisier, _ = QFileDialog.getSaveFileName(
            self, "Salvează Universul", "univers_salvat.json", "JSON Files (*.json)"
        )

        if not nume_fisier: return

        lista_de_salvat = [obiect.to_dict() for obiect in self.data_manager.obiecte_univers if
                           hasattr(obiect, 'to_dict')]

        try:
            with open(nume_fisier, 'w', encoding='utf-8') as f:
                json.dump(lista_de_salvat, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Salvare cu Succes", f"Datele au fost salvate în:\n{nume_fisier}")
        except Exception as e:
            QMessageBox.critical(self, "Eroare de Salvare", f"Nu s-a putut salva fișierul: {e}")


# =========================================================
# 4. RULAREA APLICAȚIEI
# =========================================================

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())