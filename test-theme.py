import customtkinter as ctk
# Importiere das ctk-table Modul
try:
    from CTkTable import CTkTable
except ImportError:
    print("Das 'ctk-table' Modul ist nicht installiert. Bitte installiere es.")
    exit()

# WICHTIG: Stelle sicher, dass "customtheme.json" im gleichen Ordner liegt
ctk.set_default_color_theme("orange.json") 
ctk.set_appearance_mode("dark") 


# --- FARBEN MAPPING FÜR CTkTable ---
# Dies muss manuell geschehen, da CTkTable nicht die Standard-Theme-Datei nutzt.
# Die Werte stammen aus der 'color'-Sektion deiner my_theme.json (Dark / Light)
COLOR_MAP = {
    # Hintergrund der Zellen
    "bg_cell": ("#363030", "#E6DFDF"),  # bg_light / bg_dark
    # Hintergrund der Header-Zellen
    "bg_header": ("#1D1818", "#FFFFFF"), # bg_dark / bg_light
    # Textfarbe
    "text": ("#F0ECEB", "#302626"),     # text / text
    # Farbe beim Überfahren
    "hover": ("#665C5C", "#998E8E"),    # border / border
    # Farbe der ausgewählten Zelle
    "selected": ("#C0B3B2", "#665C5C") # primary / primary
}

class ThemeDemoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Custom Theme Demo mit CTk-Widgets & CTkTable")
        self.geometry("800x650")
        
        self.mode_switch = ctk.CTkSwitch(self, 
                                         text="Dark / Light Modus", 
                                         command=self.toggle_appearance)
        self.mode_switch.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")
        
        self.tab_view.add("Buttons & Eingaben")
        self.tab_view.add("Tabelle & Container")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.setup_buttons_tab()
        self.setup_container_tab()
        
        # Sicherstellen, dass der Switch dem Startmodus entspricht
        if ctk.get_appearance_mode() == "dark":
             self.mode_switch.select()
        else:
             self.mode_switch.deselect()

    def get_ctktable_colors(self):
        """Gibt die Farb-Einstellungen für CTkTable basierend auf dem aktuellen Modus zurück."""
        mode = 0 if ctk.get_appearance_mode() == "dark" else 1
        
        return {
            "fg_color": COLOR_MAP["bg_cell"][mode],
            "header_color": COLOR_MAP["bg_header"][mode],
            "text_color": COLOR_MAP["text"][mode],
            "hover_color": COLOR_MAP["hover"][mode],
            "selected_color": COLOR_MAP["selected"][mode]
        }
        
    def toggle_appearance(self):
        """Wechselt zwischen Dark und Light Mode und aktualisiert die Tabelle."""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        
        # WICHTIG: Tabelle muss aktualisiert werden
        self.update_table_theme()
        
    def update_table_theme(self):
        """Aktualisiert die Farben der CTkTable nach einem Modus-Wechsel."""
        try:
            colors = self.get_ctktable_colors()
            
            # Da CTkTable keine direkte .configure() Methode für alle Farben hat,
            # erstellen wir die Tabelle neu oder nutzen die set_colors Methode,
            # wenn das Modul diese unterstützt. Wir simulieren hier die Neukonfiguration 
            # der wichtigsten Farben, die das Modul in neueren Versionen zulässt.
            
            self.table.fg_color = colors["fg_color"]
            self.table.header_color = colors["header_color"]
            self.table.text_color = colors["text_color"]
            self.table.hover_color = colors["hover_color"]
            
            # Manchmal muss das Widget für vollständige Aktualisierung neu gezeichnet werden
            self.table.update_idletasks()
            
        except AttributeError:
            # Falls die Tabelle noch nicht existiert oder eine ältere Version ist
            pass
            
    # [setup_buttons_tab Methode bleibt unverändert]
    def setup_buttons_tab(self):
        tab = self.tab_view.tab("Buttons & Eingaben")
        tab.columnconfigure(0, weight=1)
        ctk.CTkLabel(tab, text="--- Button Aliases (Styles) ---").grid(row=0, column=0, pady=(10, 5))
        ctk.CTkButton(tab, text="Primary (Default)").grid(row=1, column=0, padx=20, pady=5)
        ctk.CTkLabel(tab, text="--- Andere Widgets ---").grid(row=5, column=0, pady=(10, 5))
        ctk.CTkEntry(tab, placeholder_text="Eingabefeld...").grid(row=6, column=0, padx=20, pady=5)
        ctk.CTkSlider(tab, from_=0, to=100).grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        ctk.CTkCheckBox(tab, text="Option gewählt").grid(row=8, column=0, padx=20, pady=5)


    def setup_container_tab(self):
        """Konfiguriert den 'Tabelle & Container' Tab."""
        tab = self.tab_view.tab("Tabelle & Container")
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        
        # Dummy-Daten für die Tabelle
        data = [
            ["ID", "Name", "Status", "Preis"],
            [1, "Produkt A", "Verfügbar", "19.99 €"],
            [2, "Produkt B", "Veraltet", "99.00 €"],
            [3, "Produkt C", "Neu", "250.50 €"],
            [4, "Produkt D", "Verfügbar", "15.00 €"]
        ]
        
        ctk.CTkLabel(tab, text="--- CTkTable ---").grid(row=0, column=0, pady=(10, 5))

        # Farben basierend auf dem aktuellen Modus abrufen
        table_colors = self.get_ctktable_colors()
        
        # Tabelle erstellen und Farben übergeben
        self.table = CTkTable(
            tab, 
            values=data,
            # Farben direkt aus dem Dictionary übergeben
            fg_color=table_colors["fg_color"],
            header_color=table_colors["header_color"],
            text_color=table_colors["text_color"],
            hover_color=table_colors["hover_color"],
            # Weitere Einstellungen
            corner_radius=8,
            command=lambda *args: print(f"Zelle geklickt: {args[2]}"),
            width=650
        )
        self.table.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Scrollable Frame (wie zuvor)
        scroll_frame = ctk.CTkScrollableFrame(tab, label_text="Scrollbarer Log-Bereich")
        scroll_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        for i in range(5):
            ctk.CTkLabel(scroll_frame, text=f"Log-Eintrag #{i+1}").pack(padx=5, pady=2)
        
if __name__ == "__main__":
    app = ThemeDemoApp()
    app.mainloop()