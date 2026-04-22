import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_confirmation_email(patient_email, patient_name, doctor_name, date, time):
    # 1. Configuration (Use environment variables for security!)
    sender_email = "pymejohn@gmail.com"
    sender_password = "wgqe gqzz zeis batu" 
    # sender_name= "Aurora International Clinic"
    #  Create the email content
    html_body = f"""
        <html>
        <body style="font-family: sans-serif; color: #333;">
            <div style="background-color: #009688; color: white; padding: 20px; text-align: center;">
                <h1>Aurora International Clinic</h1>
            </div>
            <div style="padding: 20px; border: 1px solid #ddd;">
                <p>Dear <strong>{patient_name}</strong>,</p>
                <p>Your appointment has been successfully booked!</p>
                <p>We look forward to seeing you with <strong>{doctor_name}</strong>.</p>
                <hr>
                <p>📅 <strong>Date:</strong> {date}</p>
                <p>⏰ <strong>Time:</strong> {time}</p>
                <p>Please arrive 10 minutes early. If you need to reschedule, reply to this email.</p>
                <p>Best regards,</p>
                <p>Aurora International Clinic Team</p>
            </div>
        </body>
        </html>
        """
    message = MIMEMultipart()
    message["From"] = f"Aurora International Clinic <{sender_email}>"
    message["To"] = patient_email
    message["Subject"] = "Appointment Confirmed - Aurora International Clinic"

    body = f"""
    Hello {patient_name},

    Your appointment has been successfully booked!

    Details:
    - Doctor: {doctor_name}
    - Date: {date}
    - Time: {time}

    Please arrive 10 minutes early. If you need to reschedule, reply to this email.
    
    Best regards,
    Aurora International Clinic Team
    """
    
    # message.attach(MIMEText(body, "plain"))
    message.attach(MIMEText(html_body, "html"))
    
    # 3. Send the email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, patient_email, message.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False