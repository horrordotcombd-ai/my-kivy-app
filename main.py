from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
import sqlite3
import requests
import os

# ডাটাবেস ইনিশিয়ালাইজেশন
def init_db():
    conn = sqlite3.connect('sb_free_ai.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            prompt TEXT,
            result TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ১. Login & Signup Screen
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        layout.add_widget(Label(text="[b]SB Free Ai[/b]", markup=True, font_size=32, color=(0.1, 0.6, 0.9, 1), size_hint_y=None, height=50))
        
        self.email = TextInput(hint_text='Email Address', multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.email)
        
        self.password = TextInput(hint_text='Password', password=True, multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.password)
        
        login_btn = Button(text='Login', size_hint_y=None, height=50, background_color=(0.1, 0.6, 0.9, 1))
        login_btn.bind(on_press=self.do_login)
        layout.add_widget(login_btn)
        
        signup_btn = Button(text='Create New Account (Signup)', size_hint_y=None, height=50, background_color=(0.2, 0.7, 0.3, 1))
        signup_btn.bind(on_press=self.do_signup)
        layout.add_widget(signup_btn)
        
        self.add_widget(layout)
        
    def do_login(self, instance):
        self.manager.current = 'home'

    def do_signup(self, instance):
        self.manager.current = 'home'

# ২. Home Screen
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        layout.add_widget(Label(text="[b]Home Dashboard[/b]", markup=True, font_size=26, size_hint_y=None, height=40))
        
        img_btn = Button(text='🖼️ Create Image', size_hint_y=None, height=60, background_color=(0.9, 0.4, 0.1, 1))
        img_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'image_gen'))
        layout.add_widget(img_btn)
        
        vid_btn = Button(text='🎥 Create Video', size_hint_y=None, height=60, background_color=(0.9, 0.2, 0.2, 1))
        vid_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'video_gen'))
        layout.add_widget(vid_btn)
        
        hist_btn = Button(text='📁 History', size_hint_y=None, height=60, background_color=(0.2, 0.5, 0.8, 1))
        hist_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'history'))
        layout.add_widget(hist_btn)
        
        set_btn = Button(text='⚙️ Settings', size_hint_y=None, height=60, background_color=(0.5, 0.5, 0.5, 1))
        set_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'settings'))
        layout.add_widget(set_btn)
        
        self.add_widget(layout)

# ৩. AI Image Generator Screen
class ImageGenScreen(Screen):
    def __init__(self, **kwargs):
        super(ImageGenScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(text="AI Image Generator", font_size=20, size_hint_y=None, height=30))
        
        self.prompt = TextInput(hint_text='Enter English Image Prompt...', size_hint_y=None, height=45)
        layout.add_widget(self.prompt)
        
        layout.add_widget(Label(text="Aspect Ratio:", size_hint_y=None, height=25))
        self.ratio_spinner = Spinner(text='1:1', values=('9:16', '16:9', '1:1', '4:3'), size_hint_y=None, height=45)
        layout.add_widget(self.ratio_spinner)
        
        self.status_label = Label(text="", size_hint_y=None, height=30, color=(0.2, 0.8, 0.2, 1))
        layout.add_widget(self.status_label)
        
        gen_btn = Button(text='Generate & Save Real Image', size_hint_y=None, height=50, background_color=(0.1, 0.7, 0.5, 1))
        gen_btn.bind(on_press=self.generate_image)
        layout.add_widget(gen_btn)
        
        back_btn = Button(text='Back to Home', size_hint_y=None, height=40)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)

    def generate_image(self, instance):
        prompt_text = self.prompt.text.strip()
        if prompt_text:
            self.status_label.text = "Generating image from AI... Please wait."
            try:
                formatted_prompt = prompt_text.replace(" ", "%20")
                api_url = "https://image.pollinations.ai/prompt/{}".format(formatted_prompt)
                
                response = requests.get(api_url)
                if response.status_code == 200:
                    filename = "AI_Img_{}.jpg".format(os.urandom(4).hex())
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    conn = sqlite3.connect('sb_free_ai.db')
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO history (type, prompt, result) VALUES (?, ?, ?)", 
                                   ('Image', prompt_text, filename))
                    conn.commit()
                    conn.close()
                    
                    self.status_label.text = "Success! Saved as {}".format(filename)
                    self.prompt.text = ""
                else:
                    self.status_label.text = "Failed to generate image. Try again."
            except Exception as e:
                self.status_label.text = "Error: Check your internet connection."

