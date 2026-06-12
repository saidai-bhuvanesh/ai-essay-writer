"""
STUDX JARVIS - Vision Module
Computer vision, face recognition, and gesture detection
"""

import cv2
import logging
from typing import Optional, Tuple, List, Dict
import numpy as np

logger = logging.getLogger('JARVIS.Vision')

class CameraHandler:
    """Handle camera operations"""
    
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None
        self.is_active = False
    
    def open(self) -> bool:
        """Open camera"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if self.cap.isOpened():
                self.is_active = True
                logger.info(f"Camera {self.camera_index} opened")
                return True
            else:
                logger.error(f"Failed to open camera {self.camera_index}")
                return False
        except Exception as e:
            logger.error(f"Camera open error: {e}")
            return False
    
    def close(self):
        """Close camera"""
        if self.cap:
            self.cap.release()
            self.is_active = False
            logger.info("Camera closed")
    
    def read_frame(self) -> Optional[np.ndarray]:
        """Read a single frame"""
        if not self.cap or not self.is_active:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def get_frame_size(self) -> Tuple[int, int]:
        """Get frame dimensions"""
        if self.cap:
            return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), \
                   int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return 0, 0
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *args):
        self.close()


class FaceRecognizer:
    """Face recognition using DeepFace"""
    
    def __init__(self):
        self.model = None
        self.known_faces = {}
        self.initialized = False
        self._init_model()
    
    def _init_model(self):
        """Initialize DeepFace model"""
        try:
            from deepface import DeepFace
            self.deepface = DeepFace
            self.initialized = True
            logger.info("DeepFace model initialized")
        except ImportError:
            logger.warning("DeepFace not installed - face recognition unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize DeepFace: {e}")
    
    def add_known_face(self, user_id: int, name: str, image_path: str) -> bool:
        """Add a known face to database"""
        if not self.initialized:
            return False
        
        try:
            embedding = self.deepface.represent(image_path, model_name='VGG-Face')[0]['embedding']
            self.known_faces[user_id] = {
                'name': name,
                'embedding': np.array(embedding)
            }
            logger.info(f"Added known face: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add face: {e}")
            return False
    
    def recognize(self, frame) -> Optional[Dict]:
        """Recognize face in frame"""
        if not self.initialized:
            return None
        
        try:
            # Save frame temporarily
            import tempfile
            temp_path = tempfile.mktemp(suffix='.jpg')
            cv2.imwrite(temp_path, frame)
            
            # Get embedding
            representations = self.deepface.represent(temp_path, model_name='VGG-Face')
            
            if not representations:
                return None
            
            query_embedding = np.array(representations[0]['embedding'])
            
            # Find best match
            best_match = None
            best_distance = float('inf')
            threshold = 0.4  # Cosine distance threshold
            
            for user_id, data in self.known_faces.items():
                distance = 1 - np.dot(query_embedding, data['embedding']) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(data['embedding'])
                )
                
                if distance < best_distance and distance < threshold:
                    best_distance = distance
                    best_match = {'user_id': user_id, 'name': data['name']}
            
            return best_match
            
        except Exception as e:
            logger.debug(f"Face recognition: {e}")
            return None
    
    def verify(self, frame, user_id: int) -> bool:
        """Verify if face matches user"""
        recognized = self.recognize(frame)
        return recognized and recognized['user_id'] == user_id


class GestureDetector:
    """Gesture recognition using MediaPipe"""
    
    def __init__(self):
        self.hands = None
        self.initialized = False
        self._init_detector()
    
    def _init_detector(self):
        """Initialize MediaPipe hands detector"""
        try:
            import mediapipe as mp
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_draw = mp.solutions.drawing_utils
            self.initialized = True
            logger.info("MediaPipe hands detector initialized")
        except ImportError:
            logger.warning("MediaPipe not installed - gesture detection unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize gesture detector: {e}")
    
    def detect_gesture(self, frame) -> Optional[str]:
        """Detect gesture in frame"""
        if not self.initialized:
            return None
        
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks (optional)
                    # self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Analyze gesture
                    gesture = self._analyze_hand(hand_landmarks)
                    if gesture:
                        return gesture
            
            return None
            
        except Exception as e:
            logger.debug(f"Gesture detection: {e}")
            return None
    
    def _analyze_hand(self, hand_landmarks) -> Optional[str]:
        """Analyze hand landmarks to determine gesture"""
        try:
            # Get finger states
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            middle_tip = hand_landmarks.landmark[12]
            ring_tip = hand_landmarks.landmark[16]
            pinky_tip = hand_landmarks.landmark[20]
            
            index_base = hand_landmarks.landmark[5]
            middle_base = hand_landmarks.landmark[9]
            ring_base = hand_landmarks.landmark[13]
            pinky_base = hand_landmarks.landmark[17]
            
            # Simple gesture detection
            fingers_up = []
            
            # Thumb (comparing x coordinates for right hand)
            fingers_up.append(thumb_tip.x < hand_landmarks.landmark[3].x)
            
            # Other fingers (checking if tip is above base)
            fingers_up.append(index_tip.y < index_base.y)
            fingers_up.append(middle_tip.y < middle_base.y)
            fingers_up.append(ring_tip.y < ring_base.y)
            fingers_up.append(pinky_tip.y < pinky_base.y)
            
            # Count fingers up
            count = sum(fingers_up)
            
            if count == 5:
                return "open_palm"
            elif count == 1 and fingers_up[1]:
                return "pointing"
            elif count == 2 and fingers_up[1] and fingers_up[2]:
                return "peace_sign"
            elif count == 0:
                return "fist"
            elif fingers_up[1] and not any(fingers_up[2:]):
                return "swipe_right"
            
            return None
            
        except Exception as e:
            logger.debug(f"Hand analysis: {e}")
            return None
    
    def get_hand_positions(self, frame) -> List[Dict]:
        """Get all hand positions"""
        if not self.initialized:
            return []
        
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            hands_data = []
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    hand_data = {
                        'id': idx,
                        'landmarks': [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                    }
                    hands_data.append(hand_data)
            
            return hands_data
            
        except Exception as e:
            logger.debug(f"Hand positions: {e}")
            return []


class ObjectDetector:
    """Object detection using MediaPipe"""
    
    def __init__(self):
        self.detector = None
        self.initialized = False
        self._init_detector()
    
    def _init_detector(self):
        """Initialize MediaPipe object detector"""
        try:
            import mediapipe as mp
            self.mp_object = mp.solutions.objectron
            self.detector = self.mp_object.Objectron(
                static_image_mode=False,
                max_objects=10,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_draw = mp.solutions.drawing_utils
            self.initialized = True
            logger.info("MediaPipe object detector initialized")
        except ImportError:
            logger.warning("MediaPipe not installed - object detection unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize object detector: {e}")
    
    def detect_objects(self, frame) -> List[Dict]:
        """Detect objects in frame"""
        if not self.initialized:
            return []
        
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.detector.process(rgb_frame)
            
            objects = []
            if results.detected_objects:
                for idx, detected_object in enumerate(results.detected_objects):
                    obj_data = {
                        'label': detected_object.label[0],
                        'score': detected_object.score[0],
                        'landmarks_2d': [(lm.x, lm.y) for lm in detected_object.landmarks_2d],
                        'landmarks_3d': [(lm.x, lm.y, lm.z) for lm in detected_object.landmarks_3d]
                    }
                    objects.append(obj_data)
                    
                    # Draw box
                    self.mp_draw.draw_landmarks(
                        frame,
                        detected_object.landmarks_2d,
                        self.mp_object.BOX_CONNECTIONS
                    )
            
            return objects
            
        except Exception as e:
            logger.debug(f"Object detection: {e}")
            return []


class VisionManager:
    """Main vision management class"""
    
    def __init__(self, camera_index: int = 0):
        self.camera = CameraHandler(camera_index)
        self.face_recognizer = FaceRecognizer()
        self.gesture_detector = GestureDetector()
        self.object_detector = ObjectDetector()
        
        logger.info("Vision manager initialized")
    
    def start_camera(self) -> bool:
        """Start camera"""
        return self.camera.open()
    
    def stop_camera(self):
        """Stop camera"""
        self.camera.close()
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a frame"""
        return self.camera.read_frame()
    
    def analyze_frame(self, frame) -> Dict:
        """Analyze frame for all vision features"""
        results = {
            'faces': [],
            'gestures': [],
            'objects': []
        }
        
        # Face recognition
        face = self.face_recognizer.recognize(frame)
        if face:
            results['faces'].append(face)
        
        # Gesture detection
        gesture = self.gesture_detector.detect_gesture(frame)
        if gesture:
            results['gestures'].append(gesture)
        
        # Object detection
        objects = self.object_detector.detect_objects(frame)
        if objects:
            results['objects'] = objects
        
        return results
    
    def add_user_face(self, user_id: int, name: str, image_path: str) -> bool:
        """Add user face for recognition"""
        return self.face_recognizer.add_known_face(user_id, name, image_path)
    
    def authenticate_face(self, frame) -> Optional[Dict]:
        """Authenticate using face"""
        return self.face_recognizer.recognize(frame)


# Global vision manager
_vision_manager = None

def get_vision_manager() -> VisionManager:
    """Get vision manager instance"""
    global _vision_manager
    if _vision_manager is None:
        _vision_manager = VisionManager()
    return _vision_manager

def recognize_face(embedding) -> Optional[Dict]:
    """Quick face recognition function"""
    vm = get_vision_manager()
    return vm.face_recognizer.recognize(embedding)