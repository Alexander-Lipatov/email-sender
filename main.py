
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Form, status, Body, HTTPException, Request
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
    # subject: str = Form(...),
    # text: str = Form(...),
    # html: str = Form(None),
    # recipient_ids: list[str] = Form(...),  # список ID получателей
):

    form = await request.form()

    # Преобразуем form в обычный dict
    form_data = dict(form)

    print(form_data)
    print()

    await db.connect()

    task = await db.task.create(
        data={
            "title": 'title_message',
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