# ৪. AI Video Generator Screen
class VideoGenScreen(Screen):
    def __init__(self, **kwargs):
        super(VideoGenScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=8)
        
        layout.add_widget(Label(text="AI Video Generator", font_size=18, size_hint_y=None, height=25))
        
        self.v_prompt = TextInput(hint_text='1. English Video Prompt...', size_hint_y=None, height=38)
        layout.add_widget(self.v_prompt)
        
        self.dialogue = TextInput(hint_text='2. Bengali Dialogue...', size_hint_y=None, height=38)
        layout.add_widget(self.dialogue)
        
        self.narration = TextInput(hint_text='3. Bengali Narration...', size_hint_y=None, height=38)
        layout.add_widget(self.narration)
        
        layout.add_widget(Label(text="Video Duration:", size_hint_y=None, height=20))
        self.duration_spinner = Spinner(text='5s', values=('5s', '10s', '15s'), size_hint_y=None, height=35)
        layout.add_widget(self.duration_spinner)
        
        layout.add_widget(Label(text="Quality Mode:", size_hint_y=None, height=20))
        self.quality_spinner = Spinner(text='Standard', values=('Standard', 'High (Flux)', 'Ultra'), size_hint_y=None, height=35)
        layout.add_widget(self.quality_spinner)
        
        self.v_status = Label(text="", size_hint_y=None, height=25, color=(0.8, 0.3, 0.2, 1))
        layout.add_widget(self.v_status)
        
        gen_btn = Button(text='Generate & Save Real Video', size_hint_y=None, height=42, background_color=(0.8, 0.3, 0.2, 1))
        gen_btn.bind(on_press=self.generate_video)
        layout.add_widget(gen_btn)
        
        back_btn = Button(text='Back to Home', size_hint_y=None, height=35)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)

    def generate_video(self, instance):
        v_text = self.v_prompt.text.strip()
        diag = self.dialogue.text.strip()
        narr = self.narration.text.strip()
        dur = self.duration_spinner.text
        qual = self.quality_spinner.text
        
        if v_text:
            self.v_status.text = "Generating {} video ({})... Please wait.".format(dur, qual)
            try:
                formatted_v_prompt = v_text.replace(" ", "%20")
                video_api_url = "https://pollinations.ai/p/{}?model=flux".format(formatted_v_prompt)
                
                response = requests.get(video_api_url)
                if response.status_code == 200:
                    filename = "AI_Vid_{}.mp4".format(os.urandom(4).hex())
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    combined_info = "[{} | {}] Prompt: {} | Dialogue: {} | Narration: {}".format(dur, qual, v_text, diag, narr)
                    
                    conn = sqlite3.connect('sb_free_ai.db')
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO history (type, prompt, result) VALUES (?, ?, ?)", 
                                   ('Video', combined_info, filename))
                    conn.commit()
                    conn.close()
                    
                    self.v_status.text = "Success! Saved as {}".format(filename)
                    self.v_prompt.text = ""
                    self.dialogue.text = ""
                    self.narration.text = ""
                else:
                    self.v_status.text = "Video generation failed. Try again."
            except Exception as e:
                self.v_status.text = "Error: Check your internet connection."

