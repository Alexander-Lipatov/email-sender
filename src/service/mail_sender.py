

import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiosmtplib import SMTP
from src.config.settings import settings

async def send_email_async(
    sender_email: str,
    receiver_email: str,
    subject: str,
    body: str,
    smtp_server: str,
    smtp_port: int,
    login: str,
    password: str
):
    # Создаем объект MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject


    signature = """
<br><br>
<p>С уважением,</p>

<p>
<strong>Меркулова Татьяна Владимировна</strong><br>
Главный специалист отдела труда и мотивации<br>
ООО «Приморский металлургический завод»
</p>

<img src="https://facultetus.ru/images/logos/d3933bab099c80341c16bf59ca2baf6c.png" alt="Логотип компании" width="150">
"""

    msg.attach(MIMEText(body + signature, 'html'))

    # full_body = body + "\n\n" + signature
    # msg.attach(MIMEText(full_body, 'plain'))

    # Отправка письма
    smtp = SMTP(hostname=smtp_server, port=smtp_port, start_tls=True)
    await smtp.connect()
    await smtp.login(login, password)
    await smtp.send_message(msg)
    await smtp.quit()


async def send_email_with_semaphore(
        sender_email: str,
        receiver_email: str,
        subject: str,
        body: str,
):
    async with asyncio.Semaphore(10):
        await send_email_async(
            sender_email,
            receiver_email,
            subject,
            body,
            settings.smtp_server,
            settings.smtp_port,
            settings.login,
            settings.password
        )

# async def send_email_async(email, message):
#     async with SMTP(hostname="connect.smtp.bz", port=2525) as smtp:
#         print(email)
#         print(message)
#         await smtp.login("lap1993.12@yandex.ru", "tHZPe0nVMgSu")
#         await smtp.sendmail(
#             "lap1993.12@amber-sound.ru", email, message
#         )

# Пример использования функции


# def send_bulk_emails(db_path, smtp_server, smtp_port, login, password):
#     emails = fetch_emails_from_db(db_path)
#     for email in emails:
#         receiver_email, subject, body = email
#         send_simple_email(
#             sender_email=login,
#             receiver_email=receiver_email,
#             subject=subject,
#             body=body,
#             smtp_server=smtp_server,
#             smtp_port=smtp_port,
#             login=login,
#             password=password
#         )
