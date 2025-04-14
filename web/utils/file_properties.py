from pyrogram import Client
from typing import Any, Optional
from pyrogram.types import Message
from pyrogram.file_id import FileId
from pyrogram.raw.types.messages import Messages
from utils import temp

class FileNotFound(Exception):
    """
    Exception raised when a file is not found.
    """
    def __init__(self, message="File not found"):
        self.message = message
        super().__init__(self.message)

async def parse_file_id(message: "Message") -> Optional[FileId]:
    """
    Parse a file_id from a Message object.
    """
    media = get_media_from_message(message)
    if media:
        return FileId.decode(media.file_id)

async def parse_file_unique_id(message: "Messages") -> Optional[str]:
    """
    Parse a file_unique_id from a Message object.
    """
    media = get_media_from_message(message)
    if media:
        return media.file_unique_id

async def get_file_ids(client: Client, chat_id: int, id: int) -> Optional[FileId]:
    """
    Get file properties from a message.
    Returns a FileId object with additional attributes.
    """
    message = await client.get_messages(chat_id, id)
    if message.empty:
        raise FileNotFound
    
    media = get_media_from_message(message)
    if not media:
        raise FileNotFound("No media found in message")
    
    file_unique_id = media.file_unique_id
    file_id = await parse_file_id(message)
    
    if not file_id:
        raise FileNotFound("Could not parse file ID")
    
    # Set additional attributes on the FileId object
    setattr(file_id, "file_size", getattr(media, "file_size", 0))
    setattr(file_id, "mime_type", getattr(media, "mime_type", ""))
    setattr(file_id, "file_name", getattr(media, "file_name", ""))
    setattr(file_id, "unique_id", file_unique_id)
    
    return file_id

def get_media_from_message(message: "Message") -> Any:
    """
    Extract media object from a Message.
    Returns None if no media is found.
    """
    media_types = (
        "audio",
        "document",
        "photo",
        "sticker",
        "animation",
        "video",
        "voice",
        "video_note",
    )
    for attr in media_types:
        media = getattr(message, attr, None)
        if media:
            return media
    return None

def get_hash(media_msg: Message) -> str:
    """
    Get a short hash from the media message for verification.
    """
    media = get_media_from_message(media_msg)
    return getattr(media, "file_unique_id", "")[:6]

def get_name(media_msg: Message) -> str:
    """
    Get the filename from a media message.
    """
    media = get_media_from_message(media_msg)
    return getattr(media, 'file_name', "")

def get_media_file_size(m: Message) -> int:
    """
    Get the file size of a media message.
    """
    media = get_media_from_message(m)
    return getattr(media, "file_size", 0)