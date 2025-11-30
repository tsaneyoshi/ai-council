"""JSON-based storage for conversations."""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from .config import DATA_DIR

logger = logging.getLogger(__name__)


def ensure_data_dir():
    """Ensure the data directory exists."""
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)


def get_conversation_path(conversation_id: str) -> str:
    """Get the file path for a conversation."""
    return os.path.join(DATA_DIR, f"{conversation_id}.json")


def create_conversation(conversation_id: str) -> Dict[str, Any]:
    """
    Create a new conversation.

    Args:
        conversation_id: Unique identifier for the conversation

    Returns:
        New conversation dict
    """
    ensure_data_dir()

    conversation = {
        "id": conversation_id,
        "created_at": datetime.utcnow().isoformat(),
        "title": "New Conversation",
        "messages": []
    }

    # Save to file
    path = get_conversation_path(conversation_id)
    with open(path, 'w') as f:
        json.dump(conversation, f, indent=2)

    return conversation


def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """
    Load a conversation from storage.

    Args:
        conversation_id: Unique identifier for the conversation

    Returns:
        Conversation dict or None if not found
    """
    path = get_conversation_path(conversation_id)

    if not os.path.exists(path):
        return None

    with open(path, 'r') as f:
        return json.load(f)


def save_conversation(conversation: Dict[str, Any]):
    """
    Save a conversation to storage.

    Args:
        conversation: Conversation dict to save
    """
    ensure_data_dir()

    path = get_conversation_path(conversation['id'])
    with open(path, 'w') as f:
        json.dump(conversation, f, indent=2)


def list_conversations() -> List[Dict[str, Any]]:
    """
    List all conversations (metadata only).

    Returns:
        List of conversation metadata dicts
    """
    ensure_data_dir()

    conversations = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json') and filename != "settings.json" and not filename.startswith("file_"):
            path = os.path.join(DATA_DIR, filename)
            with open(path, 'r') as f:
                data = json.load(f)
                # Return metadata only
                conversations.append({
                    "id": data["id"],
                    "created_at": data["created_at"],
                    "title": data.get("title", "New Conversation"),
                    "message_count": len(data["messages"])
                })

    # Sort by creation time, newest first
    conversations.sort(key=lambda x: x["created_at"], reverse=True)

    return conversations


def add_user_message(conversation_id: str, content: str, files: Optional[List[Dict[str, str]]] = None):
    """
    Add a user message to a conversation.

    Args:
        conversation_id: Conversation identifier
        content: User message content
        files: Optional list of file metadata (id, name) attached to the message
    """
    conversation = get_conversation(conversation_id)
    if conversation is None:
        raise ValueError(f"Conversation {conversation_id} not found")

    message = {
        "role": "user",
        "content": content
    }
    
    if files:
        message["files"] = files

    conversation["messages"].append(message)

    logger.info(f"DEBUG: Saving user message to {conversation_id}. Total messages: {len(conversation['messages'])}")
    save_conversation(conversation)


def add_assistant_message(
    conversation_id: str,
    stage1: List[Dict[str, Any]],
    stage2: List[Dict[str, Any]],
    stage3: Dict[str, Any]
):
    """
    Add an assistant message with all 3 stages to a conversation.

    Args:
        conversation_id: Conversation identifier
        stage1: List of individual model responses
        stage2: List of model rankings
        stage3: Final synthesized response
    """
    conversation = get_conversation(conversation_id)
    if conversation is None:
        raise ValueError(f"Conversation {conversation_id} not found")

    conversation["messages"].append({
        "role": "assistant",
        "stage1": stage1,
        "stage2": stage2,
        "stage3": stage3
    })

    logger.info(f"DEBUG: Saving assistant message to {conversation_id}. Total messages: {len(conversation['messages'])}")
    save_conversation(conversation)


def update_conversation_title(conversation_id: str, title: str):
    """
    Update the title of a conversation.

    Args:
        conversation_id: Conversation identifier
        title: New title for the conversation
    """
    conversation = get_conversation(conversation_id)
    if conversation is None:
        raise ValueError(f"Conversation {conversation_id} not found")

    conversation["title"] = title
    save_conversation(conversation)


def delete_conversation(conversation_id: str):
    """
    Delete a conversation and its associated files.

    Args:
        conversation_id: Conversation identifier
    """
    # First, load conversation to find associated files
    conversation = get_conversation(conversation_id)
    if conversation:
        # Delete associated files
        for msg in conversation.get("messages", []):
            # Check for new 'files' format
            if "files" in msg:
                for file_info in msg["files"]:
                    delete_file(file_info["id"])
            # Check for old 'file_ids' format (backward compatibility)
            elif "file_ids" in msg:
                for file_id in msg["file_ids"]:
                    delete_file(file_id)

    path = get_conversation_path(conversation_id)
    if os.path.exists(path):
        os.remove(path)
    else:
        raise ValueError(f"Conversation {conversation_id} not found")


def get_file_path(file_id: str) -> str:
    """Get the file path for a file record."""
    return os.path.join(DATA_DIR, f"file_{file_id}.json")


def save_file(file_id: str, file_data: Dict[str, Any]):
    """
    Save a file record to storage.

    Args:
        file_id: Unique identifier for the file
        file_data: File data dict to save
    """
    ensure_data_dir()

    path = get_file_path(file_id)
    with open(path, 'w') as f:
        json.dump(file_data, f, indent=2)


def get_file(file_id: str) -> Optional[Dict[str, Any]]:
    """
    Load a file record from storage.

    Args:
        file_id: Unique identifier for the file

    Returns:
        File data dict or None if not found
    """
    path = get_file_path(file_id)

    if not os.path.exists(path):
        return None

    with open(path, 'r') as f:
        return json.load(f)


def delete_file(file_id: str):
    """
    Delete a file record.

    Args:
        file_id: Unique identifier for the file
    """
    path = get_file_path(file_id)
    if os.path.exists(path):
        os.remove(path)
