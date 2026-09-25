from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

from ai_brain import AIBrain


class MyAIApp(App):

    def build(self):
        self.brain = AIBrain()

        layout = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10
        )

        self.output = Label(
            text="My AI is ready.",
            font_size=22
        )

        self.input_box = TextInput(
            hint_text="Type a command...",
            multiline=False,
            font_size=20
        )

        send_button = Button(
            text="SEND",
            font_size=20,
            size_hint_y=None,
            height=60
        )

        send_button.bind(on_press=self.send_command)

        layout.add_widget(self.output)
        layout.add_widget(self.input_box)
        layout.add_widget(send_button)

        return layout

    def send_command(self, instance):
        command = self.input_box.text.strip()

        if not command:
            return

        response = self.brain.think(command)

        self.output.text = "AI: " + response

        self.input_box.text = ""


MyAIApp().run()