import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
import os
import json
from info import USE_CAPTION_FILTER, DATABASE_URL, SECOND_DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, MAX_BTN

# Enhanced to support multiple MongoDB instances
MULTI_MONGODB_URLS = os.environ.get('MULTI_MONGODB_URLS', '')
mongodb_urls = []

# Add primary database URL
if DATABASE_URL and DATABASE_URL.startswith('mongodb'):
    mongodb_urls.append(DATABASE_URL)

# Add secondary database URL if exists
if SECOND_DATABASE_URL and SECOND_DATABASE_URL.startswith('mongodb'):
    mongodb_urls.append(SECOND_DATABASE_URL)

# Add additional MongoDB URLs if configured
if MULTI_MONGODB_URLS:
    try:
        additional_urls = json.loads(MULTI_MONGODB_URLS)
        if isinstance(additional_urls, list):
            for url in additional_urls:
                if url and url not in mongodb_urls and url.startswith('mongodb'):
                    mongodb_urls.append(url)
        elif isinstance(additional_urls, str) and additional_urls.startswith('mongodb'):
            if additional_urls not in mongodb_urls:
                mongodb_urls.append(additional_urls)
    except json.JSONDecodeError:
        # Handle case where it's a single URL string
        if MULTI_MONGODB_URLS.startswith('mongodb') and MULTI_MONGODB_URLS not in mongodb_urls:
            mongodb_urls.append(MULTI_MONGODB_URLS)

# Print MongoDB configuration (redacted for security)
print(f"Using {len(mongodb_urls)} MongoDB instances")

# Check if we're using PostgreSQL
if DATABASE_URL and not DATABASE_URL.startswith('mongodb'):
    from database.sql_adapter import db_adapter, Media
    using_postgres = True
else:
    # Use MongoDB
    from pymongo.errors import DuplicateKeyError, OperationFailure 
    from umongo import Instance, Document, fields
    from motor.motor_asyncio import AsyncIOMotorClient
    from marshmallow.exceptions import ValidationError
    
    using_postgres = False
    
    # Initialize MongoDB clients, databases, and models
    mongo_clients = []
    mongo_dbs = []
    mongo_instances = []
    mongo_models = []
    
    for i, mongo_uri in enumerate(mongodb_urls):
        print(f"Connecting to MongoDB #{i+1}")
        client = AsyncIOMotorClient(mongo_uri)
        db = client[DATABASE_NAME]
        instance = Instance.from_db(db)
        
        # Create Media model for this instance
        @instance.register
        class MediaModel(Document):
            file_id = fields.StrField(attribute='_id', default=None)
            file_name = fields.StrField(required=True)
            file_size = fields.IntField(required=True)
            caption = fields.StrField(allow_none=True)
        
            class Meta:
                indexes = ('$file_name', )
                collection_name = COLLECTION_NAME
                strict = False
        
        mongo_clients.append(client)
        mongo_dbs.append(db)
        mongo_instances.append(instance)
        mongo_models.append(MediaModel)
    
    # Set the primary Media model (for backward compatibility)
    if mongo_models:
        Media = mongo_models[0]
        
    # Legacy support for the second database
    if len(mongo_models) > 1:
        SecondMedia = mongo_models[1]


