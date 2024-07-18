import re
from thefuzz import fuzz

import json
import services.shared.functions as shared
from pathlib import Path
from typing import List, Literal
from datetime import datetime, timedelta


SPAM_CONFIG_PATH = Path(__file__).parent / "spam.json"


async def check_for_spam(msg: str, msg_words: list[str]) -> dict | None:
  spam_config = await get_spam_list()

  spam_phrases: list[dict] = spam_config['spam_config']['spam_phrases']
  spam_words: list[dict] = spam_config['spam_config']['spam_words']

  for spam_word in spam_words:
    for word in msg_words:
      if fuzz.ratio(spam_word["spam"], word) > 85:
        return spam_word

  for spam_phrase in spam_phrases:
    if re.search(pattern=spam_phrase["spam"], string=msg, flags=re.IGNORECASE):
      return spam_phrase

  return None



async def open_spam_config() -> dict:
    if SPAM_CONFIG_PATH.exists():
        try:
            with open(SPAM_CONFIG_PATH, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {"spam_config": {"spam_words": [], "spam_phrases": []}}
    else:
        return {"spam_config": {"spam_words": [], "spam_phrases": []}}


async def save_spam_config(data: dict) -> None:
    with open(SPAM_CONFIG_PATH, "w") as file:
        json.dump(data, file, indent=4)
    

async def check_spam_expirations(spam_config: dict) -> dict:
    for spam_word in spam_config['spam_config']['spam_words']:
        if spam_word['expires'] < datetime.now():
            spam_config['spam_config']['spam_words'].remove(spam_word)

    for spam_phrase in spam_config['spam_config']['spam_phrases']:
        if spam_phrase['expires'] < datetime.now():
            spam_config['spam_config']['spam_phrases'].remove(spam_phrase)

    return spam_config


async def get_spam_list() -> dict:
    current_config = await open_spam_config()

    for phrase in current_config['spam_config']['spam_phrases']:
        expires = datetime.fromisoformat(phrase['expires'])
        if expires < datetime.now():
            current_config['spam_config']['spam_phrases'].remove(phrase)

    for word in current_config['spam_config']['spam_words']:
        expires = datetime.fromisoformat(word['expires'])
        if expires < datetime.now():
            current_config['spam_config']['spam_words'].remove(word)

    await save_spam_config(current_config)

    return current_config


async def discord_get_spam_list() -> str:
    spam_config = await get_spam_list()

    def format_date(date_str: str) -> str:
        try:
            dt = datetime.fromisoformat(date_str)
            now = datetime.now()
            hours_until = round((dt - now).total_seconds() / 3600)

            if hours_until >= 999:
                return "forever"
            else:
                return f"{hours_until} hours remaining"
        except ValueError:
            return date_str

    if spam_config:
        return "**__PHRASES:__**\n" + "\n".join([
            f"'_{phrase['spam']}_'  -  {format_date(phrase['expires'])}"
            for phrase in spam_config['spam_config']['spam_phrases']
        ]) + "\n\n**__WORDS:__**\n" + "\n".join([
            f"'_{word['spam']}_'  -  {format_date(word['expires'])}"
            for word in spam_config['spam_config']['spam_words']
        ])
    else:
        return "No spam config found."


async def add_spam_word(word: str, expires: Literal['3hr', '24hr', '48hr', '1wk', 'forever'], action: Literal['timeout', 'kick']) -> None:
    spam_config = await open_spam_config()

    for spam_word in spam_config['spam_config']['spam_words']:
        if spam_word['spam'] == word.lower():
            raise ValueError(f"The word '{word}' is already in the spam word list.")

    spam_config['spam_config']['spam_words'].append({"spam": word.lower(), "expires": expiration_time(expires), "action": action})
    await save_spam_config(spam_config)


async def add_spam_phrase(phrase: str, expires: Literal['3hr', '24hr', '48hr', '1wk', 'forever'], action: Literal['timeout', 'kick']) -> None:
    spam_config = await open_spam_config()

    for spam_phrase in spam_config['spam_config']['spam_phrases']:
        if spam_phrase['spam'] == phrase.lower():
            raise ValueError(f"The phrase '{phrase}' is already in the spam phrase list.")


    spam_config['spam_config']['spam_phrases'].append({"spam": phrase.lower(), "expires": expiration_time(expires), "action": action})
    await save_spam_config(spam_config)


def expiration_time(active_hours: str) -> str:
    current_time = datetime.now()
    if active_hours == '3hr':
        return (current_time + timedelta(hours=3)).isoformat()
    elif active_hours == '24hr':
        return (current_time + timedelta(hours=24)).isoformat()
    elif active_hours == '48hr':
        return (current_time + timedelta(hours=48)).isoformat()
    elif active_hours == '1wk':
        return (current_time + timedelta(weeks=1)).isoformat()
    elif active_hours == 'forever':
        return (current_time + timedelta(weeks=52*999)).isoformat()
    else:
        raise ValueError(f"Invalid active_hours value: {active_hours}")


async def remove_spam_word(word: str) -> None:
    spam_config = await open_spam_config()

    word_found = False
    new_spam_words = []

    for spam_word in spam_config['spam_config']['spam_words']:
        if spam_word["spam"] == word:
            word_found = True
        else:
            new_spam_words.append(spam_word)

    if not word_found:
        raise ValueError(f"Word '{word}' not found in timeout words.")

    spam_config['spam_config']['spam_words'] = new_spam_words
    
    await save_spam_config(spam_config)


async def remove_spam_phrase(phrase: str) -> None:
    spam_config = await open_spam_config()

    phrase_found = False
    new_spam_phrases = []

    for spam_phrase in spam_config['spam_config']['spam_phrases']:
        if spam_phrase["spam"] == phrase:
            phrase_found = True
        else:
            new_spam_phrases.append(spam_phrase)

    if not phrase_found:
        raise ValueError(f"Phrase '{phrase}' not found in timeout phrases.")

    spam_config['spam_config']['spam_phrases'] = new_spam_phrases
    
    await save_spam_config(spam_config)