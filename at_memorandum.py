import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
from PIL import Image, ImageTk

DATA_FILE = os.path.join(os.path.dirname(__file__), "progetti.json")

COLORI = {
    "verde": "#4CAF50",
    "arancione": "#FF9800",
    "rosso": "#F44336",
    "sfondo_verde": "#E8F5E9",
    "sfondo_arancione": "#FFF3E0",
    "sfondo_rosso": "#FFEBEE",
    "bianco": "#FFFFFF",
    "grigio": "#9E9E9E",
}

def carica_progetti():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def salva_progetti(progetti):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(progetti, f, indent=2, ensure_ascii=False)

def prossimo_id(progetti):
    return max((p["id"] for p in progetti), default=0) + 1

def calcola_colore(scadenza):
    if not scadenza:
        return COLORI["grigio"], COLORI["bianco"]
    try:
        giorni = (datetime.strptime(scadenza, "%Y-%m-%d").date() - date.today()).days
    except ValueError:
        return COLORI["grigio"], COLORI["bianco"]
    if giorni <= 3:
        return COLORI["rosso"], COLORI["sfondo_rosso"]
    elif giorni <= 14:
        return COLORI["arancione"], COLORI["sfondo_arancione"]
    else:
        return COLORI["verde"], COLORI["sfondo_verde"]

def formatta_data(data_str):
    if not data_str:
        return "—"
    try:
        d = datetime.strptime(data_str, "%Y-%m-%d")
        return d.strftime("%d/%m/%Y")
    except ValueError:
        return data_str

ORDINE_PRIORITA = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4}


class ProgettiDialog:
    def __init__(self, parent, progetto=None):
        self.progetto = progetto
        self.risultato = None

        dialog = tk.Toplevel(parent)
        dialog.title("Modifica Progetto" if progetto else "Nuovo Progetto")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.entry_nome = ttk.Entry(frame, width=40)
        self.entry_nome.grid(row=0, column=1, pady=3)

        ttk.Label(frame, text="Descrizione:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.entry_desc = ttk.Entry(frame, width=40)
        self.entry_desc.grid(row=1, column=1, pady=3)

        ttk.Label(frame, text="Priorità (1-5):").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.combo_priorita = ttk.Combobox(frame, values=["1 (Massima)", "2", "3", "4", "5 (Minima)"], width=37, state="readonly")
        self.combo_priorita.grid(row=2, column=1, pady=3)

        ttk.Label(frame, text="Scadenza (GG/MM/AAAA):").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.entry_scadenza = ttk.Entry(frame, width=40)
        self.entry_scadenza.grid(row=3, column=1, pady=3)

        ttk.Label(frame, text="Progresso (%):").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.scale_progresso = ttk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, length=300)
        self.scale_progresso.grid(row=4, column=1, pady=3, sticky=tk.W)
        self.label_progresso = ttk.Label(frame, text="0%")
        self.label_progresso.grid(row=4, column=1, padx=(310, 0), pady=3, sticky=tk.W)
        self.scale_progresso.configure(command=lambda v: self.label_progresso.configure(text=f"{int(float(v))}%"))

        if progetto:
            self.entry_nome.insert(0, progetto["nome"])
            self.entry_desc.insert(0, progetto.get("descrizione", ""))
            priorita = progetto.get("priorita", 3)
            self.combo_priorita.set(f"{priorita} (Massima)" if priorita == 1 else f"{priorita} (Minima)" if priorita == 5 else str(priorita))
            if progetto.get("scadenza"):
                self.entry_scadenza.insert(0, formatta_data(progetto["scadenza"]))
            self.scale_progresso.set(progetto.get("progresso", 0))
            self.label_progresso.configure(text=f"{progetto.get('progresso', 0)}%")

        frame_bottoni = ttk.Frame(frame)
        frame_bottoni.grid(row=5, column=0, columnspan=2, pady=(15, 0))
        ttk.Button(frame_bottoni, text="Annulla", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_bottoni, text="Salva", command=lambda: self.salva(dialog)).pack(side=tk.LEFT, padx=5)

        self.entry_nome.focus_set()
        parent.wait_window(dialog)

    def salva(self, dialog):
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showerror("Errore", "Il nome del progetto è obbligatorio.", parent=dialog)
            return

        scadenza_str = self.entry_scadenza.get().strip()
        scadenza = ""
        if scadenza_str:
            try:
                datetime.strptime(scadenza_str, "%d/%m/%Y")
                giorni, mese, anno = scadenza_str.split("/")
                scadenza = f"{anno}-{mese}-{giorni}"
            except ValueError:
                messagebox.showerror("Errore", "Formato data non valido. Usa GG/MM/AAAA.", parent=dialog)
                return

        priorita_raw = self.combo_priorita.get()
        priorita = 3
        if priorita_raw:
            priorita = int(priorita_raw[0])

        self.risultato = {
            "nome": nome,
            "descrizione": self.entry_desc.get().strip(),
            "priorita": priorita,
            "scadenza": scadenza,
            "progresso": int(self.scale_progresso.get()),
        }
        dialog.destroy()


