__version__ = "0.4.1"

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock

from ai_brain import AIBrain

# =========================================================
# VOSK / PYJNIUS CALLBACK CLASSES
# =========================================================

try:
    from jnius import PythonJavaClass, java_method
except Exception:
    PythonJavaClass = object

    def java_method(*args, **kwargs):
        def decorator(function):
            return function
        return decorator


class VoskModelCallback(PythonJavaClass):

    __javainterfaces__ = [
        "org/vosk/android/StorageService$Callback"
    ]

    def __init__(self, app):
        super().__init__()
        self.app = app

    @java_method("(Ljava/lang/Object;)V")
    def onComplete(self, result):
        self.app.on_vosk_model_loaded(result)


class VoskModelErrorCallback(PythonJavaClass):

    __javainterfaces__ = [
        "org/vosk/android/StorageService$Callback"
    ]

    def __init__(self, app):
        super().__init__()
        self.app = app

    @java_method("(Ljava/lang/Object;)V")
    def onComplete(self, error):
        self.app.on_vosk_model_error(error)


class VoskRecognitionListener(PythonJavaClass):

    __javainterfaces__ = [
        "org/vosk/android/RecognitionListener"
    ]

    def __init__(self, app):
        super().__init__()
        self.app = app

    @java_method("(Ljava/lang/String;)V")
    def onPartialResult(self, hypothesis):
        self.app.on_vosk_partial(hypothesis)

    @java_method("(Ljava/lang/String;)V")
    def onResult(self, hypothesis):
        self.app.on_vosk_result(hypothesis)

    @java_method("(Ljava/lang/String;)V")
    def onFinalResult(self, hypothesis):
        self.app.on_vosk_final(hypothesis)

    @java_method("(Ljava/lang/Exception;)V")
    def onError(self, exception):
        self.app.on_vosk_error(exception)

    @java_method("()V")
    def onTimeout(self):
        self.app.on_vosk_timeout()


# =========================================================
# CARD
# =========================================================

class Card(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.025, 0.08, 0.14, 1)

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

        self.bind(
            pos=self.update_bg,
            size=self.update_bg
        )

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


# =========================================================
# MAIN APP
# =========================================================

