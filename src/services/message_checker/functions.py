import services.message_checker.spam.functions as spam
import services.message_checker.faq.functions as faq
import time
import math

import services.shared.functions as shared
from config import log
from datetime import datetime, timedelta

from typing import Literal, List

async def check_msg(bot, discord, message) -> None:
  """
  Service that checks discord messages for spam, restricted words, and then possible faq questions.
  If the message is spam, it will delete the message and kick.
  If the message is a restricted word, it will delete the message and timeout.
  If the message is a faq question, it will reply with the answer to the user.


  Args:
      bot (_type_): _description_
      discord (_type_): _description_
      message (_type_): _description_
  """

  # get msg ready for checking
  clean_msg = clean_discord_message(message.content)
  clean_msg_words = clean_msg.split(' ')

  spam_result = await spam.check_for_spam(clean_msg, clean_msg_words)
  if spam_result:
    await handle_spam(message, discord, spam_result)
    return

  faq_result: dict = await faq.check_for_faq(clean_msg, clean_msg_words)

  if 'matched_links' in faq_result:
    await handle_faq(message, discord, faq_result)



async def handle_spam(message, discord, spam_dict) -> None:
  """
  Service that handles spam.
  """
  # Log spam caught
  log_message: str = (
      "⚠️ **__SPAM CAUGHT__**"
      f"\n> - <@{message.author.id}>"
      f"\n> - SPAM ACTION: {spam_dict['action']}"
      f"\n> - SPAM WORD/PHRASE: '_{spam_dict['spam']}_'"
      f"\n> - Message: {message.content}"
  )

  log.info(log_message)
  await shared.log_event(
      discord=discord, member=message.author, result_msg=log_message
  )

  # Delete the message
  await message.delete()

  # # DM User
  await dm_user(message, spam_dict)

  # # Kick or timeout user
  if spam_dict['action'] == 'kick':
    await message.author.kick()

  elif spam_dict['action'] == 'timeout':
    await message.author.timeout(
      timedelta(minutes=15),
        reason=f"Timeout word caught: {spam_dict['spam']}"
    )

  
  
async def handle_faq(message, discord, faq_result: dict) -> None:
  """
  Service that handles faq.
  """
  highest_link: dict = faq_result['highest_link']
  matched_links: List[dict] = faq_result['matched_links']

  # Log spam caught
  debug_results = "\n".join(
      [
       f"> - Link: {link['link']}"
       f"\n> - Link Keywords: {link['keywords']}"
       f"\n> - Required Keywords: {link['required_keywords']}"
       f"\n> - Keywords matched: {link['message_keywords']}"
       f"\n> - Cooldown remaining: {math.ceil((link['cooldown'] - time.time()) / 60)} minutes"
       f"\n> - Score: {link['score']}\n" 
       for link in matched_links
       ]
  )

  if highest_link['can_post']:
    await message.reply(f"-# {highest_link['link_message']} \n\n-# {highest_link['link']}",
    suppress_embeds=True)

    # reply to message 
    # -# like this
    # pass

  log_message: str = (
      "👷🏼 **__BETA FAQ QUESTION FOUND__**"
      f"\n> - <@{message.author.id}>"
      f"\n> - Message: {message.content}"
      f"\n> - Keywords in message: {highest_link['message_keywords']}"

      f"\n\n> - **__RESULT__**:"
      f"\n> - Link: {highest_link['link']}"
      f"\n> - Posting: {'Yes' if highest_link['can_post'] == True else 'No'}"
      f"\n> - Score: {highest_link['score']}"
      
      f"\n\n> - **__DEBUG RESULTS__**:\n{debug_results}"
  )

  log.info(log_message)
  await shared.log_event(
      discord=discord, member=message.author, result_msg=log_message
  )







async def author_has_godmode(bot, message) -> bool:
  """
  Service that checks if the message author is a mod and if it is, it will ignore the message.
  """

  # Check message author is not mod
  mod_names: List[str] = []
  mod_ids: List[int] = []

  if message.guild is None:
    return False

  mod_info: tuple[list[str], list[int]] | None = await shared.get_mod_info(
      bot=bot, guild_id=message.guild.id
  )

  if mod_info is not None:
      mod_names, mod_ids = mod_info

  return message.author.id in mod_ids



async def dm_user(message, spam_dict) -> None:
  """
  Service that DMs the user with the message.
  """
  try:
      await message.author.send(f"**__You have received a {spam_dict['action']} in Good Gains__** \nYou posted a message that is not allowed. We throttle & remove certain phrases/words to keep the server clean. If you were kicked you can join server again. If you were given a timeout you will be able to chat shortly. No need to apologize and thanks for keeping the server clean!\n\n**__Reason__**: \nMessage contained these phrases/words: '_{spam_dict['spam']}_'")
  except:
      pass


def clean_discord_message(message: str) -> str:
    mapping = {
        '@': 'a',
        '0': 'o',
        '3': 'e',
        '1': 'i',
        '5': 's',
        '7': 't',
    }
    return ''.join(mapping.get(char.lower(), char.lower()) for char in message)