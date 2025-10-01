import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Login ve rapor URL'leri
login_url = "https://beta.textfy.ai/api/auth/login"
report_url = "https://beta.textfy.ai/api/report-generator/reports/generate"

report_counter = 0
counter_lock = threading.Lock()

# 100 kullanıcı
accounts = [{"email": f"stress{i}@gmail.com", "password": "123123"} for i in range(1, 101)]

# Rapor payload'u (hepsi aynı)
payload = {
    "reportType": "dynamic",
    "projectContext": {
        "projectName": "Yapay Zekâ Destekli Tarımsal Tahmin Sistemi",
        "projectDescription": "Bu proje, tarım alanlarında verim tahmini, erken hastalık teşhisi ve iklim analizleri yapmak amacıyla yapay zekâ destekli bir karar destek sistemi geliştirmeyi amaçlamaktadır. Uydu görüntüleri, hava durumu verileri ve sensör verileri ile entegre çalışan bu sistem, çiftçilere doğru ve zamanında bilgi sağlayarak sürdürülebilir tarım uygulamalarını destekler.",
        "details": {
            "institutional": {"organizationName": "AgroTech Bilişim ve Tarım A.Ş."},
            "personal": {"fullName": "", "idNumber": "", "email": "", "phone": ""},
            "personnel": [
                {
                    "fullName": "Barış Karakuş",
                    "role": "Proje Yöneticisi",
                    "idNumber": "12345678901",
                    "email": "baris.karakus@agrotech.com",
                    "phone": "+90 532 456 78 90"
                }
            ]
        }
    },
    "documentPages": [],
    "guideSource": {},
    "settings": {
        "useGuideAnalysis": True,
        "useControllerAgent": True,
        "temperature": 0.4,
        "regenerateExisting": False
    },
    "visibility": "public",
    "allowedUsers": [],
    "reportTypeId": "4b3066d4-17e3-40db-bd61-bbef9799523e"
}

def create_report(account):
    global report_counter
    try:
        # 1️⃣ Login işlemi
        resp = requests.post(login_url, json=account)
        resp.raise_for_status()

        resp_json = resp.json()
        token = resp_json.get("data", {}).get("token")  # data içinden token al
        if not token:
            return f"{account['email']} -> Token alınamadı!"

        #2️⃣ Rapor oluşturma isteği
        headers = {"Authorization": f"Bearer {token}"} # alınan token burada kullanılıyor.
        report_resp = requests.post(report_url, json=payload, headers=headers)
        report_resp.raise_for_status()

        with counter_lock:
            report_counter += 1
            count = report_counter


        return f"{account['email']} -> Rapor oluşturuldu, Status: report_resp.status_code-{count}"
    except Exception as e:
        return f"{account['email']} -> Hata: {e}"

# ThreadPool ile eş zamanlı istekler
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(create_report, acc) for acc in accounts]
    for future in as_completed(futures):
        print(future.result())