# ৫. History Detail Screen
class HistoryDetailScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryDetailScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=8)
        
        layout.add_widget(Label(text="Image Preview & Video Generator", font_size=18, size_hint_y=None, height=25))
        
        self.img_preview = Image(size_hint=(1, None), height=140, source='')
        layout.add_widget(self.img_preview)
        
        self.details_label = Label(text="", size_hint_y=None, height=25, font_size=11)
        layout.add_widget(self.details_label)
        
        self.v_prompt = TextInput(hint_text='1. English Video Prompt...', size_hint_y=None, height=35)
        layout.add_widget(self.v_prompt)
        
        self.dialogue = TextInput(hint_text='2. Bengali Dialogue...', size_hint_y=None, height=35)
        layout.add_widget(self.dialogue)
        
        self.narration = TextInput(hint_text='3. Bengali Narration...', size_hint_y=None, height=35)
        layout.add_widget(self.narration)
        
        self.duration_spinner = Spinner(text='5s', values=('5s', '10s', '15s'), size_hint_y=None, height=32)
        layout.add_widget(self.duration_spinner)
        
        self.quality_spinner = Spinner(text='Standard', values=('Standard', 'High (Flux)', 'Ultra'), size_hint_y=None, height=32)
        layout.add_widget(self.quality_spinner)
        
        self.status_label = Label(text="", size_hint_y=None, height=25, color=(0.2, 0.8, 0.2, 1))
        layout.add_widget(self.status_label)
        
        gen_vid_btn = Button(text='🎥 Generate Video from This Image', size_hint_y=None, height=40, background_color=(0.9, 0.3, 0.1, 1))
        gen_vid_btn.bind(on_press=self.generate_video_from_history)
        layout.add_widget(gen_vid_btn)
        
        back_btn = Button(text='Back to History', size_hint_y=None, height=35)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'history'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
        self.current_item_data = None

    def set_data(self, item_type, prompt, result):
        self.current_item_data = (item_type, prompt, result)
        self.details_label.text = "File: {}".format(result)
        
        if item_type == 'Image' and os.path.exists(result):
            self.img_preview.source = result
            self.img_preview.reload()
        else:
            self.img_preview.source = ''

    def generate_video_from_history(self, instance):
        v_text = self.v_prompt.text.strip()
        diag = self.dialogue.text.strip()
        narr = self.narration.text.strip()
        dur = self.duration_spinner.text
        qual = self.quality_spinner.text
        
        if v_text and self.current_item_data:
            self.status_label.text = "Generating {} video from image ({})... Please wait.".format(dur, qual)
            try:
                formatted_v_prompt = v_text.replace(" ", "%20")
                video_api_url = "https://pollinations.ai/p/{}?model=flux".format(formatted_v_prompt)
                
                response = requests.get(video_api_url)
                if response.status_code == 200:
                    filename = "AI_Vid_{}.mp4".format(os.urandom(4).hex())
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    combined_info = "[{} | {}] Ref: {} | Prompt: {} | Dialogue: {} | Narration: {}".format(
                        dur, qual, self.current_item_data[2], v_text, diag, narr
                    )
                    
                    conn = sqlite3.connect('sb_free_ai.db')
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO history (type, prompt, result) VALUES (?, ?, ?)", 
                                   ('Video (From Img)', combined_info, filename))
                    conn.commit()
                    conn.close()
                    
                    self.status_label.text = "Success! Saved as {}".format(filename)
                    self.v_prompt.text = ""
                    self.dialogue.text = ""
                    self.narration.text = ""
                else:
                    self.status_label.text = "Video generation failed. Try again."
            except Exception as e:
                self.status_label.text = "Error: Check your internet connection."

# ৬. History Screen
class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.layout.add_widget(Label(text="Saved History (Click Item to Open)", font_size=20, size_hint_y=None, height=30))
        
        self.history_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.history_layout)
        self.layout.add_widget(scroll)
        
        clear_btn = Button(text='🧹 Clear All History', size_hint_y=None, height=45, background_color=(0.8, 0.1, 0.1, 1))
        clear_btn.bind(on_press=self.clear_history)
        self.layout.add_widget(clear_btn)
        
        back_btn = Button(text='Back to Home', size_hint_y=None, height=40)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        self.layout.add_widget(back_btn)
        
        self.add_widget(self.layout)

    def on_enter(self):
        self.history_layout.clear_widgets()
        conn = sqlite3.connect('sb_free_ai.db')
        cursor = conn.cursor()
        cursor.execute("SELECT type, prompt, result FROM history")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            self.history_layout.add_widget(Label(text="No history found.", size_hint_y=None, height=40))
        else:
            for row in rows:
                item_type, prompt, result = row
                btn_text = "[{}] {}... ({})".format(item_type, prompt[:30], result)
                item_btn = Button(text=btn_text, size_hint_y=None, height=50, background_color=(0.2, 0.4, 0.6, 1))
                item_btn.bind(on_press=lambda x, t=item_type, p=prompt, r=result: self.open_detail(t, p, r))
                self.history_layout.add_widget(item_btn)

    def open_detail(self, item_type, prompt, result):
        detail_screen = self.manager.get_screen('history_detail')
        detail_screen.set_data(item_type, prompt, result)
        self.manager.current = 'history_detail'

    def clear_history(self, instance):
        conn = sqlite3.connect('sb_free_ai.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history")
        conn.commit()
        conn.close()
        self.history_layout.clear_widgets()
        self.history_layout.add_widget(Label(text="No history found.", size_hint_y=None, height=40))

# ৭. Settings Screen
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(text="App Settings", font_size=20, size_hint_y=None, height=30))
        layout.add_widget(Label(text="Account: user@sbfreeai.com", size_hint_y=None, height=30))
        
        logout_btn = Button(text='Logout', size_hint_y=None, height=50, background_color=(0.8, 0.2, 0.2, 1))
        logout_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(logout_btn)
        
        back_btn = Button(text='Back to Home', size_hint_y=None, height=40)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)

# Main App Class
class SBFreeAiApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ImageGenScreen(name='image_gen'))
        sm.add_widget(VideoGenScreen(name='video_gen'))
        sm.add_name = sm.add_widget
        sm.add_name(HistoryScreen(name='history'))
        sm.add_name(HistoryDetailScreen(name='history_detail'))
        sm.add_name(SettingsScreen(name='settings'))
        return sm

if __name__ == '__main__':
    SBFreeAiApp().run()