# utils/video_utils.py:
import cv2
import tempfile
import os
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector

def extract_key_frames(video_bytes):
    with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
        temp_video_file.write(video_bytes)
        temp_video_file_path = temp_video_file.name

    video_stream = open_video(temp_video_file_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=30.0))  # Default threshold is 30.0

    scene_manager.detect_scenes(video=video_stream)
    scene_list = scene_manager.get_scene_list()

    key_frames = []
    scene_timestamps = []

    for i, scene in enumerate(scene_list):
        start, end = scene
        midpoint = start.get_seconds() + (end.get_seconds() - start.get_seconds()) / 2
        vidcap = cv2.VideoCapture(temp_video_file_path)
        vidcap.set(cv2.CAP_PROP_POS_MSEC, midpoint * 1000)
        success, image = vidcap.read()
        if success:
            key_frames.append(image)
            scene_timestamps.append((str(start), str(end)))
        vidcap.release()

    os.remove(temp_video_file_path)
    del video_stream
    return key_frames, scene_timestamps