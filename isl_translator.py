"""
Indian Sign Language Translator - IMPROVED VERSION
Fixed finger detection and added real-time debugging
"""

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from PIL import Image, ImageTk
import os
import time
from datetime import datetime
import json
from pathlib import Path
import urllib.request

class ISLTranslator:
    def __init__(self, excel_file_path=None):
        self.root = tk.Tk()
        self.root.title("Indian Sign Language Translator")
        self.root.geometry("1200x800")
        
        # Initialize MediaPipe
        self.setup_mediapipe_adapter()
        
        # Store excel file path
        self.excel_file_path = excel_file_path
        
        # Load sign language data
        self.load_sign_data()
        
        # Initialize variables
        self.mode = None
        self.camera = None
        self.hands = None
        self.is_running = False
        self.last_word_time = 0
        self.cooldown_duration = 1.5  # Reduced cooldown
        self.current_sentence = []
        self.conversation_history = []
        
        # Detection counters for stability
        self.gesture_buffer = []
        self.buffer_size = 5  # Need 5 consecutive detections
        
        # Media resources directory
        self.media_dir = os.path.join(os.path.dirname(__file__), "sign_media")
        os.makedirs(self.media_dir, exist_ok=True)
        
        # Model cache directory
        self.model_cache_dir = os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(self.model_cache_dir, exist_ok=True)
        
        # Create GUI
        self.create_gui()
        
    def load_sign_data(self):
        """Load sign language data from Excel file"""
        try:
            if self.excel_file_path and os.path.exists(self.excel_file_path):
                df = pd.read_excel(self.excel_file_path)
            else:
                messagebox.showinfo("Select Sign Data File", "Please select the signs.xlsx file")
                file_path = filedialog.askopenfilename(
                    title="Select signs.xlsx file",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
                )
                if file_path:
                    df = pd.read_excel(file_path)
                    self.excel_file_path = file_path
                else:
                    df = pd.DataFrame({
                        'Word': ['HELLO', 'THANK YOU', 'PLEASE', 'YES', 'NO', 'STOP', 'PEACE', 'OK'],
                        'Hand(s)': ['Single'] * 8,
                        'Description': [
                            'Open palm, all fingers extended',
                            'Open palm moving forward',
                            'Palm on chest area',
                            'Thumbs up',
                            'Index and middle waving',
                            'Closed fist',
                            'Index and middle extended',
                            'Thumb and index forming circle'
                        ]
                    })
                    messagebox.showwarning("Using Default Data", "Using basic default sign data.")
            
            df = df.dropna(subset=['Word'])
            self.sign_data = df.to_dict('records')
            print(f"✓ Loaded {len(self.sign_data)} signs")
        except Exception as e:
            print(f"Error loading sign data: {e}")
            self.sign_data = []

    def download_hand_landmarker_model(self):
        """Download MediaPipe hand landmarker model"""
        model_name = "hand_landmarker.task"
        model_path = os.path.join(self.model_cache_dir, model_name)
        
        if os.path.exists(model_path):
            return model_path
        
        model_url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        
        try:
            print(f"Downloading hand landmarker model...")
            urllib.request.urlretrieve(model_url, model_path)
            print(f"✓ Model saved")
            return model_path
        except Exception as ex:
            print(f"Failed to download model: {ex}")
            return None
    
    def setup_mediapipe_adapter(self):
        """Setup MediaPipe API"""
        try:
            import mediapipe as mp_local
        except Exception:
            mp_local = None

        # Try legacy solutions API
        if mp_local is not None and hasattr(mp_local, 'solutions') and hasattr(mp_local.solutions, 'hands'):
            self.api_mode = 'solutions'
            self.mp = mp_local
            self.mp_hands = mp_local.solutions.hands
            self.mp_drawing = mp_local.solutions.drawing_utils
            self.mp_drawing_styles = getattr(mp_local.solutions, 'drawing_styles', None)
            print("✓ Using MediaPipe Solutions API")
            return

        # Try Tasks API
        try:
            import mediapipe.tasks.python.vision.hand_landmarker as tasks_hand_landmarker
            self.api_mode = 'tasks'
            self.tasks_hand_landmarker = tasks_hand_landmarker
            self.mp_image = getattr(mp_local, 'Image', None)

            try:
                from mediapipe.tasks.python.vision import drawing_utils as tasks_drawing
                self.mp_drawing = tasks_drawing
            except Exception:
                self.mp_drawing = None

            self.mp_hands = None
            self.mp_drawing_styles = None
            self.hand_model_path = None
            print("✓ Using MediaPipe Tasks API")
            return
        except Exception:
            pass

        self.api_mode = None
        self.mp = None
        self.mp_hands = None
        self.mp_drawing = None
        self.mp_drawing_styles = None
    
    def create_gui(self):
        """Create the main GUI interface"""
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🤟 Indian Sign Language Translator", 
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Mode selection frame
        self.mode_frame = tk.Frame(self.root, bg="#ecf0f1")
        self.mode_frame.pack(fill=tk.BOTH, expand=True)
        
        mode_label = tk.Label(
            self.mode_frame,
            text="Select Mode:",
            font=("Arial", 18, "bold"),
            bg="#ecf0f1"
        )
        mode_label.pack(pady=50)
        
        button_frame = tk.Frame(self.mode_frame, bg="#ecf0f1")
        button_frame.pack(pady=20)
        
        sign_to_text_btn = tk.Button(
            button_frame,
            text="📹 Sign-to-Text\n(Camera Tracking)",
            font=("Arial", 16),
            width=20,
            height=4,
            bg="#3498db",
            fg="white",
            command=lambda: self.select_mode("sign_to_text"),
            cursor="hand2"
        )
        sign_to_text_btn.pack(side=tk.LEFT, padx=20)
        
        text_to_sign_btn = tk.Button(
            button_frame,
            text="✍️ Text-to-Sign\n(Display Signs)",
            font=("Arial", 16),
            width=20,
            height=4,
            bg="#2ecc71",
            fg="white",
            command=lambda: self.select_mode("text_to_sign"),
            cursor="hand2"
        )
        text_to_sign_btn.pack(side=tk.LEFT, padx=20)
        
    def select_mode(self, mode):
        """Handle mode selection"""
        self.mode = mode
        self.mode_frame.destroy()
        
        if mode == "sign_to_text":
            self.create_sign_to_text_interface()
        else:
            self.create_text_to_sign_interface()
    
    def create_sign_to_text_interface(self):
        """Create interface for sign-to-text conversion"""
        # Main container
        container = tk.Frame(self.root, bg="#ecf0f1")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Camera feed
        left_panel = tk.Frame(container, bg="#34495e", width=800)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.camera_label = tk.Label(left_panel, bg="black")
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Camera controls
        control_frame = tk.Frame(left_panel, bg="#34495e")
        control_frame.pack(fill=tk.X, pady=5)
        
        self.start_camera_btn = tk.Button(
            control_frame,
            text="▶️ Start Camera",
            font=("Arial", 12),
            bg="#27ae60",
            fg="white",
            command=self.start_camera,
            cursor="hand2",
            width=15
        )
        self.start_camera_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_camera_btn = tk.Button(
            control_frame,
            text="⏸️ Stop Camera",
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            command=self.stop_camera,
            state=tk.DISABLED,
            cursor="hand2",
            width=15
        )
        self.stop_camera_btn.pack(side=tk.LEFT, padx=5)
        
        # Right panel - Output
        right_panel = tk.Frame(container, bg="#ecf0f1", width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        right_panel.pack_propagate(False)
        
        # Current sentence
        sentence_label = tk.Label(
            right_panel,
            text="Current Sentence:",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1"
        )
        sentence_label.pack(pady=(10, 5))
        
        self.sentence_display = scrolledtext.ScrolledText(
            right_panel,
            font=("Arial", 14),
            height=6,
            wrap=tk.WORD,
            bg="white"
        )
        self.sentence_display.pack(fill=tk.X, padx=10, pady=5)
        
        # Detected word
        word_label = tk.Label(
            right_panel,
            text="Last Detected:",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1"
        )
        word_label.pack(pady=(10, 5))
        
        self.detected_word = tk.Label(
            right_panel,
            text="---",
            font=("Arial", 20, "bold"),
            bg="#3498db",
            fg="white",
            relief=tk.RAISED,
            height=2
        )
        self.detected_word.pack(fill=tk.X, padx=10, pady=5)
        
        # Cooldown indicator
        self.cooldown_label = tk.Label(
            right_panel,
            text="Ready",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#27ae60"
        )
        self.cooldown_label.pack(pady=2)
        
        # Debug info - ENHANCED
        debug_frame = tk.Frame(right_panel, bg="#34495e", relief=tk.SUNKEN, bd=2)
        debug_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(debug_frame, text="🔍 Debug Info:", font=("Arial", 10, "bold"), 
                bg="#34495e", fg="white").pack(pady=2)
        
        self.debug_label = tk.Label(
            debug_frame,
            text="Waiting for hand...",
            font=("Arial", 9),
            bg="#34495e",
            fg="#ecf0f1",
            justify=tk.LEFT,
            wraplength=350
        )
        self.debug_label.pack(pady=5, padx=5)
        
        # Conversation history
        history_label = tk.Label(
            right_panel,
            text="Conversation History:",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1"
        )
        history_label.pack(pady=(15, 5))
        
        self.history_display = scrolledtext.ScrolledText(
            right_panel,
            font=("Arial", 11),
            height=8,
            wrap=tk.WORD,
            bg="white"
        )
        self.history_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Action buttons
        action_frame = tk.Frame(right_panel, bg="#ecf0f1")
        action_frame.pack(fill=tk.X, pady=10)
        
        clear_btn = tk.Button(
            action_frame,
            text="🗑️ Clear",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            command=self.clear_sentence,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=3)
        
        save_sentence_btn = tk.Button(
            action_frame,
            text="💾 Save",
            font=("Arial", 10),
            bg="#f39c12",
            fg="white",
            command=self.save_sentence,
            cursor="hand2"
        )
        save_sentence_btn.pack(side=tk.LEFT, padx=3)
        
        download_btn = tk.Button(
            action_frame,
            text="⬇️ Download",
            font=("Arial", 10),
            bg="#9b59b6",
            fg="white",
            command=self.download_conversation,
            cursor="hand2"
        )
        download_btn.pack(side=tk.LEFT, padx=3)
    
    def create_text_to_sign_interface(self):
        """Create interface for text-to-sign conversion"""
        container = tk.Frame(self.root, bg="#ecf0f1")
        container.pack(fill=tk.BOTH, expand=True)
        
        top_panel = tk.Frame(container, bg="#ecf0f1")
        top_panel.pack(fill=tk.X, padx=10, pady=10)
        
        input_label = tk.Label(
            top_panel,
            text="Enter text to convert to signs:",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1"
        )
        input_label.pack(pady=5)
        
        self.text_input = tk.Entry(top_panel, font=("Arial", 14), width=60)
        self.text_input.pack(pady=5)
        self.text_input.bind('<Return>', lambda e: self.convert_text_to_signs())
        
        convert_btn = tk.Button(
            top_panel,
            text="🔄 Convert to Signs",
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            command=self.convert_text_to_signs,
            cursor="hand2"
        )
        convert_btn.pack(pady=10)
        
        middle_panel = tk.Frame(container, bg="white", relief=tk.SUNKEN, bd=2)
        middle_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.sign_canvas = tk.Canvas(middle_panel, bg="white")
        self.sign_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.sign_info_label = tk.Label(
            middle_panel,
            text="Enter text and click 'Convert to Signs'",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d"
        )
        self.sign_info_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        bottom_panel = tk.Frame(container, bg="#ecf0f1")
        bottom_panel.pack(fill=tk.X, padx=10, pady=10)
        
        action_frame = tk.Frame(bottom_panel, bg="#ecf0f1")
        action_frame.pack(pady=5)
        
        clear_btn = tk.Button(
            action_frame,
            text="🗑️ Clear",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            command=self.clear_text_display,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def start_camera(self):
        """Initialize and start camera"""
        try:
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                messagebox.showerror("Camera Error", "Could not access camera.")
                return
            
            if self.api_mode == 'solutions' and self.mp_hands is not None:
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                print("✓ MediaPipe Hands initialized")
            elif self.api_mode == 'tasks':
                model_path = self.download_hand_landmarker_model()
                if not model_path:
                    messagebox.showwarning("Model required", "Model not found.")
                    self.camera.release()
                    return
                
                from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarker
                self.hands = HandLandmarker.create_from_model_path(model_path)
                print("✓ Hand Landmarker initialized")
            else:
                messagebox.showerror("MediaPipe Error", "No supported API found.")
                self.camera.release()
                return
            
            self.is_running = True
            self.start_camera_btn.config(state=tk.DISABLED)
            self.stop_camera_btn.config(state=tk.NORMAL)
            
            self.update_camera_feed()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start camera: {str(e)}")
    
    def stop_camera(self):
        """Stop camera feed"""
        self.is_running = False
        if self.camera:
            self.camera.release()
        if self.hands:
            self.hands.close()
        
        if hasattr(self, '_tmp_frame_path'):
            try:
                os.unlink(self._tmp_frame_path)
            except:
                pass
        
        self.start_camera_btn.config(state=tk.NORMAL)
        self.stop_camera_btn.config(state=tk.DISABLED)
        self.camera_label.config(image='', text="Camera stopped", fg="white", bg="black")
    
    def update_camera_feed(self):
        """Update camera feed and process gestures"""
        if not self.is_running:
            return
        
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            if self.api_mode == 'solutions':
                results = self.hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style() if self.mp_drawing_styles else None,
                            self.mp_drawing_styles.get_default_hand_connections_style() if self.mp_drawing_styles else None
                        )
                    
                    self.recognize_sign(results, frame)
                else:
                    self.debug_label.config(text="No hand detected")
            
            # Update cooldown display
            time_since_last = time.time() - self.last_word_time
            if time_since_last < self.cooldown_duration:
                remaining = self.cooldown_duration - time_since_last
                self.cooldown_label.config(text=f"Cooldown: {remaining:.1f}s", fg="#e74c3c")
            else:
                self.cooldown_label.config(text="Ready", fg="#27ae60")
            
            # Display frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((780, 580), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image=img)
            
            self.camera_label.config(image=photo)
            self.camera_label.image = photo
        
        self.root.after(10, self.update_camera_feed)
    
    def recognize_sign(self, results, frame):
        """Recognize sign from hand landmarks"""
        if not results.multi_hand_landmarks:
            return
        
        # Check cooldown
        if time.time() - self.last_word_time < self.cooldown_duration:
            return
        
        num_hands = len(results.multi_hand_landmarks)
        features = self.extract_hand_features(results.multi_hand_landmarks, results.multi_handedness)
        
        detected_word = self.classify_sign(features, num_hands)
        
        # Add to buffer for stability
        self.gesture_buffer.append(detected_word)
        if len(self.gesture_buffer) > self.buffer_size:
            self.gesture_buffer.pop(0)
        
        # Check if we have consistent detection
        if len(self.gesture_buffer) >= 3:
            # Get most common gesture in buffer
            from collections import Counter
            counts = Counter(self.gesture_buffer)
            most_common = counts.most_common(1)[0]
            
            if most_common[1] >= 3 and most_common[0] is not None:  # At least 3 same detections
                final_word = most_common[0]
                
                # Update UI
                self.detected_word.config(text=final_word, bg="#27ae60")
                self.last_word_time = time.time()
                
                # Add to sentence
                self.current_sentence.append(final_word)
                self.update_sentence_display()
                
                # Clear buffer
                self.gesture_buffer = []
                
                # Visual feedback
                cv2.putText(frame, f"✓ {final_word}", (10, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                
                print(f"✓ Detected: {final_word}")
    
    def extract_hand_features(self, hand_landmarks_list, handedness_list):
        """Extract features from hand"""
        features = {'num_hands': len(hand_landmarks_list), 'hands': []}
        
        for idx, hand_landmarks in enumerate(hand_landmarks_list):
            landmarks = hand_landmarks.landmark
            hand_type = handedness_list[idx].classification[0].label
            
            hand_features = {
                'type': hand_type,
                'finger_states': self.get_finger_states(landmarks),
                'palm_direction': self.get_palm_direction(landmarks),
                'hand_position': self.get_hand_position(landmarks),
                'landmarks': landmarks
            }
            
            features['hands'].append(hand_features)
        
        return features
    
    def get_finger_states(self, landmarks):
        """Determine extended fingers - IMPROVED"""
        states = []
        
        # Thumb - check horizontal distance (more lenient)
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        # Calculate if thumb is extended
        thumb_extended = abs(thumb_tip.x - thumb_mcp.x) > 0.04
        states.append(thumb_extended)
        
        # Other fingers - check if tip is above PIP (more lenient threshold)
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        
        for tip, pip in zip(finger_tips, finger_pips):
            # Finger is extended if tip is significantly above pip
            extended = landmarks[tip].y < landmarks[pip].y - 0.02  # Reduced from 0.03
            states.append(extended)
        
        return states  # [Thumb, Index, Middle, Ring, Pinky]
    
    def get_palm_direction(self, landmarks):
        """Calculate palm direction"""
        wrist = np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z])
        mcp = np.array([landmarks[9].x, landmarks[9].y, landmarks[9].z])
        
        direction_vector = mcp - wrist
        
        if direction_vector[1] < -0.08:
            return "up"
        elif direction_vector[1] > 0.08:
            return "down"
        elif direction_vector[0] < -0.08:
            return "left"
        elif direction_vector[0] > 0.08:
            return "right"
        else:
            return "forward"
    
    def get_hand_position(self, landmarks):
        """Get hand vertical position"""
        wrist_y = landmarks[0].y
        
        if wrist_y < 0.4:
            return "high"
        elif wrist_y > 0.65:
            return "low"
        else:
            return "middle"
    
    def classify_sign(self, features, num_hands):
        """Classify the sign - IMPROVED LOGIC"""
        if not features['hands']:
            return None
        
        hand = features['hands'][0]
        finger_states = hand['finger_states']
        palm_dir = hand['palm_direction']
        hand_pos = hand['hand_position']
        
        # Count extended fingers
        extended_count = sum(finger_states)
        
        # Update debug with detailed info
        finger_names = ['👍Thumb', '☝️Index', '🖕Middle', '💍Ring', '🤙Pinky']
        extended_fingers = [finger_names[i] for i, state in enumerate(finger_states) if state]
        
        debug_text = f"Extended ({extended_count}): {', '.join(extended_fingers) if extended_fingers else 'None'}\n"
        debug_text += f"Palm: {palm_dir} | Position: {hand_pos}\n"
        debug_text += f"Raw: {finger_states}"
        
        self.debug_label.config(text=debug_text)
        
        # SIGN CLASSIFICATION with more lenient matching
        
        # 5 fingers extended - Open palm gestures
        if extended_count >= 4:  # Allow 4-5 fingers
            if hand_pos == "high":
                return "HELLO"
            elif palm_dir == "forward":
                return "THANK YOU"
            elif palm_dir == "down":
                return "PLEASE"
            else:
                return "HELLO"  # Default to HELLO for open palm
        
        # Pointing gesture - Index finger
        if finger_states[1] and extended_count == 1:
            return "YOU"
        
        if finger_states[1] and extended_count <= 2:
            if palm_dir in ["left", "right"]:
                return "ME/I"
        
        # Peace sign - Index + Middle
        if finger_states[1] and finger_states[2] and extended_count == 2:
            return "PEACE"
        
        # Three fingers
        if finger_states[1] and finger_states[2] and finger_states[3] and extended_count == 3:
            return "WATER"
        
        # Thumbs up
        if finger_states[0] and extended_count == 1:
            return "YES"
        
        # Fist (no fingers or just thumb)
        if extended_count == 0:
            return "STOP"
        
        # If nothing specific matched but we have fingers extended
        if extended_count >= 4:
            return "HELLO"
        
        return None
    
    def update_sentence_display(self):
        """Update sentence display"""
        sentence_text = " ".join(self.current_sentence)
        self.sentence_display.delete(1.0, tk.END)
        self.sentence_display.insert(1.0, sentence_text)
    
    def clear_sentence(self):
        """Clear current sentence"""
        self.current_sentence = []
        self.sentence_display.delete(1.0, tk.END)
        self.detected_word.config(text="---", bg="#3498db")
        self.gesture_buffer = []
    
    def save_sentence(self):
        """Save sentence to history"""
        if self.current_sentence:
            sentence = " ".join(self.current_sentence)
            timestamp = datetime.now().strftime("%H:%M:%S")
            entry = f"[{timestamp}] {sentence}\n"
            
            self.conversation_history.append({
                'timestamp': timestamp,
                'text': sentence,
                'mode': 'sign_to_text'
            })
            
            self.history_display.insert(tk.END, entry)
            self.history_display.see(tk.END)
            self.clear_sentence()
            messagebox.showinfo("Saved", "Sentence saved!")
    
    def download_conversation(self):
        """Download conversation"""
        if not self.conversation_history:
            messagebox.showwarning("No Data", "No conversation to download.")
            return
        
        filename = f"ISL_Conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=filename
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("INDIAN SIGN LANGUAGE - CONVERSATION\n")
                f.write("=" * 60 + "\n\n")
                
                for entry in self.conversation_history:
                    f.write(f"[{entry['timestamp']}] {entry['text']}\n")
            
            messagebox.showinfo("Success", f"Saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
    def convert_text_to_signs(self):
        """Convert text to signs"""
        text = self.text_input.get().strip().upper()
        if not text:
            return

        words = text.split()
        self.sign_canvas.delete("all")
        self.sign_info_label.place_forget()

        # Create scrollable frame for images
        self.sign_canvas.config(scrollregion=self.sign_canvas.bbox("all"))

        x_pos = 20
        y_pos = 20
        images_found = 0

        for i, word in enumerate(words):
            # Try to find image file for this word
            image_path = self._find_sign_image(word)

            if image_path:
                try:
                    # Load and resize image
                    img = Image.open(image_path)
                    img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)

                    # Create image on canvas
                    self.sign_canvas.create_image(
                        x_pos + 75, y_pos + 75,
                        image=photo,
                        tags=f"sign_{i}"
                    )

                    # Store reference to prevent garbage collection
                    if not hasattr(self, '_canvas_images'):
                        self._canvas_images = []
                    self._canvas_images.append(photo)

                    # Add word label below image
                    self.sign_canvas.create_text(
                        x_pos + 75, y_pos + 160,
                        text=word,
                        font=("Arial", 12, "bold"),
                        fill="#2c3e50"
                    )

                    images_found += 1

                except Exception as e:
                    # If image fails to load, show error text
                    self.sign_canvas.create_text(
                        x_pos + 75, y_pos + 75,
                        text=f"❌ {word}\n(Error loading)",
                        font=("Arial", 10),
                        fill="#e74c3c"
                    )
                    print(f"Error loading image for {word}: {e}")
            else:
                # No image found for this word
                self.sign_canvas.create_text(
                    x_pos + 75, y_pos + 75,
                    text=f"❓ {word}\n(No image found)",
                    font=("Arial", 10),
                    fill="#f39c12"
                )

            # Move to next position (arrange in grid)
            x_pos += 180
            if x_pos > 800:  # Wrap to next row
                x_pos = 20
                y_pos += 200

        # Show status message
        if images_found == 0:
            self.sign_canvas.create_text(
                400, 300,
                text=f"No sign images found in: {self.media_dir}",
                font=("Arial", 12),
                fill="#e74c3c"
            )
            print(f"Media directory: {self.media_dir}")
            print(f"Contents: {os.listdir(self.media_dir) if os.path.exists(self.media_dir) else 'Directory does not exist'}")

        # Update scroll region
        self.sign_canvas.config(scrollregion=self.sign_canvas.bbox("all"))

    def _find_sign_image(self, word):
        """Find image file for a sign word in sign_media folder"""
        if not os.path.exists(self.media_dir):
            return None

        # Supported image extensions
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']

        # Try exact match first
        for ext in extensions:
            file_path = os.path.join(self.media_dir, f"{word}{ext}")
            if os.path.exists(file_path):
                return file_path

        # Try case-insensitive match
        for file in os.listdir(self.media_dir):
            if file.upper().startswith(word) and any(file.lower().endswith(ext) for ext in extensions):
                return os.path.join(self.media_dir, file)

        return None
    
    def clear_text_display(self):
        """Clear text display"""
        self.text_input.delete(0, tk.END)
        self.sign_canvas.delete("all")
        self.sign_info_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        # Clear stored images
        if hasattr(self, '_canvas_images'):
            self._canvas_images = []
    
    def run(self):
        """Start application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle closing"""
        if self.is_running:
            self.stop_camera()
        self.root.destroy()


if __name__ == "__main__":
    excel_path = "/mnt/user-data/uploads/signs.xlsx"
    app = ISLTranslator(excel_file_path=excel_path)
    app.run()