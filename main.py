
from src.config.settings import settings
from src.service.mail_sender import send_email_with_semaphore
import asyncio
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Form, status, Body, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prisma import Prisma
from pydantic import BaseModel


app = FastAPI()
db: Prisma = Prisma()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def get_all_messages(request: Request) -> HTMLResponse:
    await db.connect()

    tasks = await db.task.find_many(
        order={
            'updated_at': 'desc',
        },
    )

    await db.disconnect()
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks})


@app.get("/tasks/{task_id}")
async def get_(task_id: str, request: Request):

    await db.connect()

    task = await db.task.find_unique(
        where={
            "id": task_id,

        },
        include={
            "message": True,
            "recipients": {
                "include": {
                    "recipient": True
                }
            }
        }
    )

    await db.disconnect()
    if task:
        return templates.TemplateResponse("task_detail.html", {"request": request, "task": task, 'message': task.message, "recipients": task.recipients})

    return templates.TemplateResponse("404.html", {"request": request}, status_code=status.HTTP_404_NOT_FOUND, )


class EmailMessage(BaseModel):
    subject: str
    text: str


class Recipient(BaseModel):
    email: str


@app.get('/create')
async def create_mail(request: Request):

    return templates.TemplateResponse("create_task.html", {"request": request})


@app.post('/create')
async def create_mail(
    request: Request,
    bg_tasks: BackgroundTasks,
):

    form = await request.form()

    # Преобразуем form в обычный dict
    form_data = dict(form)

    print(form_data)
    print()

    await db.connect()

    task = await db.task.create(
        data={
            "title": form_data['subject'],
            "message": {
                "create": {
                    "subject": form_data['subject'],
                    "text": form_data['message']
                }
            },
            "recipients": {
                "create": [
                    {
                        "recipient": {
                            "connectOrCreate": {
                                "where": {"email": email},
                                "create": {"email": email}
                            }
                        }
                    }
                    for email in form_data['emails'].splitlines() if email.strip()
                ]
            }
        }
    )

    await db.disconnect()

    return RedirectResponse("/", status_code=303)


@app.post("/tasks/{task_id}/send")
async def send_task(task_id: str, bg_tasks: BackgroundTasks) -> dict:
    await db.connect()

    task = await db.task.find_unique(
        where={
            "id": task_id,
        },
        include={
            "message": True,
            "recipients": {
                "include": {
                    "recipient": True
                }

            }
        }
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.disconnect()
    print(task)

    for recipient in task.recipients:
        bg_tasks.add_task(
            send_email_with_semaphore,
            'lap1993.12@amber-sound.ru',
            recipient.recipient.email,
            task.message.subject,
            task.message.text,

        )
    return RedirectResponse("/", status_code=303)


@app.get("/settings")
async def get_settings(request: Request) -> HTMLResponse:

    return templates.TemplateResponse("settings_page.html", {"request": request, "settings": settings})


@app.post("/settings")
async def update_settings(request: Request, bg_tasks: BackgroundTasks):
    form = await request.form()
    form_data = dict(form)
    print(form_data)
    settings.sender_email = form_data['sender_email']
    settings.smtp_server = form_data['smtp_server']
    settings.smtp_port = int(form_data['smtp_port'])
    settings.login = form_data['login']
    settings.password = form_data['password']
    settings.signature = form_data['signature']
    settings.save_to_json()
    return RedirectResponse("/settings", status_code=303)
