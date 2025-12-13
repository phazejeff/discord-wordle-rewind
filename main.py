from database import Database
def main():
    database_name = "database.db"
    database = Database(database_name)
    # print(database.get_average_guesses())
    # print(database.get_biggest_losers())
    # print(database.guess_count_distribution())
    # print(database.best_first_word())
    # print(database.hardest_words())
    # print(database.results_for_wordle_number(1636))
    print(database.get_unluckiest())

if __name__ == "__main__":
    main()