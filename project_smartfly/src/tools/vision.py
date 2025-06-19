from crewai.tools import BaseTool
from typing import Optional
import cv2
import src.utils.configs as c
from src.utils.model import Model
from datetime import datetime
import os

class VisionNavigationTool(BaseTool):
    name: str = "Vision Navigation Tool"
    description: str = "Analyzes the environment through video feed and provides navigation instructions"

    def __init__(self):
        super().__init__()
        self.vision_model = Model(platform='google', model_id='gemini-2.0-flash')

    def _connect_to_stream(self) -> cv2.VideoCapture:
        """Connect to the video stream."""
        video_source = c.get_video_source('webcam')
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            raise Exception("Could not open video source")
        
        return cap

    def _capture_frame(self, cap: cv2.VideoCapture) -> str:
        """Capture and save a frame from the video stream."""
        ret, frame = cap.read()
        
        if not ret:
            raise Exception("Could not read frame")

        filepath = c.FRAME_PATH
        cv2.imwrite(filepath, frame)
        return filepath

    def _analyze_frame(self) -> str:
        """Analyze the captured frame using the vision model."""
        return self.vision_model.invoke(c.NAV_SYS_PRMPT)

    def run(
        self,
        capture_only: bool = False
    ) -> str:
        """
        Run vision analysis for navigation.
        
        Args:
            capture_only: If True, only capture the frame without analysis
        """
        try:
            cap = self._connect_to_stream()
            frame_path = self._capture_frame(cap)
            cap.release()

            if capture_only:
                return {"frame_path": frame_path}

            analysis = self._analyze_frame()
            analysis


        except Exception as e:
            raise Exception(f"Error in vision navigation: {str(e)}")

    def describe(self) -> str:
        return """
        This tool provides vision-based navigation by:
        - Connecting to a video stream
        - Capturing the real-time frame
        - Analyzing the environment
        
        Parameters:
        - capture_only: Set to True to only capture frame without analysis
        """