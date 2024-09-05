from typing import List

from pydantic import BaseModel
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from core.database import get_session
from core.config import *


DELETED_STATE = 0
ACTIVE_STATE = 1

session = next(get_session())


class Email_model(BaseModel):
    greetings: str = "Hello"
    username: str
    paragraph_1: str = "We received a request to reset your password. Please use the following code to reset your password:"
    code: str
    paragraph_2: str = "If you did not request a password reset, please ignore this email or contact support if you have any questions."
    ending_1: str = "Thanks,"
    ending_2: str = "The Team"
    subject: str = "Password Recovery"
    email:str

    def get_email_html_models(self):
        html = (f"""
        <!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Recovery</title>
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
            @import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');
            </style>
            </head>
            <body class="bg-gray-100 font-sans">
            <div class="max-w-lg mx-auto bg-white shadow-lg rounded-lg overflow-hidden mt-10">
            <div class=" pt-3 pb-3 mx-8 content-center">
            <div class="flex justify-center items-center h-20 pt-3 pb-3 mx-8">
            <?xml version="1.0" encoding="UTF-8"?>
            <svg version="1.1" viewBox="0 0 2048 670" width="100" height="100" xmlns="http://www.w3.org/2000/svg">
            <path transform="translate(314,55)" d="m0 0h44l27 3 25 5 24 7 25 10 16 8 14 8 21 14 14 11 24 22 14 15 13 17 10 14 12 21 10 21 8 21 7 24 6 31 3 33v15l-3 33-6 30-8 26-8 21-9 19-10 17-10 15-10 13-9 11-29 29-14 11-17 12-19 11-17 9-19 8-24 8-26 6-29 4-15 1h-28l-29-3-26-5-29-9-19-8-26-13-21-13-18-14-10-9-13-12-8-8-7-8-13-16-9-13-8-13-12-22-10-24-8-25-6-26-3-23-2-25v-9l1-3 1-20 4-26 6-25 9-27 6-16 4 1 9 9 13 9 17 9-1 5-10 31-5 26-1 7-1 34 2 26 6 28 5 17 10 24 11 21 10 15 10 13 18 20 14 13 16 12 17 11 23 12 26 10 22 6 25 4 26 2 28-2 24-4 25-7 21-8 16-8 16-9 17-12 14-11 24-24 13-17 10-15 12-23 8-19 7-23 5-24 2-21v-35l-5-32-7-25-10-25-12-23-10-15-11-14-11-12-17-17-14-11-13-9-19-11-19-9-18-7-22-6-22-4-22-2h-21l-27 3-27 6-24 8-6 1-11-21-8-10-8-9v-2l25-10 18-6 26-6z" fill="#E12E2E"/>
            <path transform="translate(323,193)" d="m0 0h29l26 4 24 8 19 10 16 12 10 9 7 7 10 13 10 17 7 16 5 15 4 23 1 12v18l-1 7-1 1-247 1 3 17 6 16 8 14 12 13 12 9 17 9 11 4 16 3 9 1h9l19-3 19-7 14-9 11-9 9-12 5-8h59l-1 4-10 19-12 17-12 14-14 12-15 10-15 8-16 6-22 5-20 2h-16l-23-3-19-5-16-7-15-8-15-11-12-11-9-10-10-14-9-16-8-20-5-19-2-13-1-21 3-26 6-22 7-16 7-13 8-12 11-13 13-13 15-11 16-9 16-7 18-5zm6 48-17 3-15 5-13 7-13 10-8 8-9 13-6 12-5 15-1 6 2 1h190l-1-8-5-15-6-12-9-12-11-11-10-7-16-8-15-5-15-2z" fill="#E12E2E"/>
            <path transform="translate(1489,188)" d="m0 0h55l1 1v302l-2 2h-51l-1-1-1-25-13 14-10 7-14 7-15 4-19 2h-13l-21-3-18-6-16-8-14-11-9-9-10-14-7-12-7-19-4-17-1-7v-31l3-17 7-21 8-15 8-11 9-10 10-9 14-9 11-5 15-5 18-3h22l17 3 15 5 14 8 10 8 8 8v-102zm-71 122-16 3-12 5-11 7-9 9-9 14-5 13-2 10v18l4 16 7 14 8 10 8 7 14 8 13 4 6 1h17l14-3 16-8 11-8 8-9 6-10 4-11 2-9v-23l-5-16-5-10-8-10-7-7-15-9-16-5-7-1z" fill="#E12E2E"/>
            <path transform="translate(876,259)" d="m0 0h19l21 3 18 6 16 8 13 10 17 17 10 15 8 17 5 17 3 22v12l-1 11-1 1-183 1 5 15 8 15 5 6 13 9 11 5 11 3 6 1h13l18-4 13-7 10-9 6-9 4-1h54l-1 4-8 15-8 12-9 10-11 11-13 9-15 8-15 5-15 3-12 1h-12l-17-2-15-4-12-5-17-9-13-11-11-11-10-14-8-16-6-16-4-20v-26l5-23 6-15 8-15 10-13 10-11 11-9 14-9 16-7 15-4zm1 47-14 3-16 8-12 11-8 13-5 14 1 2h127l1-2-8-19-8-10-9-8-12-7-13-4-6-1z" fill="#E12E2E"/>
            <path transform="translate(1141,259)" d="m0 0h22l20 3 16 5 17 8 13 9 12 11 8 8 10 15 9 19 3 9v5l-54 1-4-4-7-12-9-10-11-7-8-4-17-4h-14l-15 3-14 7-11 9-7 9-6 12-4 13-1 6v19l3 15 8 16 8 10 10 8 14 7 13 3h18l16-4 12-6 10-8 7-8 7-12h41l15 1-1 7-6 15-8 14-8 11-9 10-13 11-16 9-14 6-18 5-20 2h-12l-22-3-21-7-17-9-14-11-11-11-11-15-8-16-5-13-4-18-1-9 1-27 4-18 6-16 8-15 12-16 10-10 14-10 12-7 19-7 15-3z" fill="#E12E2E"/>
            <path transform="translate(1767,259)" d="m0 0h17l19 3 12 4 13 7 12 10 9 13 5 12 4 16-1 4h-54l-3-11-4-6-9-5-3-1h-15l-10 4-6 7-3 9 2 8 7 8 15 8 26 8 24 8 16 9 10 9 6 8 5 10 2 7v32l-2 9-4 10-8 12-5 6-13 10-15 7-17 5-17 2h-13l-19-3-19-7-11-7-12-11-8-11-6-13-4-17 1-5 53-1 5 12 6 9 8 5 9 3h12l11-4 8-6 4-8 1-4v-7l-3-8-9-8-18-8-44-16-13-7-9-7-7-7-7-12-3-10v-25l5-16 6-10 9-10 9-8 14-8 16-5z" fill="#E12E2E"/>
            <path transform="translate(673,188)" d="m0 0h54l1 1v303l-1 1h-53l-1-1z" fill="#E12E2E"/>
            <path transform="translate(1598,266)" d="m0 0h53l1 1v225l-1 1h-52l-2-2v-224z" fill="#E12E2E"/>
            <path transform="translate(137,72)" d="m0 0h22l15 3 14 6 15 10 12 12 9 14 6 16 3 16v17l-2 13-5 15-8 13-9 11-12 10-16 8-12 4-19 3-16-1-16-4-16-8-11-8-9-9-10-15-6-14-3-13-1-9v-10l2-14 5-15 8-15 11-13 11-9 17-9 14-4zm4 13-15 3-12 5-13 9-9 9-7 11-6 13-3 12v20l3 12 5 12 9 13 7 7 13 9 16 7 10 2h17l17-4 12-6 12-9 9-10 8-14 5-16 1-6v-13l-4-17-5-11-7-11-6-7-12-9-15-7-10-3-7-1z" fill="#E12E2E"/>
            <path transform="translate(1598,188)" d="m0 0h54v47l-1 1h-53l-1-1v-46z" fill="#E12E2E"/>
            <path transform="translate(1936,201)" d="m0 0 6 1 3 5 11 27 11 29 1 1 6-14 8-21 11-26 4-2h6l1 2v74l-6 1-1-1-1-47-1-10-8 19-8 21-7 16-2 2-4-1-5-6-14-36-6-16-1 57-1 1h-7l-1-1v-73z" fill="#E12E2E"/>
            <path transform="translate(1867,202)" d="m0 0h59l2 1-2 5-2 1-23 1-1 67h-7l-2-4v-64h-24l-2-1v-5z" fill="#E12E2E"/>
            </svg>
            
            </div>
            </div>
            <div class="p-6">
            <p class="text-gray-700">{self.greetings} {self.username} ,</p>
            <p class="text-gray-700 mt-4">{self.paragraph_1}</p>
            <div class="bg-red-50 border border-red-200 text-red-900 text-center text-xl font-bold py-4 mt-6 rounded">
            {self.code}
            </div>
            <div class="flex justify-center items-center h-20">
                <a href="{CODE_LINK}" type="button" class="text-white bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700 hover:bg-gradient-to-br focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2">click here</a>
            </div>
            
            <p class="text-gray-700 mt-6">{self.paragraph_2}</p>
            <p class="text-gray-700 mt-6">{self.ending_1}</p>
            <p class="text-gray-700">{self.ending_2}</p>
            </div>
            </div>
            </body>
            </html>
            """)
        return html

#
conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=USE_CREDENTIALS
)


async def send_email(email_to_send: Email_model, recipient: List):
    message = MessageSchema(
        subject=email_to_send.subject,
        recipients=recipient,
        body=email_to_send.get_email_html_models(),
        subtype="html"
    )
    try:
        fm = FastMail(conf)
        await fm.send_message(message)
        print("Email sent successfully")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

