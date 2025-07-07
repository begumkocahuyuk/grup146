
# Tanı Haritası

<!-- LOGO -->
<p align="center">
  <img src="./assets/logo.png" alt="Tanı Haritası Logosu" width="200"/>
</p>

<h1 align="center">Veri Bilimi ve Yapay Zeka Tabanlı Hastalık Takip Sistemi</h1>

<p align="center">
  Doktor muayeneleri sonrası anonimleştirilmiş hasta verileriyle oluşturulan, bölgesel hastalık ısı haritası. <br>
  Bu sistem sayesinde viral hastalıklar hızlıca tespit edilir, civardaki doktorlar uyarılır ve teşhis süreçleri hızlanır.
</p>

---

## 👥 Takım Üyeleri

| | **İsim** | **Rol** | **LinkedIn** |
|---|---|---|---|
| <img src="./assets/sedef.jpeg" width="100"/> | **Merve** | Ürün Sahibi | [LinkedIn](https://www.linkedin.com/in/merve-yagiz) |
| <img src="./assets/begum.jpeg" width="100"/> | **Begüm** | Scrum Master | [LinkedIn](https://www.linkedin.com/in/begumbeyzakocahuyuk) |
| <img src="./assets/merve.jpeg" width="100"/> | **Sedef** | Geliştirici | [LinkedIn](https://www.linkedin.com/in/sedef-yıldırımci) |
| <img src="./assets/begum.jpg" width="100"/> | **Deniz** | Geliştirici | 
| <img src="./assets/alpay.jpg" width="100"/> | **Alpay** | Geliştirici | 

---

## 📌 Proje Konusu

Bu proje; hasta verilerindeki **kişisel bilgiler (PII)** filtrelenerek, yapay zeka destekli bir sistemle **ısı haritası oluşturarak** sağlık alanında farkındalık yaratmayı hedeflemektedir.

Amaçlarımız:
- PII’siz hasta verileriyle viral hastalıkları tespit etmek
- Harita üzerinden semptomlara dayalı dağılımları analiz etmek
- Lokasyon-temelli doktor uyarı sistemleri geliştirmek
- Hastalık tekrar döngülerini zaman serisi analizleriyle tespit etmek

---

## 🛠️ Kullanılan Teknolojiler



---

## 🚀 Kurulum

Projeyi yerelde çalıştırmak için:

```bash
git clone https://github.com/begumkocahuyuk/grup146.git
cd Grup146
npm install
npm start
```

---

## 📋 Sprint 1

### 🎯 Sprint Hedefi:
Sprint 1’de temel altyapıların hazırlanması, kullanıcı hikâyelerinin netleştirilmesi ve anonimleştirme algoritmalarının temel prototiplerinin oluşturulması hedeflenmiştir.

### 🔢 Tahmini Puan: 60  
### ✅ Gerçekleşen Puan: 45  

> Puanlama, işin karmaşıklığı, veri miktarı, teknik zorluk ve bağımlılıklar göz önüne alınarak belirlenmiştir. Küçük işler: 3 puan, orta işler: 5–8 puan, karmaşık işler: 13 puan üzerinden hesaplandı.

---

### ✅ Tamamlananlar (Done):
- Kullanıcı hikayeleri yazıldı
- Proje yapı/mimari planı oluşturuldu
- Anonimleştirilmiş örnek raporlar toplandı
- Geliştirme ortamı kuruldu
- Takım rolleri belirlendi

### 🔧 Devam Edenler (In Progress):
- Semptom verisinin ön işlenmesi
- Anonimleştirme algoritmasının testleri
- İlk modelleme (hastalık - zaman - sıklık ilişkisi)
- UI/UX tasarımının Figma üzerinden devamı

### 📌 Yapılacaklar (To Do):
- Hasta verilerinden PII bilgilerin çıkarılması (isim, TC vs.)
- Heatmap için örnek veri hazırlanması
- NLP ile semptom sınıflandırma altyapısı kurulması
- Kullanıcı arayüzü wireframe çizimleri
- Doktor paneli uyarı mekanizması
- Lokasyon verisinin harita üzerinde oturtulması

### ❌ Reddedilenler (Rejected):
- Mobil uygulama olarak tasarlanması
- E-posta uyarısı yerine push notification tercih edildi

---

### 🧐 Sprint Review
- Demo başarıyla tamamlandı ve ürün sahibine sunuldu.
- UI/UX ilk versiyonu onaylandı.
- Anonimleştirme mantığı demo üzerinden anlatıldı.
- Geri bildirim: Harita üzerinde görsellik geliştirilmeli, NLP çıktıları sprint 2’ye taşınmalı.

---

### 🔁 Sprint Retrospective

**İyi Gidenler:**
- Takım içi görev paylaşımı
- Trello üzerinden görev takibi disiplinli yürütüldü

**İyileştirme Gerekenler:**
- Kartlar daha modüler/parçalı tanımlanmalı
- Puanlama planlamadan önce netleştirilmeli

**Kararlaştırılan Aksiyonlar:**
- Günlük 15 dk stand-up zorunlu hale getirildi
- UI kararları sprint başında ortaklaşa netleştirilecek

## 🧭 Trello Sprint Panosu (Sprint 1)

<p align="center">
  <img src="./assets/sprint1-board.jpeg" alt="Sprint 1 Trello Panosu" width="800"/>
</p>

---

