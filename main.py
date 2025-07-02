from core.midi_core import MidiDevices, MidiInput, MidiOutput, MidiRouter
from core.modifiers.split import Split
import time

start_time = time.time()

def time_exec():
    end_time = time.time()
    exec_time = end_time - start_time
    formated_exec_time = f"{exec_time * 1e3:.2f} ms"
    print(formated_exec_time)

if __name__ == "__main__":
    devices = MidiDevices()
    devices.get_input_devices()
    devices.get_output_devices()

    midi_input = MidiInput()
    midi_output = MidiOutput()

    router = MidiRouter(midi_input, midi_output)

    # Modyfiers

    split = Split(split_note="")

    router.add_modyfier(split)

