from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import logging
import cv2
import numpy as np
import json
from config import OpenAIConfig
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from utils.image_utils import convert_image_to_base64
from openai import AzureOpenAI  # Use the Azure client

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

@router.post("/describe-image", response_model=DetectionResponse)
async def describe_image(file: UploadFile = File(...), model_name: str = Form(...)):
    try:
        # Read and decode the image
        image_bytes = await file.read()
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        base64_image = convert_image_to_base64(image)

        # Prepare messages (prompt remains unchanged)
        messages = [
            {"role": "system", "content": "You are an AI assistant that helps people find information."},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                {"type": "text", "text": "Do object detection and provide a description of the scene in a pure JSON without any extra formatting"}
            ]}
        ]

        if model_name not in ["gpt-4o"]:
            raise HTTPException(status_code=400, detail="Invalid model selected")

        client = AzureOpenAI(
            api_key=OpenAIConfig.api_key,
            azure_endpoint=OpenAIConfig.api_base,
            api_version=OpenAIConfig.api_version
        )

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=500
        )

        if response and response.choices:
            result = response.choices[0].message.content
            try:
                result_json = json.loads(result)
            except Exception:
                result_json = {"description": result, "objects": []}

            # If the description itself is a valid JSON string, use it as the final result.
            try:
                inner = json.loads(result_json["description"])
                # If inner is a dict, we assume it holds the detailed structure.
                if isinstance(inner, dict):
                    result_json = inner
            except Exception:
                # If parsing fails, leave result_json unchanged.
                pass

            # Ensure required keys exist
            if "description" not in result_json:
                result_json["description"] = result
            if "objects" not in result_json or not isinstance(result_json["objects"], list):
                result_json["objects"] = []

            return DetectionResponse.parse_obj(result_json)
        else:
            raise HTTPException(status_code=500, detail="Empty response from OpenAI")
    except Exception as e:
        logging.error(f"Error in describe_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
