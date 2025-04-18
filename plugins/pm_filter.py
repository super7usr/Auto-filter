import asyncio
import re
from time import time as time_now
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
from datetime import datetime, timedelta
from info import SECOND_DATABASE_URL, TIME_ZONE, ADMINS, URL, MAX_BTN, BIN_CHANNEL, IS_STREAM, DELETE_TIME, FILMS_LINK, LOG_CHANNEL, SUPPORT_GROUP, SUPPORT_LINK, UPDATES_LINK, LANGUAGES, QUALITY
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from utils import get_size, is_subscribed, is_check_admin, get_wish, get_shortlink, get_readable_time, get_poster, temp, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import Media, get_search_results, get_file_details, delete_files
from plugins.smart_preview import smart_analyzer
from plugins.preview_wizard import preview_wizard

BUTTONS = {}
CAP = {}

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_search(client, message):
    if message.text.startswith("/"):
        return

    s = await message.reply("<b><i>⚠️ Processing your request...</i></b>")
    settings = await get_settings(message.chat.id)
    search = message.text.strip()
    files, offset, total_results = await get_search_results(search)
    
    if not files:
        search_query = search.replace(" ", "+")
        web_search_url = f"{URL}movie?q={search_query}"
        btn = [[
            InlineKeyboardButton("⚠️ Instructions", callback_data='instructions'),
            InlineKeyboardButton("🔎 Google Search", url=web_search_url)
        ],[
            InlineKeyboardButton("🎬 IMDB Search", url=f"https://www.imdb.com/find?q={search_query}")
        ]]
        
        if settings["spell_check"]:
            await advantage_spell_chok(message, s)
        else:
            n = await s.edit_text(
                text=f"👋 Hello {message.from_user.mention},\n\nI couldn't find <b>'{search}'</b> in my database. 😔",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await client.send_message(LOG_CHANNEL, f"#No_Result\n\nRequester: {message.from_user.mention}\nContent: {search}")
            await asyncio.sleep(60)
            await n.delete()
            try:
                await message.delete()
            except:
                pass
        return
            
    await auto_filter(client, message, s)

    if not files:
        if settings["spell_check"]:
            s = await message.reply(f"<b><i>⚠️ `{message.text}` searching...</i></b>")
            await advantage_spell_chok(message, s)
        else:
            # No files and no spell check, send web search option
            search_query = message.text.replace(" ", "+")
            web_search_url = f"{URL}movie?q={search_query}"
            btn = [[
                InlineKeyboardButton("🌐 Web Search", url=web_search_url)
            ]]
            await message.reply_text(
                f"<b>No results found for:</b> <code>{message.text}</code>\n\n<b>Try searching on our web server:</b>",
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.HTML
            )
        return

    key = f"{message.chat.id}-{message.id}"
    temp.FILES[key] = files

    # Always use web-like display for search results in private chat
    from info import URL
    search_query = message.text.replace(" ", "+")

    # Create a web-like display with server links for each file
    files_link = ''

    # Create buttons for additional options
    btn = []

    # First, check if we need to use shortlinks
    if settings['shortlink']:
        # Create a web-style listing with shortlinks
        for file_num, file in enumerate(files, start=1):
            file_size = get_size(file.file_size)
            file_name = file.file_name
            # Use the direct file ID format for telegram link
            telegram_link = f"https://t.me/{temp.U_NAME}?start=file_1_{file.file_id}" 

            # Generate shortlink
            try:
                short_link = await get_shortlink(settings['url'], settings['api'], telegram_link)
                files_link += f"""<b>\n\n{file_num}. <a href="{short_link}">[{file_size}] {file_name}</a></b>"""

                # Web links will be handled centrally now, not per file
            except Exception as e:
                print(f"Error generating shortlink: {e}")
                # Fallback to regular link
                files_link += f"""<b>\n\n{file_num}. <a href="{telegram_link}">[{file_size}] {file_name}</a></b>"""
    else:
        # Create a web-style listing without shortlinks
        for file_num, file in enumerate(files, start=1):
            file_size = get_size(file.file_size)
            file_name = file.file_name
            # Use the direct file ID format for telegram link
            telegram_link = f"https://t.me/{temp.U_NAME}?start=file_1_{file.file_id}"
            files_link += f"""<b>\n\n{file_num}. <a href="{telegram_link}">[{file_size}] {file_name}</a></b>"""

            # Web links will be handled centrally now, not per file

    # Add mood search button
    btn.append([
        InlineKeyboardButton("🎭 Mood Search", callback_data="show_moods"),
        InlineKeyboardButton("🎬 IMDB", url=f"https://www.imdb.com/find?q={search_query}")
    ])

    # Add web search button
    if add_web_search:
        web_search_url = f"{URL}movie?q={search_query}"
        btn.append([
            InlineKeyboardButton("🌐 Web Search", url=web_search_url)
        ])

    if offset != "":
        try:
            total_pages = math.ceil(int(total_results)/10)
            current_page = math.ceil(int(offset)/10) + 1
            btn.append(
                [InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="pages"),
                 InlineKeyboardButton(text="NEXT ⏩", callback_data=f"next_{message.from_user.id}_{key}_{offset}")]
            )
        except:
            pass

    # Combine file links with web links for a comprehensive view
    msg_text = f"<b>📥 Found {total_results} results for:</b> <code>{message.text}</code>"
    msg_text += files_link

    # Add a single web link instead of multiple ones
    if files:
        file = files[0]  # Use the first file for the watch online link
        file_web_url = f"{URL}watch/{file.file_id}/{file.file_name.replace(' ', '_')}"
        msg_text += f"\n\n<b>🌐 <a href=\"{file_web_url}\">Watch Online</a></b>"

    btn.append([InlineKeyboardButton("❌ Close ❌", callback_data="close_data")])

    await message.reply_text(msg_text, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.group & filters.text & filters.incoming)
