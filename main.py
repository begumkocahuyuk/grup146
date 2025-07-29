from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER 
import os # veriler.txt dosyasının varlığını kontrol etmek için

# FastAPI uygulamasını başlat
app = FastAPI(
    title="Hastalık Takip Sistemi",
    description="FastAPI ve Jinja2 kullanılarak geliştirilmiş bir hastalık takip ve analiz sistemi.",
    version="1.0.0",
)

# Oturum (session) yönetimini etkinleştir
# GÜVENLİK UYARISI: 'cok-gizli-oturum-anahtari_burayi_degistirin' yerine
# üretim ortamında güçlü, rastgele oluşturulmuş ve ortam değişkenlerinden gelen bir anahtar KULLANMALISINIZ!
app.add_middleware(SessionMiddleware, secret_key="cok-gizli-oturum-anahtari_burayi_degistirin")

# HTML şablonlarının bulunduğu dizini belirt
templates = Jinja2Templates(directory="templates")

# Eğer static dosyalarınız (CSS, JS, resimler) 'assets' klasöründeyse bu satırı etkinleştirin
# Örneğin: 'assets/css/style.css' dosyasına '/static/css/style.css' üzerinden erişilebilir.
# app.mount("/static", StaticFiles(directory="assets"), name="static")

# Sahte kullanıcı listesi (gerçek uygulamada veritabanından gelmeli)
fake_users = {
    "begum": {"username": "begum", "password": "1234"},
    "admin": {"username": "admin", "password": "admin123"}
}

# --- Rota Tanımlamaları ---

@app.get("/", response_class=HTMLResponse)
async def root_redirect():
    """
    Uygulama ana dizinine ('/') gidildiğinde kullanıcıyı login sayfasına yönlendirir.
    """
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    """
    Kullanıcı giriş (login) sayfasını gösterir.
    """
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})

