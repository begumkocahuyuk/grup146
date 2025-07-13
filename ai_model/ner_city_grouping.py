from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import spacy

# 1. MODELLERİ YÜKLE
tokenizer = AutoTokenizer.from_pretrained("d4data/biomedical-ner-all")
model = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")
medical_ner = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

nlp = spacy.load("en_core_web_sm")

# Türkiye şehirleri listesi (eklenebilir)
turkiye_sehirleri = [
    "adana", "adıyaman", "afyon", "ağrı", "amasya", "ankara", "antalya", "artvin", "aydın",
    "balıkesir", "bilecik", "bingöl", "bitlis", "bolu", "burdur", "bursa", "çanakkale",
    "çankırı", "çorum", "denizli", "diyarbakır", "edirne", "elazığ", "erzincan", "erzurum",
    "eskişehir", "gaziantep", "giresun", "gümüşhane", "hakkari", "hatay", "isparta", "mersin",
    "istanbul", "izmir", "kars", "kastamonu", "kayseri", "kırklareli", "kırşehir", "kocaeli",
    "konya", "kütahya", "malatya", "manisa", "kahramanmaraş", "mardin", "muğla", "muş",
    "nevşehir", "niğde", "ordu", "rize", "sakarya", "samsun", "siirt", "sinop", "sivas",
    "tekirdağ", "tokat", "trabzon", "tunceli", "şanlıurfa", "uşak", "van", "yozgat",
    "zonguldak", "aksaray", "bayburt", "karaman", "kırıkkale", "batman", "şırnak",
    "bartın", "ardahan", "ığdır", "yalova", "karabük", "kilis", "osmaniye", "düzce"
]


# 2. HASTALIKLARI TESPİT EDEN FONKSİYON
def get_diseases_from_text(text):
    raw_entities = medical_ner(text)
    print(f"[DEBUG] Raw Entities: {raw_entities}")
    diseases = []

    valid_tags = {
        "DISEASE", "Disease_disorder", "History", "Symptom", "Medical_condition",
        "Sign", "Condition", "Problem", "Sign_symptom", "Family_history",
    }

    current = ""
    for ent in raw_entities:
        tag = ent["entity_group"]
        word = ent["word"]

        if tag in valid_tags:
            if word.startswith("##"):
                current += word[2:]
            else:
                if current:
                    diseases.append(current)
                current = word
        else:
            if current:
                diseases.append(current)
                current = ""
    if current:
        diseases.append(current)

    # Yaygın teşhisleri manuel yakala
    common_terms = [
        "liver failure", "pneumonia", "heart disease", "stroke", "cancer",
        "kidney failure", "hypertension", "migraine", "bronchitis", "asthma", "anxiety"
    ]

    for term in common_terms:
        if term.lower() in text.lower():
            diseases.append(term)

    return diseases

# 3. RAPORU TXT DOSYASINDAN OKU
with open("rapor.txt", "r", encoding="utf-8") as f:
    text_lines = f.readlines()

grouped = {}

# 4. HER SATIRI İŞLE
for line in text_lines:
    line = line.strip()
    if not line:
        continue

    doc = nlp(line)
    cities_in_line = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

    # spaCy şehir bulamazsa kendi listemizden ara
    if not cities_in_line:
        line_lower = line.lower()
        for city in turkiye_sehirleri:
            if city in line_lower:
                cities_in_line.append(city)
                break


    if not cities_in_line:
        print(f"[UYARI] Şehir bulunamadı: {line}")
        continue

    city = cities_in_line[0]

    if city not in grouped:
        grouped[city] = []

    diseases = get_diseases_from_text(line)
    grouped[city].extend(diseases)

# 5. SONUÇLARI YAZDIR
print("\n--- Disease Mentions Grouped by City ---\n")
for city, diseases in grouped.items():
    clean = set(diseases)
    print(f"{city.title()}: {clean}")
