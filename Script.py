
class script(object):

    START_TXT = """<b>👋 Hey {}, 

🤖 I'm <span class="highlight">Auto Filter with Link Shortener</span> bot!

💯 Add me to your group as admin and I'll provide movies with your custom shortened links!

🌟 Enjoy premium features and earn while sharing content!</b>"""

    MY_ABOUT_TXT = """<b>🤖 <u>Bot Specifications</u> 🤖</b>

<b>🔹 Server:</b> <a href=https://www.heroku.com><b>Heroku</b></a>
<b>🔹 Database:</b> <a href=https://www.mongodb.com><b>MongoDB</b></a>
<b>🔹 Language:</b> <a href=https://www.python.org><b>Python</b></a>
<b>🔹 Library:</b> <a href=https://pyrogram.org><b>Pyrogram</b></a>
<b>🔹 Build Status:</b> <code>v2.5.1 [Stable]</code>"""

    MY_OWNER_TXT = """<b>👑 <u>Bot Owner Information</u> 👑</b>

<b>🔸 Name:</b> <code>HA Bots</code>
<b>🔸 Username:</b> @HA_Bots
<b>🔸 Country:</b> <code>Sri Lanka 🇱🇰</code>
<b>🔸 Experience:</b> <code>Chatbot & Automation</code>"""

    STATUS_TXT = """<b>📊 <u>Bot Status</u> 📊</b>

<b>📁 Total Files:</b> <code>{}</code>
<b>👤 Total Users:</b> <code>{}</code>
<b>👥 Total Chats:</b> <code>{}</code>
<b>💾 Used Storage:</b> <code>{}</code>
<b>🆓 Free Storage:</b> <code>{}</code>

<b>📊 Second DB Status:</b>
<b>💾 Used Storage:</b> <code>{}</code>
<b>🆓 Free Storage:</b> <code>{}</code>
<b>⏰ Bot Uptime:</b> <code>{}</code>"""

    NEW_GROUP_TXT = """<b>🔔 #NewGroup</b>

<b>📋 Title:</b> <code>{}</code>
<b>🆔 ID:</b> <code>{}</code>
<b>👤 Username:</b> <code>{}</code>
<b>👥 Total Members:</b> <code>{}</code>"""

    NEW_USER_TXT = """<b>🔔 #NewUser</b>

<b>👤 Name:</b> {}
<b>🆔 ID:</b> <code>{}</code>"""

    NOT_FILE_TXT = """<b>👋 Hello {},

😕 I couldn't find "<code>{}</code>" in my database!</b>

<b>💡 Suggestions:</b>
• <b>🔍 Try a Google search and check your spelling</b>
• <b>📝 Read the instructions for better results</b>
• <b>🕒 Content might not be released yet</b>"""
    
    EARN_TXT = """<b>💰 <u>How to Earn with this Bot</u> 💰</b>

<b>Now you can monetize your group and earn passive income!</b>

<b>🔹 Step 1:</b> Add this bot to your group with admin permissions

<b>🔹 Step 2:</b> Create an account on <a href=https://telegram.me/how_to_download_channel/14>mdisklink.link</a> or any other shortener

<b>🔹 Step 3:</b> Connect your shortener with the bot using the instructions below

<b>💎 Benefits:</b>
• <b>Free to use - no subscription fees</b>
• <b>Automatic content sharing with your shortlinks</b>
• <b>Earn from each link click</b>"""

    HOW_TXT = """<b>🔗 <u>How to Connect Your Shortener</u> 🔗</b>

<b>Connect your shortener with these simple steps:</b>

<b>📝 Command Format:</b>
<code>/set_shortlink shortener_site shortener_api</code>

<b>📋 Example:</b>
<code>/set_shortlink mdisklink.link 5843c3cc645f5077b2200a2c77e0344879880b3e</code>

<b>🔍 Check Active Shortener:</b>
<code>/get_shortlink</code>

<b>⚠️ Important Notes:</b>
• <b>You must be a visible admin (not anonymous)</b>
• <b>Only group admins can set the shortener</b>
• <b>Ensure your API key is correct</b>"""

    IMDB_TEMPLATE = """<b>✅ I found: <code>{query}</code></b>

<b>🎬 Title:</b> <a href={url}>{title}</a>
<b>🎭 Genres:</b> {genres}
<b>📅 Year:</b> <a href={url}/releaseinfo>{year}</a>
<b>⭐ Rating:</b> <a href={url}/ratings>{rating} / 10</a>
<b>🗣️ Languages:</b> {languages}
<b>⏱️ Runtime:</b> {runtime} minutes

<b>🔍 Requested by:</b> {message.from_user.mention}
<b>©️ Powered by:</b> <b>{message.chat.title}</b>"""

    FILE_CAPTION = """<b>📁 {file_name}</b>

<b>💬 Join <a href="https://t.me/HA_Bots">@HA_Bots</a> for more files</b>

<b>🚫 Please click on the close button when done</b>"""

    WELCOME_TEXT = """<b>👋 Hello {mention}, 

🎉 Welcome to {title} group!

💬 Feel free to ask for movies and series</b>"""

    HELP_TXT = """<b>📚 <u>Bot Commands Guide</u> 📚</b>

<b>Note:</b> <spoiler>Try each command without arguments to see detailed instructions</spoiler>

<b>🌟 Special Features:</b>
• <b>Smart Preview</b> - Get detailed info about files with our AI-powered analyzer
• <b>Interactive Preview</b> - View multi-page previews with technical details, plot summary, and more
• <b>Visual Tags</b> - Color-coded tags to identify quality and format at a glance

<b>📝 Type /commands to see the full list of commands</b>"""
    
    ADMIN_COMMAND_TXT = """<b>⚙️ <u>Admin Commands</u> ⚙️</b>

<b>🔹 /index_channels</b> - Check indexed channels
<b>🔹 /stats</b> - Check bot statistics
<b>🔹 /delete</b> - Delete files by query
<b>🔹 /delete_all</b> - Delete all indexed files
<b>🔹 /broadcast</b> - Send message to all users
<b>🔹 /grp_broadcast</b> - Broadcast to groups
<b>🔹 /pin_broadcast</b> - Pinned broadcast to users
<b>🔹 /pin_grp_broadcast</b> - Pinned broadcast to groups
<b>🔹 /restart</b> - Restart the bot
<b>🔹 /leave</b> - Leave a group
<b>🔹 /unban_grp</b> - Enable group access
<b>🔹 /ban_grp</b> - Disable group access
<b>🔹 /ban_user</b> - Ban a user
<b>🔹 /unban_user</b> - Unban a user
<b>🔹 /users</b> - View all users details
<b>🔹 /chats</b> - View all groups
<b>🔹 /invite_link</b> - Generate invite link
<b>🔹 /index</b> - Index channels"""
    
    USER_COMMAND_TXT = """<b>🛠️ <u>User Commands</u> 🛠️</b>

<b>🔸 /start</b> - Check if bot is online
<b>🔸 /settings</b> - Customize group settings
<b>🔸 /setup_filters</b> - Start the filter setup wizard
<b>🔸 /set_template</b> - Set custom IMDB template
<b>🔸 /set_caption</b> - Set custom file caption
<b>🔸 /set_shortlink</b> - Set custom shortlink 
<b>🔸 /get_custom_settings</b> - View current settings
<b>🔸 /set_welcome</b> - Set custom welcome message
<b>🔸 /set_tutorial</b> - Set custom tutorial link
<b>🔸 /id</b> - Check group/channel ID
<b>🔸 /set_fsub</b> - Set force subscribe channels
<b>🔸 /remove_fsub</b> - Remove force subscribe"""
    
    FILTER_WIZARD_TXT = """<b>🧙‍♂️ <u>Filter Setup Wizard</u> 🧙‍♂️</b>

The Filter Setup Wizard helps you configure your group's filtering settings step by step.

<b>How to use:</b>
1. Type /setup_filters in your group
2. Follow the on-screen instructions
3. Configure auto filter settings
4. Set up search result preferences
5. Customize media display options
6. Complete the setup

<b>Available Settings:</b>
• Auto Filter - Automatically respond to file requests
• Spell Check - Suggest corrections when no results
• Link Mode - Display results as links
• IMDb Integration - Show movie/series information
• Shortlink - Use custom link shorteners
• Auto Delete - Automatically remove old search results

All settings can be customized through the wizard interface."""
    
    MOOD_SEARCH_TXT = """<b>🎭 <u>Mood-Based Content Search</u> 🎭</b>

<b>Find perfect content based on your current mood with our emoji search!</b>

<b>How it works:</b>
• Click on the mood search button
• Select an emoji that matches your current mood
• Get content recommendations tailored to your mood

<b>Available Mood Categories:</b>
• 😊 Happy - Feel-good comedies and uplifting stories
• 😢 Sad - Emotional dramas and moving experiences
• 😱 Scary - Horror and suspense for thrill seekers
• 🤣 Laugh - Comedies guaranteed to make you laugh
• ❤️ Romantic - Love stories and heart-warming tales
• 🔥 Action - High-energy adventures and excitement
• 🧠 Thought-provoking - Mind-bending and philosophical films
• 🦸 Fantasy - Superhero, sci-fi and magical adventures
• 👪 Family - Kid-friendly and wholesome entertainment
• 🎭 Artistic - Indie films and artistic masterpieces

<b>Try it now by clicking the "Mood Search" button in search results!</b>"""

    SOURCE_TXT = """<b>🧩 <u>Bot Source Code</u> 🧩</b>

<b>🤖 This bot is an open source project</b>

<b>📦 Source:</b> <a href=https://github.com/HA-Bots/Auto-Filter-Bot><b>GitHub Repository</b></a>

<b>👨‍💻 Developer:</b> <a href=https://t.me/HA_Bots>@HA_Bots</a>"""
