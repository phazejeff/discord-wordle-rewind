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
        cur.execute("CREATE TABLE IF NOT EXISTS users (user_Id INTEGER NOT NULL, username TEXT NOT NULL, nickname TEXT, avatar TEXT NOT NULL);")
        self.con.commit()
        cur.close()

    def input_wordle(self, user_id: int, wordle: Wordle):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM wordle WHERE user_id = ? AND wordle_number = ?", (user_id, wordle.wordle_number))
        results = cur.fetchall()
        if len(results) != 0:
            return
        cur.execute("INSERT INTO wordle VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, wordle.wordle_number, wordle.guess_amount, *wordle.guesses))

    def input_user(self, user_id: int, username: str, nickname: str | None, avatar: str):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        results = cur.fetchall()
        if len(results) != 0:
            return
        cur.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (user_id, username, nickname, avatar))

    def get_total_wordles(self):
        cur = self.con.cursor()
        cur.execute("SELECT user_id, COUNT(*) FROM wordle GROUP BY user_id ORDER BY COUNT(*) DESC;")
        result = cur.fetchall()
        cur.close()
        return result
    
    def remove_less_than_twenty(self):
        cur = self.con.cursor()
        cur.execute("DELETE FROM wordle WHERE user_id IN (SELECT user_id FROM wordle GROUP BY user_id HAVING COUNT(*) < 20)")
        self.con.commit()
        cur.close()

    def get_average_guesses(self):
        cur = self.con.cursor()
        cur.execute("SELECT user_id, AVG(guess_count) as average_guess_count FROM wordle GROUP BY user_id ORDER BY average_guess_count;")
        result = cur.fetchall()
        cur.close()
        return result
    
    def get_biggest_losers(self):
        cur = self.con.cursor()
        cur.execute("SELECT user_id, COUNT(guess_count) as losses FROM wordle WHERE guess_count = 7 GROUP BY user_id ORDER BY losses DESC;")
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
        GROUP BY user_id
        ORDER BY avg_first_guess_score;
        ''')
        result = cur.fetchall()
        cur.close()
        return result
    
    def hardest_words(self):
        cur = self.con.cursor()
        cur.execute('''SELECT 
        wordle_number,
        AVG(guess_count) AS avg_guess_count,
        COUNT(*) AS plays
        FROM wordle
        GROUP BY wordle_number
        ORDER BY avg_guess_count DESC
        LIMIT 5;
        ''')
        result = cur.fetchall()
        cur.close()
        return result
    
    def results_for_wordle_number(self, number: int):
        cur = self.con.cursor()
        cur.execute("SELECT * FROM wordle WHERE wordle_number = ?", (number,))
        result = cur.fetchall()
        cur.close()
        return result
    
    def get_unluckiest(self):
        cur = self.con.cursor()
        cur.execute('''WITH unlucky AS (
            SELECT
                user_id,
                (
                    ((guess1 >> 1) & 1) + ((guess1 >> 3) & 1) + ((guess1 >> 5) & 1) +
                    ((guess1 >> 7) & 1) + ((guess1 >> 9) & 1) +

                    ((guess2 >> 1) & 1) + ((guess2 >> 3) & 1) + ((guess2 >> 5) & 1) +
                    ((guess2 >> 7) & 1) + ((guess2 >> 9) & 1) +

                    ((guess3 >> 1) & 1) + ((guess3 >> 3) & 1) + ((guess3 >> 5) & 1) +
                    ((guess3 >> 7) & 1) + ((guess3 >> 9) & 1)
                )
                - (6 - guess_count) AS score
            FROM wordle
        )
        SELECT
            user_id,
            AVG(score) AS avg_unluckiness
        FROM unlucky
        GROUP BY user_id
        ORDER BY avg_unluckiness DESC
        LIMIT 5;
        ''')
        results = cur.fetchall()
        return results
    
    def longest_streak(self):
        cur = self.con.cursor()
        cur.execute('''WITH wins AS (
            SELECT
                user_id,
                wordle_number,
                ROW_NUMBER() OVER (
                    PARTITION BY user_id
                    ORDER BY wordle_number
                ) AS rn
            FROM wordle
            WHERE guess_count < 7
        ),
        streaks AS (
            SELECT
                user_id,
                wordle_number,
                wordle_number - rn AS streak_group
            FROM wins
        )
        SELECT
            user_id,
            wordle_number,
            COUNT(*) AS longest_streak
        FROM streaks
        GROUP BY user_id, streak_group
        ORDER BY longest_streak DESC
        LIMIT 5;
        ''')
        results = cur.fetchall()
        return results
    
    def longest_good_streak(self):
        cur = self.con.cursor()
        cur.execute('''WITH wins AS (
            SELECT
                user_id,
                wordle_number,
                ROW_NUMBER() OVER (
                    PARTITION BY user_id
                    ORDER BY wordle_number
                ) AS rn
            FROM wordle
            WHERE guess_count < 5
        ),
        streaks AS (
            SELECT
                user_id,
                wordle_number,
                wordle_number - rn AS streak_group
            FROM wins
        )
        SELECT
            user_id,
            wordle_number,
            COUNT(*) AS longest_streak
        FROM streaks
        GROUP BY user_id, streak_group
        ORDER BY longest_streak DESC
        LIMIT 5;
        ''')
        results = cur.fetchall()
        return results
    
    def longest_great_streak(self):
        cur = self.con.cursor()
        cur.execute('''WITH wins AS (
            SELECT
                user_id,
                wordle_number,
                ROW_NUMBER() OVER (
                    PARTITION BY user_id
                    ORDER BY wordle_number
                ) AS rn
            FROM wordle
            WHERE guess_count < 4
        ),
        streaks AS (
            SELECT
                user_id,
                wordle_number,
                wordle_number - rn AS streak_group
            FROM wins
        )
        SELECT
            user_id,
            wordle_number,
            COUNT(*) AS longest_streak
        FROM streaks
        GROUP BY user_id, streak_group
        ORDER BY longest_streak DESC
        LIMIT 5;
        ''')
        results = cur.fetchall()
        return results

    def commit(self):
        self.con.commit()