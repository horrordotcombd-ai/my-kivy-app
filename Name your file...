from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import requests

class SBFreeAiApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.output_label = Label(text='SB Free AI - আপনার প্রশ্ন লিখুন', size_hint_y=None, height=100)
        layout.add_widget(self.output_label)
        
        self.input_box = TextInput(hint_text='এখানে কিছু লিখুন...', size_hint_y=None, height=50)
        layout.add_widget(self.input_box)
        
        submit_btn = Button(text='সাবমিট করুন', size_hint_y=None, height=50)
        submit_btn.bind(on_press=self.send_query)
        layout.add_widget(submit_btn)
        
        return layout

    def send_query(self, instance):
        text = self.input_box.text
        if text:
            self.output_label.text = f'উত্তর: আপনি লিখেছেন - "{text}"'
        else:
            self.output_label.text = 'অনুগ্রহ করে কিছু লিখে দিন!'

if __name__ == '__main__':
    SBFreeAiApp().run()
