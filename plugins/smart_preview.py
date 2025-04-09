import re
import json
from datetime import datetime
from utils import get_poster
from info import ADMINS, LONG_IMDB_DESCRIPTION
import logging

logger = logging.getLogger(__name__)

class SmartContentAnalyzer:
    """Class to analyze media content and provide smart insights"""
    
    def __init__(self):
        """Initialize the analyzer"""
        self.title_patterns = {
            "year": r'\b(19\d{2}|20\d{2})\b',
            "resolution": r'\b(720p|1080p|2160p|4K|UHD|HD|FULL\s*HD)\b',
            "language": r'\b(MULTI|DUAL|DUBBED|ORG|ENGLISH|HINDI|TAMIL|TELUGU)\b',
            "source": r'\b(WEB-?DL|BLU-?RAY|HDRip|DVDRip|CAM|HDCAM|DVD)\b',
            "codec": r'\b(x264|x265|HEVC|AVC|H\.?264|H\.?265)\b',
            "quality": r'\b(AAC|AAC2|DD5\.1|AC3|DOLBY|ATMOS|DTS)\b',
        }
    
    def extract_features_from_filename(self, filename):
        """Extract features from the filename"""
        features = {}
        
        # Convert to uppercase for case-insensitive matching
        upper_filename = filename.upper()
        
        # Extract each feature type
        for feature_type, pattern in self.title_patterns.items():
            matches = re.findall(pattern, upper_filename, re.IGNORECASE)
            if matches:
                features[feature_type] = matches[0]
        
        # Clean up the title by removing known patterns
        clean_title = filename
        for pattern in self.title_patterns.values():
            clean_title = re.sub(pattern, '', clean_title, flags=re.IGNORECASE)
        
        # Remove common separators and clean up
        clean_title = re.sub(r'[._\-\[\]()]', ' ', clean_title)
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
        
        # Try to extract the base name (assumes the first part before any technical terms)
        base_name_match = re.match(r'^(.*?)(?:\s+\d{4}|\s+720p|\s+1080p|\s+S\d{2}E\d{2})', clean_title, re.IGNORECASE)
        if base_name_match:
            features['base_name'] = base_name_match.group(1).strip()
        else:
            features['base_name'] = clean_title
        
        # Check for TV Series pattern (SxxExx)
        series_match = re.search(r'S(\d{1,2})E(\d{1,2})', filename, re.IGNORECASE)
        if series_match:
            features['content_type'] = 'TV Series'
            features['season'] = int(series_match.group(1))
            features['episode'] = int(series_match.group(2))
        else:
            features['content_type'] = 'Movie'
        
        return features
    
    async def get_enhanced_metadata(self, search_query, filename):
        """Get enhanced metadata combining filename analysis and IMDb data"""
        features = self.extract_features_from_filename(filename)
        
        # Get IMDb data
        imdb_data = await get_poster(search_query, file=filename)
        
        # Combine the data
        metadata = {
            "title": features.get('base_name', ''),
            "content_type": features.get('content_type', 'Movie'),
            "technical_info": {},
            "imdb_data": imdb_data if imdb_data else {}
        }
        
        # Add technical information
        for key in ['resolution', 'language', 'source', 'codec', 'quality', 'year']:
            if key in features:
                metadata['technical_info'][key] = features[key]
        
        # Add season/episode info if it's a TV series
        if features.get('content_type') == 'TV Series':
            metadata['season'] = features.get('season')
            metadata['episode'] = features.get('episode')
        
        return metadata
    
    def generate_smart_preview(self, metadata):
        """Generate a smart preview card with the metadata"""
        # Base preview with title and type
        preview = f"🎬 <b>{metadata['title']}</b>\n\n"
        
        # Add content type and year
        content_type = metadata['content_type']
        preview += f"📋 <b>Type:</b> {content_type}\n"
        
        # Add year if available
        if metadata['technical_info'].get('year'):
            preview += f"📅 <b>Year:</b> {metadata['technical_info']['year']}\n"
        elif metadata['imdb_data'] and metadata['imdb_data'].get('year'):
            preview += f"📅 <b>Year:</b> {metadata['imdb_data']['year']}\n"
        
        # Add IMDb rating if available
        if metadata['imdb_data'] and metadata['imdb_data'].get('rating'):
            preview += f"⭐ <b>IMDb:</b> {metadata['imdb_data']['rating']}/10\n"
        
        # Add language if available
        if metadata['technical_info'].get('language'):
            preview += f"🗣️ <b>Language:</b> {metadata['technical_info']['language']}\n"
        elif metadata['imdb_data'] and metadata['imdb_data'].get('languages'):
            preview += f"🗣️ <b>Language(s):</b> {metadata['imdb_data']['languages']}\n"
        
        # Add resolution and quality
        if metadata['technical_info'].get('resolution'):
            preview += f"📊 <b>Resolution:</b> {metadata['technical_info']['resolution']}\n"
        
        # Add source
        if metadata['technical_info'].get('source'):
            preview += f"🎞️ <b>Source:</b> {metadata['technical_info']['source']}\n"
        
        # For TV Series, add season and episode
        if content_type == 'TV Series' and 'season' in metadata and 'episode' in metadata:
            preview += f"📺 <b>Season {metadata['season']}, Episode {metadata['episode']}</b>\n"
        
        # Add genres if available from IMDb
        if metadata['imdb_data'] and metadata['imdb_data'].get('genres'):
            preview += f"🎭 <b>Genres:</b> {metadata['imdb_data']['genres']}\n"
        
        # Add a short plot if available
        if metadata['imdb_data'] and metadata['imdb_data'].get('plot'):
            plot = metadata['imdb_data']['plot']
            # Truncate plot if too long
            if len(plot) > 150:
                plot = plot[:147] + "..."
            preview += f"\n📝 <b>Plot:</b> {plot}\n"
        
        # Add technical details section
        tech_details = []
        if metadata['technical_info'].get('codec'):
            tech_details.append(f"Codec: {metadata['technical_info']['codec']}")
        if metadata['technical_info'].get('quality'):
            tech_details.append(f"Audio: {metadata['technical_info']['quality']}")
        
        if tech_details:
            preview += f"\n🔧 <b>Technical:</b> {' | '.join(tech_details)}\n"
        
        return preview

# Create a singleton instance
smart_analyzer = SmartContentAnalyzer()