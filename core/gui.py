import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.oscilator import PhisisOrganPipe
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class OrganPipeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Phisis Organ Pipe Generator")

        self.pipe = PhisisOrganPipe()

        self.params = {
            'f0': ("Podstawowa częstotliwość (Hz)", 20, 2000, 1),
            'pipe_length': ("Długość piszczałki (m)", 0.1, 5.0, 0.01),
            'mod_depth': ("Głębokość modulacji", 0.0, 0.1, 0.001),
            'lfo_freq': ("Częstotliwość LFO (Hz)", 0.01, 20, 0.01),
            'nonlinear_gain': ("Wzmocnienie nieliniowe", 0.0, 3.0, 0.01),
            'clip_level': ("Poziom przesterowania", 0.1, 1.0, 0.01),
            'noise_level': ("Poziom szumu", 0.0, 0.1, 0.001),
            'rate_scale': ("Skala szumu", 0.0, 1.0, 0.01),
            'tfbk': ("Współczynnik tłumienia (tfbk)", 0.0, 1.0, 0.01),
            'attack_time': ("Czas ataku (s)", 0.0, 2.0, 0.01),
            'decay_time': ("Czas zaniku (s)", 0.0, 2.0, 0.01),
            'sustain_level': ("Poziom podtrzymania", 0.0, 1.0, 0.01),
            'release_time': ("Czas wybrzmienia (s)", 0.0, 3.0, 0.01),
        }

        self.vars = {}
        self.scales = {}
        self.entries = {}

        self.create_widgets()

    def create_widgets(self):
        row = 0
        for param, (label, min_val, max_val, step) in self.params.items():
            ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=3)

            var = tk.DoubleVar(value=self.pipe.params.get(param, 0.0))
            self.vars[param] = var

            scale = ttk.Scale(self, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                              variable=var, command=lambda val, p=param: self.on_scale_change(p, val))
            scale.grid(row=row, column=1, sticky="ew", padx=5)
            self.scales[param] = scale

            entry = ttk.Entry(self, width=8)
            entry.grid(row=row, column=2, sticky="w", padx=5)
            entry.insert(0, f"{var.get():.3f}")
            entry.bind("<Return>", lambda e, p=param: self.on_entry_change(p))
            entry.bind("<FocusOut>", lambda e, p=param: self.on_entry_change(p))
            self.entries[param] = entry

            row += 1

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=10)

        play_btn = ttk.Button(btn_frame, text="Odtwórz (2s)", command=self.play_sound)
        play_btn.pack(side=tk.LEFT, padx=5)

        export_btn = ttk.Button(btn_frame, text="Eksportuj parametry", command=self.export_parameters)
        export_btn.pack(side=tk.LEFT, padx=5)

        stop_btn = ttk.Button(btn_frame, text="Zamknij", command=self.destroy)
        stop_btn.pack(side=tk.LEFT, padx=5)

        self.grid_columnconfigure(1, weight=1)

    def on_scale_change(self, param, val):
        value = float(val)
        self.pipe.set_parameter(param, value)
        # Aktualizuj wpis w Entry tylko, jeśli różni się od obecnego, aby uniknąć pętli
        current_text = self.entries[param].get()
        new_text = f"{value:.3f}"
        if current_text != new_text:
            self.entries[param].delete(0, tk.END)
            self.entries[param].insert(0, new_text)

    def on_entry_change(self, param):
        try:
            val_str = self.entries[param].get()
            value = float(val_str)
        except ValueError:
            messagebox.showerror("Błąd", f"Niepoprawna wartość dla {param}")
            # Przywróć poprzednią wartość
            self.entries[param].delete(0, tk.END)
            self.entries[param].insert(0, f"{self.vars[param].get():.3f}")
            return

        min_val = self.scales[param]['from']
        max_val = self.scales[param]['to']

        # Ogranicz wartość do zakresu
        if value < min_val:
            value = min_val
        elif value > max_val:
            value = max_val

        self.vars[param].set(value)
        self.pipe.set_parameter(param, value)
        # Suwak automatycznie się zaktualizuje dzięki zmiennej DoubleVar

        # Aktualizuj wpis (może zostać zmodyfikowany ograniczeniem)
        self.entries[param].delete(0, tk.END)
        self.entries[param].insert(0, f"{value:.3f}")

    def play_sound(self):
        duration = 2.0
        try:
            sound = self.pipe.generate_note(duration)
            sound = sound / np.max(np.abs(sound))
            sd.play(sound.astype(np.float32), self.pipe.fs)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wygenerować dźwięku:\n{e}")

    def export_parameters(self):
        params_to_export = {k: self.vars[k].get() for k in self.vars}
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json")],
                                                 title="Zapisz parametry jako")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(params_to_export, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Eksport zakończony", f"Parametry zapisano do pliku:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać parametrów:\n{e}")

if __name__ == "__main__":
    app = OrganPipeGUI()
    app.mainloop()
