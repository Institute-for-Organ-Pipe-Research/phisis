from midi_core import MidiModifier

class Split(MidiModifier):
    def __init__(self, split_note, input_channel, output_channel: int):
        super().__init__()
        self.split_note = split_note
        self.input_channel = input_channel
        self.output_channel = output_channel

    def modyfy(self, message):
        if message.type == ["note_on", "note_off"]:
            if message.channel == self.input_channel:
                if message.note > self.split_note:
                    output_message = message.copy(channel=self.output_channel)
                    return message
            else:
                return message
            
    def save_state(self):
        """Zwraca stan modyfikatora Split."""
        return {
            "type": "Split",
            "split_note": self.split_note,
            "input_channel": self.input_channel,
            "output_channel": self.output_channel,
        }

    def load_state(self, state):
        """Przywraca stan modyfikatora Split."""
        self.split_note = state["split_note"]
        self.input_channel = state["input_channel"]
        self.output_channel = state["output_channel"]