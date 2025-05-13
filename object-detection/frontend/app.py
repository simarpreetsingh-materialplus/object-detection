import os
import streamlit as st
import requests
import time
import shutil
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.video_splitter import split_video_ffmpeg

# Set the FastAPI endpoint base URL (adjust if needed)
FASTAPI_BASE_URL = "http://fastapi_container:8000"

# Ensure necessary directories exist
os.makedirs('scenes', exist_ok=True)
os.makedirs('key_frames', exist_ok=True)

st.title("Object Detection Chatbot")

# Initialize session state for results and scene timestamps
if "results" not in st.session_state:
    st.session_state.results = []  # For video endpoint results
if "scene_timestamps" not in st.session_state:
    st.session_state.scene_timestamps = []

# Model aliases (your endpoint expects this format)
model_aliases = {
    "GPT-4o": "gpt-4o"
}
selected_alias = st.selectbox("Select Model", list(model_aliases.keys()))

tab1, tab2 = st.tabs(["Video Upload", "Image Upload"])

with tab1:
    st.header("Video Upload")
    uploaded_video_file = st.file_uploader("Choose a video...", type=["mp4", "avi"])
    if uploaded_video_file:
        # Save the uploaded video temporarily
        video_path = "temp_video.mp4"
        with open(video_path, "wb") as f:
            f.write(uploaded_video_file.getvalue())

        scenes_output_dir = 'scenes'
        st.write("**Starting scene detection...**")
        video_manager = VideoManager([video_path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector())
        base_timecode = video_manager.get_base_timecode()
        video_manager.set_downscale_factor()
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        scene_list = scene_manager.get_scene_list(base_timecode)
        split_video_ffmpeg([video_path], scene_list, scenes_output_dir)
        st.write(f"**Scenes detected: {len(scene_list)}**")

        # Save scene timestamps
        st.session_state.scene_timestamps = [(str(start), str(end)) for start, end in scene_list]
        for i, (start, end) in enumerate(st.session_state.scene_timestamps):
            st.write(f"**Scene {i + 1}: Start {start}, End {end}**")

        st.write("**Starting key frame extraction...**")
        key_frames_output_dir = 'key_frames'
        key_frames = []
        for i, scene in enumerate(scene_list):
            start, end = scene
            midpoint = start.get_seconds() + (end.get_seconds() - start.get_seconds()) / 2
            key_frame_path = os.path.join(key_frames_output_dir, f"key_frame_{i + 1}.jpg")
            cmd = f"ffmpeg -ss {midpoint} -i {video_path} -vframes 1 {key_frame_path}"
            result = os.system(cmd)
            if result == 0 and os.path.exists(key_frame_path):
                key_frames.append(key_frame_path)
            else:
                st.write(f"Failed to extract key frame for scene {i + 1} at {midpoint:.2f}s")
        
        st.write(f"**Extracted {len(key_frames)} key frames.**")
        if key_frames:
            st.image(key_frames, caption=[f"Key Frame {i + 1}" for i in range(len(key_frames))], width=200)
        else:
            st.write("No key frames extracted.")

        st.write("**Starting object detection on key frames...**")
        model_name = model_aliases[selected_alias]
        st.session_state.results = []  # Reset previous results
        for i, key_frame_path in enumerate(key_frames):
            with open(key_frame_path, "rb") as f:
                files = {"file": f}
                data = {"model_name": model_name}
                response = requests.post(f"{FASTAPI_BASE_URL}/image/describe-image", files=files, data=data)
                if response.status_code == 200:
                    result = response.json()
                    # We assume the endpoint returns a JSON with a "description" key containing the full parsed scene details.
                    if "description" in result:
                        st.write(f"**Key Frame {i + 1} Result (Description Only):**")
                        st.json(result["description"])
                    else:
                        st.write("No description available")
                    st.session_state.results.append(result)
                    start, end = st.session_state.scene_timestamps[i]
                    st.write(f"**Timestamp for Key Frame {i + 1}:** ({start}, {end})")
                    time.sleep(60)
                else:
                    st.write(f"Error processing key frame {i + 1}: {response.text}")
        
        st.write("**Combined Key Frames Descriptions (JSON):**")
        # Combine only the description field from each result:
        combined = [res["description"] for res in st.session_state.results if "description" in res]
        st.json(combined)

        # Cleanup temporary files/directories
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(scenes_output_dir):
            shutil.rmtree(scenes_output_dir)
        if os.path.exists(key_frames_output_dir):
            shutil.rmtree(key_frames_output_dir)

with tab2:
    st.header("Image Upload")
    uploaded_image_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_image_file:
        with open("temp_image.jpg", "wb") as f:
            f.write(uploaded_image_file.getvalue())
        image_path = "temp_image.jpg"
        st.write("**Starting object detection on image...**")
        model_name = model_aliases[selected_alias]
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {"model_name": model_name}
            response = requests.post(f"{FASTAPI_BASE_URL}/image/describe-image", files=files, data=data)
            if response.status_code == 200:
                result = response.json()
                if "description" in result:
                    st.write("**Image Detection Result (Description Only) in JSON:**")
                    st.json(result["description"])
                else:
                    st.write("No description available")
                st.image(image_path, caption="Uploaded Image", use_column_width=True)
            else:
                st.write(f"Error processing image: {response.text}")
        if os.path.exists(image_path):
            os.remove(image_path)
