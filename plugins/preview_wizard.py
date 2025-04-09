import re
import json
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import enums
from utils import get_poster, temp
from info import ADMINS, LONG_IMDB_DESCRIPTION
import logging
from plugins.smart_preview import smart_analyzer

logger = logging.getLogger(__name__)

class ContentPreviewWizard:
    """Class for creating interactive content previews with visual tags"""
    
    def __init__(self):
        """Initialize the preview wizard"""
        self.preview_states = {}  # Store user preview states
        self.tag_colors = {
            "4K": "🟦",   # Blue
            "HD": "🟩",   # Green
            "SD": "🟨",   # Yellow
            "CAM": "🟥",  # Red
            "WEB-DL": "🟪", # Purple
            "BLU-RAY": "🟪", # Purple
            "HEVC": "⬜",  # White
            "x265": "⬜",  # White
            "DDL": "🟧",   # Orange
            "MULTI": "🟫", # Brown
            "DUBBED": "🟫", # Brown
            "SUBTITLED": "🟫", # Brown
        }
    
    def get_quality_tag(self, file_name):
        """Extract quality tag from filename"""
        # Match common quality patterns
        quality_patterns = [
            (r'2160p|4K|UHD', "4K"),
            (r'1080p|FHD|FULL\s*HD', "HD"),
            (r'720p|HD', "HD"),
            (r'480p|SD', "SD"),
            (r'CAM|HDCAM', "CAM"),
            (r'WEB-?DL', "WEB-DL"),
            (r'BLU-?RAY', "BLU-RAY"),
            (r'HEVC|H\.?265', "HEVC"),
            (r'x265', "x265"),
            (r'DDL', "DDL"),
            (r'MULTI', "MULTI"),
            (r'DUBBED', "DUBBED"),
            (r'SUBTITLES|SUBS', "SUBTITLED"),
        ]
        
        for pattern, tag in quality_patterns:
            if re.search(pattern, file_name, re.IGNORECASE):
                return tag
        
        return None
    
    def get_visual_tags(self, file_name):
        """Generate visual tags for the content"""
        tags = []
        
        quality_tag = self.get_quality_tag(file_name)
        if quality_tag and quality_tag in self.tag_colors:
            tags.append(f"{self.tag_colors[quality_tag]} {quality_tag}")
        
        # Extract media type (Movie, TV Show, Anime, etc.)
        if re.search(r'S\d{1,2}E\d{1,2}', file_name, re.IGNORECASE):
            tags.append("📺 TV Series")
        elif re.search(r'anime|アニメ', file_name, re.IGNORECASE):
            tags.append("🎭 Anime") 
        else:
            tags.append("🎬 Movie")
        
        # Extract language if present
        language_patterns = [
            (r'hindi|हिन्दी', "🇮🇳 Hindi"),
            (r'english|eng', "🇬🇧 English"),
            (r'tamil|தமிழ்', "🇮🇳 Tamil"),
            (r'telugu|తెలుగు', "🇮🇳 Telugu"),
            (r'spanish|español', "🇪🇸 Spanish"),
            (r'french|français', "🇫🇷 French"),
            (r'german|deutsch', "🇩🇪 German"),
            (r'italian|italiano', "🇮🇹 Italian"),
            (r'japanese|日本語', "🇯🇵 Japanese"),
            (r'korean|한국어', "🇰🇷 Korean"),
            (r'chinese|中文', "🇨🇳 Chinese"),
            (r'dual|multi', "🌐 Multi-Language"),
        ]
        
        for pattern, tag in language_patterns:
            if re.search(pattern, file_name, re.IGNORECASE):
                tags.append(tag)
                break
        
        # Add file size tag if available
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(GB|MB)', file_name, re.IGNORECASE)
        if size_match:
            size, unit = size_match.groups()
            tags.append(f"💾 {size}{unit}")
        
        return tags
    
    async def generate_preview_markup(self, file_id, file_name, user_id, current_page=0):
        """Generate the preview markup with navigation buttons"""
        # Get enhanced metadata
        enhanced_metadata = None
        
        try:
            # Try to get IMDb data for additional info
            search_query = re.sub(r'\.(mkv|mp4|avi|mov)$', '', file_name)
            search_query = re.sub(r'[._\-\[\]()]', ' ', search_query)
            imdb_data = await get_poster(search_query, file=file_name)
            
            if imdb_data:
                # Get enhanced metadata
                enhanced_metadata = await smart_analyzer.get_enhanced_metadata(search_query, file_name)
        except Exception as e:
            logger.error(f"Error getting enhanced metadata: {e}")
            
        # Get visual tags
        visual_tags = self.get_visual_tags(file_name)
        
        # Define pages for the wizard
        pages = [
            {"name": "Overview", "icon": "🔍"},
            {"name": "Technical", "icon": "🔧"},
            {"name": "Plot", "icon": "📜"},
            {"name": "Download", "icon": "📥"}
        ]
        
        # Store the content data in temp storage if it doesn't exist
        wizard_key = f"wizard_{file_id}_{user_id}"
        if wizard_key not in temp.SMART_PREVIEWS:
            temp.SMART_PREVIEWS[wizard_key] = {
                "file_id": file_id,
                "file_name": file_name,
                "visual_tags": visual_tags,
                "enhanced_metadata": enhanced_metadata,
                "imdb_data": imdb_data
            }
        
        # Create page content
        page_content = self.get_page_content(temp.SMART_PREVIEWS[wizard_key], current_page)
        
        # Create page navigation buttons
        nav_buttons = []
        for i, page in enumerate(pages):
            if i == current_page:
                # Current page - highlight it
                label = f"• {page['icon']} {page['name']} •"
            else:
                label = f"{page['icon']} {page['name']}"
            nav_buttons.append(
                InlineKeyboardButton(label, callback_data=f"preview_page#{file_id}#{user_id}#{i}")
            )
        
        # Split navigation buttons into rows
        nav_rows = [nav_buttons[i:i+2] for i in range(0, len(nav_buttons), 2)]
        
        # Add the action buttons
        action_buttons = []
        
        # Download or stream button
        action_buttons.append(
            InlineKeyboardButton("📥 Download", callback_data=f"file#{file_id}")
        )
        
        # Add IMDB button if we have data
        if imdb_data and "url" in imdb_data and imdb_data["url"]:
            action_buttons.append(
                InlineKeyboardButton("🎬 IMDb", url=imdb_data["url"])
            )
        
        # Web streaming button
        from info import URL
        if URL:
            file_web_url = f"{URL}watch/{file_id}/{file_name.replace(' ', '_')}"
            action_buttons.append(
                InlineKeyboardButton("🌐 Stream Online", url=file_web_url)
            )
        
        # Add action buttons row
        btn = nav_rows + [action_buttons]
        
        # Add close button
        btn.append([InlineKeyboardButton("❌ Close", callback_data="close_data")])
        
        return page_content, InlineKeyboardMarkup(btn)
    
    def get_page_content(self, content_data, page_index):
        """Get content for a specific page"""
        file_name = content_data["file_name"]
        visual_tags = content_data["visual_tags"]
        enhanced_metadata = content_data["enhanced_metadata"]
        imdb_data = content_data["imdb_data"]
        
        # Page 0: Overview
        if page_index == 0:
            # Format title
            if enhanced_metadata and "title" in enhanced_metadata:
                title = enhanced_metadata["title"]
            else:
                # Extract title from filename with some cleaning
                title = re.sub(r'\.(mkv|mp4|avi|mov)$', '', file_name)
                title = re.sub(r'[._]', ' ', title)
                title = re.sub(r'\[.*?\]|\(.*?\)', '', title).strip()
            
            # Start with header
            content = f"<b>🎬 {title}</b>\n\n"
            
            # Add visual tags
            if visual_tags:
                content += "<b>Tags:</b> " + " ".join(visual_tags) + "\n\n"
            
            # Add rating if available
            if imdb_data and "rating" in imdb_data and imdb_data["rating"]:
                content += f"<b>⭐ Rating:</b> {imdb_data['rating']}/10\n"
            
            # Add year if available
            if imdb_data and "year" in imdb_data and imdb_data["year"]:
                content += f"<b>📅 Year:</b> {imdb_data['year']}\n"
            
            # Add genres if available
            if imdb_data and "genres" in imdb_data and imdb_data["genres"]:
                content += f"<b>🎭 Genres:</b> {imdb_data['genres']}\n"
            
            # Add languages if available
            if imdb_data and "languages" in imdb_data and imdb_data["languages"]:
                content += f"<b>🗣️ Languages:</b> {imdb_data['languages']}\n"
            
            # Add runtime if available
            if imdb_data and "runtime" in imdb_data and imdb_data["runtime"]:
                content += f"<b>⏱️ Runtime:</b> {imdb_data['runtime']} minutes\n"
                
            return content
        
        # Page 1: Technical Details
        elif page_index == 1:
            content = f"<b>🔧 Technical Details</b>\n\n"
            
            # Add file name
            content += f"<b>📄 File:</b> {file_name}\n\n"
            
            # Add technical info from enhanced metadata
            if enhanced_metadata and "technical_info" in enhanced_metadata:
                tech_info = enhanced_metadata["technical_info"]
                
                if "resolution" in tech_info:
                    content += f"<b>📊 Resolution:</b> {tech_info['resolution']}\n"
                
                if "source" in tech_info:
                    content += f"<b>📀 Source:</b> {tech_info['source']}\n"
                
                if "codec" in tech_info:
                    content += f"<b>🎞️ Codec:</b> {tech_info['codec']}\n"
                
                if "quality" in tech_info:
                    content += f"<b>🔊 Audio:</b> {tech_info['quality']}\n"
            
            # If there's no enhanced metadata, add basic info
            if not enhanced_metadata or not enhanced_metadata.get("technical_info"):
                # Extract resolution
                resolution_match = re.search(r'(720p|1080p|2160p|4K|UHD)', file_name, re.IGNORECASE)
                if resolution_match:
                    content += f"<b>📊 Resolution:</b> {resolution_match.group(1)}\n"
                
                # Extract source
                source_match = re.search(r'(WEB-?DL|BLU-?RAY|HDRip|DVDRip|CAM|HDCAM)', file_name, re.IGNORECASE)
                if source_match:
                    content += f"<b>📀 Source:</b> {source_match.group(1)}\n"
                
                # Extract codec
                codec_match = re.search(r'(x264|x265|HEVC|AVC|H\.?264|H\.?265)', file_name, re.IGNORECASE)
                if codec_match:
                    content += f"<b>🎞️ Codec:</b> {codec_match.group(1)}\n"
                
                # Extract audio
                audio_match = re.search(r'(AAC|AAC2|DD5\.1|AC3|DOLBY|ATMOS|DTS)', file_name, re.IGNORECASE)
                if audio_match:
                    content += f"<b>🔊 Audio:</b> {audio_match.group(1)}\n"
            
            # If TV Series, add season and episode info
            if enhanced_metadata and enhanced_metadata.get("content_type") == "TV Series":
                content += f"\n<b>📺 Season {enhanced_metadata.get('season')}, Episode {enhanced_metadata.get('episode')}</b>\n"
            elif re.search(r'S(\d{1,2})E(\d{1,2})', file_name, re.IGNORECASE):
                match = re.search(r'S(\d{1,2})E(\d{1,2})', file_name, re.IGNORECASE)
                content += f"\n<b>📺 Season {match.group(1)}, Episode {match.group(2)}</b>\n"
            
            return content
        
        # Page 2: Plot
        elif page_index == 2:
            content = f"<b>📜 Plot & Cast</b>\n\n"
            
            # Add plot if available
            if imdb_data and "plot" in imdb_data and imdb_data["plot"]:
                plot = imdb_data["plot"]
                # Limit plot length
                if len(plot) > 300:
                    plot = plot[:297] + "..."
                content += f"<b>📝 Plot:</b> {plot}\n\n"
            else:
                content += "<b>📝 Plot:</b> No plot information available.\n\n"
            
            # Add cast if available
            if imdb_data and "cast" in imdb_data and imdb_data["cast"]:
                cast = imdb_data["cast"]
                # Limit cast length
                if len(cast) > 150:
                    cast = cast[:147] + "..."
                content += f"<b>👥 Cast:</b> {cast}\n\n"
            
            # Add director if available
            if imdb_data and "director" in imdb_data and imdb_data["director"]:
                content += f"<b>🎬 Director:</b> {imdb_data['director']}\n"
            
            return content
        
        # Page 3: Download options
        elif page_index == 3:
            content = f"<b>📥 Download & Stream</b>\n\n"
            
            # File name
            content += f"<b>📄 File:</b> {file_name}\n\n"
            
            # Add download instructions
            content += "<b>📲 How to Download:</b>\n"
            content += "• Click the 📥 Download button below\n"
            content += "• You'll be redirected to Telegram bot\n"
            content += "• The file will be sent to you directly\n\n"
            
            # Add streaming instructions
            content += "<b>🌐 How to Stream Online:</b>\n"
            content += "• Click the 🌐 Stream Online button\n"
            content += "• The file will open in a web player\n"
            content += "• Enjoy watching without downloading\n"
            
            return content
        
        # Fallback
        return f"<b>Preview for:</b> {file_name}"

# Create a singleton instance
preview_wizard = ContentPreviewWizard()