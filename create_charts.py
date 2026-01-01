from matplotlib.axes import Axes
from database import Database
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import numpy as np
import os

from wordleapi import get_answer_from_game_number

OUTPUT_FOLDER = 'output'

def load_avatar(url, size=128):
    r = requests.get(url, timeout=5)
    img = Image.open(BytesIO(r.content)).convert("RGBA")
    img = img.resize((size, size))

    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    img.putalpha(mask)
    return img

def plot_data(database: Database, data: list[tuple[int, float | int]], title: str, soft_desc: str, hard_desc: str, filename: str):
    users = []
    for user_id, count in data:
        uid, username, nickname, avatar_url, color_int = database.get_user(user_id)
        if type(count) == float:
            count = round(count, 2)
        users.append({
            "name": nickname or username,
            "count": count,
            "avatar": avatar_url,
            "color": f"#{color_int:06x}" if color_int else "#5865F2"
        })

    max_count = users[0]['count']
    top_users = [u for u in users if u["count"] == max_count]

    # Use subplots for auto layout
    fig, (ax_top, ax_bar) = plt.subplots(
        2, 1, figsize=(8, 10), gridspec_kw={"height_ratios": [0.4, 0.6]}
    )
    fig.patch.set_facecolor("#2B2D31")
    ax_top: Axes
    ax_bar: Axes
    
    # TOP USER PANEL
    ax_top.set_facecolor("#1E1F22")
    ax_top.axis("off")
    ax_top.set_xlim(0, 1)
    ax_top.set_ylim(0, 1)

    # Figure DPI and size
    fig_width, fig_height = fig.get_size_inches()
    dpi = fig.dpi

    avatar_size = 140
    spacing = 40  # space between avatars (px)

    total_width = len(top_users) * avatar_size + (len(top_users) - 1) * spacing
    start_x = int(fig_width * dpi * 0.5 - total_width / 2)

    # Center avatar under name
    avatar_y = int(fig_height * dpi * 0.6)          # vertical position from bottom

    # Title (centered above everyone)
    fig.text(
        0.5, 0.925, title,
        ha="center", va="center",
        fontsize=32, fontweight="bold", color="#F2F3F5"
    )

    usernames_text = ""
    for i, user in enumerate(top_users):
        x_px = start_x + i * (avatar_size + spacing)

        # Avatar
        avatar_img = load_avatar(user["avatar"], size=avatar_size)
        fig.figimage(avatar_img, xo=x_px, yo=avatar_y, zorder=10)

        usernames_text += user["name"] + " & "
    
    usernames_text = usernames_text.removesuffix(" & ")
    # Name
    fig.text(
        0.5, 0.85, usernames_text,
        ha="center", va="center",
        fontsize=28, fontweight="bold",
        color= user["color"] if len(top_users) == 1 else "#5865F2"
    )

    # Count
    fig.text(
        0.5, 0.775, f"{top_users[0]['count']} {soft_desc}",
        ha="center", va="center",
        fontsize=20, color="#B5BAC1"
    )

    fig.text(0.5, 0.02, hard_desc,
            ha="center", va="center", fontsize=16, fontweight="light", color="#F2F3F5A4")

    # BAR CHART
    ax_bar.set_facecolor("#2B2D31")

    # Names with nickname + (username)
    names = []
    for u, d in zip(users, data):
        user_id = d[0]
        username = database.get_user(user_id)[1]
        display_name = u['name']
        label = f"{display_name}\n({username})" if display_name != username else display_name
        names.append(label)

    names = names[::-1]
    counts = [u["count"] for u in users][::-1]
    colors = [u["color"] for u in users][::-1]
    y_pos = np.arange(len(names))

    bars = ax_bar.barh(y_pos, counts, color=colors, height=0.6)
    ax_bar.set_yticks(y_pos)
    ax_bar.set_yticklabels(names)

    ax_bar.tick_params(axis="x", colors="#B5BAC1", labelsize=12)
    ax_bar.tick_params(axis="y", colors="#F2F3F5", labelsize=14)

    ax_bar.set_xlim(left=max(min(counts) - np.std(counts), 0))

    for spine in ax_bar.spines.values():
        spine.set_visible(False)

    ax_bar.xaxis.grid(False)
    ax_bar.yaxis.grid(False)

    # Value labels
    for bar in bars:
        w = bar.get_width()
        ax_bar.text(w + max(counts)*0.02, bar.get_y() + bar.get_height()/2,
                    f"{w}", va="center", ha="left", fontsize=12, color="#F2F3F5")

    # Auto-adjust layout so labels aren't cut off
    plt.tight_layout()
    plt.xticks([])
    plt.savefig(os.path.join(OUTPUT_FOLDER, filename))

def summarize_attempts(attempts):
    total = len(attempts)
    failed = sum(1 for a in attempts if a[2] == 7)
    avg = round(
        sum(6 if a[2] == 7 else a[2] for a in attempts) / total,
        2
    )
    return total, failed, avg

