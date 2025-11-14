import csv
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk # Importa Pillow per la gestione delle immagini

def carica_file():
    """Apri una finestra per selezionare il file CSV e carica i nomi dei campi."""
    file_path = filedialog.askopenfilename(filetypes=[("File CSV", "*.csv")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

        # Leggi l'intestazione del CSV per popolare il menu a tendina
        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                header = next(reader)  # Leggi la prima riga (intestazione)
                combo_campo["values"] = header
                if "essere" in header:
                    combo_campo.current(header.index("essere"))  # Seleziona "essere" di default
                else:
                    combo_campo.current(0)  # Altrimenti seleziona il primo campo
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile leggere il file:\n{str(e)}")

def salva_risultati():
    """Salva i risultati in un file CSV scelto dall'utente."""
    if not hasattr(salva_risultati, "conteggi"):
        messagebox.showerror("Errore", "Nessun risultato da salvare. Esegui prima l'analisi!")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("File CSV", "*.csv")]
    )
    if file_path:
        with open(file_path, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Valore", "Conteggio"])
            for valore, count in sorted(salva_risultati.conteggi.items(), key=lambda x: x[1], reverse=True):
                writer.writerow([valore, count])
        messagebox.showinfo("Successo", f"Risultati salvati in:\n{file_path}")

def salva_grafico(fig):
    """Salva il grafico in formato SVG, PNG o PDF."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".svg",
        filetypes=[
            ("SVG", "*.svg"),
            ("PNG", "*.png"),
            ("PDF", "*.pdf")
        ]
    )
    if file_path:
        fig.savefig(file_path, bbox_inches="tight")
        messagebox.showinfo("Successo", f"Grafico salvato in:\n{file_path}")

def analizza_file():
    """Legge il file CSV, conta i valori del campo selezionato e mostra il grafico."""
    file_csv = entry_file.get()
    if not file_csv:
        messagebox.showerror("Errore", "Seleziona prima un file CSV!")
        return

    campo_selezionato = combo_campo.get()
    if not campo_selezionato:
        messagebox.showerror("Errore", "Seleziona un campo da analizzare!")
        return

    try:
        conteggi = defaultdict(int)
        with open(file_csv, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                valore = row.get(campo_selezionato, "")
                if valore:  # Ignora valori vuoti
                    conteggi[valore] += 1

        # Salva i conteggi per il salvataggio successivo
        salva_risultati.conteggi = conteggi

        # Stampa i risultati nella finestra
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, f"Statistiche per il campo '{campo_selezionato}':\n")
        for valore, count in sorted(conteggi.items(), key=lambda x: x[1], reverse=True):
            text_output.insert(tk.END, f"{valore}: {count}\n")

        # Mostra il grafico
        mostra_grafico(conteggi, campo_selezionato)

    except Exception as e:
        messagebox.showerror("Errore", f"Si è verificato un errore:\n{str(e)}")

def mostra_grafico(conteggi, campo_selezionato):
    """Mostra il grafico nel frame dedicato."""
    global fig  # Rendi la figura globale per poterla salvare successivamente
    valori, counts = zip(*sorted(conteggi.items(), key=lambda x: x[1], reverse=True))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(valori, counts)
    ax.set_title(f"Distribuzione dei valori per '{campo_selezionato}'")
    ax.set_xticklabels(valori, rotation=45, ha="right")
    ax.set_ylabel("Conteggio")

    # Cancella il grafico precedente (se esiste)
    for widget in frame_grafico.winfo_children():
        widget.destroy()

    # Integra il grafico nella GUI
    canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# --- Creazione della GUI ---
root = tk.Tk()
root.title("Statistiche CSV - Analisi Campi")

# --- Header con logo e nome software ---
frame_header = tk.Frame(root, padx=10, pady=10)
frame_header.pack(fill=tk.X)

# Carica e ridimensiona il logo "Statistics Basics"
try:
    img_sb = Image.open("icons/statistics_basics_icon.png")
    img_sb = img_sb.resize((130, 113), Image.LANCZOS) # Ridimensiona a 40x40 pixel
    photo_sb = ImageTk.PhotoImage(img_sb)
    label_sb_icon = tk.Label(frame_header, image=photo_sb)
    label_sb_icon.image = photo_sb # Mantieni un riferimento per evitare che venga eliminato dal garbage collector
    label_sb_icon.pack(side=tk.LEFT, padx=(0, 10))
except FileNotFoundError:
    messagebox.showwarning("Avviso", "Impossibile trovare 'icons/statistics_basics_icon.png'. Assicurati che il file sia nella cartella corretta.")
    photo_sb = None # Imposta a None se l'immagine non viene caricata

# Testo del titolo
frame_title_text = tk.Frame(frame_header)
frame_title_text.pack(side=tk.LEFT, anchor=tk.NW)
tk.Label(frame_title_text, text="Statistics Basics", font=("Helvetica", 16, "bold")).pack(anchor=tk.W)
tk.Label(frame_title_text, text="(Arc-Team Tools)", font=("Helvetica", 10)).pack(anchor=tk.W)


# Frame per il caricamento del file
frame_file = tk.Frame(root, padx=10, pady=10)
frame_file.pack(fill=tk.X)

tk.Label(frame_file, text="File CSV:").pack(side=tk.LEFT)
entry_file = tk.Entry(frame_file, width=50)
entry_file.pack(side=tk.LEFT, expand=True, fill=tk.X)
tk.Button(frame_file, text="Sfoglia...", command=carica_file).pack(side=tk.LEFT)

# Frame per la selezione del campo
frame_campo = tk.Frame(root, padx=10, pady=5)
frame_campo.pack(fill=tk.X)

tk.Label(frame_campo, text="Campo da analizzare:").pack(side=tk.LEFT)
combo_campo = ttk.Combobox(frame_campo, width=30)
combo_campo.pack(side=tk.LEFT, expand=True, fill=tk.X)

# Pulsante per avviare l'analisi
tk.Button(root, text="Analizza", command=analizza_file).pack(pady=5)

# Frame per l'output testuale
frame_output = tk.Frame(root, padx=10, pady=10)
frame_output.pack(fill=tk.BOTH, expand=True)

text_output = tk.Text(frame_output, height=10)
text_output.pack(fill=tk.BOTH, expand=True)

# Frame per il grafico
frame_grafico = tk.Frame(root, padx=10, pady=10)
frame_grafico.pack(fill=tk.BOTH, expand=True)

# Frame per i pulsanti di salvataggio
frame_salva = tk.Frame(root, padx=10, pady=5)
frame_salva.pack(fill=tk.X)

# Pulsante per salvare i risultati
tk.Button(frame_salva, text="Salva Risultati", command=salva_risultati).pack(side=tk.LEFT, padx=5)

# Pulsante per salvare il grafico
tk.Button(frame_salva, text="Salva Grafico", command=lambda: salva_grafico(fig) if 'fig' in globals() else messagebox.showerror("Errore", "Nessun grafico da salvare. Esegui prima l'analisi!")).pack(side=tk.LEFT, padx=5)

# --- Footer con "Powered by Arc-Team" e logo Arc-Team ---
frame_footer = tk.Frame(root, padx=10, pady=5)
frame_footer.pack(fill=tk.X, side=tk.BOTTOM)

# Carica e ridimensiona il logo "Arc-Team" (questo va impacchettato prima)
try:
    img_arcteam = Image.open("icons/arc-team_logo.png")
    img_arcteam = img_arcteam.resize((300, 70), Image.LANCZOS) # Ridimensiona a una dimensione adatta
    photo_arcteam = ImageTk.PhotoImage(img_arcteam)
    label_arcteam_icon = tk.Label(frame_footer, image=photo_arcteam)
    label_arcteam_icon.image = photo_arcteam # Mantieni un riferimento
    label_arcteam_icon.pack(side=tk.RIGHT) # Impacchetta a destra
except FileNotFoundError:
    messagebox.showwarning("Avviso", "Impossibile trovare 'icons/arc-team_logo.png'. Assicurati che il file sia nella cartella corretta.")
    photo_arcteam = None # Imposta a None se l'immagine non viene caricata

# Testo "Powered by Arc-Team" (questo va impacchettato dopo)
tk.Label(frame_footer, text="Powered by Arc-Team", font=("Helvetica", 9)).pack(side=tk.RIGHT, padx=(10, 0)) # Impacchetta a destra


# Avvia la GUI
root.mainloop()
