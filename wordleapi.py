import requests
URL = 'https://wordlehints.co.uk/wp-json/wordlehint/v1/answers'

def get_answer_from_game_number(number: int) -> str:
    r = requests.get(URL + f'?game={number}').json()
    return r['results'][0]['answer']