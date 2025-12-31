import cv2
import numpy as np


class Canvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)

        # Stroke state
        self.prev_point = None

        # Brush config
        self.current_color = (255, 0, 0)
        self.brush_thickness = 8
        self.eraser_thickness = 50

        # Smoothing with adaptive window
        self.smooth_points = []
        self.smooth_window = 5  # Increased for smoother lines

        # Enhanced undo history
        self.history = []
        self.max_history = 20  # More undo steps
        self.stroke_active = False

        # Frame-loss handling with adaptive threshold
        self.missing_frames = 0
        self.max_missing = 5

        # Performance optimization
        self.dirty_region = None  # Track changed areas

    # ---------------- COLOR ----------------
    def set_color(self, color_tuple):
        """Set color using BGR tuple"""
        if isinstance(color_tuple, tuple) and len(color_tuple) == 3:
            self.current_color = color_tuple

    def set_color_by_name(self, name):
        """Legacy method for color name support"""
        colors = {
            "BLUE": (255, 0, 0),
            "GREEN": (0, 255, 0),
            "RED": (0, 0, 255),
            "YELLOW": (0, 255, 255),
            "PURPLE": (255, 0, 255),
            "ORANGE": (0, 165, 255),
            "WHITE": (255, 255, 255),
            "CYAN": (255, 255, 0),
            "MAGENTA": (255, 0, 255)
        }
        self.current_color = colors.get(name, self.current_color)

    # ---------------- DRAW ----------------
    def draw(self, x, y, eraser=False):
        """Enhanced drawing with better smoothing and bounds checking"""
        self.missing_frames = 0

        # Bounds checking
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))

        # Save canvas once per stroke (for undo)
        if not self.stroke_active:
            self.save_state()
            self.stroke_active = True

        # Add to smoothing buffer
        self.smooth_points.append((x, y))
        if len(self.smooth_points) > self.smooth_window:
            self.smooth_points.pop(0)

        # Weighted smoothing (more weight to recent points)
        if len(self.smooth_points) >= 2:
            weights = np.linspace(0.5, 1.0, len(self.smooth_points))
            weights = weights / weights.sum()
            
            avg_x = int(sum(p[0] * w for p, w in zip(self.smooth_points, weights)))
            avg_y = int(sum(p[1] * w for p, w in zip(self.smooth_points, weights)))
            current_point = (avg_x, avg_y)
        else:
            current_point = (x, y)

        # First point initialization
        if self.prev_point is None:
            self.prev_point = current_point
            # Draw a dot for single clicks
            color = (0, 0, 0) if eraser else self.current_color
            thickness = self.eraser_thickness if eraser else self.brush_thickness
            cv2.circle(self.canvas, current_point, thickness // 2, color, -1)
            return

        # Draw line between points
        color = (0, 0, 0) if eraser else self.current_color
        thickness = self.eraser_thickness if eraser else self.brush_thickness

        # Use LINE_AA for anti-aliased lines (smoother)
        cv2.line(
            self.canvas,
            self.prev_point,
            current_point,
            color,
            thickness,
            cv2.LINE_AA
        )

        # Update dirty region for potential optimization
        self._update_dirty_region(self.prev_point, current_point, thickness)

        self.prev_point = current_point

    def _update_dirty_region(self, p1, p2, thickness):
        """Track which regions of canvas have changed"""
        x1, y1 = p1
        x2, y2 = p2
        
        min_x = max(0, min(x1, x2) - thickness)
        max_x = min(self.width, max(x1, x2) + thickness)
        min_y = max(0, min(y1, y2) - thickness)
        max_y = min(self.height, max(y1, y2) + thickness)
        
        if self.dirty_region is None:
            self.dirty_region = (min_x, min_y, max_x, max_y)
        else:
            old_x1, old_y1, old_x2, old_y2 = self.dirty_region
            self.dirty_region = (
                min(min_x, old_x1),
                min(min_y, old_y1),
                max(max_x, old_x2),
                max(max_y, old_y2)
            )


    def reset(self):
        """Reset stroke state when hand is not detected"""
        self.missing_frames += 1
        if self.missing_frames >= self.max_missing:
            self.prev_point = None
            self.smooth_points.clear()
            self.stroke_active = False
            self.missing_frames = 0
            self.dirty_region = None

    def clear(self):
        """Clear entire canvas"""
        self.save_state()
        self.canvas[:] = 0
        self.prev_point = None
        self.smooth_points.clear()
        self.stroke_active = False
        self.dirty_region = None

 
    def save_state(self):
        """Save current canvas state to history"""
        # Only save if canvas has content (optimization)
        if np.any(self.canvas):
            self.history.append(self.canvas.copy())
            if len(self.history) > self.max_history:
                self.history.pop(0)

    def undo(self):
        """Undo last action"""
        if self.history:
            self.canvas = self.history.pop()
            self.prev_point = None
            self.smooth_points.clear()
            self.stroke_active = False
            self.dirty_region = None
            return True
        return False

    # ---------------- SAVE/LOAD ----------------
    def save_to_file(self, filename="canvas_drawing.png"):
        """Save canvas to image file"""
        try:
            cv2.imwrite(filename, self.canvas)
            return True
        except Exception as e:
            print(f"Error saving canvas: {e}")
            return False

    def load_from_file(self, filename):
        """Load canvas from image file"""
        try:
            loaded = cv2.imread(filename)
            if loaded is not None and loaded.shape[:2] == (self.height, self.width):
                self.save_state()  # Save current state before loading
                self.canvas = loaded
                return True
        except Exception as e:
            print(f"Error loading canvas: {e}")
        return False

    # ---------------- ACCESS ----------------
    def get_canvas(self):
        """Return copy of canvas"""
        return self.canvas.copy()

    def get_canvas_view(self):
        """Return view of canvas (no copy, for performance)"""
        return self.canvas

    def set_brush_size(self, size):
        """Set brush thickness with bounds"""
        self.brush_thickness = max(1, min(50, int(size)))

    def set_eraser_size(self, size):
        """Set eraser thickness with bounds"""
        self.eraser_thickness = max(10, min(100, int(size)))

    # ---------------- UTILITY ----------------
    def is_empty(self):
        """Check if canvas is empty"""
        return not np.any(self.canvas)

    def get_bounding_box(self):
        """Get bounding box of all drawn content"""
        gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        coords = cv2.findNonZero(gray)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            return (x, y, w, h)
        return None

    def crop_to_content(self):
        """Crop canvas to actual content"""
        bbox = self.get_bounding_box()
        if bbox:
            x, y, w, h = bbox
            return self.canvas[y:y+h, x:x+w]
        return self.canvas