async def group_search(client, message):
    chat_id = message.chat.id
    settings = await get_settings(chat_id)
    user_id = message.from_user.id if message and message.from_user else 0
    if settings["auto_filter"]:
        if not user_id:
            await message.reply("I'm not working for anonymous admin!")
            return
        if message.chat.id == SUPPORT_GROUP:
            files, offset, total = await get_search_results(message.text)
            if files:
                btn = [[
                    InlineKeyboardButton("Here", url=FILMS_LINK)
                ]]
                await message.reply_text(f'Total {total} results found in this group', reply_markup=InlineKeyboardMarkup(btn))
            return

        if message.text.startswith("/"):
            return

        elif '@admin' in message.text.lower() or '@admins' in message.text.lower():
            if await is_check_admin(client, message.chat.id, message.from_user.id):
                return
            admins = []
            async for member in client.get_chat_members(chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                if not member.user.is_bot:
                    admins.append(member.user.id)
                    if member.status == enums.ChatMemberStatus.OWNER:
                        if message.reply_to_message:
                            try:
                                sent_msg = await message.reply_to_message.forward(member.user.id)
                                await sent_msg.reply_text(f"#Attention\n★ User: {message.from_user.mention}\n★ Group: {message.chat.title}\n\n★ <a href={message.reply_to_message.link}>Go to message</a>", disable_web_page_preview=True)
                            except:
                                pass
                        else:
                            try:
                                sent_msg = await message.forward(member.user.id)
                                await sent_msg.reply_text(f"#Attention\n★ User: {message.from_user.mention}\n★ Group: {message.chat.title}\n\n★ <a href={message.link}>Go to message</a>", disable_web_page_preview=True)
                            except:
                                pass
            hidden_mentions = (f'[\u2064](tg://user?id={user_id})' for user_id in admins)
            await message.reply_text('Report sent!' + ''.join(hidden_mentions))
            return

        elif re.findall(r'https?://\S+|www\.\S+|t\.me/\S+|@\w+', message.text):
            if await is_check_admin(client, message.chat.id, message.from_user.id):
                return
            await message.delete()
            return await message.reply('Links not allowed here!')

        elif '#request' in message.text.lower():
            if message.from_user.id in ADMINS:
                return
            await client.send_message(LOG_CHANNEL, f"#Request\n★ User: {message.from_user.mention}\n★ Group: {message.chat.title}\n\n★ Message: {re.sub(r'#request', '', message.text.lower())}")
            await message.reply_text("Request sent!")
            return  
        else:
            s = await message.reply(f"<b><i>⚠️ `{message.text}` searching...</i></b>")
            await auto_filter(client, message, s)
    else:
        k = await message.reply_text('Auto Filter Off! ❌')
        await asyncio.sleep(5)
        await k.delete()
        try:
            await message.delete()
        except:
            pass

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search:
        await query.answer(f"Hello {query.from_user.first_name},\nSend New Request Again!", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    temp.FILES[key] = files
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b>⚠️ This message will be auto deleted after <code>{get_readable_time(DELETE_TIME)}</code> to avoid copyright issues</b>" if settings["auto_delete"] else ''
    files_link = ''

    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=offset+1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_1_{file.file_id}>[{get_size(file.file_size)}] {file.file_name}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"📂 {get_size(file.file_size)} {file.file_name}", callback_data=f'file#{file.file_id}')
        ]
            for file in files
        ]
    if settings['shortlink']:
        btn.insert(0,
            [InlineKeyboardButton("📰 Languages", callback_data=f"languages#{key}#{req}#{offset}"),
            InlineKeyboardButton("🔍 Quality", callback_data=f"quality#{key}#{req}#{offset}")]
        )
    else:
        btn.insert(0,
            [InlineKeyboardButton("📰 Languages", callback_data=f"languages#{key}#{req}#{offset}"),
            InlineKeyboardButton("🔍 Quality", callback_data=f"quality#{key}#{req}#{offset}")]
        )
        

    if 0 < offset <= MAX_BTN:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - MAX_BTN

    # Add Web Search and IMDb buttons
    web_search_url = f"{URL}movie?q={search}"
    search_query = search.replace(" ", "+")
    btn.append([
        InlineKeyboardButton("🌐 Web Search", url=web_search_url),
        InlineKeyboardButton("🎬 IMDB", url=f"https://www.imdb.com/find?q={search_query}")
    ])
    
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("« Back", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("Next »", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("« Back", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
                InlineKeyboardButton("Next »", callback_data=f"next_{req}_{key}_{n_offset}")
            ]
        )
    await query.message.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^languages"))
async def languages_(client: Client, query: CallbackQuery):
    _, key, req, offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)
    btn = [
        [InlineKeyboardButton(text=LANGUAGES[i].title(), callback_data=f"lang_search#{LANGUAGES[i]}#{key}#{offset}#{req}"),
         InlineKeyboardButton(text=LANGUAGES[i+1].title(), callback_data=f"lang_search#{LANGUAGES[i+1]}#{key}#{offset}#{req}")]
        for i in range(0, len(LANGUAGES)-1, 2)
    ]
    btn.append([InlineKeyboardButton(text="🔙 Back to Main Page", callback_data=f"next_{req}_{key}_{offset}")])  
    await query.message.edit_text("<b>🌐 Select Your Preferred Language</b>", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"^quality"))
