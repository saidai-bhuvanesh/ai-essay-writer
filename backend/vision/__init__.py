"""
STUDX JARVIS - Vision Module
"""

from .computer_vision import (
    VisionManager, CameraHandler, FaceRecognizer, 
    GestureDetector, ObjectDetector, get_vision_manager, recognize_face
)

__all__ = [
    'VisionManager', 'CameraHandler', 'FaceRecognizer',
    'GestureDetector', 'ObjectDetector', 'get_vision_manager', 'recognize_face'
]