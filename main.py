from fastapi import FastAPI, BackgroundTasks, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
# import smtplib
# from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update if deployed
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)


# Form data model
class EmailRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    date: str
    destination: str
    departure: str
    rooms: int
    days: int
    people: int
    message: str
    comments: str


@app.post("/send-email/")
async def send_email(email_data: EmailRequest, background_tasks: BackgroundTasks):
    try:
        conf = ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
            MAIL_FROM=email_data.email,
            MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
            MAIL_PORT=int(os.getenv("MAIL_PORT")),
            MAIL_SERVER=os.getenv("MAIL_SERVER"),
            MAIL_SSL_TLS=False,  # Gmail doesn't use SSL over port 587
            MAIL_STARTTLS=True,
            USE_CREDENTIALS=True
        )

        format_body = f"""<h3> From: {email_data.name} </h3>
    <h3> Email: {email_data.email} </h3>
    <h3> Phone no. : {email_data.phone} </h3>
    <h3> Departure Date: {email_data.date} </h3>
    <h3> Destination: {email_data.destination} </h3>
    <h3> Departure City: {email_data.departure} </h3>
    <h3> Number of Rooms: {email_data.rooms} </h3>
    <h3> Number of Days to Stay: {email_data.days} </h3>
    <h3> Number of People: {email_data.people} </h3>
    <h3> Comments: {email_data.comments}
    """

        message = MessageSchema(
            subject=f"Concordia Expedition Trip Plan by {email_data.email}",
            recipients=[os.getenv("MAIL_USERNAME")],
            body=format_body,
            subtype="html"  # or "plain"
        )

        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message, message)
        return JSONResponse({"message": "Email has been sent"}, status_code=status.HTTP_200_OK, media_type="application/json")
    except Exception as e:
        print(e)
        return JSONResponse({"error": "Error executing send-email!"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, media_type="application/json")

if __name__ == "__main__":
    uvicorn.run(app)
