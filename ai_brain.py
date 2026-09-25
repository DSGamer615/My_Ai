class AIBrain:

    def __init__(self):
        self.name = "My AI"
        self.memory = {}
        self.pending_action = None

    def think(self, command):

        command = command.lower().strip()

        # --------------------------------
        # 1. Handle confirmation
        # --------------------------------

        if self.pending_action:

            if command in ["yes", "yeah", "yep", "sure", "ok", "okay"]:
                action = self.pending_action
                self.pending_action = None

                return f"EXECUTE:{action}"

            elif command in ["no", "nope", "cancel"]:
                self.pending_action = None
                return "Okay, cancelled."

            else:
                return "Please answer yes or no."

        # --------------------------------
        # 2. Greetings
        # --------------------------------

        if command in ["hi", "hello", "hey"]:
            return "Hello! I'm ready."

        # --------------------------------
        # 3. Name
        # --------------------------------

        if "what is your name" in command:
            return f"My name is {self.name}."

        # --------------------------------
        # 4. Remember
        # --------------------------------

        if command.startswith("remember "):

            information = command[9:].strip()

            if not information:
                return "What should I remember?"

            self.memory["user_info"] = information

            return "Okay, I'll remember that."

        # --------------------------------
        # 5. Memory
        # --------------------------------

        if "what do you remember" in command:

            if not self.memory:
                return "I don't have anything saved yet."

            return "I remember: " + self.memory["user_info"]

        # --------------------------------
        # 6. Open something
        # --------------------------------

        if command.startswith("open "):

            app = command[5:].strip()

            if not app:
                return "Which app do you want me to open?"

            self.pending_action = f"open {app}"

            return f"I understand that you want to open {app}. Should I do that?"

        # --------------------------------
        # 7. Unknown command
        # --------------------------------

        return "I'm not sure what you mean. Can you explain?"


# =====================================