class CompitiDialog:
    def __init__(self, parent, progetto, progetti):
        self.progetto = progetto
        self.progetti = progetti
        self.compiti = progetto.setdefault("compiti", [])

        dialog = tk.Toplevel(parent)
        dialog.title(f"Compiti - {progetto['nome']}")
        dialog.geometry("520x400")
        dialog.minsize(400, 300)
        dialog.transient(parent)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=f"Compiti per: {progetto['nome']}", font=("Helvetica", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))

        frame_lista = tk.Frame(frame)
        frame_lista.pack(fill=tk.BOTH, expand=True)

        self.lista = tk.Listbox(frame_lista, font=("Helvetica", 10), selectbackground="#DDEEFF")
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.lista.yview)
        self.lista.configure(yscrollcommand=scrollbar.set)
        self.lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lista.bind("<Double-1>", lambda e: self.toggle_stato())

        frame_bottoni = tk.Frame(frame)
        frame_bottoni.pack(fill=tk.X, pady=(10, 0))

        self.btn_nuovo = tk.Button(frame_bottoni, text="+ Nuovo Compito", bg=COLORI["verde"], fg="white",
                                    font=("Helvetica", 9, "bold"), padx=8, command=self.nuovo_compito)
        self.btn_nuovo.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_modifica = tk.Button(frame_bottoni, text="Modifica", padx=8, command=self.modifica_compito)
        self.btn_modifica.pack(side=tk.LEFT, padx=5)

        self.btn_toggle = tk.Button(frame_bottoni, text="  Cambia Stato  ", padx=8, command=self.toggle_stato)
        self.btn_toggle.pack(side=tk.LEFT, padx=5)

        self.btn_elimina = tk.Button(frame_bottoni, text="Elimina", padx=8, command=self.elimina_compito)
        self.btn_elimina.pack(side=tk.LEFT, padx=5)

        ttk.Separator(frame_bottoni, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        self.btn_chiudi = tk.Button(frame_bottoni, text="Chiudi", padx=8, command=dialog.destroy)
        self.btn_chiudi.pack(side=tk.RIGHT, padx=5)

        self.aggiorna_lista()
        parent.wait_window(dialog)

    def aggiorna_lista(self):
        self.lista.delete(0, tk.END)
        for i, c in enumerate(self.compiti):
            stato = c.get("stato", "in_corso")
            icona = "[x]" if stato == "completato" else "[ ]"
            self.lista.insert(tk.END, f"  {icona}  {c['nome']}")
            if stato == "completato":
                self.lista.itemconfig(i, fg=COLORI["grigio"])

    def prossimo_id_compito(self):
        return max((c["id"] for c in self.compiti), default=0) + 1

    def compito_selezionato(self):
        sel = self.lista.curselection()
        if not sel:
            messagebox.showinfo("Info", "Seleziona un compito.", parent=self.lista)
            return None
        return sel[0], self.compiti[sel[0]]

    def nuovo_compito(self):
        nome = simpledialog.askstring("Nuovo Compito", "Nome del compito:", parent=self.lista)
        if nome and nome.strip():
            self.compiti.append({
                "id": self.prossimo_id_compito(),
                "nome": nome.strip(),
                "stato": "in_corso",
            })
            salva_progetti(self.progetti)
            self.aggiorna_lista()

    def modifica_compito(self):
        risultato = self.compito_selezionato()
        if not risultato:
            return
        idx, compito = risultato
        nome = simpledialog.askstring("Modifica Compito", "Nome:", initialvalue=compito["nome"], parent=self.lista)
        if nome and nome.strip():
            compito["nome"] = nome.strip()
            salva_progetti(self.progetti)
            self.aggiorna_lista()

    def toggle_stato(self):
        risultato = self.compito_selezionato()
        if not risultato:
            return
        _, compito = risultato
        compito["stato"] = "completato" if compito.get("stato", "in_corso") == "in_corso" else "in_corso"
        salva_progetti(self.progetti)
        self.aggiorna_lista()

    def elimina_compito(self):
        risultato = self.compito_selezionato()
        if not risultato:
            return
        idx, compito = risultato
        if messagebox.askyesno("Conferma", f"Eliminare il compito '{compito['nome']}'?", parent=self.lista):
            self.compiti.pop(idx)
            salva_progetti(self.progetti)
            self.aggiorna_lista()


class ATMemorandum:
    def __init__(self, root):
        self.root = root
        self.root.title("AT Memorandum - Gestione Progetti")
        self.root.geometry("900x600")
        self.root.minsize(700, 450)

        self.progetti = carica_progetti()
        self.crea_header()
        self.crea_toolbar()
        self.crea_lista()
        self.crea_footer()
        self.aggiorna_lista()

    def crea_header(self):
        frame_header = tk.Frame(self.root, padx=10, pady=10)
        frame_header.pack(fill=tk.X)

        icona_path = os.path.join(os.path.dirname(__file__), "icons", "memorandum_icon.png")
        try:
            img = Image.open(icona_path)
            img = img.resize((48, 48), Image.LANCZOS)
            self.header_icon = ImageTk.PhotoImage(img)
            tk.Label(frame_header, image=self.header_icon).pack(side=tk.LEFT, padx=(0, 10))
        except Exception:
            pass

        frame_title = tk.Frame(frame_header)
        frame_title.pack(side=tk.LEFT)
        tk.Label(frame_title, text="AT Memorandum", font=("Helvetica", 18, "bold")).pack(anchor=tk.W)
        tk.Label(frame_title, text="(Arc-Team Tools)", font=("Helvetica", 10), fg=COLORI["grigio"]).pack(anchor=tk.W)

        tk.Label(self.root, background=COLORI["grigio"], height=1).pack(fill=tk.X)

    def crea_toolbar(self):
        frame = tk.Frame(self.root, padx=10, pady=8)
        frame.pack(fill=tk.X)

        self.btn_nuovo = tk.Button(frame, text="+ Nuovo Progetto", bg=COLORI["verde"], fg="white",
                                   font=("Helvetica", 10, "bold"), padx=10, command=self.nuovo_progetto)
        self.btn_nuovo.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_modifica = tk.Button(frame, text="Modifica", padx=10, command=self.modifica_progetto)
        self.btn_modifica.pack(side=tk.LEFT, padx=5)

        self.btn_elimina = tk.Button(frame, text="Elimina", padx=10, command=self.elimina_progetto)
        self.btn_elimina.pack(side=tk.LEFT, padx=5)

        ttk.Separator(frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        self.btn_completa = tk.Button(frame, text="Segna Completo", padx=10, command=self.segna_completo)
        self.btn_completa.pack(side=tk.LEFT, padx=5)

        ttk.Separator(frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        self.btn_compiti = tk.Button(frame, text="Compiti", padx=10, command=self.gestisci_compiti)
        self.btn_compiti.pack(side=tk.LEFT, padx=5)

    def crea_lista(self):
        frame_lista = tk.Frame(self.root, padx=10, pady=5)
        frame_lista.pack(fill=tk.BOTH, expand=True)

        colonne = ("nome", "descrizione", "priorita", "scadenza", "progresso")
        self.tree = ttk.Treeview(frame_lista, columns=colonne, show="tree", selectmode="browse")

        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("nome", text="Progetto / Compiti", anchor=tk.W)
        self.tree.heading("descrizione", text="Descrizione", anchor=tk.W)
        self.tree.heading("priorita", text="Priorità", anchor=tk.CENTER)
        self.tree.heading("scadenza", text="Scadenza", anchor=tk.CENTER)
        self.tree.heading("progresso", text="Progresso", anchor=tk.CENTER)

        self.tree.column("#0", width=40, stretch=False)
        self.tree.column("nome", width=220, minwidth=140)
        self.tree.column("descrizione", width=240, minwidth=100)
        self.tree.column("priorita", width=70, stretch=False)
        self.tree.column("scadenza", width=100, stretch=False)
        self.tree.column("progresso", width=100, stretch=False)

        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.tag_configure("verde", background=COLORI["sfondo_verde"])
        self.tree.tag_configure("arancione", background=COLORI["sfondo_arancione"])
        self.tree.tag_configure("rosso", background=COLORI["sfondo_rosso"])
        self.tree.tag_configure("completato", foreground=COLORI["grigio"])

        self.tree.bind("<Double-1>", lambda e: self.al_doppio_click())

        frame_riepilogo = tk.Frame(self.root, padx=10, pady=5)
        frame_riepilogo.pack(fill=tk.X)
        self.label_riepilogo = tk.Label(frame_riepilogo, text="", font=("Helvetica", 9), fg=COLORI["grigio"])
        self.label_riepilogo.pack(side=tk.LEFT)

    def crea_footer(self):
        frame_footer = tk.Frame(self.root, padx=10, pady=5)
        frame_footer.pack(fill=tk.X, side=tk.BOTTOM)

        icona_path = os.path.join(os.path.dirname(__file__), "..", "Arc-Team-Tools-main", "icons", "arc-team_logo.png")
        try:
            img = Image.open(icona_path)
            img = img.resize((180, 42), Image.LANCZOS)
            self.footer_photo = ImageTk.PhotoImage(img)
            tk.Label(frame_footer, image=self.footer_photo).pack(side=tk.RIGHT, padx=(0, 5))
        except Exception:
            pass

        tk.Label(frame_footer, text="Powered by Arc-Team", font=("Helvetica", 9)).pack(side=tk.RIGHT)

    def aggiorna_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.progetti:
            self.label_riepilogo.configure(text="Nessun progetto. Clicca '+ Nuovo Progetto' per iniziare!")
            return

        self.progetti.sort(key=lambda p: (p.get("completato", False), ORDINE_PRIORITA.get(p.get("priorita", 3), 2), p.get("scadenza", "")))

        completi = 0
        for p in self.progetti:
            if p.get("completato"):
                completi += 1
                progetto_tag = "completato"
            else:
                _, sfondo = calcola_colore(p.get("scadenza", ""))
                progetto_tag = "verde"
                for t, c in [("rosso", COLORI["sfondo_rosso"]), ("arancione", COLORI["sfondo_arancione"]), ("verde", COLORI["sfondo_verde"])]:
                    if sfondo == c:
                        progetto_tag = t
                        break

            priorita = p.get("priorita", 3)
            scadenza = formatta_data(p.get("scadenza", ""))
            progresso = p.get("progresso", 0)

            if p.get("completato"):
                nome_display = f"  {p['nome']}  (Completato)"
            else:
                nome_display = f"  {p['nome']}"

            pid = f"p_{p['id']}"
            self.tree.insert("", tk.END, iid=pid, text="",
                             values=(nome_display, p.get("descrizione", ""), str(priorita), scadenza, f"{progresso}%"),
                             tags=(progetto_tag,))

            for c in p.get("compiti", []):
                cid = f"{pid}_t_{c['id']}"
                stato = c.get("stato", "in_corso")
                icona = "[x]" if stato == "completato" else "[ ]"
                task_tag = "completato" if stato == "completato" else progetto_tag
                self.tree.insert(pid, tk.END, iid=cid, text="",
                                 values=(f"    {icona} {c['nome']}", "", "", "", ""),
                                 tags=(task_tag,))

            if not p.get("completato"):
                self.tree.set(pid, "progresso", f"{progresso}%")

        totale = len(self.progetti)
        attivi = totale - completi
        self.label_riepilogo.configure(
            text=f"Progetti: {totale} totali, {attivi} attivi, {completi} completati"
        )

    def nuovo_progetto(self):
        dialog = ProgettiDialog(self.root)
        if dialog.risultato:
            p = dialog.risultato
            p["id"] = prossimo_id(self.progetti)
            p["completato"] = False
            p["creato"] = date.today().isoformat()
            self.progetti.append(p)
            salva_progetti(self.progetti)
            self.aggiorna_lista()

    def al_doppio_click(self):
        selected = self.tree.selection()
        if not selected:
            return
        iid = selected[0]
        if "_t_" in iid:
            return
        self.modifica_progetto()

    def progetto_da_selezione(self):
        selected = self.tree.selection()
        if not selected:
            return None
        iid = selected[0]
        if not iid.startswith("p_") or "_t_" in iid:
            return None
        pid = int(iid[2:])
        return next((p for p in self.progetti if p["id"] == pid), None)

    def modifica_progetto(self):
        progetto = self.progetto_da_selezione()
        if not progetto:
            messagebox.showinfo("Info", "Seleziona un progetto (non un compito) da modificare.")
            return

        dialog = ProgettiDialog(self.root, progetto=progetto)
        if dialog.risultato:
            progetto.update(dialog.risultato)
            salva_progetti(self.progetti)
            self.aggiorna_lista()

    def elimina_progetto(self):
        progetto = self.progetto_da_selezione()
        if not progetto:
            messagebox.showinfo("Info", "Seleziona un progetto (non un compito) da eliminare.")
            return

        if messagebox.askyesno("Conferma", f"Eliminare il progetto '{progetto['nome']}'?"):
            self.progetti = [p for p in self.progetti if p["id"] != progetto["id"]]
            salva_progetti(self.progetti)
            self.aggiorna_lista()

    def segna_completo(self):
        progetto = self.progetto_da_selezione()
        if not progetto:
            messagebox.showinfo("Info", "Seleziona un progetto (non un compito) da completare.")
            return

        if progetto.get("completato"):
            progetto["completato"] = False
            progetto["progresso"] = 0
        else:
            progetto["completato"] = True
            progetto["progresso"] = 100
        salva_progetti(self.progetti)
        self.aggiorna_lista()

    def gestisci_compiti(self):
        progetto = self.progetto_da_selezione()
        if not progetto:
            messagebox.showinfo("Info", "Seleziona un progetto (non un compito) per gestirne i compiti.")
            return
        CompitiDialog(self.root, progetto, self.progetti)


if __name__ == "__main__":
    root = tk.Tk()
    app = ATMemorandum(root)
    root.mainloop()