async def save_file(media):
    """Save file in database with support for multiple MongoDB instances"""
    
    if using_postgres:
        # PostgreSQL version
        file_id = unpack_new_file_id(media.file_id)
        file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.file_name))
        file_caption = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.caption))
        
        media_data = {
            "file_id": file_id,
            "file_name": file_name,
            "file_size": media.file_size,
            "caption": file_caption
        }
        
        result = db_adapter.save_file(media_data)
        if result:
            print(f'Saved - {file_name}')
            return 'suc'
        else:
            print(f'Already Saved - {file_name}')
            return 'dup'
    else:
        # MongoDB version
        # TODO: Find better way to get same file_id for same media to avoid duplicates
        file_id = unpack_new_file_id(media.file_id)
        file_name = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.file_name))
        file_caption = re.sub(r"@\w+|(_|\-|\.|\+)", " ", str(media.caption))
        
        # Check if file exists in any database first (to avoid duplicate attempts)
        for i, model in enumerate(mongo_models):
            try:
                exists = await model.find_one({'_id': file_id})
                if exists:
                    print(f'Already saved in DB #{i+1} - {file_name}')
                    return 'dup'
            except Exception as e:
                print(f'Error checking DB #{i+1}: {e}')
        
        # Try to save to each database in order until successful
        for i, model in enumerate(mongo_models):
            try:
                file = model(
                    file_id=file_id,
                    file_name=file_name,
                    file_size=media.file_size,
                    caption=file_caption
                )
                await file.commit()
                print(f'Saved to DB #{i+1} - {file_name}')
                return 'suc'
            except ValidationError:
                print(f'Validation error in DB #{i+1} - {file_name}')
                continue
            except DuplicateKeyError:
                print(f'Already saved in DB #{i+1} - {file_name}')
                return 'dup'
            except OperationFailure as e:
                print(f'Operation failure in DB #{i+1}: {e}')
                continue
            except Exception as e:
                print(f'Error saving to DB #{i+1}: {e}')
                continue
        
        # If we get here, all databases failed
        print(f'Failed to save to any database - {file_name}')
        return 'err'

async def get_search_results(query, max_results=MAX_BTN, offset=0, lang=None):
    """Search for files across all configured MongoDB instances"""
    query = str(query) # to ensure the query is string to stripe.
    query = query.strip()
    
    if using_postgres:
        # PostgreSQL version
        results = db_adapter.get_search_results(query, max_results=max_results, offset=offset)
        
        # Convert PostgreSQL results to match MongoDB format
        files = []
        for result in results:
            file_dict = result.copy()
            # Add _id field to match MongoDB format
            file_dict['_id'] = file_dict['file_id']
            
            # Convert dict to object for compatibility
            class FileObject:
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        setattr(self, key, value)
            
            file_obj = FileObject(**file_dict)
            files.append(file_obj)
        
        # Handle language filtering if specified
        if lang:
            lang_files = [file for file in files if lang in file.file_name.lower()]
            filtered_files = lang_files[:max_results]
            total_results = len(lang_files)
            next_offset = offset + max_results
            if next_offset >= total_results:
                next_offset = ''
            return filtered_files, next_offset, total_results
        
        total_results = len(files)
        next_offset = offset + max_results
        if next_offset >= total_results:
            next_offset = ''
        return files, next_offset, total_results
    else:
        # MongoDB version
        if not query:
            raw_pattern = '.'
        elif ' ' not in query:
            raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
        else:
            raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]') 
        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except:
            regex = query
    
        if USE_CAPTION_FILTER:
            filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
        else:
            filter = {'file_name': regex}
    
        # Search across all MongoDB instances
        results = []
        for i, model in enumerate(mongo_models):
            try:
                cursor = model.find(filter)
                db_results = [doc async for doc in cursor]
                if db_results:
                    print(f"Found {len(db_results)} results in DB #{i+1}")
                    results.extend(db_results)
            except Exception as e:
                print(f"Error searching DB #{i+1}: {e}")
    
        if lang:
            lang_files = [file for file in results if lang in file.file_name.lower()]
            files = lang_files[offset:][:max_results]
            total_results = len(lang_files)
            next_offset = offset + max_results
            if next_offset >= total_results:
                next_offset = ''
            return files, next_offset, total_results
            
        total_results = len(results)
        files = results[offset:][:max_results]
        next_offset = offset + max_results
        if next_offset >= total_results:
            next_offset = ''   
        return files, next_offset, total_results
    
    
