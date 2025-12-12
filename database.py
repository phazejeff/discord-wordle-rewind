from __future__ import annotations
import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wordle import Wordle

class Database:
    def __init__(self, database_name: str):
        self.con = sqlite3.connect(database_name)
        cur = self.con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS wordle (user_id INTEGER NOT NULL, wordle_number INTEGER NOT NULL, guess_count INTEGER NOT NULL, guess1 INTEGER, guess2 INTEGER, guess3 INTEGER, guess4 INTEGER, guess5 INTEGER, guess6 INTEGER);")
        self.con.commit()
        cur.close()

    def input_wordle(self, user_id: int, wordle: Wordle):
        cur = self.con.cursor()
        cur.execute("INSERT INTO wordle VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, wordle.wordle_number, wordle.guess_amount, *wordle.guesses))

    def get_average_guesses(self):
        cur = self.con.cursor()
        cur.execute("SELECT user_id, AVG(guess_count) as average_guess_count FROM wordle GROUP BY user_id;")
        result = cur.fetchall()
        cur.close()
        return result
    
    def get_biggest_losers(self):
        cur = self.con.cursor()
        cur.execute("SELECT user_id, COUNT(guess_count) as losses FROM wordle WHERE guess_count = 7 GROUP BY user_id;")
        result = cur.fetchall()
        cur.close()
        return result
    
    def guess_count_distribution(self):
        cur = self.con.cursor()
        cur.execute('''
        SELECT user_id,
        SUM(CASE WHEN guess_count = 1 THEN 1 ELSE 0 END) as g1,
        SUM(CASE WHEN guess_count = 2 THEN 1 ELSE 0 END) as g2,
        SUM(CASE WHEN guess_count = 3 THEN 1 ELSE 0 END) as g3,
        SUM(CASE WHEN guess_count = 4 THEN 1 ELSE 0 END) as g4,
        SUM(CASE WHEN guess_count = 5 THEN 1 ELSE 0 END) as g5,
        SUM(CASE WHEN guess_count = 6 THEN 1 ELSE 0 END) as g6
        FROM wordle GROUP BY user_id;
        ''')
        result = cur.fetchall()
        cur.close()
        return result
    
    def best_first_word(self):
        cur = self.con.cursor()
        cur.execute('''
        SELECT user_id,
        AVG(
            ((guess1 & 1) + ((guess1 >> 1) & 1) * 2) +
            (((guess1 >> 2) & 1) + ((guess1 >> 3) & 1) * 2) +
            (((guess1 >> 4) & 1) + ((guess1 >> 5) & 1) * 2) +
            (((guess1 >> 6) & 1) + ((guess1 >> 7) & 1) * 2) +
            (((guess1 >> 8) & 1) + ((guess1 >> 9) & 1) * 2)
        ) AS avg_first_guess_score
        FROM wordle
        GROUP BY user_id;
        ''')
        result = cur.fetchall()
        cur.close()
        return result

    def commit(self):
        self.con.commit()