async def quality(client: Client, query: CallbackQuery):
    _, key, req, offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)
    btn = [
        [InlineKeyboardButton(text=QUALITY[i].title(), callback_data=f"qual_search#{QUALITY[i]}#{key}#{offset}#{req}"),
         InlineKeyboardButton(text=QUALITY[i+1].title(), callback_data=f"qual_search#{QUALITY[i+1]}#{key}#{offset}#{req}")]
        for i in range(0, len(QUALITY)-1, 2)
    ]
    btn.append([InlineKeyboardButton(text="🔙 Back to Main Page", callback_data=f"next_{req}_{key}_{offset}")])  
    await query.message.edit_text("<b>🎞️ Select Your Preferred Quality</b>", disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex(r"^lang_search"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)

    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search:
        await query.answer(f"Hello {query.from_user.first_name},\nSend New Request Again!", show_alert=True)
        return 

    files, l_offset, total_results = await get_search_results(search, lang=lang)
    if not files:
        await query.answer(f"Sorry '{lang.title()}' language files not found 😕", show_alert=1)
        return
    temp.FILES[key] = files
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b>⚠️ This message will be auto deleted after <code>{get_readable_time(DELETE_TIME)}</code> to avoid copyright issues</b>" if settings["auto_delete"] else ''
    files_link = ''

    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_1_{file.file_id}>[{get_size(file.file_size)}] {file.file_name}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"📂 {get_size(file.file_size)} {file.file_name}", callback_data=f'file#{file.file_id}')
        ]
            for file in files
        ]
    if settings['shortlink']:
        btn.insert(1,
            [InlineKeyboardButton("🔍 Quality", callback_data=f"quality#{key}#{req}#{offset}")]
        )
    else:
        btn.insert(1,
            [InlineKeyboardButton("♻️ Send All ♻️", callback_data=f"send_all#{key}#{req}"),
            InlineKeyboardButton("🔍 Quality", callback_data=f"quality#{key}#{req}#{offset}")]
        )

    if l_offset != "":
        btn.append(
            [InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton(text="Next »", callback_data=f"lang_next#{req}#{key}#{lang}#{l_offset}#{offset}")]
        )
    btn.append([InlineKeyboardButton(text="⪻ Back to Main Page", callback_data=f"next_{req}_{key}_{offset}")])
    await query.message.edit_text(cap + files_link + del_msg, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^lang_next"))
async def lang_next_page(bot, query):
    ident, req, key, lang, l_offset, offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)
    try:
        l_offset = int(l_offset)
    except:
        l_offset = 0
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b>⚠️ This message will be auto deleted after <code>{get_readable_time(DELETE_TIME)}</code> to avoid copyright issues</b>" if settings["auto_delete"] else ''
    if not search:
        await query.answer(f"Hello {query.from_user.first_name},\nSend New Request Again!", show_alert=True)
        return
    files, n_offset, total = await get_search_results(search, offset=l_offset, lang=lang)
    if not files:
        return
    temp.FILES[key] = files
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0
    files_link = ''
    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=l_offset+1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{file.file_id}>[{get_size(file.file_size)}] {file.file_name}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"✨ {get_size(file.file_size)} ⚡️ {file.file_name}", callback_data=f'file#{file.file_id}')
        ]
            for file in files
        ]
    if settings['shortlink']:
        btn.insert(1,
            [InlineKeyboardButton("♻️ Send All ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}')),
            InlineKeyboardButton("🔍 Quality", callback_data=f"quality#{key}#{req}#{l_offset}")]
        )
    else:
        btn.insert(1,
            [InlineKeyboardButton("♻️ Send All ♻️", callback_data=f"send_all#{key}#{req}"),
            InlineKeyboardButton("🔍 Quality", callback_data=f"quality#{key}#{req}#{l_offset}")]
        )
    if 0 < l_offset <= MAX_BTN:
        b_offset = 0
    elif l_offset == 0:
        b_offset = None
    else:
        b_offset = l_offset - MAX_BTN
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("« Back", callback_data=f"lang_next#{req}#{key}#{lang}#{b_offset}#{offset}"),
             InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons")]
        )
    elif b_offset is None:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("Next »", callback_data=f"lang_next#{req}#{key}#{lang}#{n_offset}#{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton("« Back", callback_data=f"lang_next#{req}#{key}#{lang}#{b_offset}#{offset}"),
             InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("Next »", callback_data=f"lang_next#{req}#{key}#{lang}#{n_offset}#{offset}")]
        )
    btn.append([InlineKeyboardButton(text="⪻ Back to Main Page", callback_data=f"next_{req}_{key}_{offset}")])
    await query.message.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^qual_search"))
