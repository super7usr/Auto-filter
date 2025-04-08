
class script(object):

    START_TXT = """<b>👋 ʜᴇʏ {}, 

🤖 ɪ'ᴍ <span class="highlight">ᴀᴜᴛᴏ ғɪʟᴛᴇʀ ᴡɪᴛʜ ʟɪɴᴋ sʜᴏʀᴛᴇɴᴇʀ</span> ʙᴏᴛ!

💯 ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀs ᴀᴅᴍɪɴ ᴀɴᴅ ɪ'ʟʟ ᴘʀᴏᴠɪᴅᴇ ᴍᴏᴠɪᴇs ᴡɪᴛʜ ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ sʜᴏʀᴛᴇɴᴇᴅ ʟɪɴᴋs!

🌟 ᴇɴᴊᴏʏ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs ᴀɴᴅ ᴇᴀʀɴ ᴡʜɪʟᴇ sʜᴀʀɪɴɢ ᴄᴏɴᴛᴇɴᴛ!</b>"""

    MY_ABOUT_TXT = """<b>🤖 <u>ʙᴏᴛ sᴘᴇᴄɪғɪᴄᴀᴛɪᴏɴs</u> 🤖</b>

<b>🔹 sᴇʀᴠᴇʀ:</b> <a href=https://www.heroku.com><b>ʜᴇʀᴏᴋᴜ</b></a>
<b>🔹 ᴅᴀᴛᴀʙᴀsᴇ:</b> <a href=https://www.mongodb.com><b>ᴍᴏɴɢᴏᴅʙ</b></a>
<b>🔹 ʟᴀɴɢᴜᴀɢᴇ:</b> <a href=https://www.python.org><b>ᴘʏᴛʜᴏɴ</b></a>
<b>🔹 ʟɪʙʀᴀʀʏ:</b> <a href=https://pyrogram.org><b>ᴘʏʀᴏɢʀᴀᴍ</b></a>
<b>🔹 ʙᴜɪʟᴅ sᴛᴀᴛᴜs:</b> <code>ᴠ2.5.1 [sᴛᴀʙʟᴇ]</code>"""

    MY_OWNER_TXT = """<b>👑 <u>ʙᴏᴛ ᴏᴡɴᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</u> 👑</b>

<b>🔸 ɴᴀᴍᴇ:</b> <code>ʜᴀ ʙᴏᴛs</code>
<b>🔸 ᴜsᴇʀɴᴀᴍᴇ:</b> @HA_Bots
<b>🔸 ᴄᴏᴜɴᴛʀʏ:</b> <code>sʀɪ ʟᴀɴᴋᴀ 🇱🇰</code>
<b>🔸 ᴇxᴘᴇʀɪᴇɴᴄᴇ:</b> <code>ᴄʜᴀᴛʙᴏᴛ & ᴀᴜᴛᴏᴍᴀᴛɪᴏɴ</code>"""

    STATUS_TXT = """<b>📊 <u>ʙᴏᴛ sᴛᴀᴛᴜs</u> 📊</b>

<b>📁 ᴛᴏᴛᴀʟ ғɪʟᴇs:</b> <code>{}</code>
<b>👤 ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{}</code>
<b>👥 ᴛᴏᴛᴀʟ ᴄʜᴀᴛs:</b> <code>{}</code>
<b>💾 ᴜsᴇᴅ sᴛᴏʀᴀɢᴇ:</b> <code>{}</code>
<b>🆓 ғʀᴇᴇ sᴛᴏʀᴀɢᴇ:</b> <code>{}</code>

<b>📊 sᴇᴄᴏɴᴅ ᴅʙ sᴛᴀᴛᴜs:</b>
<b>💾 ᴜsᴇᴅ sᴛᴏʀᴀɢᴇ:</b> <code>{}</code>
<b>🆓 ғʀᴇᴇ sᴛᴏʀᴀɢᴇ:</b> <code>{}</code>
<b>⏰ ʙᴏᴛ ᴜᴘᴛɪᴍᴇ:</b> <code>{}</code>"""

    NEW_GROUP_TXT = """<b>🔔 #ɴᴇᴡɢʀᴏᴜᴘ</b>

<b>📋 ᴛɪᴛʟᴇ:</b> <code>{}</code>
<b>🆔 ɪᴅ:</b> <code>{}</code>
<b>👤 ᴜsᴇʀɴᴀᴍᴇ:</b> <code>{}</code>
<b>👥 ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs:</b> <code>{}</code>"""

    NEW_USER_TXT = """<b>🔔 #ɴᴇᴡᴜsᴇʀ</b>

<b>👤 ɴᴀᴍᴇ:</b> {}
<b>🆔 ɪᴅ:</b> <code>{}</code>"""

    NOT_FILE_TXT = """<b>👋 ʜᴇʟʟᴏ {},

😕 ɪ ᴄᴏᴜʟᴅɴ'ᴛ ғɪɴᴅ "<code>{}</code>" ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ!</b>

<b>💡 sᴜɢɢᴇsᴛɪᴏɴs:</b>
• <b>🔍 ᴛʀʏ ᴀ ɢᴏᴏɢʟᴇ sᴇᴀʀᴄʜ ᴀɴᴅ ᴄʜᴇᴄᴋ ʏᴏᴜʀ sᴘᴇʟʟɪɴɢ</b>
• <b>📝 ʀᴇᴀᴅ ᴛʜᴇ ɪɴsᴛʀᴜᴄᴛɪᴏɴs ғᴏʀ ʙᴇᴛᴛᴇʀ ʀᴇsᴜʟᴛs</b>
• <b>🕒 ᴄᴏɴᴛᴇɴᴛ ᴍɪɢʜᴛ ɴᴏᴛ ʙᴇ ʀᴇʟᴇᴀsᴇᴅ ʏᴇᴛ</b>"""
    
    EARN_TXT = """<b>💰 <u>ʜᴏᴡ ᴛᴏ ᴇᴀʀɴ ᴡɪᴛʜ ᴛʜɪs ʙᴏᴛ</u> 💰</b>

<b>ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴍᴏɴᴇᴛɪᴢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴇᴀʀɴ ᴘᴀssɪᴠᴇ ɪɴᴄᴏᴍᴇ!</b>

<b>🔹 sᴛᴇᴘ 1:</b> ᴀᴅᴅ ᴛʜɪs ʙᴏᴛ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴡɪᴛʜ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs

<b>🔹 sᴛᴇᴘ 2:</b> ᴄʀᴇᴀᴛᴇ ᴀɴ ᴀᴄᴄᴏᴜɴᴛ ᴏɴ <a href=https://telegram.me/how_to_download_channel/14>ᴍᴅɪsᴋʟɪɴᴋ.ʟɪɴᴋ</a> ᴏʀ ᴀɴʏ ᴏᴛʜᴇʀ sʜᴏʀᴛɴᴇʀ

<b>🔹 sᴛᴇᴘ 3:</b> ᴄᴏɴɴᴇᴄᴛ ʏᴏᴜʀ sʜᴏʀᴛɴᴇʀ ᴡɪᴛʜ ᴛʜᴇ ʙᴏᴛ ᴜsɪɴɢ ᴛʜᴇ ɪɴsᴛʀᴜᴄᴛɪᴏɴs ʙᴇʟᴏᴡ

<b>💎 ʙᴇɴᴇғɪᴛs:</b>
• <b>ғʀᴇᴇ ᴛᴏ ᴜsᴇ - ɴᴏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴇᴇs</b>
• <b>ᴀᴜᴛᴏᴍᴀᴛɪᴄ ᴄᴏɴᴛᴇɴᴛ sʜᴀʀɪɴɢ ᴡɪᴛʜ ʏᴏᴜʀ sʜᴏʀᴛʟɪɴᴋs</b>
• <b>ᴇᴀʀɴ ғʀᴏᴍ ᴇᴀᴄʜ ʟɪɴᴋ ᴄʟɪᴄᴋ</b>"""

    HOW_TXT = """<b>🔗 <u>ʜᴏᴡ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ʏᴏᴜʀ sʜᴏʀᴛɴᴇʀ</u> 🔗</b>

<b>ᴄᴏɴɴᴇᴄᴛ ʏᴏᴜʀ sʜᴏʀᴛɴᴇʀ ᴡɪᴛʜ ᴛʜᴇsᴇ sɪᴍᴘʟᴇ sᴛᴇᴘs:</b>

<b>📝 ᴄᴏᴍᴍᴀɴᴅ ғᴏʀᴍᴀᴛ:</b>
<code>/set_shortlink sʜᴏʀᴛɴᴇʀ_sɪᴛᴇ sʜᴏʀᴛɴᴇʀ_ᴀᴘɪ</code>

<b>📋 ᴇxᴀᴍᴘʟᴇ:</b>
<code>/set_shortlink mdisklink.link 5843c3cc645f5077b2200a2c77e0344879880b3e</code>

<b>🔍 ᴄʜᴇᴄᴋ ᴀᴄᴛɪᴠᴇ sʜᴏʀᴛɴᴇʀ:</b>
<code>/get_shortlink</code>

<b>⚠️ ɪᴍᴘᴏʀᴛᴀɴᴛ ɴᴏᴛᴇs:</b>
• <b>ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀ ᴠɪsɪʙʟᴇ ᴀᴅᴍɪɴ (ɴᴏᴛ ᴀɴᴏɴʏᴍᴏᴜs)</b>
• <b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴄᴀɴ sᴇᴛ ᴛʜᴇ sʜᴏʀᴛɴᴇʀ</b>
• <b>ᴇɴsᴜʀᴇ ʏᴏᴜʀ ᴀᴘɪ ᴋᴇʏ ɪs ᴄᴏʀʀᴇᴄᴛ</b>"""

    IMDB_TEMPLATE = """<b>✅ ɪ ғᴏᴜɴᴅ: <code>{query}</code></b>

<b>🎬 ᴛɪᴛʟᴇ:</b> <a href={url}>{title}</a>
<b>🎭 ɢᴇɴʀᴇs:</b> {genres}
<b>📅 ʏᴇᴀʀ:</b> <a href={url}/releaseinfo>{year}</a>
<b>⭐ ʀᴀᴛɪɴɢ:</b> <a href={url}/ratings>{rating} / 10</a>
<b>🗣️ ʟᴀɴɢᴜᴀɢᴇs:</b> {languages}
<b>⏱️ ʀᴜɴᴛɪᴍᴇ:</b> {runtime} ᴍɪɴᴜᴛᴇs

<b>🔍 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:</b> {message.from_user.mention}
<b>©️ ᴘᴏᴡᴇʀᴇᴅ ʙʏ:</b> <b>{message.chat.title}</b>"""

    FILE_CAPTION = """<b>📁 {file_name}</b>

<b>💬 ᴊᴏɪɴ <a href="https://t.me/HA_Bots">@HA_Bots</a> ғᴏʀ ᴍᴏʀᴇ ғɪʟᴇs</b>

<b>🚫 ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ᴄʟᴏsᴇ ʙᴜᴛᴛᴏɴ ᴡʜᴇɴ ᴅᴏɴᴇ</b>"""

    WELCOME_TEXT = """<b>👋 ʜᴇʟʟᴏ {mention}, 

🎉 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {title} ɢʀᴏᴜᴘ!

💬 ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ ᴀsᴋ ғᴏʀ ᴍᴏᴠɪᴇs ᴀɴᴅ sᴇʀɪᴇs</b>"""

    HELP_TXT = """<b>📚 <u>ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs ɢᴜɪᴅᴇ</u> 📚</b>

<b>ɴᴏᴛᴇ:</b> <spoiler>ᴛʀʏ ᴇᴀᴄʜ ᴄᴏᴍᴍᴀɴᴅ ᴡɪᴛʜᴏᴜᴛ ᴀʀɢᴜᴍᴇɴᴛs ᴛᴏ sᴇᴇ ᴅᴇᴛᴀɪʟᴇᴅ ɪɴsᴛʀᴜᴄᴛɪᴏɴs</spoiler>

<b>📝 ᴛʏᴘᴇ /commands ᴛᴏ sᴇᴇ ᴛʜᴇ ғᴜʟʟ ʟɪsᴛ ᴏғ ᴄᴏᴍᴍᴀɴᴅs</b>"""
    
    ADMIN_COMMAND_TXT = """<b>⚙️ <u>ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs</u> ⚙️</b>

<b>🔹 /index_channels</b> - ᴄʜᴇᴄᴋ ɪɴᴅᴇxᴇᴅ ᴄʜᴀɴɴᴇʟs
<b>🔹 /stats</b> - ᴄʜᴇᴄᴋ ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs
<b>🔹 /delete</b> - ᴅᴇʟᴇᴛᴇ ғɪʟᴇs ʙʏ ǫᴜᴇʀʏ
<b>🔹 /delete_all</b> - ᴅᴇʟᴇᴛᴇ ᴀʟʟ ɪɴᴅᴇxᴇᴅ ғɪʟᴇs
<b>🔹 /broadcast</b> - sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜsᴇʀs
<b>🔹 /grp_broadcast</b> - ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ɢʀᴏᴜᴘs
<b>🔹 /pin_broadcast</b> - ᴘɪɴɴᴇᴅ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴜsᴇʀs
<b>🔹 /pin_grp_broadcast</b> - ᴘɪɴɴᴇᴅ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ɢʀᴏᴜᴘs
<b>🔹 /restart</b> - ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ
<b>🔹 /leave</b> - ʟᴇᴀᴠᴇ ᴀ ɢʀᴏᴜᴘ
<b>🔹 /unban_grp</b> - ᴇɴᴀʙʟᴇ ɢʀᴏᴜᴘ ᴀᴄᴄᴇss
<b>🔹 /ban_grp</b> - ᴅɪsᴀʙʟᴇ ɢʀᴏᴜᴘ ᴀᴄᴄᴇss
<b>🔹 /ban_user</b> - ʙᴀɴ ᴀ ᴜsᴇʀ
<b>🔹 /unban_user</b> - ᴜɴʙᴀɴ ᴀ ᴜsᴇʀ
<b>🔹 /users</b> - ᴠɪᴇᴡ ᴀʟʟ ᴜsᴇʀs ᴅᴇᴛᴀɪʟs
<b>🔹 /chats</b> - ᴠɪᴇᴡ ᴀʟʟ ɢʀᴏᴜᴘs
<b>🔹 /invite_link</b> - ɢᴇɴᴇʀᴀᴛᴇ ɪɴᴠɪᴛᴇ ʟɪɴᴋ
<b>🔹 /index</b> - ɪɴᴅᴇx ᴄʜᴀɴɴᴇʟs"""
    
    USER_COMMAND_TXT = """<b>🛠️ <u>ᴜsᴇʀ ᴄᴏᴍᴍᴀɴᴅs</u> 🛠️</b>

<b>🔸 /start</b> - ᴄʜᴇᴄᴋ ɪғ ʙᴏᴛ ɪs ᴏɴʟɪɴᴇ
<b>🔸 /settings</b> - ᴄᴜsᴛᴏᴍɪᴢᴇ ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs
<b>🔸 /set_template</b> - sᴇᴛ ᴄᴜsᴛᴏᴍ ɪᴍᴅʙ ᴛᴇᴍᴘʟᴀᴛᴇ
<b>🔸 /set_caption</b> - sᴇᴛ ᴄᴜsᴛᴏᴍ ғɪʟᴇ ᴄᴀᴘᴛɪᴏɴ
<b>🔸 /set_shortlink</b> - sᴇᴛ ᴄᴜsᴛᴏᴍ sʜᴏʀᴛʟɪɴᴋ 
<b>🔸 /get_custom_settings</b> - ᴠɪᴇᴡ ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs
<b>🔸 /set_welcome</b> - sᴇᴛ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ
<b>🔸 /set_tutorial</b> - sᴇᴛ ᴄᴜsᴛᴏᴍ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ
<b>🔸 /id</b> - ᴄʜᴇᴄᴋ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ ɪᴅ
<b>🔸 /set_fsub</b> - sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟs
<b>🔸 /remove_fsub</b> - ʀᴇᴍᴏᴠᴇ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ"""
    
    SOURCE_TXT = """<b>🧩 <u>ʙᴏᴛ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ</u> 🧩</b>

<b>🤖 ᴛʜɪs ʙᴏᴛ ɪs ᴀɴ ᴏᴘᴇɴ sᴏᴜʀᴄᴇ ᴘʀᴏᴊᴇᴄᴛ</b>

<b>📦 sᴏᴜʀᴄᴇ:</b> <a href=https://github.com/HA-Bots/Auto-Filter-Bot><b>ɢɪᴛʜᴜʙ ʀᴇᴘᴏsɪᴛᴏʀʏ</b></a>

<b>👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ:</b> <a href=https://t.me/HA_Bots>@HA_Bots</a>"""
