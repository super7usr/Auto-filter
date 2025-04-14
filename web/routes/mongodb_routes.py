"""
MongoDB management routes for admin dashboard
"""
import os
import json
import logging
from aiohttp import web
from web.utils.admin_utils import admin_auth_required
from database.mongodb_utils import get_mongodb_stats, move_data_between_mongodb, get_all_mongodb_urls
from info import DATABASE_URL, SECOND_DATABASE_URL, MULTI_MONGODB_URLS

logger = logging.getLogger(__name__)

# Create routes
routes = web.RouteTableDef()

@routes.get('/admin/mongodb')
@admin_auth_required
async def admin_mongodb_page(request):
    """Render the MongoDB management page"""
    
    # Get MongoDB URLs (masked for security)
    primary_db_url = "Not configured"
    if DATABASE_URL:
        # Show only domain, not username/password
        parts = DATABASE_URL.split('@')
        if len(parts) > 1:
            primary_db_url = f"mongodb://*****@{parts[-1]}"
        else:
            primary_db_url = DATABASE_URL
    
    secondary_db_url = "Not configured"
    if SECOND_DATABASE_URL:
        parts = SECOND_DATABASE_URL.split('@')
        if len(parts) > 1:
            secondary_db_url = f"mongodb://*****@{parts[-1]}"
        else:
            secondary_db_url = SECOND_DATABASE_URL
    
    additional_db_count = 0
    if MULTI_MONGODB_URLS:
        try:
            urls = json.loads(MULTI_MONGODB_URLS)
            if isinstance(urls, list):
                additional_db_count = len(urls)
            elif isinstance(urls, str):
                additional_db_count = 1
        except json.JSONDecodeError:
            if MULTI_MONGODB_URLS.startswith(('mongodb://', 'mongodb+srv://')):
                additional_db_count = 1
    
    # Load and render the template
    with open('web/template/admin_mongodb.html', 'r') as file:
        html = file.read()
    
    # Replace placeholders with actual data
    html = html.replace('{{primary_db_url}}', primary_db_url)
    html = html.replace('{{secondary_db_url}}', secondary_db_url)
    html = html.replace('{{additional_db_count}}', str(additional_db_count))
    
    return web.Response(text=html, content_type='text/html')

@routes.get('/api/admin/mongodb/status')
@admin_auth_required
async def api_mongodb_status(request):
    """API endpoint to get MongoDB status"""
    try:
        # Get MongoDB stats
        stats = await get_mongodb_stats()
        
        # Format stats for the API response
        databases = []
        for db in stats:
            database_info = {
                'name': db['instance'],
                'domain': db.get('url', 'unknown'),
                'documentCount': db.get('doc_count', 0),
                'storageSize': db.get('storage_size_mb', 0),
                'collectionSize': db.get('collection_size_mb', 0),
                'avgObjSize': db.get('avg_obj_size_kb', 0),
                'status': 'online' if 'error' not in db else 'offline'
            }
            
            if 'error' in db:
                database_info['error'] = db['error']
                
            databases.append(database_info)
        
        return web.json_response({
            'success': True,
            'databases': databases,
            'totalDatabases': len(databases)
        })
    except Exception as e:
        logger.error(f"Error getting MongoDB status: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)

@routes.post('/api/admin/mongodb/migrate')
@admin_auth_required
async def api_mongodb_migrate(request):
    """API endpoint to start data migration between MongoDB instances"""
    try:
        # Parse request body
        data = await request.json()
        source_db = int(data.get('sourceDb', -1))
        target_db = int(data.get('targetDb', -1))
        
        # Validate parameters
        urls = get_all_mongodb_urls()
        if source_db < 0 or source_db >= len(urls):
            return web.json_response({
                'success': False,
                'error': 'Invalid source database'
            }, status=400)
            
        if target_db < 0 or target_db >= len(urls):
            return web.json_response({
                'success': False,
                'error': 'Invalid target database'
            }, status=400)
            
        if source_db == target_db:
            return web.json_response({
                'success': False,
                'error': 'Source and target databases cannot be the same'
            }, status=400)
        
        # Start migration in the background
        import asyncio
        operation_id = f"migrate_{source_db}_to_{target_db}_{int(asyncio.get_event_loop().time())}"
        
        async def run_migration():
            try:
                result = await move_data_between_mongodb(source_db, target_db)
                logger.info(f"Migration completed: {result}")
            except Exception as e:
                logger.error(f"Migration failed: {e}")
        
        # Start migration task
        asyncio.create_task(run_migration())
        
        return web.json_response({
            'success': True,
            'message': 'Migration started',
            'operationId': operation_id,
            'sourceDb': source_db,
            'targetDb': target_db
        })
    except Exception as e:
        logger.error(f"Error starting migration: {e}")
        return web.json_response({
            'success': False,
            'error': str(e)
        }, status=500)