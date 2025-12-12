from wordle import Wordle
from database import Database
def main():
    database_name = "database.db"
    wordle = Wordle('''Wordle 1,637 5/6

🟨🟩⬛⬛⬛
⬛🟩⬛🟩🟩
⬛🟩⬛🟩🟩
⬛🟩🟩🟩🟩
🟩🟩🟩🟩🟩''')
    database = Database(database_name)
    database.input_wordle(1, wordle)

    wordle = Wordle('''Wordle 1,636 4/6

⬛⬛⬛⬛🟨
🟨⬛🟩⬛⬛
⬛⬛🟩⬛🟩
🟩🟩🟩🟩🟩''')
    database.input_wordle(1, wordle)

    wordle = Wordle('''Wordle 1,616 X/6

⬛⬛⬛⬛🟨
⬛🟨⬛⬛⬛
⬛⬛🟨⬛🟩
⬛🟩⬛🟩🟩
⬛🟩🟩🟩🟩
⬛🟩🟩🟩🟩''')
    database.input_wordle(1, wordle)
    database.commit()
    print(database.get_average_guesses())
    print(database.get_biggest_losers())
    print(database.guess_count_distribution())
    print(database.best_first_word())
    print(database.hardest_words())
    print(database.results_for_wordle_number(1636))
    print(database.get_unluckiest())

if __name__ == "__main__":
    main()