def plot_ranked_word_stats(
    database: Database,
    ranked_words: list[tuple[int, float]],
    word_attempts: list[tuple],
    title: str,
    stat_label: str,
    footer_desc: str,
    filename: str,
):
    words = []
    for game_num, value in ranked_words:
        words.append({
            "game": game_num,
            "word": get_answer_from_game_number(game_num),
            "value": round(value, 2),
        })

    top_word = words[0]

    attempts_for_top_word = [
        a for a in word_attempts if a[1] == top_word["game"]
    ]

    attempt_count, fail_count, actual_avg = summarize_attempts(attempts_for_top_word)

    # ---- FIGURE ----
    fig, (ax_top, ax_bar) = plt.subplots(
        2, 1, figsize=(8, 10),
        gridspec_kw={"height_ratios": [0.4, 0.6]}
    )

    fig.patch.set_facecolor("#2B2D31")

    # ---- TOP PANEL ----
    ax_top.set_facecolor("#1E1F22")
    ax_top.axis("off")
    ax_top.set_xlim(0, 1)
    ax_top.set_ylim(0, 1)

    fig_width, fig_height = fig.get_size_inches()
    dpi = fig.dpi
    avatar_x = int(fig_width * dpi * 0.5 - 140 / 2)  # center horizontally

    fig.text(
        0.5, 0.925, title,
        ha="center", va="center",
        fontsize=32, fontweight="bold",
        color="#F2F3F5"
    )

    fig.text(
        0.5, 0.82, top_word["word"],
        ha="center", va="center",
        fontsize=48, fontweight="bold",
        color="#ED4245"
    )

    fig.text(
        0.5, 0.725,
        f"{top_word['value']} {stat_label}",
        ha="center", va="center",
        fontsize=22,
        color="#B5BAC1"
    )

    fig.text(
        0.5, 0.66,
        f"{fail_count}/{attempt_count} players failed\nWordle #{top_word['game']}",
        ha="center", va="center",
        fontsize=16,
        color="#F2F3F5A4"
    )

    fig.text(
        0.5, 0.02,
        footer_desc,
        ha="center", va="center",
        fontsize=14,
        color="#F2F3F5A4"
    )

    # ---- BAR CHART ----
    ax_bar.set_facecolor("#2B2D31")

    labels = [
        f"{w['word']}  (#{w['game']})"
        for w in words
    ][::-1]

    values = [w["value"] for w in words][::-1]
    y_pos = np.arange(len(labels))

    bars = ax_bar.barh(
        y_pos,
        values,
        height=0.6,
        color="#5865F2"
    )

    ax_bar.set_yticks(y_pos)
    ax_bar.set_yticklabels(labels)

    ax_bar.tick_params(axis="x", colors="#B5BAC1", labelsize=12)
    ax_bar.tick_params(axis="y", colors="#F2F3F5", labelsize=14)

    ax_bar.set_xlim(left=max(min(values) - np.std(values), 0))

    for spine in ax_bar.spines.values():
        spine.set_visible(False)

    ax_bar.xaxis.grid(False)
    ax_bar.yaxis.grid(False)

    for bar in bars:
        w = bar.get_width()
        ax_bar.text(
            w + max(values) * 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{w}",
            va="center",
            ha="left",
            fontsize=12,
            color="#F2F3F5"
        )

    plt.tight_layout()
    plt.xticks([])
    plt.savefig(os.path.join(OUTPUT_FOLDER, filename))

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_FOLDER):
        os.mkdir(OUTPUT_FOLDER)

    database = Database('database.db')
    data = database.get_total_wordles()
    plot_data(database, data, "Biggest Wordler", "Wordles Played", "", "biggest_wordler.png")
    data = database.get_average_guesses()
    plot_data(database, data, "Greatest Wordler", "Average Guesses", "", "avg_guesses.png")
    data = database.get_biggest_losers()
    plot_data(database, data, "Biggest Loser", "Wordles Failed", "", "biggest_losers.png")
    data = database.get_unluckiest()
    plot_data(database, data, "Unluckiest", "Unlucky Score", "green letter count within first 3 guesses - (6 - total guesses)", "unluckiest.png")
    data = database.best_first_word()
    plot_data(database, data, "Meta Player", "Correct Letters In First Guess", "Green letters count as 2, yellow letters 1", "meta_players.png")
    data = database.longest_streak()
    plot_data(database, data, "Mr. Consistent", "Solved Wordles In A Row", "", "streak.png")
    data = database.longest_good_streak()
    plot_data(database, data, "Professor Consistent", "Solved Wordles In 4 Guesses Or Under In A Row", "", "good_streak.png")
    data = database.longest_great_streak()
    plot_data(database, data, "Doctor Consistent", "Solved Wordles In 3 Guesses Or Under In A Row", "", "great_streak.png")
    data = database.most_twos()
    plot_data(database, data, "BANG!", "Solved Wordles In 2 guesses", "", "BANG.png")
    data = database.hardest_words()
    user_data = database.results_for_wordle_number(data[0][0])
    plot_ranked_word_stats(database, data, user_data, "Hardest Wordle", "Average Guesses", "Failed wordles count as 7 guesses", "hardest.png")
    data = database.results_for_wordle_number_short(data[0][0])
    plot_data(database, data, "Rock Hard", "Guesses On The Hardest Wordle", "", "hardest_users.png")
    data = database.most_yellow()
    plot_data(database, data, "Where's Waldo?", "Average Yellow Letters Per Wordle", "", "most_yellows.png")
    data = database.easiest_words()
    user_data = database.results_for_wordle_number(data[0][0])
    user_data.reverse()
    plot_ranked_word_stats(database, data, user_data, "Easiest Wordle", "Average Guesses", "", "easiest.png")
    data = database.results_for_wordle_number_short(data[0][0])
    plot_data(database, data, "....Bang?", "Guesses On The Easiest Wordle", "", "easiest_users.png")
    data = database.get_unluckiest_word()
    user_data = database.results_for_wordle_number(data[0][0])
    user_data.reverse()
    plot_ranked_word_stats(database, data, user_data, "Stupid Wordle", "Average Unlucky Score", "green letter count within first 3 guesses - (6 - total guesses)", "unluckiest_word.png")
    data = database.results_for_wordle_number_short(data[0][0])
    plot_data(database, data, "Bruh.", "Guesses On The Unluckiest Wordle", "", "unluckiest_word_users.png")