class MyAIApp(App):

    def build(self):

        self.brain = AIBrain()

        # Vosk objects
        self.vosk_model = None
        self.vosk_recognizer = None
        self.vosk_speech_service = None

        # Keep Java callback objects alive
        self.vosk_model_callback = None
        self.vosk_model_error_callback = None
        self.vosk_listener = None

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        with root.canvas.before:
            Color(0.008, 0.025, 0.05, 1)

            self.background = RoundedRectangle(
                pos=root.pos,
                size=root.size
            )

        root.bind(
            pos=lambda obj, value:
            setattr(self.background, "pos", value),

            size=lambda obj, value:
            setattr(self.background, "size", value)
        )

        # =================================================
        # HEADER
        # =================================================

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(75)
        )

        header.add_widget(
            Label(
                text="J A R V I S",
                font_size=dp(28),
                bold=True,
                color=(0.1, 0.9, 1, 1)
            )
        )

        header.add_widget(
            Label(
                text="AI COMMAND CENTER",
                font_size=dp(11),
                color=(0.2, 0.7, 0.9, 1)
            )
        )

        root.add_widget(header)

        # =================================================
        # SYSTEM STATUS
        # =================================================

        status = Card(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            padding=dp(10)
        )

        status.add_widget(
            Label(
                text="● SYSTEM STATUS",
                font_size=dp(15),
                color=(0.2, 0.9, 0.5, 1)
            )
        )

        status.add_widget(
            Label(
                text="OPTIMAL",
                font_size=dp(15),
                color=(0.3, 1, 0.6, 1)
            )
        )

        root.add_widget(status)

        # =================================================
        # AI CORE
        # =================================================

        core = Card(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(5)
        )

        core.add_widget(
            Label(
                text="AI CORE",
                font_size=dp(14),
                color=(0.2, 0.7, 1, 1)
            )
        )

        core.add_widget(
            Label(
                text="● ACTIVE",
                font_size=dp(25),
                bold=True,
                color=(0.1, 0.9, 1, 1)
            )
        )

        core.add_widget(
            Label(
                text="My AI is online and ready",
                font_size=dp(13),
                color=(0.5, 0.7, 0.8, 1)
            )
        )

        root.add_widget(core)

        # =================================================
        # INFORMATION
        # =================================================

        info = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(100)
        )

        info.add_widget(
            self.make_info_card(
                "MEMORY",
                "● READY"
            )
        )

        info.add_widget(
            self.make_info_card(
                "VOICE",
                "● VOSK"
            )
        )

        root.add_widget(info)

        # =================================================
        # RESPONSE
        # =================================================

        response_card = Card(
            orientation="vertical",
            padding=dp(10)
        )

        self.output = Label(
            text="Welcome, operator.\nLoading offline voice...",
            font_size=dp(17),
            halign="center",
            valign="middle",
            color=(0.75, 0.9, 1, 1)
        )

        self.output.bind(
            size=lambda obj, value:
            setattr(obj, "text_size", value)
        )

        response_card.add_widget(self.output)

        root.add_widget(response_card)

        # =================================================
        # QUICK COMMANDS
        # =================================================

        root.add_widget(
            Label(
                text="QUICK COMMANDS",
                size_hint_y=None,
                height=dp(30),
                font_size=dp(13),
                color=(0.1, 0.75, 1, 1)
            )
        )

        commands = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(90)
        )

        commands.add_widget(
            self.quick_button("HELLO")
        )

        commands.add_widget(
            self.quick_button("MY NAME")
        )

        commands.add_widget(
            self.quick_button("MEMORY")
        )

        commands.add_widget(
            self.quick_button("SYSTEM")
        )

        root.add_widget(commands)

        # =================================================
        # COMMAND INPUT
        # =================================================

        self.input_box = TextInput(
            hint_text="Enter command...",
            multiline=False,
            font_size=dp(18),
            size_hint_y=None,
            height=dp(55),
            padding=[dp(15), dp(15)],
            foreground_color=(0.8, 0.95, 1, 1),
            background_color=(0.02, 0.08, 0.13, 1)
        )

        self.input_box.bind(
            on_text_validate=self.send_command
        )

        root.add_widget(self.input_box)

        # =================================================
        # BUTTONS
        # =================================================

        buttons = GridLayout(
            cols=2,
            spacing=dp(8),
            size_hint_y=None,
            height=dp(60)
        )

        send = Button(
            text="▶ EXECUTE",
            font_size=dp(15),
            bold=True,
            background_normal="",
            background_color=(0.02, 0.35, 0.5, 1),
            color=(0.7, 0.95, 1, 1)
        )

        send.bind(
            on_press=self.send_command
        )

        mic = Button(
            text="🎙  VOICE",
            font_size=dp(15),
            bold=True,
            background_normal="",
            background_color=(0.02, 0.25, 0.4, 1),
            color=(0.7, 0.95, 1, 1)
        )

        mic.bind(
            on_press=self.start_voice
        )

        buttons.add_widget(send)
        buttons.add_widget(mic)

        root.add_widget(buttons)

        # =================================================
        # LOAD VOSK AFTER UI
        # =================================================

        Clock.schedule_once(
            lambda dt: self.load_vosk_model(),
            0.5
        )

        return root

    # =====================================================
    # VOSK MODEL LOADING
    # =====================================================

    def load_vosk_model(self):

        try:

            from jnius import autoclass

            StorageService = autoclass(
                "org.vosk.android.StorageService"
            )

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            self.output.text = (
                "Loading Vosk model..."
            )

            # Keep callbacks alive
            self.vosk_model_callback = (
                VoskModelCallback(self)
            )

            self.vosk_model_error_callback = (
                VoskModelErrorCallback(self)
            )

            StorageService.unpack(
                PythonActivity.mActivity,
                "model",
                "model",
                self.vosk_model_callback,
                self.vosk_model_error_callback
            )

        except Exception as e:

            self.output.text = (
                "VOSK LOAD ERROR:\n"
                + str(e)
            )

    # =====================================================
    # VOSK MODEL SUCCESS
    # =====================================================

    def on_vosk_model_loaded(self, model):

        self.vosk_model = model

        self.output.text = (
            "Vosk model loaded successfully.\n"
            "Press VOICE."
        )

    # =====================================================
    # VOSK MODEL ERROR
    # =====================================================

    def on_vosk_model_error(self, exception):

        self.vosk_model = None

        self.output.text = (
            "VOSK MODEL ERROR:\n"
            + str(exception)
        )

    # =====================================================
    # INFORMATION CARD
    # =====================================================

    def make_info_card(self, title, status):

        card = Card(
            orientation="vertical",
            padding=dp(8)
        )

        card.add_widget(
            Label(
                text=title,
                font_size=dp(12),
                color=(0.3, 0.7, 0.9, 1)
            )
        )

        card.add_widget(
            Label(
                text=status,
                font_size=dp(15),
                color=(0.3, 0.95, 0.7, 1)
            )
        )

        return card

    # =====================================================
    # QUICK BUTTON
    # =====================================================

    def quick_button(self, text):

        button = Button(
            text=text,
            font_size=dp(13),
            background_normal="",
            background_color=(0.03, 0.13, 0.2, 1),
            color=(0.4, 0.85, 1, 1)
        )

        button.bind(
            on_press=lambda instance:
            self.quick_command(text)
        )

        return button

    # =====================================================
    # QUICK COMMAND
    # =====================================================

    def quick_command(self, command):

        commands = {
            "HELLO": "hello",
            "MY NAME": "what is your name",
            "MEMORY": "what do you remember",
            "SYSTEM": "hello"
        }

        self.input_box.text = commands[command]

        self.send_command(None)

    # =====================================================
    # SEND COMMAND
    # =====================================================

    def send_command(self, instance):

        command = self.input_box.text.strip()

        if not command:
            return

        response = self.brain.think(command)

        if response.startswith("EXECUTE:"):

            action = response.replace(
                "EXECUTE:",
                "",
                1
            ).strip()

            if action.startswith("open "):

                app_name = action[5:].strip()

                self.open_android_app(app_name)

                return

        self.output.text = response

        self.input_box.text = ""

    # =====================================================
    # START VOSK VOICE
    # =====================================================

    def start_voice(self, instance):

        # If already listening, stop it
        if self.vosk_speech_service is not None:

            self.stop_voice()

            return

        # Model must be loaded first
        if self.vosk_model is None:

            self.output.text = (
                "Vosk model is not ready yet."
            )

            return

        # Request microphone permission
        try:

            from android.permissions import (
                request_permissions,
                Permission
            )

            request_permissions([
                Permission.RECORD_AUDIO
            ])

        except Exception:
            pass

        try:

            from jnius import autoclass

            Recognizer = autoclass(
                "org.vosk.Recognizer"
            )

            SpeechService = autoclass(
                "org.vosk.android.SpeechService"
            )

            self.vosk_recognizer = Recognizer(
                self.vosk_model,
                16000.0
            )

            self.vosk_speech_service = SpeechService(
                self.vosk_recognizer,
                16000.0
            )

            # Proper PyJNIus Java interface implementation
            self.vosk_listener = (
                VoskRecognitionListener(self)
            )

            self.output.text = (
                "Listening offline..."
            )

            self.vosk_speech_service.startListening(
                self.vosk_listener
            )

        except Exception as e:

            self.output.text = (
                "Vosk voice failed:\n"
                + str(e)
            )

            self.cleanup_vosk()

    # =====================================================
    # VOSK PARTIAL RESULT
    # =====================================================

    def on_vosk_partial(self, hypothesis):

        try:

            self.output.text = (
                "Listening...\n"
                + str(hypothesis)
            )

        except Exception:
            pass

    # =====================================================
    # VOSK RESULT
    # =====================================================

    def on_vosk_result(self, hypothesis):

        try:

            import json

            data = json.loads(
                str(hypothesis)
            )

            text = data.get(
                "text",
                ""
            ).strip()

            if text:

                self.input_box.text = text

        except Exception:
            pass

    # =====================================================
    # VOSK FINAL RESULT
    # =====================================================

    def on_vosk_final(self, hypothesis):

        try:

            import json

            data = json.loads(
                str(hypothesis)
            )

            text = data.get(
                "text",
                ""
            ).strip()

            self.cleanup_vosk()

            if text:

                self.input_box.text = text

                self.send_command(None)

            else:

                self.output.text = (
                    "I couldn't understand you."
                )

        except Exception as e:

            self.cleanup_vosk()

            self.output.text = (
                "Voice processing error:\n"
                + str(e)
            )

    # =====================================================
    # VOSK ERROR
    # =====================================================

    def on_vosk_error(self, error):

        self.output.text = (
            "Vosk microphone error:\n"
            + str(error)
        )

        self.cleanup_vosk()

    # =====================================================
    # VOSK TIMEOUT
    # =====================================================

    def on_vosk_timeout(self):

        self.cleanup_vosk()

        self.output.text = (
            "Listening stopped."
        )

    # =====================================================
    # STOP VOICE
    # =====================================================

    def stop_voice(self):

        try:

            if self.vosk_speech_service is not None:

                self.vosk_speech_service.stop()

        except Exception:
            pass

        self.cleanup_vosk()

        self.output.text = (
            "Voice stopped."
        )

    # =====================================================
    # CLEANUP VOSK
    # =====================================================

    def cleanup_vosk(self):

        try:

            if self.vosk_speech_service is not None:

                self.vosk_speech_service.shutdown()

        except Exception:
            pass

        self.vosk_speech_service = None
        self.vosk_recognizer = None

    # =====================================================
    # ANDROID APP LAUNCHER
    # =====================================================

    def open_android_app(self, app_name):

        self.output.text = (
            "Opening " + app_name + "..."
        )

        try:

            from jnius import autoclass

            Intent = autoclass(
                "android.content.Intent"
            )

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            apps = {
                "youtube":
                    "com.google.android.youtube",

                "chrome":
                    "com.android.chrome",

                "whatsapp":
                    "com.whatsapp",

                "settings":
                    "com.android.settings"
            }

            package_name = apps.get(
                app_name.lower()
            )

            if not package_name:

                self.output.text = (
                    "I don't know how to open "
                    + app_name
                )

                self.input_box.text = ""

                return

            activity = PythonActivity.mActivity

            intent = Intent(
                Intent.ACTION_MAIN
            )

            intent.addCategory(
                Intent.CATEGORY_LAUNCHER
            )

            intent.setPackage(
                package_name
            )

            activity.startActivity(intent)

            self.output.text = (
                "Opening " + app_name + "..."
            )

        except Exception as e:

            self.output.text = (
                app_name +
                " could not be opened.\n"
                + str(e)
            )

        self.input_box.text = ""

    # =====================================================
    # APP SHUTDOWN
    # =====================================================

    def on_stop(self):

        self.cleanup_vosk()


# =========================================================
# RUN APP
# =========================================================

MyAIApp().run()