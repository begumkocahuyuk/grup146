from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_302_FOUND
from fastapi import Query
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

# HTML dosyaları templates klasöründe
templates = Jinja2Templates(directory="templates")


# Sahte kullanıcı listesi
fake_users = {
    "begum": {"username": "begum", "password": "1234"},
    "admin": {"username": "admin", "password": "admin123"}
}
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request, username: str = Query(None)):
    if not username:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": username})

@app.get("/index", response_class=HTMLResponse)
def get_index(request: Request, username: str = Query(None)):
    if not username:
        # username yoksa login sayfasına yönlendir
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request, "username": username})
@app.get("/sempton", response_class=HTMLResponse)
def semptomlar(request: Request):
    diagnosis_counts = {}
    username = request.session.get("username", "Anonim")  # Varsayılan "Anonim"

    try:
        with open("veriler.txt", "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                parts = line.strip().split(",")
                if len(parts) >= 9:
                    diagnosis = parts[6].strip()  # 6. index doğru olan
                    diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1
    except FileNotFoundError:
        diagnosis_counts = {}

    return templates.TemplateResponse(
        "semptom.html",
        {
            "request": request,
            "username": username,
            "diagnosis_counts": diagnosis_counts
        }
    )
@app.get("/heatmap", response_class=HTMLResponse)
def get_index(request: Request, username: str = Query(None)):
    if not username:
        # username yoksa login sayfasına yönlendir
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("heatmap.html", {"request": request, "username": username})

# Login sayfası gösterimi
@app.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})

# Login formdan veri gönderilince
@app.post("/login", response_class=HTMLResponse)
def post_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = fake_users.get(username)
    if not user or user["password"] != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Hatalı kullanıcı adı veya şifre."})
    
    response = RedirectResponse(url=f"/index?username={username}", status_code=303)
    return response

# Data-entry sayfasında kullanıcı adı alınır
@app.get("/data-entry", response_class=HTMLResponse)
def get_data_entry(request: Request, username: str = Query(None)):
    return templates.TemplateResponse("data-entry.html", {"request": request, "message": "", "username": username})

# Formdan gelen verileri işleyip kayıt et
@app.post("/data-entry", response_class=HTMLResponse)
def post_data_entry(
    request: Request,
    name: str = Form(...),
    sehir: str = Form(...),
    ilce: str = Form(...),
    age: str = Form(...),
    cinsiyet: str = Form(...),
    symptoms: str = Form(...),
    diagnosis: str = Form(...),
    date: str = Form(...),
    username: str = Form(...)

):
    # Basit kayıt simülasyonu – ileride veritabanına kaydedilecek
    with open("veriler.txt", "a", encoding="utf-8") as f:
        f.write(f"{name},{sehir},{ilce},{age},{cinsiyet},{symptoms},{diagnosis},{date},{username}\n")

    return templates.TemplateResponse("data-entry.html", {
        "request": request,
        "message": "Veri başarıyla kaydedildi!"
    })

@app.get("/vakalar", response_class=HTMLResponse)
def get_vakalar(request: Request, username: str = Query(None)):
    if not username:
        return RedirectResponse(url="/login")

    vakalar = []
    with open("veriler.txt", "r", encoding="utf-8") as file:
        for line in file:
            satir = line.strip().split(",")
            if len(satir) == 9 and satir[8] == username:
                vakalar.append({
                    "name": satir[0],
                    "sehir": satir[1],
                    "ilce": satir[2],
                    "age": satir[3],
                    "cinsiyet": satir[4],
                    "symptoms": satir[5],
                    "diagnosis": satir[6],
                    "date": satir[7]
                })

    return templates.TemplateResponse("vakalar.html", {
        "request": request,
        "username": username,
        "vakalar": vakalar
    })