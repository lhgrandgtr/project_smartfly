import os
from dotenv import load_dotenv

load_dotenv()

# File paths and server configuration
os.makedirs("frames", exist_ok=True)
FRAME_PATH = './frames/frame.png'
BLUETOOTH_PORT = '/dev/rfcomm0'
SERVER_URL = 'http://localhost:5000'
BAUD_RATE = 115200

# Video source configuration
VIDEO_SOURCE_TYPE = os.getenv("VIDEO_SOURCE_TYPE", "ip_camera")  # Options: 'ip_camera', 'webcam', 'file'
VIDEO_URL = os.getenv("VIDEO_URL", "http://192.168.56.181:8080/video")
WEBCAM_INDEX = int(os.getenv("WEBCAM_INDEX", "0"))  # Default webcam
VIDEO_FILE_PATH = os.getenv("VIDEO_FILE_PATH", "")

def get_video_source(source = 'ip_camera'):
    """Get the appropriate video source based on configuration"""
    if VIDEO_SOURCE_TYPE == source:
        return WEBCAM_INDEX
    elif VIDEO_SOURCE_TYPE == source and VIDEO_FILE_PATH:
        return VIDEO_FILE_PATH
    return VIDEO_URL

# Analysis configuration
FRAME_INTERVAL = int(os.getenv("FRAME_INTERVAL", "5"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))

# Vision system prompt
NAV_SYS_PRMPT = (
    'You are a navigation system for a toy car. You can control the robot using the following commands:'
    'forward, backward, left, right, stop. '
    'You can also control the speed. '
    'You should navigate the car to the given destination from the image as fast as possible.'
)

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", '')
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", '')
