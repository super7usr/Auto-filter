import logging
import motor.motor_asyncio
from typing import Dict, Union, Optional, List
from info import DATABASE_URI

logger = logging.getLogger(__name__)

class AdsDB:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)
        self.db = self.client["Autofilter"]
        self.ads_col = self.db["ads_settings"]
        
    async def create_default_settings(self):
        """Create default settings for ads if not already present"""
        settings = {
            'ads_code': '',
            'frequency': 5,  # How often to show ads (every X results)
            'enabled': False,  # Whether ads are enabled
            'detect_adblock': True,  # Whether to detect adblock
            'adblock_message': 'We noticed you\'re using an ad blocker. Please disable it to support this service.'
        }
        
        await self.ads_col.insert_one(settings)
        return settings
    
    async def get_ads_settings(self) -> Dict:
        """Retrieve current ad settings"""
        settings = await self.ads_col.find_one()
        
        if not settings:
            # Create default settings if none exist
            settings = await self.create_default_settings()
            
        return settings
    
    async def update_ads_settings(self, 
                                 ads_code: Optional[str] = None,
                                 frequency: Optional[int] = None,
                                 enabled: Optional[bool] = None,
                                 detect_adblock: Optional[bool] = None,
                                 adblock_message: Optional[str] = None) -> Dict:
        """Update ad settings with provided values"""
        settings = await self.get_ads_settings()
        update_data = {}
        
        # Only update fields that are provided
        if ads_code is not None:
            update_data['ads_code'] = ads_code
        
        if frequency is not None:
            update_data['frequency'] = frequency
        
        if enabled is not None:
            update_data['enabled'] = enabled
            
        if detect_adblock is not None:
            update_data['detect_adblock'] = detect_adblock
            
        if adblock_message is not None:
            update_data['adblock_message'] = adblock_message
        
        if update_data:
            await self.ads_col.update_one(
                {'_id': settings['_id']},
                {'$set': update_data}
            )
            
        # Return updated settings
        return await self.get_ads_settings()

# Initialize the database singleton
ads_db = AdsDB()