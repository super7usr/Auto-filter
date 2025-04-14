"""
Ads handler utility for search results
"""
import logging
import re
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_ads_settings():
    """Get the current ad settings from the database"""
    try:
        from database.ads_db import ads_db
        return await ads_db.get_ads_settings()
    except Exception as e:
        logger.error(f"Error retrieving ad settings: {e}")
        # Return default settings
        return {
            'ads_code': '',
            'frequency': 5,
            'enabled': False,
            'detect_adblock': True,
            'adblock_message': 'We noticed you\'re using an ad blocker. Please disable it to support this service.'
        }

async def inject_ads_into_results(results: List[Dict], ad_positions: Optional[List[int]] = None) -> Tuple[List[Dict], bool]:
    """
    Inject ads into search results at calculated positions
    
    Args:
        results: List of search result items
        ad_positions: Optional list of positions to inject ads (if None, calculated based on settings)
        
    Returns:
        Tuple of (modified_results, has_ads)
    """
    try:
        # Get current ad settings
        settings = await get_ads_settings()
        
        # Check if ads are enabled and if we have ad code
        if not settings.get('enabled', False) or not settings.get('ads_code', '').strip():
            return results, False
        
        # Get the ad code
        ad_code = settings.get('ads_code', '').strip()
        
        # Get frequency
        frequency = settings.get('frequency', 5)
        
        # Calculate ad positions if not provided
        if ad_positions is None:
            ad_positions = [i * frequency for i in range(1, (len(results) // frequency) + 1)]
            
        # Create lightbox ad wrapper
        ad_html = create_lightbox_ad(ad_code, settings.get('detect_adblock', True), 
                                    settings.get('adblock_message', ''))
        
        # Inject ads at calculated positions
        modified_results = results.copy()
        offset = 0
        
        for pos in ad_positions:
            # Adjusted position accounting for previously added ads
            adjusted_pos = pos + offset
            
            # Don't add after the end of the list
            if adjusted_pos > len(modified_results):
                break
                
            # Create ad item
            ad_item = {
                'is_ad': True,
                'ad_html': ad_html
            }
            
            # Insert ad at the position
            modified_results.insert(adjusted_pos, ad_item)
            offset += 1
            
        return modified_results, True
        
    except Exception as e:
        logger.error(f"Error injecting ads: {e}")
        return results, False

def create_lightbox_ad(ad_code: str, detect_adblock: bool = True, adblock_message: str = '') -> str:
    """
    Create a lightbox HTML container for the ad
    
    Args:
        ad_code: The ad code to include
        detect_adblock: Whether to detect ad blockers
        adblock_message: Message to show when ad blocker is detected
        
    Returns:
        HTML string for the lightbox ad
    """
    # Generate a unique ID for each ad lightbox to avoid conflicts
    import uuid
    unique_id = str(uuid.uuid4()).replace('-', '')
    
    # Basic styling for the lightbox
    lightbox_html = f"""
    <div class="search-result-item ad-item">
        <div class="ad-trigger-container" onclick="showAdLightbox_{unique_id}()">
            <div class="sponsored-badge">
                <i class="fas fa-ad"></i> Sponsored
            </div>
            <div class="ad-trigger">
                <div class="ad-preview">
                    <i class="fas fa-bullhorn fa-2x"></i>
                    <h4>Special Offer</h4>
                    <p>Click to view this sponsored content</p>
                    <button class="btn btn-primary btn-sm">View Now</button>
                </div>
            </div>
        </div>
    </div>

    <div class="ad-lightbox" id="adLightbox_{unique_id}">
        <div class="ad-lightbox-content">
            <div class="ad-lightbox-header">
                <h5 class="ad-title">Sponsored Content</h5>
                <button type="button" class="ad-close-btn" onclick="closeAdLightbox_{unique_id}()">&times;</button>
            </div>
            <div class="ad-lightbox-body">
                <div class="ad-container" id="adContainer_{unique_id}">
                    {ad_code}
                </div>
                
                <div class="ad-blocker-message" id="adBlockMessage_{unique_id}" style="display: none;">
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>{adblock_message}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <style>
        .sponsored-badge {{
            background-color: rgba(0, 114, 255, 0.1);
            color: #0088ff;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            display: inline-block;
            margin-bottom: 8px;
        }}
        
        .ad-trigger-container {{
            cursor: pointer;
            padding: 15px;
            border-radius: 8px;
            background: linear-gradient(145deg, #071428, #0a1d3a);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            margin-bottom: 20px;
        }}
        
        .ad-trigger-container:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0, 114, 255, 0.2);
            border-color: rgba(0, 114, 255, 0.3);
        }}
        
        .ad-preview {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 15px;
            color: rgba(255, 255, 255, 0.9);
            text-align: center;
        }}
        
        .ad-preview i {{
            color: #0088ff;
            margin-bottom: 15px;
        }}
        
        .ad-preview h4 {{
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .ad-preview p {{
            margin-bottom: 15px;
            color: rgba(255, 255, 255, 0.7);
        }}
        
        .ad-lightbox {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            z-index: 10000;
            justify-content: center;
            align-items: center;
        }}
        
        .ad-lightbox-content {{
            background-color: #091634;
            border-radius: 10px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 0 30px rgba(0, 114, 255, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
            animation: adFadeIn_{unique_id} 0.4s ease-out;
        }}
        
        @keyframes adFadeIn_{unique_id} {{
            from {{
                opacity: 0;
                transform: scale(0.9);
            }}
            to {{
                opacity: 1;
                transform: scale(1);
            }}
        }}
        
        .ad-lightbox-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .ad-title {{
            margin: 0;
            font-size: 1.1rem;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.7);
        }}
        
        .ad-close-btn {{
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.7);
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
            line-height: 1;
            padding: 0;
            margin: 0;
        }}
        
        .ad-close-btn:hover {{
            color: white;
            transform: scale(1.1);
        }}
        
        .ad-lightbox-body {{
            padding: 1.5rem;
        }}
        
        .ad-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 250px;
        }}
        
        .ad-sponsored-label {{
            text-align: center;
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.4);
            margin-top: 1rem;
        }}
        
        .ad-blocker-message {{
            text-align: center;
            padding: 1rem;
        }}
        
        .ad-blocker-message i {{
            font-size: 2rem;
            color: #f59e0b;
            margin-bottom: 1rem;
        }}
        
        .ad-btn {{
            display: inline-block;
            background: linear-gradient(45deg, #0072ff, #00c6ff);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            margin-top: 0.5rem;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .ad-btn:hover {{
            background: linear-gradient(45deg, #0066e8, #00b4f0);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 114, 255, 0.4);
        }}
    </style>
    
    <script>
        // Function to show the ad lightbox
        function showAdLightbox_{unique_id}() {{
            const lightbox = document.getElementById('adLightbox_{unique_id}');
            if (lightbox) {{
                lightbox.style.display = 'flex';
                // Check for ad blockers after opening
                checkAdBlocker_{unique_id}();
            }}
        }}
        
        // Function to close the ad lightbox
        function closeAdLightbox_{unique_id}() {{
            const lightbox = document.getElementById('adLightbox_{unique_id}');
            if (lightbox) {{
                lightbox.style.display = 'none';
            }}
        }}
        
        // Check for ad blockers
        function checkAdBlocker_{unique_id}() {{
            const detectAdBlock = {str(detect_adblock).lower()};
            
            if (!detectAdBlock) return;
            
            setTimeout(function() {{
                const adContainer = document.getElementById('adContainer_{unique_id}');
                const adBlockerMessage = document.getElementById('adBlockMessage_{unique_id}');
                
                // Simple check - if ad container height is 0 or very small, likely blocked
                if (adContainer && (adContainer.offsetHeight < 10 || adContainer.innerHTML.trim() === '')) {{
                    // Hide ad container
                    adContainer.style.display = 'none';
                    
                    // Show message
                    if (adBlockerMessage) {{
                        adBlockerMessage.style.display = 'block';
                    }}
                }}
            }}, 1000); // Check after 1 second to allow ads to load
        }}
        
        // Close when clicking outside the content
        document.getElementById('adLightbox_{unique_id}').addEventListener('click', function(e) {{
            if (e.target === this) {{
                closeAdLightbox_{unique_id}();
            }}
        }});
    </script>
    """
    
    return lightbox_html

def add_ads_to_html(html: str, positions: List[int], ad_html: str) -> str:
    """
    Add ads to HTML content at specified positions
    
    Args:
        html: The HTML content
        positions: List of positions to inject ads
        ad_html: The ad HTML to inject
        
    Returns:
        Modified HTML with ads
    """
    # This is a simplistic implementation that would need to be adjusted
    # based on the actual HTML structure
    lines = html.split('\n')
    offset = 0
    
    for pos in positions:
        adjusted_pos = pos + offset
        if adjusted_pos < len(lines):
            lines.insert(adjusted_pos, ad_html)
            offset += 1
            
    return '\n'.join(lines)

def render_ad_item(item: Dict) -> str:
    """
    Render an ad item
    
    Args:
        item: The ad item dictionary
        
    Returns:
        HTML string for the ad
    """
    if item.get('is_ad'):
        return item.get('ad_html', '')
    return ''