async def quality_search(client: Client, query: CallbackQuery):
    _, qual, key, offset, req = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search:
        await query.answer(f"Hello {query.from_user.first_name},\nSend New Request Again!", show_alert=True)
        return
    files, l_offset, total_results = await get_search_results(search, lang=qual)
    if not files:
        await query.answer(f"Sorry '{qual.title()}' language files not found 😕", show_alert=1)
        return
    temp.FILES[key] = files
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b>⚠️ This message will be auto deleted after <code>{get_readable_time(DELETE_TIME)}</code> to avoid copyright issues</b>" if settings["auto_delete"] else ''
    files_link = ''
    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{file.file_id}>[{get_size(file.file_size)}] {file.file_name}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"📂 {get_size(file.file_size)} {file.file_name}", callback_data=f'file#{file.file_id}')
        ]
            for file in files
        ]
    if settings['shortlink']:
        btn.insert(0,
            [InlineKeyboardButton("♻️ Send All ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}'))]
        )
    else:
        btn.insert(0,
            [InlineKeyboardButton("♻️ Send All ♻️", callback_data=f"send_all#{key}#{req}")]
        )  
    if l_offset != "":
        btn.append(
            [InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton(text="Next »", callback_data=f"qual_next#{req}#{key}#{qual}#{l_offset}#{offset}")]
        )
    btn.append([InlineKeyboardButton(text="⪻ Back to Main Page", callback_data=f"next_{req}_{key}_{offset}")])
    await query.message.edit_text(cap + files_link + del_msg, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^qual_next"))
async def quality_next_page(bot, query):
    ident, req, key, qual, l_offset, offset = query.data.split("#")
    if int(req) != query.from_user.id:
        return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)
    try:
        l_offset = int(l_offset)
    except:
        l_offset = 0
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b>⚠️ This message will be auto deleted after <code>{get_readable_time(DELETE_TIME)}</code> to avoid copyright issues</b>" if settings["auto_delete"] else ''
    if not search:
        await query.answer(f"Hello {query.from_user.first_name},\nSend New Request Again!", show_alert=True)
        return
    files, n_offset, total = await get_search_results(search, offset=l_offset, lang=qual)
    if not files:
        return
    temp.FILES[key] = files
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0
    files_link = ''
    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=l_offset+1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{file.file_id}>[{get_size(file.file_size)}] {file.file_name}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"✨ {get_size(file.file_size)} ⚡️ {file.file_name}", callback_data=f'file#{file.file_id}')
        ]
            for file in files
        ]
    if settings['shortlink']:
        btn.insert(0,
            [InlineKeyboardButton("♻️ Send All ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}'))]
        )
    else:
        btn.insert(0,
            [InlineKeyboardButton("♻️ Send All ♻️", callback_data=f"send_all#{key}#{req}")]
        )
    if 0 < l_offset <= MAX_BTN:
        b_offset = 0
    elif l_offset == 0:
        b_offset = None
    else:
        b_offset = l_offset - MAX_BTN
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("« Back", callback_data=f"qual_next#{req}#{key}#{qual}#{b_offset}#{offset}"),
             InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons")]
        )
    elif b_offset is None:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("Next »", callback_data=f"qual_next#{req}#{key}#{qual}#{n_offset}#{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton("« Back", callback_data=f"qual_next#{req}#{key}#{qual}#{b_offset}#{offset}"),
             InlineKeyboardButton(f"{math.ceil(int(l_offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("Next »", callback_data=f"qual_next#{req}#{key}#{qual}#{n_offset}#{offset}")]
        )
    btn.append([InlineKeyboardButton(text="⪻ Back to Main Page", callback_data=f"next_{req}_{key}_{offset}")])
    await query.message.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantagespoll_choker(bot, query):
    _, id, user =query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)
    movie = await get_poster(id, id=True)
    search = movie.get('title')
    s = await query.message.edit_text(f"<b><i><code>{search}</code> Check In My Database...</i></b>")
    await query.answer('')
    files, offset, total_results = await get_search_results(search)
    if files:
        k = (search, files, offset, total_results)
        awaitauto_filter(bot, query, s, k)
    else:
        k = await query.message.edit(f"👋 Hello {query.from_user.mention},\n\nI don't find <b>'{search}'</b> in my database. 😔")
        await bot.send_message(LOG_CHANNEL, f"#No_Result\n\nRequester: {query.from_user.mention}\nContent: {search}")
        await asyncio.sleep(60)
        await k.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

@Client.on_callback_query(filters.regex(r"^smart_preview"))
async def smart_preview_callback(client: Client, query: CallbackQuery):
    _, file_id, user_id = query.data.split("#")

    # Check if user is authorized to see this preview
    if int(user_id) != 0 and query.from_user.id != int(user_id):
        return await query.answer(
            f"Hello {query.from_user.first_name},\nThis Smart Preview is not for you!",
            show_alert=True
        )

    # Get the smart preview from temp storage
    smart_preview_text = temp.SMART_PREVIEWS.get(file_id)

    if not smart_preview_text:
        # If no preview is stored, try to generate it on the fly
        try:
            # Find the file in the database
            from database.ia_filterdb import get_file_details
            file_details = await get_file_details(file_id)

            if file_details:
                file = file_details[0]
                # Get search term from the original message or use the filename
                search_query = query.message.text.split("results for:")[1].split("\n")[0].strip() if "results for:" in query.message.text else file.file_name

                # Generate metadata and preview
                enhanced_metadata = await smart_analyzer.get_enhanced_metadata(search_query, file.file_name)
                smart_preview_text = smart_analyzer.generate_smart_preview(enhanced_metadata)

                # Store for future use
                temp.SMART_PREVIEWS[file_id] = smart_preview_text
            else:
                smart_preview_text = "<b>❌ No smart preview available for this file.</b>"
        except Exception as e:
            print(f"Error generating smart preview: {e}")
            smart_preview_text = "<b>❌ Could not generate smart preview: Error in processing file metadata.</b>"

    # Create buttons
    if 'results for:' in query.message.text:
        search_term = query.message.text.split('results for:')[1].split('\n')[0].strip()
    else:
        try:
            search_term = file.file_name
        except:
            search_term = "Unknown"

    btn = [
        [InlineKeyboardButton("🔍 IMDb", url=f"https://www.imdb.com/find?q={search_term}"),
         InlineKeyboardButton("🎬 Download", callback_data=f"file#{file_id}")]
    ]

    # Add close button
    btn.append([InlineKeyboardButton("❌ Close", callback_data="close_data")])

    # Option to view interactive preview
    btn.insert(0, [InlineKeyboardButton("🌟 Interactive Preview", callback_data=f"preview_page#{file_id}#{user_id}#0")])

    # Send as a new message to avoid replacing the search results
    await query.answer("Generating Smart Preview...")
    await client.send_message(
        chat_id=query.message.chat.id,
        text=f"<b>🧠 Smart Preview</b>\n\n{smart_preview_text}",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_callback_query(filters.regex(r"^preview_page"))
async def preview_page_callback(client: Client, query: CallbackQuery):
    _, file_id, user_id, page_index = query.data.split("#")

    # Check if user is authorized to see this preview
    if int(user_id) != 0 and query.from_user.id != int(user_id):
        return await query.answer(
            f"Hello {query.from_user.first_name},\nThis Interactive Preview is not for you!",
            show_alert=True
        )

    try:
        # Get file details
        file_details = await get_file_details(file_id)
        if not file_details:
            return await query.answer("File not found! Please try a different file.", show_alert=True)

        file = file_details[0]
        file_name = file.file_name

        # Generate the preview content and markup
        content, markup = await preview_wizard.generate_preview_markup(
            file_id=file_id,
            file_name=file_name,
            user_id=user_id,
            current_page=int(page_index)
        )

        # Edit the message to show the new page
        await query.message.edit_text(
            text=content,
            reply_markup=markup,
            parse_mode=enums.ParseMode.HTML
        )

        await query.answer(f"Viewing page {int(page_index) + 1}")

    except Exception as e:
        print(f"Error in preview wizard: {e}")
        await query.answer("Error generating preview. Please try again.", show_alert=True)

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        try:
            user = query.message.reply_to_message.from_user.id
        except:
            user = query.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(f"Hello {query.from_user.first_name},\nThis Is Not For You!", show_alert=True)
        await query.answer("Closed!")
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        try:
            user = query.message.reply_to_message.from_user.id
        except:
            user = query.message.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)

        # Check if in private chat or group and construct valid URL
        base_url = f"https://t.me/{temp.U_NAME}"
        if query.message.chat.type == enums.ChatType.PRIVATE:
            # Use the standard format with the correct group ID for private messages
            valid_url = f"{base_url}?start=file_1927155351_{file_id}"
            await query.answer(url=valid_url)
        else:
            # Use the group ID format for group chats
            chat_id = str(query.message.chat.id).replace("-", "_")  # Handle negative chat IDs
            valid_url = f"{base_url}?start=file_{chat_id}_{file_id}"
            await query.answer(url=valid_url)

    elif query.data.startswith("get_del_file"):
        ident, group_id, file_id = query.data.split("#")
        # Use the format with group_id for backward compatibility
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=file_{group_id}_{file_id}")
        await query.message.delete()

    elif query.data.startswith("get_del_send_all_files"):
        ident, group_id, key = query.data.split("#")
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=all_{group_id}_{key}")
        await query.message.delete()

    elif query.data.startswith("stream"):
        try:
            file_id = query.data.split('#', 1)[1]
            # Send media to the bin channel to get a message_id
            msg = await client.send_cached_media(chat_id=BIN_CHANNEL, file_id=file_id)
            
            # Get proper message_id for streaming
            message_id = msg.id
            
            # Get file name (use generic "video" if not available)
            if msg.video:
                file_name = msg.video.file_name if msg.video.file_name else "video"
            elif msg.document:
                file_name = msg.document.file_name if msg.document.file_name else "document"
            else:
                file_name = "media"
            
            # Generate secure hash from message object (first 6 chars are enough)
            from utils import get_hash
            secure_hash = get_hash(msg)
            
            # Create streaming and download links with the correct hash
            # Format for streaming video: /watch/{message_id}?hash={hash}
            # Use the new dedicated watch endpoint with improved player UI
            watch = f"{URL}/watch/{message_id}?hash={secure_hash}"
            
            # For download links, keep the original format
            download = f"{URL}/{message_id}/{file_name}?hash={secure_hash}"
            
            # Create buttons with proper styling
            btn=[[
                InlineKeyboardButton("🎬 Watch Online", url=watch),
                InlineKeyboardButton("⬇️ Download", url=download)
            ],[
                InlineKeyboardButton('❌ Close', callback_data='close_data')
            ]]
            reply_markup=InlineKeyboardMarkup(btn)
            
            # Update the message with the new buttons
            await query.edit_message_reply_markup(
                reply_markup=reply_markup
            )
            
            # Log the stream request
            user = query.from_user.mention if query.from_user else "Unknown User"
            print(f"Stream link generated for {user}: {watch}")
            
        except Exception as e:
            print(f"Stream error: {str(e)}")
            await query.answer("Unable to generate streaming links. Please try again.", show_alert=True)


    elif query.data.startswith("checksub"):
        ident, mc = query.data.split("#")
        settings = await get_settings(int(mc.split("_", 2)[1]))
        btn = await is_subscribed(client, query, settings['fsub'])
        if btn:
            await query.answer(f"Hello {query.from_user.first_name},\nPlease join my updates channel and try again.", show_alert=True)
            btn.append(
                [InlineKeyboardButton("🔁 Try Again 🔁", callback_data=f"checksub#{mc}")]
            )
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
            return
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start={mc}")
        await query.message.delete()

    elif query.data.startswith("unmuteme"):
        ident, userid = query.data.split("#")
        user_id = query.from_user.id
        settings = await get_settings(int(query.message.chat.id))
        if userid == "0":
            await query.answer("You are anonymous admin !", show_alert=True)
            return
        if userid != str(user_id):
            await query.answer("Not For You ☠️", show_alert=True)
            return
        btn = await is_subscribed(client, query, settings['fsub'])
        if btn:
           await query.answer("Kindly Join Given Channel To Get Unmute", show_alert=True)
        else:
            await client.unban_chat_member(query.message.chat.id, user_id)
            await query.answer("Unmuted Successfully !", show_alert=True)
            try:
                await query.message.delete()
            except:
                return

    elif query.data == "buttons":
        await query.answer("⚠️")

    elif query.data == "instructions":
        await query.answer("Movie request format.\nExample:\nBlack Adam or Black Adam 2022\n\nTV Reries request format.\nExample:\nLoki S01E01 or Loki S01 E01\n\nDon't use symbols.", show_alert=True)

    elif query.data == "start":
        buttons = []
        buttons.append([InlineKeyboardButton("+ Add me to your Group +", url=f'http://t.me/{temp.U_NAME}?startgroup=start')])
        if UPDATES_LINK and SUPPORT_LINK:
            buttons.append([
                InlineKeyboardButton('ℹ️ Updates', url=UPDATES_LINK),
                InlineKeyboardButton('💡 Support', url=SUPPORT_LINK)
            ])
        buttons.extend([[
            InlineKeyboardButton('👨‍🚒 Help', callback_data='help'),
            InlineKeyboardButton('📚 About', callback_data='about')
        ]])
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('❁✗❍═❰ 🆁︎🅴︎🅽︎🅸︎🆂︎🅷︎ ❱═❍✗❁', url='https://t.me/renish_rgi')
        ],[
            InlineKeyboardButton('⬅️ Back', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MY_ABOUT_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "stats":
        if query.from_user.id not in ADMINS:
            return await query.answer("ADMINS Only!", show_alert=True)
        files = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        used_size = get_size(await db.get_db_size())
        free_size = get_size(536870912 - await db.get_db_size())

        if SECOND_DATABASE_URL:
            secnd_used_size = get_size(await db.get_second_db_size())
            secnd_free_size = get_size(536870912 - await db.get_second_db_size())
        else:
            secnd_used_size = '-'
            secnd_free_size = '-'
        uptime = get_readable_time(time_now() - temp.START_TIME)
        buttons = [[
            InlineKeyboardButton('« Back', callback_data='about')
        ]]
        await query.message.edit_text(script.STATUS_TXT.format(files, users, chats, used_size, free_size, secnd_used_size, secnd_free_size, uptime), reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif query.data == "earn":
        buttons = [[
            InlineKeyboardButton('💰 how to connect shortner', callback_data='howshort')
        ],[
            InlineKeyboardButton('⬅️ Back', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EARN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "howshort":
        buttons = [[
            InlineKeyboardButton('≼ Back', callback_data='earn')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HOW_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('User Command', callback_data='user_command'),
            InlineKeyboardButton('Admin Command', callback_data='admin_command')
        ],[
            InlineKeyboardButton('🎭 Mood Search', callback_data='mood_cmd')
        ],[
            InlineKeyboardButton('« Back', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT,
            reply_markup=reply_markup
        )

    elif query.data == "user_command":
        buttons = [[
            InlineKeyboardButton('« Back', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.USER_COMMAND_TXT,
            reply_markup=reply_markup
        )

    # Filter wizard functionality removed

    elif query.data == "admin_command":
        if query.from_user.id not in ADMINS:
            return await query.answer("ADMINS Only!", show_alert=True)
        buttons = [[
            InlineKeyboardButton('« Back', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_COMMAND_TXT,
            reply_markup=reply_markup
        )

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            await query.answer("This Is Not For You!", show_alert=True)
            return

        if status == "True":
            await save_group_settings(int(grp_id), set_type, False)
            await query.answer("❌")
        else:
            await save_group_settings(int(grp_id), set_type, True)
            await query.answer("✅")

        settings = await get_settings(int(grp_id))

        if settings is not None:
            buttons = [[
                InlineKeyboardButton('Auto Filter', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}'),
                InlineKeyboardButton('✅ Yes' if settings["auto_filter"] else '❌ No', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}')
            ],[
                InlineKeyboardButton('IMDb Poster', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}'),
                InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}')
            ],[
                InlineKeyboardButton('Spelling Check', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}'),
                InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}')
            ],[
                InlineKeyboardButton('Auto Delete', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}'),
                InlineKeyboardButton(f'{get_readable_time(DELETE_TIME)}' if settings["auto_delete"] else '❌ No', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}')
            ],[
                InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',),
                InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No', callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}'),
            ],[
                InlineKeyboardButton('Shortlink', callback_data=f'setgs#shortlink#{settings["shortlink"]}#{grp_id}'),
                InlineKeyboardButton('✅ Yes' if settings["shortlink"] else '❌ No', callback_data=f'setgs#shortlink#{settings["shortlink"]}#{grp_id}'),
            ],[
                InlineKeyboardButton('Result Page', callback_data=f'setgs#links#{settings["links"]}#{str(grp_id)}'),
                InlineKeyboardButton('⛓ Link' if settings["links"] else '🧲 Button', callback_data=f'setgs#links#{settings["links"]}#{str(grp_id)}')
            ],[
                InlineKeyboardButton('Stream', callback_data=f'setgs#is_stream#{settings.get("is_stream", IS_STREAM)}#{str(grp_id)}'),
                InlineKeyboardButton('✅ On' if settings.get("is_stream", IS_STREAM) else '❌ Off', callback_data=f'setgs#is_stream#{settings.get("is_stream", IS_STREAM)}#{str(grp_id)}')
            ],[
                InlineKeyboardButton('🧙‍♂️ Use Setup Wizard', callback_data=f'setup_wizard_now')
            ],[
                InlineKeyboardButton('❌ Close ❌', callback_data='close_data')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
        else:
            await query.message.edit_text("Something went wrong!")

    elif query.data == "delete_all":
        files = await Media.count_documents()
        await query.answer('Deleting...')
        await Media.collection.drop()
        await query.message.edit_text(f"Successfully deleted {files} files")

    elif query.data.startswith("delete"):
        _, query_ = query.data.split("_", 1)
        deleted = 0
        await query.message.edit('Deleting...')
        total, files = await delete_files(query_)
        async for file in files:
            await Media.collection.delete_one({'_id': file.file_id})
            deleted += 1
        await query.message.edit(f'Deleted {deleted} files in your database in your query {query_}')

    elif query.data.startswith("send_all"):
        ident, key, req = query.data.split("#")
        if int(req) != query.from_user.id:
            return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)        
        files = temp.FILES.get(key)
        if not files:
            await query.answer(f"Hello {query.from_user.first_name},\nSend New Request Again!", show_alert=True)
            return        
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}")

    elif query.data == "unmute_all_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("This Is Not For You!", show_alert=True)
            return
        users_id = []
        await query.message.edit("Unmute all started! This process maybe get some time...")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.RESTRICTED):
                users_id.append(member.user.id)
            for user_id in users_id:
                await client.unban_chat_member(query.message.chat.id, user_id)
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'Something went wrong.\n\n<code>{e}</code>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"Successfully unmuted <code>{len(users_id)}</code> users.")
        else:
            await query.message.reply('Nothing to unmute users.')

    elif query.data == "unban_all_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("This Is Not For You!", show_alert=True)
            return
        users_id = []
        await query.message.edit("Unban all started! This process maybe get some time...")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.BANNED):
                users_id.append(member.user.id)
            for user_id in users_id:
                await client.unban_chat_member(query.message.chat.id, user_id)
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'Something went wrong.\n\n<code>{e}</code>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"Successfully unban <code>{len(users_id)}</code> users.")
        else:
            await query.message.reply('Nothing to unban users.')

    elif query.data == "kick_muted_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("This Is Not For You!", show_alert=True)
            return
        users_id = []
        await query.message.edit("Kick muted users started! This process maybe get some time...")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.RESTRICTED):
                users_id.append(member.user.id)
            for user_id in users_id:
                await client.ban_chat_member(query.message.chat.id, user_id, datetime.now(TIME_ZONE) + timedelta(seconds=30))
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'Something went wrong.\n\n<code>{e}</code>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"Successfully kicked muted <code>{len(users_id)}</code> users.")
        else:
            await query.message.reply('Nothing to kick muted users.')

    elif query.data == "kick_deleted_accounts_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("This Is Not For You!", show_alert=True)
            return
        users_id = []
        await query.message.edit("Kick deleted accounts started! This process maybe get some time...")
        try:
            async for member in client.get_chat_members(query.message.chat.id):
                if member.user.is_deleted:
                    users_id.append(member.user.id)
            for user_id in users_id:
                await client.ban_chat_member(query.message.chat.id, user_id, datetime.now(TIME_ZONE) + timedelta(seconds=30))
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'Something went wrong.\n\n<code>{e}</code>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"Successfully kicked deleted <code>{len(users_id)}</code> accounts.")
        else:
            await query.message.reply('Nothing to kick deleted accounts.')

    # Mood-based filtering callbacks
    elif query.data == "mood_cmd":
        # Display the mood search help text
        buttons = [[
            InlineKeyboardButton('Try Mood Search Now', callback_data='show_moods')
        ],[
            InlineKeyboardButton('« Back', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MOOD_SEARCH_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

    elif query.data == "show_moods":
        # Import and call the mood filter module to show mood options
        from plugins.mood_filter import show_mood_options
        await show_mood_options(client, query)

    elif query.data.startswith("mood_"):
        # Import and call the mood filter module to handle mood selection
        from plugins.mood_filter import handle_mood_selection
        await handle_mood_selection(client, query)

    elif query.data == "back_to_search":
        # Import and call the mood filter module to go back to search
        from plugins.mood_filter import back_to_search
        await back_to_search(client, query)



async def auto_filter(client, msg, s, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        search = message.text
        files, offset, total_results = await get_search_results(search)
        if not files:
            if settings["spell_check"]:
                await advantage_spell_chok(message, s)
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    req = message.from_user.id if message and message.from_user else 0
    key = f"{message.chat.id}-{message.id}"
    temp.FILES[key] = files
    BUTTONS[key] = search
    files_link = ""

    # Prepare web search URL
    search_query = search.replace(" ", "+")
    from info import URL
    web_search_url = f"{URL}movie?q={search_query}"

    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_1_{file.file_id}>[{get_size(file.file_size)}] {file.file_name}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"📂 {get_size(file.file_size)} {file.file_name}", callback_data=f'file#{file.file_id}')
        ]
            for file in files
        ]   

    # Add web search button for all results
    if search_query:
        web_search_url = f"{URL}movie?q={search_query}"
        btn.append([
            InlineKeyboardButton("🌐 Web Search", url=web_search_url),
            InlineKeyboardButton("🎬 IMDB", url=f"https://www.imdb.com/find?q={search_query}")
        ])

    if offset != "":
        if settings['shortlink']:
            btn.insert(1,
                [InlineKeyboardButton("📰 Languages", callback_data=f"languages#{key}#{req}#{offset}"),
                 InlineKeyboardButton("🔍 Quality", callback_data=f"quality#{key}#{req}#{offset}")]
            )
        else:
            btn.insert(1,
                [InlineKeyboardButton("📰 Languages", callback_data=f"languages#{key}#{req}#{offset}"),
                 InlineKeyboardButton("🔍 Quality", callback_data=f"quality#{key}#{req}#{offset}")]
            )
        btn.append(
            [InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton(text="Next »", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        if settings['shortlink']:
            btn.insert(1,
                [InlineKeyboardButton("♻️ Send All ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{message.chat.id}_{key}'))]
            )
        else:
            btn.insert(1,
                [InlineKeyboardButton("♻️ Send All ♻️", callback_data=f"send_all#{key}#{req}")]
            )
    # Smart preview button removed

    # Get IMDb data for traditional display
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None

    # Get enhanced metadata for first file
    first_file = files[0]
    enhanced_metadata = None

    # Enable smart preview by default if IMDb data is available
    if settings.get("smart_preview", True) and imdb:
        try:
            # Generate enhanced metadata with our smart analyzer
            enhanced_metadata = await smart_analyzer.get_enhanced_metadata(search, first_file.file_name)
            # Generate smart preview text
            smart_preview_text = smart_analyzer.generate_smart_preview(enhanced_metadata)
            # Store smart preview for use in callback
            temp.SMART_PREVIEWS[first_file.file_id] = smart_preview_text
        except Exception as e:
            print(f"Error generating smart preview: {e}")

    # Use traditional template for regular display
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b>💭 Hey {message.from_user.mention},\n♻️ here i found for your search {search}...</b>"
    CAP[key] = cap
    del_msg = f"\n\n<b>⚠️ This message will be auto deleted after <code>{get_readable_time(DELETE_TIME)}</code> to avoid copyright issues</b>" if settings["auto_delete"] else ''
    if imdb and imdb.get('poster'):
        await s.delete()
        try:
            k = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024] + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            k = await message.reply_photo(photo=poster, caption=cap[:1024] + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
        except Exception as e:
            k = await message.reply_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
    else:
        k = await s.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        if settings["auto_delete"]:
            await asyncio.sleep(DELETE_TIME)
            await k.delete()
            try:
                await message.delete()
            except:
                pass

async def advantage_spell_chok(message, s):
    search = message.text
    search_query = search.replace(" ", "+")
    from info import URL
    web_search_url = f"{URL}movie?q={search_query}"
    btn = [[
        InlineKeyboardButton("⚠️ Instructions ⚠️", callback_data='instructions'),
        InlineKeyboardButton("🔎 Search Google 🔍", url=f"https://www.google.com/search?q={search_query}")
    ]]

    # Add more web search options
    web_search_btn = [[
        InlineKeyboardButton("🎬 IMDB Search", url=f"https://www.imdb.com/find?q={search_query}"),
        InlineKeyboardButton("📚 Wikipedia", url=f"https://en.wikipedia.org/wiki/Special:Search?search={search_query}")
    ]]
    btn.extend(web_search_btn)

    try:
        movies = await get_poster(search, bulk=True)
    except:
        n = await s.edit_text(text=script.NOT_FILE_TXT.format(message.from_user.mention, search), reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(60)
        await n.delete()
        try:
            await message.delete()
        except:
            pass
        return
    if not movies:
        n = await s.edit_text(text=script.NOT_FILE_TXT.format(message.from_user.mention, search), reply_markup=InlineKeyboardMarkup(btn))
        await temp.BOT.send_message(LOG_CHANNEL, f"#No_Result\n\nRequester: {message.from_user.mention}\nContent: {search}")
        await asyncio.sleep(60)
        await n.delete()
        try:
            await message.delete()
        except:
            pass
        return
    user = message.from_user.id if message.from_user else 0
    buttons = [[
        InlineKeyboardButton(text=movie.get('title'), callback_data=f"spolling#{movie.movieID}#{user}")
    ]
        for movie in movies
    ]

    # Add web search option to movie results too
    buttons.insert(0, [
        InlineKeyboardButton("🌐 Search Web", url=web_search_url)
    ])

    buttons.append(
        [InlineKeyboardButton("🚫 close 🚫", callback_data="close_data")]
    )
    s = await s.edit_text(text=f"👋 Hello {message.from_user.mention},\n\nI couldn't find the <b>'{search}'</b> you requested.\nSelect if you meant one of these? 👇", reply_markup=InlineKeyboardMarkup(buttons))
    await asyncio.sleep(300)
    await s.delete()
    try:
        await message.delete()
    except:
        pass
