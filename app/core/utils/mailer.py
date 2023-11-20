from typing import List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Environment, PackageLoader, select_autoescape
from pydantic import BaseModel, EmailStr

from app.core.settings import settings

env = Environment(
    loader=PackageLoader("app", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


class EmailSchema(BaseModel):
    email: List[EmailStr]


class Email:
    def __init__(self, name: str, url: str, email: List[EmailStr]):
        self.name = name
        self.sender = "Edu Predict <from@example.com>"
        self.email = email
        self.url = url
        pass

    async def send_mail(self, subject, template):
        # Define the config
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.EMAIL_USERNAME,
            MAIL_PASSWORD=settings.EMAIL_PASSWORD,
            MAIL_FROM=settings.EMAIL_FROM,
            MAIL_PORT=settings.EMAIL_PORT,
            MAIL_SERVER=settings.EMAIL_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )
        # Generate the HTML template base on the template name
        template = env.get_template(f"{template}.html")

        html = template.render(url=self.url, first_name=self.name, subject=subject)

        # Define the message options
        message = MessageSchema(
            subject=subject, recipients=self.email, body=html, subtype="html"
        )

        # Send the email
        fm = FastMail(conf)
        await fm.send_message(message)
