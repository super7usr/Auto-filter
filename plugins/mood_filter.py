import re
import random
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from Script import script
from database.ia_filterdb import get_mood_results
from info import ADMINS, MAX_BTN
from utils import temp, get_size, get_settings
import math

MOOD_EMOJI_MAP = {
    "happy": "😊",
    "sad": "😢",
    "scary": "😱",
    "laugh": "🤣",
    "romantic": "❤️",
    "action": "🔥",
    "thought_provoking": "🧠",
    "fantasy": "🦸",
    "family": "👪",
    "artistic": "🎭",
}

MOOD_KEYWORDS = {
    "happy": ["feel-good", "uplifting", "happy", "positive", "heartwarming", "joy", "inspiring"],
    "sad": ["emotional", "drama", "tearjerker", "tragedy", "sad", "moving", "melancholy"],
    "scary": ["horror", "thriller", "scary", "suspense", "spooky", "terrifying", "creepy"],
    "laugh": ["comedy", "funny", "hilarious", "laugh", "humor", "parody", "slapstick"],
    "romantic": ["romance", "love", "romantic", "relationship", "passion", "dating", "wedding"],
    "action": ["action", "adventure", "fight", "chase", "explosion", "thrill", "stunt"],
    "thought_provoking": ["mind-bending", "philosophical", "thought", "psychology", "cerebral", "deep"],
    "fantasy": ["fantasy", "superhero", "magic", "sci-fi", "supernatural", "mythical", "powers"],
    "family": ["family", "kids", "children", "animated", "wholesome", "disney", "pixar"],
    "artistic": ["indie", "art", "cinema", "experimental", "festival", "acclaimed", "masterpiece"]
}

async def detect_mood_from_text(text):
    """Detect the most likely mood based on the description text"""
    
    # Make text lowercase for better matching
    text = text.lower()
    
    # Count matches for each mood category
    mood_scores = {}
    for mood, keywords in MOOD_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        mood_scores[mood] = score
    
    # Get the mood with the highest score
    max_mood = max(mood_scores.items(), key=lambda x: x[1])
    if max_mood[1] > 0:
        return max_mood[0]
    
    # If no keywords match, return a random mood
    return random.choice(list(MOOD_KEYWORDS.keys()))

async def get_mood_keyboard():
    """Generate keyboard with mood emojis"""
    
    btn = []
    row = []
    
    # Create rows with 2 buttons each
    for mood, emoji in MOOD_EMOJI_MAP.items():
        mood_readable = mood.replace('_', ' ').title()
        row.append(InlineKeyboardButton(f"{emoji} {mood_readable}", callback_data=f"mood_{mood}"))
        
        if len(row) == 2:
            btn.append(row)
            row = []
            
    # Add any remaining items
    if row:
        btn.append(row)
        
    # Add back button
    btn.append([InlineKeyboardButton("🔙 Back to Search", callback_data="back_to_search")])
    
    return InlineKeyboardMarkup(btn)

async def show_mood_options(client, query):
    """Show the mood selection keyboard"""
    
    await query.message.edit_text(
        text=script.MOOD_SEARCH_TXT,
        reply_markup=await get_mood_keyboard(),
        disable_web_page_preview=True
    )

async def handle_mood_selection(client, query):
    """Handle the mood selection and show relevant content"""
    
    # Extract mood from callback data
    mood = query.data.split("_")[1]
    
    # Get primary and additional keywords for the selected mood
    primary_keyword = MOOD_KEYWORDS[mood][0]
    additional_keywords = MOOD_KEYWORDS[mood][1:]
    
    # Search for content matching the mood
    files, offset, total_results = await get_mood_results(
        primary_keyword=primary_keyword, 
        additional_keywords=additional_keywords
    )
    
    if not files:
        await query.answer("No content found for this mood. Try another mood!", show_alert=True)
        return
    
    settings = await get_settings(query.message.chat.id)
    
    # Format message and buttons
    btn = []
    msg_text = f"<b>🎭 {MOOD_EMOJI_MAP[mood]} {mood.replace('_', ' ').title()} Content ({total_results} results)</b>\n\n"
    
    if settings['links']:
        # Link format
        for file_num, file in enumerate(files, start=1):
            msg_text += f"""<b>{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{file.file_id}>[{get_size(file.file_size)}] {file.file_name}</a></b>\n"""
    else:
        # Button format
        btn = [
            [InlineKeyboardButton(
                text=f"{MOOD_EMOJI_MAP[mood]} {get_size(file.file_size)} {file.file_name}", 
                callback_data=f'file#{file.file_id}'
            )]
            for file in files
        ]
    
    # Add navigation buttons
    if offset != "" and offset != 0:
        btn.append(
            [
                InlineKeyboardButton(
                    text=f"1/{math.ceil(int(total_results) / MAX_BTN)}", 
                    callback_data="pages"
                ),
                InlineKeyboardButton(
                    text="Next ⏩", 
                    callback_data=f"next_mood_{mood}_{offset}"
                )
            ]
        )
    
    # Add back to moods button
    btn.append([InlineKeyboardButton("🔙 Back to Moods", callback_data="show_moods")])
    
    # Add close button
    btn.append([InlineKeyboardButton("❌ Close ❌", callback_data="close_data")])
    
    # Send response
    await query.message.edit_text(
        text=msg_text,
        reply_markup=InlineKeyboardMarkup(btn),
        disable_web_page_preview=True
    )

async def back_to_search(client, query):
    """Return to the main search interface"""
    
    # This would typically return to the original search results
    # But since we don't store the original search, we'll just show a message
    
    await query.message.edit_text(
        text="<b>🔍 Search for movies or series to get started!</b>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔎 Search Inline", switch_inline_query_current_chat='')],
            [InlineKeyboardButton("❌ Close ❌", callback_data="close_data")]
        ])
    )