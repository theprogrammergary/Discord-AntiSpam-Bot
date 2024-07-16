"""
Service that checks messages for timeout words
"""
import re
from datetime import datetime, timedelta
import json

from fuzzywuzzy import fuzz
from typing import List, Literal
from pathlib import Path

import services.shared.functions as shared
from config import log

CONFIG_PATH = Path(__file__).parent / "config.json"


async def check_msg(bot, discord, message) -> None:
    """
    Service that is called to check messages for timeout words.
    (Ignores bots and moderators)

    Args:
        bot (Bot): _description_
        discord (discord): _description_
        message (discord.Message): _description_
    """

    msg_content: str = message.content
    member: discord.Member = message.author

    if member.bot:
        return

    mod_names: List[str] = []
    mod_ids: List[int] = []

    mod_info: tuple[list[str], list[int]] | None = await shared.get_mod_info(
        bot=bot, guild_id=member.guild.id
    )

    if mod_info is not None:
        mod_names, mod_ids = mod_info

    if message.author.id in mod_ids:
        return
    

    timeout_word = await found_timeout_word(msg=msg_content)
    if timeout_word is not None:

        # Log spam caught
        log_message: str = (
            "⚠️ **__TIMEOUT WORD CAUGHT__**"
            f"\n> - <@{message.author.id}>"
            f"\n> - Content: {msg_content}"
        )

        log.info(log_message)
        await shared.log_event(
            discord=discord, member=message.author, result_msg=log_message
        )


        # Delete the message
        await message.delete()


        # Timeout the user
        await member.timeout(
            timedelta(minutes=15),
            reason=f"Timeout word caught: {timeout_word['word']}"
        )

        # DM the user
        try:
            await message.author.send(f"**__You have been timed out in the Good Gains discord__** \n\n**__Reason__**: \n{timeout_word['dm_message']}")
        except:
            pass




async def found_timeout_word(msg) -> dict | None:
    msg_lower = msg.lower()
    msg_lower_wordlist = msg_lower.split(' ')
    timeout_words = await get_words()
    
    for timeout_word in timeout_words:
        if timeout_word["word"] in msg_lower:
            return timeout_word

        for word in msg_lower_wordlist:
            if (get_word_similarity(word=word, timeout_word=timeout_word["word"]) > 85):
                return timeout_word


    return None


def get_word_similarity(word: str, timeout_word: str) -> float:
    """
    Get the similarity between the message and the timeout word.
    """

    mapped_word = map_special_chars(word=word)
    return  fuzz.ratio(timeout_word, mapped_word)



def map_special_chars(word: str) -> str:
    mapping = {
        '@': 'a',
        '0': 'o',
        '3': 'e',
        '1': 'i',
        '5': 's',
        '7': 't',
        # Add more mappings as needed
    }
    return ''.join(mapping.get(char, char) for char in word)



async def add(word: str,
                   active_hours: Literal['3hr', '24hr', '48hr', '1wk', 'forever'],
                   dm_message: str) -> None:
    """
    Add a timeout word.
    """

    config_data = await load_config()

    for timeout_word in config_data["timeout_words"]:
        if timeout_word["word"] == word:
            raise ValueError(f"The word '{word}' is already in the timeout list.")

    from datetime import datetime, timedelta

    def calculate_active_until(active_hours: str) -> str:
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

    config_data["timeout_words"].append({
        "word": word,
        "active_until": calculate_active_until(active_hours=active_hours),
        "dm_message": dm_message
    })

    await save_config(config_data)



async def load_config() -> dict:
    """
    Open the config file.
    """

    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {"timeout_words": []}
    else:
        return {"timeout_words": []}
    


async def save_config(config_data: dict) -> None:
    """
    Save the config to the file.
    """

    with open(CONFIG_PATH, "w") as file:
        json.dump(config_data, file, indent=4)
    

async def get_words() -> List[dict]:
    """
    Get all timeout words.
    """

    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r") as file:
                config_data = json.load(file)
                timeout_words = config_data.get("timeout_words", [])

    
                active_timeout_words = await check_timeword_expiration(timeout_words)

                return active_timeout_words
        except json.JSONDecodeError:
            return []
    else:
        return []
    

async def check_timeword_expiration(timeout_words: List[dict]) -> List[dict]:
    """
    Check if any timeout words have expired.
    """

    current_time = datetime.now()
    active_timeout_words = [
        word for word in timeout_words
        if datetime.fromisoformat(word["active_until"]) > current_time
    ]

    # Save the updated config if any words were removed
    if len(active_timeout_words) != len(timeout_words):
        config_data = await load_config()
        config_data["timeout_words"] = active_timeout_words
        await save_config(config_data)

    return active_timeout_words


async def list_timeout_words() -> str:
    """
    List all timeout words.
    """

    timeout_words = await get_words()

    if timeout_words:
        return "**__CURRENT TIMEOUT WORDS:__**\n\n" + "\n\n".join([
            f"**WORD:** {word['word']}\n"
            f"**ACTIVE UNTIL:** {word['active_until']}\n"
            f"**DM MESSAGE:** {word['dm_message']}"
            for word in timeout_words
        ])
    else:
        return "No timeout words found."



async def remove(word: str) -> None:
    """
    Remove a timeout word or reset the config if the word is "all".
    """

    config_data = await load_config()

    if word == "all":
        config_data["timeout_words"] = []
    else:
        timeout_words = config_data.get("timeout_words", [])

        word_found = False
        new_timeout_words = []

        for w in timeout_words:
            if w["word"] == word:
                word_found = True
            else:
                new_timeout_words.append(w)

        if not word_found:
            raise ValueError(f"Word '{word}' not found in timeout words.")

        config_data["timeout_words"] = new_timeout_words
    
    await save_config(config_data)