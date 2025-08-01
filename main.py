from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER
from dotenv import load_dotenv
import google.generativeai as genai
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
import markdown
from bs4 import BeautifulSoup
import json
app = FastAPI(
    title="Hastalık Takip Sistemi",
    description="FastAPI ve Jinja2 kullanılarak geliştirilmiş bir hastalık takip ve analiz sistemi.",
    version="1.0.0",
)

app.add_middleware(SessionMiddleware, secret_key="cok-gizli-oturum-anahtari_burayi_degistirin")

templates = Jinja2Templates(directory="templates")

# Sahte kullanıcı verisi
fake_users = {
    "begum": {"username": "begum", "password": "1234"},
    "admin": {"username": "admin", "password": "admin123"}
}

@app.get("/", response_class=HTMLResponse)
async def root_redirect():
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})

@app.post("/login", response_class=HTMLResponse)
def post_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = fake_users.get(username)
    if not user or user["password"] != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Hatalı kullanıcı adı veya şifre."})
    return RedirectResponse(url=f"/dashboard?username={username}", status_code=HTTP_303_SEE_OTHER)

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request, username: str = Query(None)):
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": username})

@app.get("/index", response_class=HTMLResponse)
def get_index(request: Request, username: str = Query(None)):
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("index.html", {"request": request, "username": username})

@app.get("/semptom", response_class=HTMLResponse)
def get_semptom_analysis(request: Request, username: str = Query(None)):
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)

    diagnosis_counts = {}
    if os.path.exists("veriler.txt"):
        try:
            with open("veriler.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    parts = line.strip().split(",")
                    if len(parts) >= 7:
                        diagnosis = parts[6].strip()
                        diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1
        except Exception as e:
            print(f"Error reading veriler.txt for semptom: {e}")
            diagnosis_counts = {"Hata": "Veri okunamadı."}
    else:
        print("veriler.txt dosyası bulunamadı.")

    return templates.TemplateResponse(
        "semptom.html",
        {"request": request, "username": username, "diagnosis_counts": diagnosis_counts}
    )

@app.get("/heatmap", response_class=HTMLResponse)
def get_heatmap_page(request: Request, username: str = Query(None)):
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("heatmap.html", {"request": request, "username": username})

@app.get("/alerts", response_class=HTMLResponse)
def get_alert_panel(request: Request, username: str = Query(None)):
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)

    active_alerts = [
        {"type": "Vaka Artışı", "region": "İstanbul / Fatih", "datetime": "29.07.2025 14:30", "status": "critical", "condition": "Son 24 saatte vaka sayısı %30 arttı."},
        {"type": "Yoğun Semptom", "region": "İzmir / Konak", "datetime": "29.07.2025 11:45", "status": "high", "condition": "'Boğaz Ağrısı' semptomunda belirgin artış."},
        {"type": "Yeni Bölge Riski", "region": "Ankara / Mamak", "datetime": "28.07.2025 22:10", "status": "medium", "condition": "Yeni vaka kümelenmesi tespit edildi."},
        {"type": "Bilgilendirme", "region": "Genel", "datetime": "28.07.2025 09:00", "status": "info", "condition": "Güncel semptom analizi raporu hazır."}
    ]

    alert_rules = [
        {"name": "Bölgesel Vaka Artışı", "threshold": "Vaka sayısı 24 saatte %25 artarsa", "notified": "İl Sağlık Müdürlüğü, Bölge Doktorları", "active": "Evet"},
        {"name": "Nadir Semptom Yayılımı", "threshold": "Yeni bir semptom 48 saatte >10 vaka olursa", "notified": "Uzman Doktorlar, Halk Sağlığı", "active": "Evet"},
        {"name": "Yoğunluk Bildirimi", "threshold": "Tek bir ilçede >50 aktif vaka olursa", "notified": "Tüm Sistem Kullanıcıları", "active": "Hayır"}
    ]

    return templates.TemplateResponse(
        "alerts.html",
        {
            "request": request,
            "username": username,
            "active_alerts": active_alerts,
            "alert_rules": alert_rules
        }
    )

@app.get("/data-entry", response_class=HTMLResponse)
def get_data_entry(request: Request, username: str = Query(None)):
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("data-entry.html", {"request": request, "message": "", "username": username})

@app.post("/data-entry", response_class=HTMLResponse)
def post_data_entry(
    request: Request,
    name: str = Form(...),
    sehir: str = Form(...),
    ilce: str = Form(...),
    age: str = Form(...),
    cinsiyet: str = Form(...),
    symptoms: str = Form(...),
    date: str = Form(...),
    username: str = Form(...)
):
    try:
        diagnosis = create_todo_with_gemini(age, cinsiyet, symptoms)
        update_result = update_json_data(sehir, diagnosis)
        with open("veriler.txt", "a", encoding="utf-8") as f:
            f.write(f"{name},{sehir},{ilce},{age},{cinsiyet},{symptoms},{diagnosis},{date},{username}\n")

        # ✅ Başarılıysa direkt dashboard sayfasına yönlendir
        return RedirectResponse(url=f"/dashboard?username={username}", status_code=303)

    except Exception as e:
        message = f"Veri kaydedilirken hata oluştu: {e}"
        print(f"Error writing to veriler.txt: {e}")

        # Hata varsa aynı sayfada mesajla göster
        return templates.TemplateResponse("data-entry.html", {
            "request": request,
            "message": message,
            "username": username
        })

@app.get("/vakalar", response_class=HTMLResponse)
def get_vakalar(request: Request, username: str = Query(None)):
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)

    vakalar = []
    if os.path.exists("veriler.txt"):
        try:
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
        except Exception as e:
            print(f"Error reading veriler.txt for vakalar: {e}")
    else:
        print("veriler.txt dosyası bulunamadı.")

    return templates.TemplateResponse("vakalar.html", {
        "request": request,
        "username": username,
        "vakalar": vakalar
    })


# Sahte kullanıcı verisi
def markdown_to_text(markdown_string):
    html = markdown.markdown(markdown_string)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    return text


def create_todo_with_gemini(age: str, gender: str, symptoms: str):
    load_dotenv()
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set in environment variables")

    genai.configure(api_key=api_key)
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash")    
    prompt_intro = (
        f"A patient reported the following symptoms: {symptoms}. Age: {age}, Gender: {gender}. "
        "Based on this information, predict the disease in only one word. "
        "Reply with a disease name in Turkish. Do not provide any explanation."
    )

    response = llm.invoke(
        [
            HumanMessage(content="You are a medical expert."),
            HumanMessage(content=prompt_intro),
        ]
    )
    return markdown_to_text(response.content)

def update_json_data(sehir, diagnosis):
    json_path = "harita-veri.json"

    if not os.path.exists(json_path):
        data = []
    else:
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    for item in data:
        if item["sehir"] == sehir and item["tani"] == diagnosis:  # düzeltildi
            item["kisi_sayisi"] += 1
            break
    else:
        data.append({
            "sehir": sehir,
            "tani": diagnosis,
            "kisi_sayisi": 1
        })

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return f"JSON yazma hatası: {e}"
