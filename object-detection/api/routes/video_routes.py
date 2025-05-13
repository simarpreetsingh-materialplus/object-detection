from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import logging
import time
import json
from typing import List, Optional, Dict, Any
from utils.video_utils import extract_key_frames
from utils.image_utils import convert_image_to_base64
from pydantic import BaseModel, Field
from openai import AzureOpenAI  # Use the Azure client
from config import OpenAIConfig

router = APIRouter()

class DetectedObject(BaseModel):
    name: str = Field(..., alias="type")
    confidence: float = Field(default=0.0)

    class Config:
        extra = "allow"

class DetectionResponse(BaseModel):
    description: str
    objects: List[DetectedObject] = []

    class Config:
        extra = "allow"

class VideoDetectionResponse(BaseModel):
    key_frames: List[DetectionResponse]

    class Config:
        extra = "allow"

@router.post("/describe-video", response_model=VideoDetectionResponse)
async def describe_video(file: UploadFile = File(...), model_name: str = Form(...)):
    try:
        video_bytes = await file.read()
        key_frames, scene_timestamps = extract_key_frames(video_bytes)
        if not key_frames:
            raise HTTPException(status_code=500, detail="No key frames extracted from video")

        key_frame_results: List[DetectionResponse] = []
        client = AzureOpenAI(
            api_key=OpenAIConfig.api_key,
            azure_endpoint=OpenAIConfig.api_base,
            api_version=OpenAIConfig.api_version
        )

        # Process key frames in batches of 3
        for i in range(0, len(key_frames), 3):
            batch_frames = key_frames[i:i+3]
            for frame in batch_frames:
                base64_image = convert_image_to_base64(frame)
                messages = [
                    {"role": "system", "content": "You are an AI assistant that helps people find information."},
                    {"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                        {"type": "text", "text": "Do object detection and provide a description of the scene along with a JSON representation of the contents."}
                    ]}
                ]
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=1500
                )
                if response and response.choices:
                    result = response.choices[0].message.content
                    try:
                        result_json = json.loads(result)
                    except Exception:
                        result_json = {"description": result, "objects": []}
                    # If the description is itself a JSON string, use it instead
                    try:
                        inner = json.loads(result_json["description"])
                        if isinstance(inner, dict) and "objects" in inner:
                            result_json = inner
                    except Exception:
                        pass
                    if "description" not in result_json:
                        result_json["description"] = result
                    if "objects" not in result_json or not isinstance(result_json["objects"], list):
                        result_json["objects"] = []
                    key_frame_results.append(DetectionResponse.parse_obj(result_json))
            remaining_frames = len(key_frames) - (i + 3)
            if remaining_frames <= 2:
                time.sleep(120)  # Pause if needed

        return VideoDetectionResponse(key_frames=key_frame_results)
    except Exception as e:
        logging.error(f"Error in describe_video: {e}")
        raise HTTPException(status_code=500, detail=str(e))
