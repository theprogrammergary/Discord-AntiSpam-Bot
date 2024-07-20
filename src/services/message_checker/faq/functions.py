import json

import time
from typing import List
from pathlib import Path
from thefuzz import fuzz, process

from config import log

FAQ_CONFIG_PATH = Path(__file__).parent / "faq.json"


async def check_for_faq(msg: str, msg_words: List[str]) -> dict:

  faq_config = await open_faq_config()
  faq_words = list(set(
    word
    for link in faq_config["faq_config"]["links"]
    for keyword in link["keywords"] + link["required_keywords"]
    for word in keyword.split()
  ))

  found_words: dict = {"question_words": [], "faq_words": []}

  for word in msg_words:
    cleaned_word = word.rstrip('?')

    if cleaned_word in faq_words and cleaned_word not in found_words["faq_words"]:
      found_words["faq_words"].append(cleaned_word)

    if cleaned_word in faq_config["faq_config"]["question_words"] or '?' in word:
      found_words["question_words"].append(word)


  if len(found_words["faq_words"]) > 1:
    return await map_keywords_to_links(found_words["faq_words"], faq_config)

  return {}


async def open_faq_config() -> dict:
    if FAQ_CONFIG_PATH.exists():
        try:
            with open(FAQ_CONFIG_PATH, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {"faq_config": {"question_words": [], "faq_words": [], "links": []}}
    else:
        return {"faq_config": {"question_words": [], "faq_words": [], "links": []}}
    

async def save_faq_config(data: dict) -> None:
    with open(FAQ_CONFIG_PATH, "w") as file:
        json.dump(data, file, indent=4)


async def map_keywords_to_links(keywords: List[str], faq_config: dict) -> dict:

  matched_links = []
  user_keywords = ' '.join(keywords)
  has_required_keywords = False

  for link in faq_config["faq_config"]["links"]:
    link_keywords = [' '.join(link["keywords"] + link["required_keywords"])]

    match, score, *_ = process.extractOne(user_keywords, link_keywords)

    # TODO: needs to be at least 90% match
    if match and score > 50: 

      for required_keyword in link["required_keywords"]:
        if required_keyword not in keywords:
          has_required_keywords = False
          break
        else:
          has_required_keywords = True
    

      if has_required_keywords:
        matched_links.append({
        "link": link["link"],
        "link_message": link["message"],
        "required_keywords": link["required_keywords"],
        "keywords": link["keywords"],
        "message_keywords": user_keywords,
        "score": score,
        "cooldown": link["cooldown"],
      })


  if len(matched_links) == 0:
    return {}

  highest_link = max(matched_links, key=lambda x: x['score'])
  
  if time.time() > highest_link["cooldown"]:
    highest_link["can_post"] = True
    
    for link in faq_config["faq_config"]["links"]:
        if link["link"] == highest_link["link"]:
            link["cooldown"] = time.time() + 300
            break
        
    await save_faq_config(faq_config)
  else:
    highest_link["can_post"] = False

  matched_links.sort(key=lambda x: x['score'], reverse=True)

  return {
    "matched_links": matched_links,
    "highest_link": highest_link
  }



