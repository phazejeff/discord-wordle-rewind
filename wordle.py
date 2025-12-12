class Wordle:
    def __init__(self, text: str):
        self.text = text
        self.wordle_number, self.guess_amount, self.guesses = Wordle.extract_from_text(text)

    @staticmethod
    def convert_guess_to_int(text: str) -> int:
        guess_int = 0
        guess_mapping = {
            "⬛" : 0b00,
            "⬜" : 0b00,
            "🟨" : 0b01,
            "🟩" : 0b10
        }
        for i, color in enumerate(text):
            shift = 2 * (4 - i)
            guess_int |= (guess_mapping[color] << shift)
        return guess_int

    @staticmethod
    def extract_from_text(text: str) -> tuple[int, list[int]]:
        lines = text.splitlines()
        wordle_number_str = lines[0].split()[1]
        wordle_number = int(wordle_number_str.replace(',', ''))
        guesses: list[int] = [None] * 6
        for i, line in enumerate(lines[2:]):
            guesses[i] = Wordle.convert_guess_to_int(line)
        
        # if they didn't win the wordle, then call it 7 guesses
        if i == 5 and guesses[i] != 0b1010101010:
            guess_amount = 7
        else:
            guess_amount = i + 1

        return wordle_number, guess_amount, guesses