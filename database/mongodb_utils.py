"""
Utility functions for MongoDB database management and statistics
"""
import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URL, SECOND_DATABASE_URL, MULTI_MONGODB_URLS, DATABASE_NAME, COLLECTION_NAME

# Collect all MongoDB URLs
def get_all_mongodb_urls():
    """Get all configured MongoDB URLs"""
    urls = []
    
    # Add primary database URL
    if DATABASE_URL and DATABASE_URL.startswith('mongodb'):
        urls.append(DATABASE_URL)
    
    # Add secondary database URL if exists
    if SECOND_DATABASE_URL and SECOND_DATABASE_URL.startswith('mongodb'):
        urls.append(SECOND_DATABASE_URL)
    
    # Add additional MongoDB URLs if configured
    if MULTI_MONGODB_URLS:
        try:
            # Try to parse as JSON array
            additional_urls = json.loads(MULTI_MONGODB_URLS)
            if isinstance(additional_urls, list):
                for url in additional_urls:
                    if url and url not in urls and url.startswith('mongodb'):
                        urls.append(url)
            elif isinstance(additional_urls, str) and additional_urls.startswith('mongodb'):
                if additional_urls not in urls:
                    urls.append(additional_urls)
        except json.JSONDecodeError:
            # Handle case where it's a single URL string
            if MULTI_MONGODB_URLS.startswith('mongodb') and MULTI_MONGODB_URLS not in urls:
                urls.append(MULTI_MONGODB_URLS)
    
    return urls

async def get_mongodb_stats():
    """Get statistics for all configured MongoDB instances"""
    urls = get_all_mongodb_urls()
    stats = []
    
    for i, url in enumerate(urls):
        try:
            # Connect to MongoDB instance
            client = AsyncIOMotorClient(url)
            db = client[DATABASE_NAME]
            collection = db[COLLECTION_NAME]
            
            # Get document count
            doc_count = await collection.count_documents({})
            
            # Get database stats
            db_stats = await db.command("dbStats")
            storage_size = db_stats.get("storageSize", 0)
            storage_size_mb = round(storage_size / (1024 * 1024), 2) if storage_size else 0
            
            # Get collection stats if available
            try:
                coll_stats = await db.command("collStats", COLLECTION_NAME)
                coll_size = coll_stats.get("size", 0)
                coll_size_mb = round(coll_size / (1024 * 1024), 2) if coll_size else 0
                avg_obj_size = coll_stats.get("avgObjSize", 0)
                avg_obj_size_kb = round(avg_obj_size / 1024, 2) if avg_obj_size else 0
            except Exception:
                coll_size_mb = 0
                avg_obj_size_kb = 0
            
            # Add to stats list
            stats.append({
                "instance": f"DB #{i+1}",
                "url": url.split('@')[-1].split('/')[0],  # Extract domain only for security
                "doc_count": doc_count,
                "storage_size_mb": storage_size_mb,
                "collection_size_mb": coll_size_mb,
                "avg_obj_size_kb": avg_obj_size_kb
            })
            
            client.close()
        except Exception as e:
            stats.append({
                "instance": f"DB #{i+1}",
                "url": url.split('@')[-1].split('/')[0],  # Extract domain only for security
                "error": str(e),
                "doc_count": 0,
                "storage_size_mb": 0
            })
    
    return stats

async def move_data_between_mongodb(source_index, target_index, batch_size=100, query=None):
    """
    Move data between MongoDB instances
    
    Args:
        source_index: Index of source database in the URLs list
        target_index: Index of target database in the URLs list
        batch_size: Number of documents to process in each batch
        query: Optional filter query
    
    Returns:
        Dictionary with operation statistics
    """
    urls = get_all_mongodb_urls()
    
    if source_index >= len(urls) or target_index >= len(urls):
        return {"error": "Invalid database indices"}
    
    if source_index == target_index:
        return {"error": "Source and target databases cannot be the same"}
    
    source_url = urls[source_index]
    target_url = urls[target_index]
    
    try:
        # Connect to source and target databases
        source_client = AsyncIOMotorClient(source_url)
        source_db = source_client[DATABASE_NAME]
        source_collection = source_db[COLLECTION_NAME]
        
        target_client = AsyncIOMotorClient(target_url)
        target_db = target_client[DATABASE_NAME]
        target_collection = target_db[COLLECTION_NAME]
        
        # Set default query if not provided
        if query is None:
            query = {}
            
        # Get total count for progress tracking
        total_docs = await source_collection.count_documents(query)
        
        if total_docs == 0:
            return {"message": "No documents found in source database with specified query"}
        
        # Process in batches
        processed = 0
        duplicates = 0
        moved = 0
        errors = 0
        
        cursor = source_collection.find(query)
        batch = []
        
        async for doc in cursor:
            processed += 1
            
            # Remove MongoDB internal _id field to avoid errors
            if '_id' in doc:
                doc_id = doc['_id']
                del doc['_id']
            else:
                doc_id = None
            
            batch.append(doc)
            
            # Process batch when it reaches the specified size
            if len(batch) >= batch_size:
                try:
                    # Try to insert batch
                    result = await target_collection.insert_many(batch, ordered=False)
                    moved += len(result.inserted_ids)
                except Exception as e:
                    # Check if error is due to duplicates
                    if "duplicate key error" in str(e):
                        # Some documents were inserted, others were duplicates
                        inserted = getattr(e, 'details', {}).get('nInserted', 0)
                        moved += inserted
                        duplicates += (len(batch) - inserted)
                    else:
                        errors += len(batch)
                        print(f"Error during batch insert: {e}")
                
                # Clear batch for next iteration
                batch = []
        
        # Process remaining documents in the last batch
        if batch:
            try:
                result = await target_collection.insert_many(batch, ordered=False)
                moved += len(result.inserted_ids)
            except Exception as e:
                if "duplicate key error" in str(e):
                    inserted = getattr(e, 'details', {}).get('nInserted', 0)
                    moved += inserted
                    duplicates += (len(batch) - inserted)
                else:
                    errors += len(batch)
                    print(f"Error during final batch insert: {e}")
        
        return {
            "total_documents": total_docs,
            "processed": processed,
            "moved": moved,
            "duplicates": duplicates,
            "errors": errors,
            "source": f"DB #{source_index+1}",
            "target": f"DB #{target_index+1}"
        }
    
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Close connections
        source_client.close()
        target_client.close()