async def delete_files(query):
    """Delete files across all MongoDB instances that match the query"""
    query = query.strip()
    
    if using_postgres:
        # PostgreSQL version
        total = db_adapter.delete_files(query)
        # Return minimal info needed for the response
        class FilesCursor:
            def __init__(self, count):
                self.count = count
                
            async def to_list(self, length=0):
                return [{"file_name": f"Deleted {self.count} files"}]
                
        return total, FilesCursor(total)
    else:
        # MongoDB version
        if not query:
            raw_pattern = '.'
        elif ' ' not in query:
            raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
        else:
            raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
        
        try:
            regex = re.compile(raw_pattern, flags=re.IGNORECASE)
        except:
            regex = query
        
        filter = {'file_name': regex}
        total_deleted = 0
        deleted_filenames = []
        
        # Delete from all MongoDB instances
        for i, model in enumerate(mongo_models):
            try:
                # Count documents before deletion
                db_total = await model.count_documents(filter)
                if db_total > 0:
                    # Get file names for reporting
                    cursor = model.find(filter)
                    files = [doc async for doc in cursor]
                    for file in files:
                        deleted_filenames.append(file.file_name)
                    
                    # Delete the files
                    await model.collection.delete_many(filter)
                    print(f"Deleted {db_total} files from DB #{i+1}")
                    total_deleted += db_total
            except Exception as e:
                print(f"Error deleting from DB #{i+1}: {e}")
        
        # Return results in format expected by the bot
        class FilesCursor:
            def __init__(self, files):
                self.files = files
                
            async def to_list(self, length=0):
                return [{"file_name": filename} for filename in self.files[:length or len(self.files)]]
        
        return total_deleted, FilesCursor(deleted_filenames)

async def get_file_details(query):
    """Get file details from all MongoDB instances"""
    if using_postgres:
        # PostgreSQL version
        file_details = db_adapter.get_file_details(query)
        
        # Convert to list of objects to match MongoDB format
        results = []
        for file_dict in file_details:
            # Add _id field to match MongoDB format
            file_dict['_id'] = file_dict['file_id']
            
            # Convert dict to object for compatibility
            class FileObject:
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        setattr(self, key, value)
            
            file_obj = FileObject(**file_dict)
            results.append(file_obj)
            
        return results
    else:
        # MongoDB version - search all databases
        filter = {'file_id': query}
        results = []
        
        # Search in all MongoDB instances
        for i, model in enumerate(mongo_models):
            try:
                cursor = model.find(filter)
                files = await cursor.to_list(length=1)
                if files:
                    print(f"Found file details in DB #{i+1}")
                    results.extend(files)
                    # If we found the file, no need to check other DBs
                    break
            except Exception as e:
                print(f"Error getting file details from DB #{i+1}: {e}")
        
        return results

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id

async def get_mood_results(primary_keyword, additional_keywords=None, offset=0, max_results=MAX_BTN):
    """
    Search for content based on mood keywords
    
    Args:
        primary_keyword: The main mood keyword to search for
        additional_keywords: Additional mood keywords to enhance the search
        offset: The offset for pagination
        max_results: Maximum number of results to return
        
    Returns:
        Tuple of (files, next_offset, total_results)
    """
    if additional_keywords is None:
        additional_keywords = []
    
    # Get base results using primary keyword
    files, next_offset, total_results = await get_search_results(primary_keyword, offset, max_results)
    
    # If we have additional keywords, filter the results
    if additional_keywords and files:
        # Create a combined pattern of all additional keywords
        pattern = '|'.join(additional_keywords)
        try:
            regex = re.compile(pattern, flags=re.IGNORECASE)
            
            # Filter files that match any additional keyword
            enhanced_files = []
            for file in files:
                if regex.search(file.file_name.lower()) or (hasattr(file, 'caption') and file.caption and regex.search(file.caption.lower())):
                    enhanced_files.append(file)
            
            if enhanced_files:
                # We found files matching additional keywords, use these
                total_enhanced = len(enhanced_files)
                next_offset = offset + max_results
                if next_offset >= total_enhanced:
                    next_offset = ''
                return enhanced_files, next_offset, total_enhanced
        except:
            # If regex fails, continue with original results
            pass
    
    # Return original results if no additional filtering or if filtering didn't work
    return files, next_offset, total_results
