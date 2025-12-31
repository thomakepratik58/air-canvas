import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np


class HandTracker:
    def __init__(self, mode='performance'):
        """
        Initialize hand tracker with configurable modes
        
        Args:
            mode: 'performance' (fast, lower accuracy) or 'quality' (slower, higher accuracy)
        """
        # Configuration based on mode
        if mode == 'quality':
            detection_conf = 0.7
            presence_conf = 0.7
            tracking_conf = 0.7
        else:  # performance mode (default)
            detection_conf = 0.5
            presence_conf = 0.5
            tracking_conf = 0.5
        
        try:
            base_options = python.BaseOptions(
                model_asset_path="hand_landmarker.task"
            )

            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=1,  # Single hand for better performance
                min_hand_detection_confidence=detection_conf,
                min_hand_presence_confidence=presence_conf,
                min_tracking_confidence=tracking_conf,
            )

            self.detector = vision.HandLandmarker.create_from_options(options)
            self.results = None
            
            # Tracking state
            self.last_landmarks = None
            self.hand_detected = False
            self.detection_history = []
            self.history_size = 5
            
            # Performance metrics
            self.detection_count = 0
            self.failed_detections = 0
            
            # Stability tracking
            self.stable_landmarks = None
            self.stability_alpha = 0.3  # Exponential moving average factor
            
            self.initialized = True
            print("✅ Hand tracker initialized successfully")
            
        except Exception as e:
            self.detector = None
            self.initialized = False
            print(f"❌ Error initializing hand tracker: {e}")
            print("Make sure 'hand_landmarker.task' model file exists in the project directory")
            print("\n📥 To download the model, run: python download_model.py")
            raise

    def detect(self, img):
        """
        Detect hand landmarks in image
        
        Args:
            img: BGR image from OpenCV
        """
        # Check if detector is initialized
        if not hasattr(self, 'detector') or self.detector is None:
            self.results = None
            self.hand_detected = False
            return
        
        try:
            # Convert BGR to RGB (MediaPipe expects RGB)
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Create MediaPipe Image object
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            
            # Detect hand landmarks
            self.results = self.detector.detect(mp_image)
            
            # Update detection state
            if self.results and self.results.hand_landmarks:
                self.hand_detected = True
                self.detection_count += 1
                self.detection_history.append(True)
            else:
                self.hand_detected = False
                self.failed_detections += 1
                self.detection_history.append(False)
            
            # Keep history size limited
            if len(self.detection_history) > self.history_size:
                self.detection_history.pop(0)
                
        except Exception as e:
            print(f"Detection error: {e}")
            self.results = None
            self.hand_detected = False

    def get_landmarks(self, img):
        """
        Get processed hand landmarks with stability filtering
        
        Args:
            img: BGR image (for dimension reference)
            
        Returns:
            List of (id, x, y) tuples or None if no hand detected
        """
        if not self.results or not self.results.hand_landmarks:
            self.stable_landmarks = None
            return None

        h, w, _ = img.shape
        lm_list = []

        # Extract landmarks
        for i, lm in enumerate(self.results.hand_landmarks[0]):
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list.append((i, cx, cy))

        # Apply stability filter (exponential moving average)
        if self.stable_landmarks is None:
            self.stable_landmarks = lm_list
        else:
            stabilized = []
            for i in range(len(lm_list)):
                old_id, old_x, old_y = self.stable_landmarks[i]
                new_id, new_x, new_y = lm_list[i]
                
                # Smooth position using exponential moving average
                smooth_x = int(old_x * (1 - self.stability_alpha) + new_x * self.stability_alpha)
                smooth_y = int(old_y * (1 - self.stability_alpha) + new_y * self.stability_alpha)
                
                stabilized.append((new_id, smooth_x, smooth_y))
            
            self.stable_landmarks = stabilized
            lm_list = stabilized

        self.last_landmarks = lm_list
        return lm_list

    def get_raw_landmarks(self, img):
        """
        Get raw landmarks without stability filtering
        Useful when you need instant response
        """
        if not self.results or not self.results.hand_landmarks:
            return None

        h, w, _ = img.shape
        lm_list = []

        for i, lm in enumerate(self.results.hand_landmarks[0]):
            cx, cy = int(lm.x * w), int(lm.y * h)
            lm_list.append((i, cx, cy))

        return lm_list

    def is_hand_stable(self):
        """
        Check if hand detection is stable (not flickering)
        Returns True if hand has been consistently detected
        """
        if len(self.detection_history) < self.history_size:
            return False
        
        # At least 80% of recent frames should have hand detected
        stable_threshold = 0.8
        detection_rate = sum(self.detection_history) / len(self.detection_history)
        return detection_rate >= stable_threshold

    def get_hand_confidence(self):
        """
        Get confidence score for current hand detection (0-1)
        """
        if not self.results or not self.results.hand_landmarks:
            return 0.0
        
        # Check detection history stability
        if len(self.detection_history) < 2:
            return 0.5
        
        stability = sum(self.detection_history) / len(self.detection_history)
        return stability

    def draw_landmarks(self, img, landmarks=None, draw_connections=True):
        """
        Draw hand landmarks and connections on image for debugging
        
        Args:
            img: Image to draw on
            landmarks: Landmark list (uses last detected if None)
            draw_connections: Whether to draw connections between landmarks
        """
        if landmarks is None:
            landmarks = self.last_landmarks
        
        if not landmarks:
            return img

        # Draw connections first (so they appear behind points)
        if draw_connections:
            connections = [
                # Thumb
                (0, 1), (1, 2), (2, 3), (3, 4),
                # Index
                (0, 5), (5, 6), (6, 7), (7, 8),
                # Middle
                (0, 9), (9, 10), (10, 11), (11, 12),
                # Ring
                (0, 13), (13, 14), (14, 15), (15, 16),
                # Pinky
                (0, 17), (17, 18), (18, 19), (19, 20),
                # Palm
                (5, 9), (9, 13), (13, 17)
            ]
            
            for connection in connections:
                start_idx, end_idx = connection
                if start_idx < len(landmarks) and end_idx < len(landmarks):
                    start = (landmarks[start_idx][1], landmarks[start_idx][2])
                    end = (landmarks[end_idx][1], landmarks[end_idx][2])
                    cv2.line(img, start, end, (0, 255, 0), 2)

        # Draw landmark points
        for i, lm in enumerate(landmarks):
            _, x, y = lm
            
            # Different colors for different parts
            if i in [4, 8, 12, 16, 20]:  # Fingertips
                color = (0, 0, 255)  # Red
                radius = 6
            elif i == 0:  # Wrist
                color = (255, 0, 0)  # Blue
                radius = 8
            else:
                color = (0, 255, 0)  # Green
                radius = 4
            
            cv2.circle(img, (x, y), radius, color, -1)
            cv2.circle(img, (x, y), radius + 2, (255, 255, 255), 1)

        return img

    def get_hand_bbox(self, landmarks=None):
        """
        Get bounding box around hand
        
        Returns:
            (x, y, w, h) or None if no hand detected
        """
        if landmarks is None:
            landmarks = self.last_landmarks
        
        if not landmarks:
            return None

        xs = [lm[1] for lm in landmarks]
        ys = [lm[2] for lm in landmarks]
        
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        
        # Add padding
        padding = 20
        x_min = max(0, x_min - padding)
        y_min = max(0, y_min - padding)
        
        w = x_max - x_min + 2 * padding
        h = y_max - y_min + 2 * padding
        
        return (x_min, y_min, w, h)

    def get_handedness(self):
        """
        Get whether detected hand is left or right
        
        Returns:
            'Left', 'Right', or None
        """
        if not self.results or not self.results.handedness:
            return None
        
        # MediaPipe returns handedness as seen from camera perspective
        handedness = self.results.handedness[0][0]
        return handedness.category_name

    def get_statistics(self):
        """
        Get detection statistics for debugging
        
        Returns:
            Dictionary with detection stats
        """
        total = self.detection_count + self.failed_detections
        success_rate = (self.detection_count / total * 100) if total > 0 else 0
        
        return {
            'total_frames': total,
            'successful_detections': self.detection_count,
            'failed_detections': self.failed_detections,
            'success_rate': success_rate,
            'currently_stable': self.is_hand_stable(),
            'confidence': self.get_hand_confidence()
        }

    def reset_statistics(self):
        """Reset tracking statistics"""
        self.detection_count = 0
        self.failed_detections = 0
        self.detection_history.clear()

    def set_stability_factor(self, alpha):
        """
        Adjust stability/responsiveness trade-off
        
        Args:
            alpha: 0.0 (very stable, laggy) to 1.0 (instant, jittery)
        """
        self.stability_alpha = max(0.0, min(1.0, alpha))

    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'detector') and self.detector:
                self.detector.close()
        except Exception as e:
            print(f"Cleanup error: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()