@app.post("/login", response_class=HTMLResponse)
def post_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    Login formundan gelen kullanıcı adı ve şifreyi doğrular.
    Başarılı giriş durumunda kullanıcıyı dashboard'a yönlendirir, aksi takdirde hata mesajı gösterir.
    """
    user = fake_users.get(username)
    if not user or user["password"] != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Hatalı kullanıcı adı veya şifre."})
    
    # Login başarılı olursa /dashboard sayfasına yönlendir
    return RedirectResponse(url=f"/dashboard?username={username}", status_code=HTTP_303_SEE_OTHER)

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request, username: str = Query(None)):
    """
    Kullanıcının kontrol paneli (dashboard) sayfasını gösterir.
    Kullanıcı adı query parametresi olarak gelmezse login sayfasına yönlendirir.
    """
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": username})

@app.get("/index", response_class=HTMLResponse)
def get_index(request: Request, username: str = Query(None)):
    """
    Ana (index) sayfasını gösterir. Genellikle dashboard ile entegre veya alternatif bir başlangıç sayfası olabilir.
    Kullanıcı adı query parametresi olarak gelmezse login sayfasına yönlendirir.
    """
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("index.html", {"request": request, "username": username})

@app.get("/semptom", response_class=HTMLResponse)
def get_semptom_analysis(request: Request, username: str = Query(None)):
    """
    Semptom Analizi sayfasını gösterir.
    'veriler.txt' dosyasından teşhis verilerini okuyarak semptom sayımlarını hesaplar.
    Kullanıcı adı query parametresi olarak gelmezse login sayfasına yönlendirir.
    """
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)

    diagnosis_counts = {}
    if os.path.exists("veriler.txt"):
        try:
            with open("veriler.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip(): # Boş satırları atla
                        continue
                    parts = line.strip().split(",")
                    if len(parts) >= 7: # Teşhis (diagnosis) için en az 7 parça olmalı (0'dan başlayınca 6. index)
                        diagnosis = parts[6].strip()
                        diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1
        except Exception as e: # Daha genel bir hata yakalama (izin vb. sorunlar için)
            print(f"Error reading veriler.txt for semptom: {e}")
            diagnosis_counts = {"Hata": "Veri okunamadı."}
    else:
        print("veriler.txt dosyası bulunamadı.")


    return templates.TemplateResponse(
        "semptom.html",
        {
            "request": request,
            "username": username,
            "diagnosis_counts": diagnosis_counts
        }
    )

@app.get("/heatmap", response_class=HTMLResponse)
def get_heatmap_page(request: Request, username: str = Query(None)):
    """
    Isı Haritası sayfasını gösterir.
    Kullanıcı adı query parametresi olarak gelmezse login sayfasına yönlendirir.
    """
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("heatmap.html", {"request": request, "username": username})

@app.get("/alerts", response_class=HTMLResponse) # Rota adı "/alerts" olarak güncellendi
def get_alert_panel(request: Request, username: str = Query(None)):
    """
    Uyarı Paneli sayfasını gösterir.
    Kullanıcı adı query parametresi olarak gelmezse login sayfasına yönlendirir.
    HTML şablonuna dinamik uyarı ve kural verileri gönderir.
    """
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    
    # Uyarıları göstermek için örnek veri (şimdilik statik)
    # GERÇEK UYGULAMADA: Bu veriler bir veritabanından, harici bir API'den
    # veya dinamik olarak hesaplanarak gelmelidir.
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
            "active_alerts": active_alerts, # HTML'e gönderilecek
            "alert_rules": alert_rules      # HTML'e gönderilecek
        }
    )

@app.get("/data-entry", response_class=HTMLResponse)
def get_data_entry(request: Request, username: str = Query(None)):
    """
    Veri Girişi sayfasını gösterir.
    Kullanıcı adı query parametresi olarak gelmezse login sayfasına yönlendirir.
    """
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
    diagnosis: str = Form(...),
    date: str = Form(...),
    username: str = Form(...) # Form'dan gelen username'i al
):
    """
    Veri giriş formundan gelen verileri işleyip 'veriler.txt' dosyasına kaydeder.
    Başarılı kayıt sonrası mesaj ile data-entry sayfasına geri döner.
    """
    try:
        with open("veriler.txt", "a", encoding="utf-8") as f:
            f.write(f"{name},{sehir},{ilce},{age},{cinsiyet},{symptoms},{diagnosis},{date},{username}\n")
        message = "Veri başarıyla kaydedildi!"
    except Exception as e:
        message = f"Veri kaydedilirken hata oluştu: {e}"
        print(f"Error writing to veriler.txt: {e}")

    # Veri kaydedildikten sonra kullanıcıyı aynı sayfaya yönlendirelim ve mesaj gösterelim
    # username'i tekrar göndermeyi unutmayın
    return templates.TemplateResponse("data-entry.html", {
        "request": request,
        "message": message,
        "username": username
    })

@app.get("/vakalar", response_class=HTMLResponse)
def get_vakalar(request: Request, username: str = Query(None)):
    """
    Vakalar sayfasını gösterir ve 'veriler.txt' dosyasından ilgili kullanıcının vakalarını listeler.
    Kullanıcı adı query parametresi olarak gelmezse login sayfasına yönlendirir.
    """
    if not username:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)

    vakalar = []
    if os.path.exists("veriler.txt"):
        try:
            with open("veriler.txt", "r", encoding="utf-8") as file:
                for line in file:
                    satir = line.strip().split(",")
                    # Satırın beklenen formatta olup olmadığını ve kullanıcının adının eşleşip eşleşmediğini kontrol et
                    # diagnosis (6. index), date (7. index), username (8. index)
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
            # Hata durumunda boş liste ile devam edilebilir veya kullanıcıya gösterilebilir.
    else:
        print("veriler.txt dosyası bulunamadı.")

    return templates.TemplateResponse("vakalar.html", {
        "request": request,
        "username": username,
        "vakalar": vakalar
    })