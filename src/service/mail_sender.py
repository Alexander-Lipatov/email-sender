



from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


async def send_simple_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, login, password):
    # Создаем объект MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Добавляем тело письма
    msg.attach(MIMEText(body, 'plain'))

    # Устанавливаем соединение с сервером
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(login, password)

    # Отправляем письмо
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()

# Пример использования функции
send_simple_email(
    sender_email="your_email@example.com",
    receiver_email="receiver@example.com",
    subject="Тестовое письмо",
    body="Это тестовое письмо, отправленное с помощью Python.",
    smtp_server="smtp.example.com",
    smtp_port=587,
    login="your_email@example.com",
    password="your_password"
)
