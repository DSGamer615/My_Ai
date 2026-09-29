__version__ = "0.5.0"

import os
import json
import shutil
import threading

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


# ============================================================
# JARVIS UI CARD
# ============================================================

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


# ============================================================
# MAIN APP
# ============================================================

class MyAIApp(App):

    def build(self):

        # ----------------------------------------------------
        # AI BRAIN
        # ----------------------------------------------------

        self.brain = AIBrain()

        # ----------------------------------------------------
        # VOSK
        # ----------------------------------------------------

        self.vosk_model = None
        self.vosk_recognizer = None

        self.audio_record = None
        self.voice_thread = None
        self.voice_running = False

        self.model_path = None

        # ----------------------------------------------------
        # ROOT
        # ----------------------------------------------------

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

        # ====================================================
        # HEADER
        # ====================================================

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

        # ====================================================
        # SYSTEM STATUS
        # ====================================================

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

        # ====================================================
        # AI CORE
        # ====================================================

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

        # ====================================================
        # INFO CARDS
        # ====================================================

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

        # ====================================================
        # RESPONSE PANEL
        # ====================================================

        response_card = Card(
            orientation="vertical",
            padding=dp(10)
        )

        self.output = Label(
            text="Welcome, operator.\nPreparing offline voice...",
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

        # ====================================================
        # QUICK COMMANDS
        # ====================================================

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

        # ====================================================
        # COMMAND INPUT
        # ====================================================

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

        # ====================================================
        # BUTTONS
        # ====================================================

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

        # ====================================================
        # LOAD VOSK
        # ====================================================

        Clock.schedule_once(
            lambda dt: self.load_vosk_model(),
            0.5
        )

        return root

    # ========================================================
    # VOSK MODEL LOADING
    # ========================================================

    def load_vosk_model(self):

        self.output.text = (
            "Preparing Vosk model...\n"
            "Please wait."
        )

        threading.Thread(
            target=self.prepare_vosk_model,
            daemon=True
        ).start()

    def prepare_vosk_model(self):

        try:

            from jnius import autoclass

            # ------------------------------------------------
            # Android activity
            # ------------------------------------------------

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            activity = PythonActivity.mActivity

            # ------------------------------------------------
            # Android asset manager
            # ------------------------------------------------

            asset_manager = activity.getAssets()

            # ------------------------------------------------
            # Internal application storage
            # ------------------------------------------------

            files_dir = activity.getFilesDir()

            files_path = str(
                files_dir.getAbsolutePath()
            )

            model_destination = os.path.join(
                files_path,
                "vosk-model-small-en-in-0.4"
            )

            # ------------------------------------------------
            # Copy model from APK assets
            # ------------------------------------------------

            Clock.schedule_once(
                lambda dt:
                self.set_output(
                    "Copying Vosk model...\n"
                    "First launch may take a little time."
                )
            )

            self.copy_asset_folder(
                asset_manager,
                "model",
                model_destination
            )

            # ------------------------------------------------
            # Load Vosk Model
            # ------------------------------------------------

            Model = autoclass(
                "org.vosk.Model"
            )

            model = Model(
                model_destination
            )

            self.vosk_model = model
            self.model_path = model_destination

            Clock.schedule_once(
                lambda dt:
                self.set_output(
                    "Vosk model loaded successfully.\n"
                    "Press VOICE."
                )
            )

        except Exception as e:

            error_text = str(e)

            Clock.schedule_once(
                lambda dt:
                self.set_output(
                    "VOSK LOAD ERROR:\n"
                    + error_text
                )
            )

    # ========================================================
    # COPY APK ASSET DIRECTORY
    # ========================================================

    def copy_asset_folder(
        self,
        asset_manager,
        asset_folder,
        destination
    ):

        if not os.path.exists(destination):
            os.makedirs(destination)

        children = asset_manager.list(
            asset_folder
        )

        # ----------------------------------------------------
        # Directory
        # ----------------------------------------------------

        if children and len(children) > 0:

            for child in children:

                source_child = (
                    asset_folder
                    + "/"
                    + str(child)
                )

                destination_child = os.path.join(
                    destination,
                    str(child)
                )

                self.copy_asset_folder(
                    asset_manager,
                    source_child,
                    destination_child
                )

            return

        # ----------------------------------------------------
        # File
        # ----------------------------------------------------

        self.copy_asset_file(
            asset_manager,
            asset_folder,
            destination
        )

    # ========================================================
    # COPY SINGLE ASSET FILE
    # ========================================================

    def copy_asset_file(
        self,
        asset_manager,
        asset_path,
        destination_path
    ):

        from jnius import autoclass

        FileOutputStream = autoclass(
            "java.io.FileOutputStream"
        )

        input_stream = None
        output_stream = None

        try:

            input_stream = asset_manager.open(
                asset_path
            )

            output_stream = FileOutputStream(
                destination_path
            )

            # 8 KB buffer
            buffer = bytearray(8192)

            while True:

                count = input_stream.read(
                    buffer,
                    0,
                    len(buffer)
                )

                if count <= 0:
                    break

                output_stream.write(
                    buffer,
                    0,
                    count
                )

        finally:

            try:
                if input_stream is not None:
                    input_stream.close()
            except Exception:
                pass

            try:
                if output_stream is not None:
                    output_stream.close()
            except Exception:
                pass

    # ========================================================
    # VOICE START
    # ========================================================

    def start_voice(self, instance):

        if self.voice_running:

            self.stop_voice()

            return

        if self.vosk_model is None:

            self.output.text = (
                "Vosk model is not ready yet."
            )

            return

        # ----------------------------------------------------
        # Request microphone permission
        # ----------------------------------------------------

        try:

            from android.permissions import (
                request_permissions,
                Permission
            )

            request_permissions(
                [Permission.RECORD_AUDIO]
            )

        except Exception:
            pass

        # ----------------------------------------------------
        # Start microphone
        # ----------------------------------------------------

        try:

            from jnius import autoclass

            AudioRecord = autoclass(
                "android.media.AudioRecord"
            )

            AudioSource = autoclass(
                "android.media.MediaRecorder$AudioSource"
            )

            AudioFormat = autoclass(
                "android.media.AudioFormat"
            )

            # ------------------------------------------------
            # Audio settings
            # ------------------------------------------------

            sample_rate = 16000

            channel_config = (
                AudioFormat.CHANNEL_IN_MONO
            )

            audio_format = (
                AudioFormat.ENCODING_PCM_16BIT
            )

            # ------------------------------------------------
            # Buffer
            # ------------------------------------------------

            min_buffer = AudioRecord.getMinBufferSize(
                sample_rate,
                channel_config,
                audio_format
            )

            if min_buffer <= 0:
                min_buffer = 8192

            buffer_size = max(
                min_buffer,
                8192
            )

            # ------------------------------------------------
            # Create AudioRecord
            # ------------------------------------------------

            self.audio_record = AudioRecord(
                AudioSource.VOICE_RECOGNITION,
                sample_rate,
                channel_config,
                audio_format,
                buffer_size * 2
            )

            # ------------------------------------------------
            # Check recorder
            # ------------------------------------------------

            state = self.audio_record.getState()

            if state != AudioRecord.STATE_INITIALIZED:

                self.audio_record.release()

                self.audio_record = None

                self.output.text = (
                    "Microphone could not be initialized."
                )

                return

            # ------------------------------------------------
            # Create recognizer
            # ------------------------------------------------

            from jnius import autoclass

            Recognizer = autoclass(
                "org.vosk.Recognizer"
            )

            self.vosk_recognizer = Recognizer(
                self.vosk_model,
                16000.0
            )

            # ------------------------------------------------
            # Start recording
            # ------------------------------------------------

            self.audio_record.startRecording()

            self.voice_running = True

            self.output.text = (
                "🎙 Listening offline...\n"
                "Speak now."
            )

            # ------------------------------------------------
            # Start Python voice thread
            # ------------------------------------------------

            self.voice_thread = threading.Thread(
                target=self.voice_loop,
                daemon=True
            )

            self.voice_thread.start()

        except Exception as e:

            self.output.text = (
                "VOICE START ERROR:\n"
                + str(e)
            )

            self.cleanup_voice()

    # ========================================================
    # VOICE LOOP
    # ========================================================

    def voice_loop(self):

        try:

            # ------------------------------------------------
            # Java byte array
            # ------------------------------------------------

            from jnius import jarray

            buffer_size = 8192

            audio_buffer = jarray(
                "b",
                buffer_size
            )

            while self.voice_running:

                if self.audio_record is None:
                    break

                # ------------------------------------------------
                # Read microphone
                # ------------------------------------------------

                count = self.audio_record.read(
                    audio_buffer,
                    0,
                    buffer_size
                )

                if count <= 0:
                    continue

                # ------------------------------------------------
                # Send PCM to Vosk
                # ------------------------------------------------

                accepted = (
                    self.vosk_recognizer.acceptWaveForm(
                        audio_buffer,
                        count
                    )
                )

                # ------------------------------------------------
                # Speech result
                # ------------------------------------------------

                if accepted:

                    result = str(
                        self.vosk_recognizer.getResult()
                    )

                    Clock.schedule_once(
                        lambda dt,
                        r=result:
                        self.process_vosk_result(r)
                    )

                else:

                    partial = str(
                        self.vosk_recognizer.getPartialResult()
                    )

                    Clock.schedule_once(
                        lambda dt,
                        p=partial:
                        self.show_partial_result(p)
                    )

            # ------------------------------------------------
            # Final result
            # ------------------------------------------------

            if self.vosk_recognizer is not None:

                final_result = str(
                    self.vosk_recognizer.getFinalResult()
                )

                Clock.schedule_once(
                    lambda dt,
                    r=final_result:
                    self.process_final_result(r)
                )

        except Exception as e:

            error_text = str(e)

            Clock.schedule_once(
                lambda dt:
                self.voice_error(error_text)
            )

    # ========================================================
    # PARTIAL RESULT
    # ========================================================

    def show_partial_result(self, result):

        try:

            data = json.loads(
                result
            )

            text = data.get(
                "partial",
                ""
            ).strip()

            if text:

                self.output.text = (
                    "🎙 Listening...\n"
                    + text
                )

        except Exception:
            pass

    # ========================================================
    # NORMAL RESULT
    # ========================================================

    def process_vosk_result(self, result):

        try:

            data = json.loads(
                result
            )

            text = data.get(
                "text",
                ""
            ).strip()

            if text:

                self.output.text = (
                    "You said:\n"
                    + text
                )

                self.input_box.text = text

        except Exception:
            pass

    # ========================================================
    # FINAL RESULT
    # ========================================================

    def process_final_result(self, result):

        try:

            data = json.loads(
                result
            )

            text = data.get(
                "text",
                ""
            ).strip()

            self.cleanup_voice()

            if text:

                self.input_box.text = text

                self.send_command(
                    None
                )

            else:

                self.output.text = (
                    "I couldn't understand you."
                )

        except Exception as e:

            self.cleanup_voice()

            self.output.text = (
                "Voice processing error:\n"
                + str(e)
            )

    # ========================================================
    # VOICE ERROR
    # ========================================================

    def voice_error(self, error):

        self.cleanup_voice()

        self.output.text = (
            "Vosk microphone error:\n"
            + error
        )

    # ========================================================
    # STOP VOICE
    # ========================================================

    def stop_voice(self):

        self.voice_running = False

        try:

            if self.audio_record is not None:

                self.audio_record.stop()

        except Exception:
            pass

        self.cleanup_voice()

        self.output.text = (
            "Voice stopped."
        )

    # ========================================================
    # CLEANUP VOICE
    # ========================================================

    def cleanup_voice(self):

        self.voice_running = False

        try:

            if self.audio_record is not None:

                try:
                    self.audio_record.stop()
                except Exception:
                    pass

                try:
                    self.audio_record.release()
                except Exception:
                    pass

        except Exception:
            pass

        self.audio_record = None

        self.vosk_recognizer = None

        self.voice_thread = None

    # ========================================================
    # UI OUTPUT
    # ========================================================

    def set_output(self, text):

        self.output.text = text

    # ========================================================
    # INFO CARD
    # ========================================================

    def make_info_card(
        self,
        title,
        status
    ):

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

    # ========================================================
    # QUICK BUTTON
    # ========================================================

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

    # ========================================================
    # QUICK COMMAND
    # ========================================================

    def quick_command(self, command):

        commands = {
            "HELLO": "hello",
            "MY NAME": "what is your name",
            "MEMORY": "what do you remember",
            "SYSTEM": "hello"
        }

        self.input_box.text = commands[
            command
        ]

        self.send_command(
            None
        )

    # ========================================================
    # SEND COMMAND
    # ========================================================

    def send_command(self, instance):

        command = self.input_box.text.strip()

        if not command:
            return

        response = self.brain.think(
            command
        )

        if response.startswith(
            "EXECUTE:"
        ):

            action = response.replace(
                "EXECUTE:",
                "",
                1
            ).strip()

            if action.startswith(
                "open "
            ):

                app_name = action[
                    5:
                ].strip()

                self.open_android_app(
                    app_name
                )

                return

        self.output.text = response

        self.input_box.text = ""

    # ========================================================
    # OPEN ANDROID APP
    # ========================================================

    def open_android_app(
        self,
        app_name
    ):

        self.output.text = (
            "Opening "
            + app_name
            + "..."
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

            activity = (
                PythonActivity.mActivity
            )

            intent = Intent(
                Intent.ACTION_MAIN
            )

            intent.addCategory(
                Intent.CATEGORY_LAUNCHER
            )

            intent.setPackage(
                package_name
            )

            activity.startActivity(
                intent
            )

            self.output.text = (
                "Opening "
                + app_name
                + "..."
            )

        except Exception as e:

            self.output.text = (
                app_name
                + " could not be opened.\n"
                + str(e)
            )

        self.input_box.text = ""

    # ========================================================
    # APP STOP
    # ========================================================

    def on_stop(self):

        self.cleanup_voice()


# ============================================================
# START
# ============================================================

MyAIApp().run()