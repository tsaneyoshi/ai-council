"""FastAPI backend for LLM Council."""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import json
import asyncio
import base64

from . import storage
from . import files
from .settings import get_settings
from .council import run_full_council, generate_conversation_title, stage1_collect_responses, stage2_collect_rankings, stage3_synthesize_final, calculate_aggregate_rankings

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Council API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateConversationRequest(BaseModel):
    """Request to create a new conversation."""
    pass


class SendMessageRequest(BaseModel):
    """Request to send a message in a conversation."""
    content: str
    file_ids: Optional[List[str]] = None


class ConversationMetadata(BaseModel):
    """Conversation metadata for list view."""
    id: str
    created_at: str
    title: str
    message_count: int


class Conversation(BaseModel):
    """Full conversation with all messages."""
    id: str
    created_at: str
    title: str
    messages: List[Dict[str, Any]]


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "LLM Council API"}


@app.get("/api/conversations", response_model=List[ConversationMetadata])
async def list_conversations():
    """List all conversations (metadata only)."""
    return storage.list_conversations()


@app.post("/api/conversations", response_model=Conversation)
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation."""
    conversation_id = str(uuid.uuid4())
    conversation = storage.create_conversation(conversation_id)
    return conversation


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file, process it (text/image), and return metadata.
    """
    try:
        # Read content for storage (to allow download later)
        original_content = await file.read()
        original_base64 = base64.b64encode(original_content).decode('utf-8')
        
        # Reset cursor for processing
        await file.seek(0)

        # Process file (extract text or prepare image for Vision)
        processed_data = await files.process_file(file)
        
        # Save to storage
        file_id = str(uuid.uuid4())
        file_data = {
            "id": file_id,
            "filename": file.filename,
            "original_content": original_base64,
            **processed_data # Merge processed_data (content, type, media_type)
        }
        storage.save_file(file_id, file_data)
        
        # Create preview
        preview = ""
        if processed_data["type"] == "text":
            preview = processed_data["content"][:100] + "..." if len(processed_data["content"]) > 100 else processed_data["content"]
        elif processed_data["type"] == "image":
            preview = "[Image ready for Vision]"
        elif processed_data["type"] == "mixed":
            preview = "[PDF/Document ready for Vision]"
            
        return {
            "id": file_id,
            "filename": file.filename,
            "preview": preview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/files/{file_id}/download")
async def download_file(file_id: str):
    """Download a file."""
    file_data = storage.get_file(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")
    
    if "original_content" not in file_data:
        raise HTTPException(status_code=400, detail="Original content not available for this file")
        
    try:
        # Decode base64 content
        content_bytes = base64.b64decode(file_data["original_content"])
        
        # Determine media type (fallback to application/octet-stream)
        media_type = file_data.get("media_type", "application/octet-stream")
        
        # Return as downloadable file
        return Response(
            content=content_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_data["filename"]}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/settings")
async def get_settings_endpoint():
    """Get current settings."""
    return get_settings().to_dict()


class UpdateSettingsRequest(BaseModel):
    """Request to update settings."""
    openrouter_api_key: Optional[str] = None
    council_models: Optional[List[str]] = None
    chairman_model: Optional[str] = None
    organization_name: Optional[str] = None


@app.post("/api/settings")
async def update_settings_endpoint(request: UpdateSettingsRequest):
    """Update settings."""
    try:
        settings = get_settings()
        update_data = request.dict(exclude_unset=True)
        settings.update(update_data)
        return settings.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """Get a specific conversation with all its messages."""
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


class UpdateConversationRequest(BaseModel):
    """Request to update a conversation."""
    title: str


@app.patch("/api/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, request: UpdateConversationRequest):
    """Update a conversation (e.g. title)."""
    try:
        storage.update_conversation_title(conversation_id, request.title)
        return {"status": "success", "id": conversation_id, "title": request.title}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    try:
        storage.delete_conversation(conversation_id)
        return {"status": "success", "id": conversation_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/conversations/{conversation_id}/message")
async def send_message(conversation_id: str, request: SendMessageRequest):
    """
    Send a message and run the 3-stage council process.
    Returns the complete response with all stages.
    """
    # Check if conversation exists
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check if this is the first message
    is_first_message = len(conversation["messages"]) == 0

    # Process files if any
    full_content = request.content
    if request.file_ids:
        file_contexts = []
        for file_id in request.file_ids:
            file_data = storage.get_file(file_id)
            if file_data:
                file_contexts.append(f"--- File: {file_data['filename']} ---\n{file_data['content']}\n--- End of File ---")
        
        if file_contexts:
            full_content = f"{request.content}\n\n" + "\n\n".join(file_contexts)

    # Prepare file metadata
    files_meta = []
    if request.file_ids:
        for file_id in request.file_ids:
            file_data = storage.get_file(file_id)
            if file_data:
                files_meta.append({"id": file_id, "name": file_data['filename']})

    # Add user message
    storage.add_user_message(conversation_id, full_content, files_meta)

    # If this is the first message, generate a title
    if is_first_message:
        title = await generate_conversation_title(request.content) # Use original content for title
        storage.update_conversation_title(conversation_id, title)

    # Run the 3-stage council process
    stage1_results, stage2_results, stage3_result, metadata = await run_full_council(
        full_content
    )

    # Add assistant message with all stages
    # Add assistant message with all stages
    storage.add_assistant_message(
        conversation_id,
        stage1_results,
        stage2_results,
        stage3_result,
        metadata
    )

    # Return the complete response with metadata
    return {
        "stage1": stage1_results,
        "stage2": stage2_results,
        "stage3": stage3_result,
        "metadata": metadata
    }


@app.post("/api/conversations/{conversation_id}/message/stream")
async def send_message_stream(conversation_id: str, request: SendMessageRequest):
    """
    Send a message and stream the 3-stage council process.
    Returns Server-Sent Events as each stage completes.
    """
    # Check if conversation exists
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check if this is the first message
    is_first_message = len(conversation["messages"]) == 0

    async def event_generator():
        try:
            # Process files if any
            full_content = request.content
            
            # 1. Start title generation in parallel (don't await yet)
            title_task = None
            if is_first_message:
                title_task = asyncio.create_task(generate_conversation_title(request.content)) # Use original content for title

            # 2. Process files and build context
            message_content = []
            
            # Add user text first
            if request.content:
                message_content.append({
                    "type": "text",
                    "text": request.content
                })

            if request.file_ids:
                print(f"Processing {len(request.file_ids)} files for stream...")
                for file_id in request.file_ids:
                    file_data = storage.get_file(file_id)
                    if file_data:
                        # Process file content based on type
                        if file_data.get("type") == "image":
                            # Image content
                            message_content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{file_data.get('media_type', 'image/jpeg')};base64,{file_data['content']}"
                                }
                            })
                            message_content.append({
                                "type": "text",
                                "text": f"\n[Attached Image: {file_data['filename']}]"
                            })
                        elif file_data.get("type") == "mixed":
                            # Mixed content (e.g. PDF pages as images)
                            message_content.append({
                                "type": "text",
                                "text": f"\n[Attached Document: {file_data['filename']}]"
                            })
                            # Add all mixed content items (images/text)
                            if isinstance(file_data['content'], list):
                                message_content.extend(file_data['content'])
                        else:
                            # Text content
                            text_content = file_data.get("content", "")
                            message_content.append({
                                "type": "text",
                                "text": f"\n\n--- File: {file_data['filename']} ---\n{text_content}\n--- End of File ---"
                            })

            # Add user message to storage (simplified for now, actual multimodal storage would be more complex)
            stored_user_content = request.content
            files_meta = []
            if request.file_ids:
                for file_id in request.file_ids:
                    file_data = storage.get_file(file_id)
                    if file_data:
                        files_meta.append({"id": file_id, "name": file_data['filename']})
                
            storage.add_user_message(conversation_id, stored_user_content, files_meta)

            # 3. Run the council process
            # Stage 1: Collect responses
            yield f"data: {json.dumps({'type': 'stage1_start', 'status': 'collecting_responses'})}\n\n"
            stage1_results = await stage1_collect_responses(message_content)
            yield f"data: {json.dumps({'type': 'stage1_complete', 'results': stage1_results})}\n\n"

            # Stage 2: Collect rankings
            yield f"data: {json.dumps({'type': 'stage2_start', 'status': 'ranking_responses'})}\n\n"
            stage2_results, label_to_model = await stage2_collect_rankings(message_content, stage1_results)
            aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)
            yield f"data: {json.dumps({'type': 'stage2_complete', 'results': stage2_results, 'aggregate': aggregate_rankings})}\n\n"

            # Stage 3: Synthesize final answer
            yield f"data: {json.dumps({'type': 'stage3_start', 'status': 'synthesizing_final'})}\n\n"
            stage3_result = await stage3_synthesize_final(message_content, stage1_results, stage2_results)
            yield f"data: {json.dumps({'type': 'stage3_complete', 'result': stage3_result})}\n\n"

            # Wait for title generation if it was started
            if title_task:
                title = await title_task
                storage.update_conversation_title(conversation_id, title)
                yield f"data: {json.dumps({'type': 'title_complete', 'title': title})}\n\n"

            # Save complete assistant message
            # Save complete assistant message
            metadata = {
                "label_to_model": label_to_model,
                "aggregate_rankings": aggregate_rankings
            }
            storage.add_assistant_message(
                conversation_id,
                stage1_results,
                stage2_results,
                stage3_result,
                metadata
            )

            # Send completion event
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        except Exception as e:
            # Log the full exception
            logger.error(f"Error in event_generator: {str(e)}", exc_info=True)
            # Send error event
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
