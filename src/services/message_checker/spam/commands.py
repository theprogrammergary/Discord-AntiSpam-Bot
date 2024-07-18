import services.message_checker.spam.functions as spam
from config import log

import discord
from typing import Literal

async def handle_spam_filter_delete(interaction: discord.Interaction, type: Literal['word', 'phrase'], spam_string: str) -> None:
    """
    Handle spam filter delete
    """ 

    await interaction.response.send_message(content=f"Deleting spam {type} '{spam_string}'...", ephemeral=True)

    try :
        if type == "word":
            if len(spam_string.split()) > 1:
                raise ValueError("deletion of spam word failed: only one word is allowed for this type")
            await spam.remove_spam_word(word=spam_string)
            await interaction.edit_original_response(content=f"spam {type} '{spam_string}' removed")
        else:
            if len(spam_string.split()) <= 1:
                raise ValueError("deletion of spam phrase failed: needs to be multiple words")
            await spam.remove_spam_phrase(phrase=spam_string)
            await interaction.edit_original_response(content=f"spam {type} '{spam_string}' removed")


    except ValueError as e:
        log.error(msg=f"ValueError in spam_filter_delete command - {e}")
        await interaction.edit_original_response(content=f"Error: {str(e)}")
    except Exception as e:
        log.error(msg=f"Error in spam_filter_delete command - {e}")
        await interaction.edit_original_response(content="Error: Unable to remove spam filter.")


async def handle_spam_filter_create(interaction: discord.Interaction,
                            type: Literal['word', 'phrase'],
                            spam_string: str,
                            active_hours: Literal['3hr', '24hr', '48hr', '1wk', 'forever'],
                            action: Literal['timeout', 'kick']) -> None:
    """
    Add a spam filter to the spam config.
    """

    await interaction.response.send_message(content=f"Adding {type} to spam config...", ephemeral=True, suppress_embeds=True)


    try :
        if type == "word":
            if len(spam_string.split()) > 1:
                raise ValueError("creation of spam word failed: only one word is allowed for this type")
            await spam.add_spam_word(word=spam_string, expires=active_hours, action=action)
        else:
            if len(spam_string.split()) <= 1:
                raise ValueError("creation of spam phrase failed: needs to be multiple words")
            await spam.add_spam_phrase(phrase=spam_string, expires=active_hours, action=action)


        await interaction.edit_original_response(content=f"spam {type} '{spam_string}' created for {active_hours}")


    except ValueError as e:
        log.error(msg=f"ValueError in spam_filter_create command - {e}")
        await interaction.edit_original_response(content=f"Error: {str(e)}")
    except Exception as e:
        log.error(msg=f"Error in spam_filter_create command - {e}")
        await interaction.edit_original_response(content="Error: Unable to add spam filter.")


async def handle_spam_filter_list(interaction: discord.Interaction) -> None:
    """
    List spam config.
    """
    await interaction.response.send_message(content=f"Getting spam config...", ephemeral=True, suppress_embeds=True)


    try :
        response: str = await spam.discord_get_spam_list()
        await interaction.edit_original_response(content=response)
    except Exception as e:
        log.error(msg=f"Error in getting spam filter config command - {e}")
        await interaction.edit_original_response(content="Unable to list spam config.")
