import yaml
import os
from midi_core import Stop, Divisional, Divisionals, StopIDGenerator, DivisionalIDGenerator
from pathlib import Path


class PresetManager:
    def __init__(self, organs_dir="organs", presets_file="presets.yaml"):
        # Użyj Path do zarządzania ścieżkami
        self.organs_dir = Path(organs_dir).absolute()
        self.presets_file = Path(presets_file).absolute()

    def save_preset(self, organ_name, preset_name, divisions_state, couplers_state):
        """Wczytuje preset z pliku TOML."""
        
        
    def load_preset(self, preset_name, divisionals, couplers):
        """
        Wczytuje preset z pliku TOML i aktualizuje stan organów.
        
        """




class Setzer:
    def __init__(self, preset_manager) -> None:
        self.last_prreset_number

    