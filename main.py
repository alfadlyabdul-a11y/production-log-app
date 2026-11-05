from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.camera import Camera
from kivy.network.urlrequest import UrlRequest
from kivy.core.window import Window
import json
import base64
from datetime import datetime

# Windows Camera Hardware Crash Hotfix
from kivy.core.camera.camera_opencv import CameraOpenCV
CameraOpenCV.fps = 30

SERVER_IP = "10.1.30.44"  # Make sure this matches your current Wi-Fi network IP
SERVER_URL = f"http://{SERVER_IP}:5000/update-excel"

class ExcelUpdaterApp(App):
    def build(self):
        # Premium Slate Dark theme background
        Window.clearcolor = (0.09, 0.11, 0.16, 1)
        
        # ScrollView container for smooth scrolling on any mobile screen width
        root_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        
        self.layout = BoxLayout(orientation='vertical', padding=25, spacing=15, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        
        # Main Dashboard Title Accent Row Banner
        self.layout.add_widget(Label(
            text="✨ PRODUCTION LOG DASHBOARD", 
            font_size='22sp', 
            bold=True, 
            color=(0, 0.8, 1, 1),  # Vibrant Neon Blue accent
            size_hint_y=None, 
            height=45
        ))
        
        # Helper function to generate premium styled input modules quickly
        def create_input_block(label_text, placeholder_text):
            label = Label(
                text=label_text, 
                font_size='15sp', 
                bold=True,
                color=(0.85, 0.9, 0.95, 1), 
                size_hint_y=None, 
                height=25, 
                halign='left', 
                text_size=(Window.width - 50, None)
            )
            self.layout.add_widget(label)
            
            field = TextInput(
                hint_text=placeholder_text,
                hint_text_color=(0.4, 0.48, 0.55, 1),
                multiline=False, 
                font_size='16sp', 
                padding=[12, 12, 12, 12],
                background_normal='',
                background_color=(0.14, 0.17, 0.23, 1), # Soft deep inner contrast frame
                foreground_color=(1, 1, 1, 1),          # White text color entry 
                cursor_color=(0, 0.8, 1, 1),
                size_hint_y=None, 
                height=48
            )
            self.layout.add_widget(field)
            return field

        # Generate inputs with friendly, contextual guidance hints
        self.input_shift = create_input_block("⏰ Production Shift:", "e.g., Day Shift / Night Shift")
        self.input_sn = create_input_block("🔢 Serial Number (SN):", "e.g., SN-98725A")
        self.input_wo = create_input_block("📋 Work Order (WO):", "e.g., WO-2026-004")
        self.input_location = create_input_block("📍 Station Location:", "e.g., Assembly Line 3")
        self.input_remark = create_input_block("💬 Operator Remarks:", "Type any observations or notes here...")
        
        # Camera Section Viewport Border Wrapper
        self.layout.add_widget(Label(
            text="📸 Live Camera Viewfinder:", 
            font_size='15sp', 
            bold=True,
            color=(0.85, 0.9, 0.95, 1), 
            size_hint_y=None, 
            height=25,
            halign='left',
            text_size=(Window.width - 50, None)
        ))
        
        self.camera = Camera(play=True, resolution=(640, 480), size_hint_y=None, height=260)
        self.layout.add_widget(self.camera)
        
        # Colorful Action Button 1: Take Photo (Vibrant Safety Amber Orange)
        self.snap_btn = Button(
            text="📷 SNAP ATTACHMENT PHOTO", 
            font_size='15sp', 
            bold=True, 
            background_normal='', 
            background_color=(0.95, 0.6, 0.1, 1), 
            size_hint_y=None, 
            height=50
        )
        self.snap_btn.bind(on_press=self.capture_photo)
        self.layout.add_widget(self.snap_btn)
        
        self.captured_images_list = []
        
        # Colorful Action Button 2: Submit Entry (Production Success Green)
        self.submit_btn = Button(
            text="🚀 SUBMIT TO SERVER SPREADSHEET", 
            font_size='16sp', 
            bold=True, 
            background_normal='', 
            background_color=(0.1, 0.72, 0.4, 1), 
            size_hint_y=None, 
            height=58
        )
        self.submit_btn.bind(on_press=self.send_data)
        self.layout.add_widget(self.submit_btn)
        
        # High contrast status footer layout node
        self.status_label = Label(
            text="System Ready • 0 photos cached", 
            font_size='14sp', 
            bold=True,
            color=(0.55, 0.65, 0.75, 1), 
            size_hint_y=None, 
            height=35
        )
        self.layout.add_widget(self.status_label)
        
        root_scroll.add_widget(self.layout)
        return root_scroll

    def capture_photo(self, instance):
        temp_filename = "temp_snap.png"
        self.camera.export_to_png(temp_filename)
        
        try:
            with open(temp_filename, "rb") as image_file:
                b64_string = base64.b64encode(image_file.read()).decode('utf-8')
                self.captured_images_list.append(b64_string)
                
            self.status_label.text = f"✅ Photo added! Total captured: {len(self.captured_images_list)}"
            self.status_label.color = (0.2, 0.85, 0.5, 1) # Success text green
        except Exception as e:
            self.status_label.text = f"❌ Capture Error: {str(e)}"
            self.status_label.color = (0.9, 0.3, 0.3, 1) # Alert error red

    def send_data(self, instance):
        if not self.input_sn.text.strip():
            self.status_label.text = "⚠️ Validation Error: Serial Number (SN) is required!"
            self.status_label.color = (0.95, 0.6, 0.1, 1)
            return

        payload = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "shift": self.input_shift.text.strip(),
            "sn": self.input_sn.text.strip(),
            "wo": self.input_wo.text.strip(),
            "location": self.input_location.text.strip(),
            "remark": self.input_remark.text.strip(),
            "pictures_data_list": self.captured_images_list
        }
        
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.status_label.text = "🔄 Uploading data packets to Wi-Fi server..."
        self.status_label.color = (0, 0.7, 1, 1) # Processing Blue
        
        UrlRequest(
            SERVER_URL,
            req_body=json.dumps(payload),
            req_headers=headers,
            on_success=self.on_request_success,
            on_failure=self.on_request_failure,
            on_error=self.on_request_error
        )

    def on_request_success(self, request, result):
        self.status_label.text = f"🎉 Success: {result.get('message', 'Excel Updated!')}"
        self.status_label.color = (0.2, 0.85, 0.5, 1)
        
        # Flush form data strings upon successful log transmission
        self.input_shift.text = ""
        self.input_sn.text = ""
        self.input_wo.text = ""
        self.input_location.text = ""
        self.input_remark.text = ""
        self.captured_images_list = []

    def on_request_failure(self, request, result):
        self.status_label.text = f"❌ Server Rejection: {result}"
        self.status_label.color = (0.9, 0.3, 0.3, 1)

    def on_request_error(self, request, error):
        self.status_label.text = "❌ Network Disconnected: Is your computer's server script active?"
        self.status_label.color = (0.9, 0.3, 0.3, 1)

if __name__ == '__main__':
    ExcelUpdaterApp().run()
