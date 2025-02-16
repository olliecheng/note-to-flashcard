import toga
from toga.style.pack import COLUMN, LEFT, RIGHT, ROW, Pack

import traceback
import json
import csv
import copy
import keyring
import os

import external


class Settings:
    def __init__(self, app_id, path, default):
        os.makedirs(path, exist_ok=True)
        self.path = path / "config.json"

        self.app_id = app_id
        self.default = default
        self.keyring_user = "OpenAI_API_key"

        self.params = {}
        self.key = ""

        print(f"Settings on path {self.path}, appID {app_id}")

        self.load()

    def load(self):
        try:
            with open(self.path) as f:
                self.params = json.load(f)
        except Exception as e:
            print(f"Could not load settings due to {e}, resetting...")
            self.params = copy.deepcopy(self.default)

        self.key = keyring.get_password(self.app_id, self.keyring_user) or ""

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.params, f)
        keyring.set_password(self.app_id, self.keyring_user, self.key)


class ConverterApp(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = None
        self.settings = Settings(self.app_id, self.paths.config, {
            "tags": "",
            "headers": False,
            "delimiter": ","
        })

    def startup(self):
        def on_change_handler(_widget):
            self.cache = None
            if self.api_entry.value and self.notes_entry.value:
                self.button.enabled = True
            else:
                self.button.enabled = False

        box = toga.Box()
        box.style.update(direction = COLUMN, padding_left = 50, padding_right = 50, padding_bottom = 50, padding_top = 30)

        header_box = toga.Box()
        header_box.style.update(direction = ROW, padding_bottom = 20, alignment = "bottom")

        header_label = toga.Label("Notes to Flashcards")
        header_label.style.font_size = 20
        header_label.style.flex = 1
        header_label.style.font_weight = "bold"

        version_label = toga.Label("v1.0b1")

        header_box.add(header_label, version_label)

        api_box = toga.Box()
        api_box.style.update(direction = ROW, padding_bottom = 20)

        api_label = toga.Label("OpenAI API Key")
        api_label.style.padding_right = 10
        self.api_entry = toga.PasswordInput(on_change=on_change_handler, value=self.settings.key)
        self.api_entry.style.flex = 1

        api_box.add(api_label, self.api_entry)

        self.notes_entry = toga.MultilineTextInput(placeholder="Notes go here...", on_change=on_change_handler)
        self.notes_entry.style.padding_bottom = 20
        self.notes_entry.style.flex = 1
        self.notes_entry.scroll_to_top()

        #
        # OPTIONS
        #

        options_label = toga.Label("Options")
        options_label.style.font_weight = "bold"
        options_label.style.padding_bottom = 10

        self.separator = toga.Selection(items=[",", ";", ":"], value=self.settings.params["delimiter"])
        self.separator.style.padding_right = 40
        self.separator.style.padding_left = 5

        self.include_headers = toga.Switch("Include headers", value=self.settings.params["headers"])

        options_box_1 = toga.Box(
            children=[
                toga.Label("Separator"),
                self.separator,
                self.include_headers
            ]
        )
        options_box_1.style.alignment = "center"
        options_box_1.style.padding_bottom = 10

        self.tags = toga.TextInput(placeholder="Space-separated tags", value=self.settings.params["tags"])
        self.tags.style.padding_left = 5
        self.tags.style.flex = 1
        options_box_2 = toga.Box(
            children = [
                toga.Label("Tags"),
                self.tags
            ]
        )
        options_box_2.style.alignment = "center"
        options_box_2.style.padding_bottom = 20

        #
        # CONVERT AND STATUS
        #

        self.button = toga.Button("Convert", on_press=self.button_handler)
        self.button.style.padding_bottom = 10

        self.status_label = toga.Label("Ready")
        self.status_label.style.font_weight = "bold"
        self.status_label.style.flex = 1

        self.status_spin = toga.ActivityIndicator()
        self.status_spin.style.height = 20

        status_box = toga.Box(
            children = [
                self.status_label,
                self.status_spin
            ]
        )
        status_box.style.alignment = "center"

        box.add(
            header_box,
            api_box,
            self.notes_entry,
            options_label,
            options_box_1,
            options_box_2,
            self.button,
            status_box
        )

        self.main_window = toga.MainWindow()
        self.main_window.content = box
        self.main_window.show()

        on_change_handler(None)
        self.notes_entry.focus()

    def start_computation(self):
        self.button.enabled = False
        self.status_spin.start()

    def end_computation(self):
        self.button.enabled = True
        self.status_spin.stop()

    async def button_handler(self, _widget):
        self.start_computation()

        # save options
        self.settings.key = self.api_entry.value
        self.settings.params = {
            "tags": self.tags.value,
            "headers": self.include_headers.value,
            "delimiter": str(self.separator.value)
        }
        try:
            self.settings.save()
        except Exception as e:
            print(e)
            traceback.print_exc()

        # get file location dialog
        file_dialog = toga.SaveFileDialog("Save .csv", "flashcards.csv", file_types=["csv"])
        path = await self.main_window.dialog(file_dialog)
        if not path:
            self.status_label.text = "User cancelled save operation"
            self.end_computation()
            return
        print(path)

        try:
            self.status_label.text = "Contacting OpenAI... this may take a few seconds!"

            if not self.cache:
                response = await external.make_json(self.settings.key, self.notes_entry.value)
                self.cache = response
            else:
                print("Using cached")
                response = self.cache

            flashcards = json.loads(response)

            with open(path, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["question", "answer", "tags"], delimiter=self.settings.params["delimiter"])

                if self.settings.params["headers"]:
                    writer.writeheader()

                for card in flashcards["flashcards"]:
                    card["tags"] = self.settings.params["tags"]
                    writer.writerow(card)

            self.status_label.text = f"Written to {path}"

        except Exception as e:
            exc = traceback.format_exc()
            dialog = toga.StackTraceDialog("Error", f"OpenAI error: {e}", exc)
            await self.main_window.dialog(dialog)
            self.status_label.text = f"{e} Try again."

        self.end_computation()

def main():
    return ConverterApp("Note to Flashcard", "au.id.oyc.note_to_flashcard")


if __name__ == "__main__":
    main().main_loop()
