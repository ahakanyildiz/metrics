# Python 3.11 slim tabanlı imaj kullan
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem güncellemelerini yap ve gerekli sistem paketlerini yükle
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını yükle
RUN pip install --no-cache-dir psutil

# Metrics dosyasını kopyala
COPY metrics.py /app/

# CSV rapor dosyası için volume oluştur
VOLUME ["/app/reports"]

# Rapor dosyasının reports klasörüne yazılması için environment variable ayarla
ENV REPORT_FILE="/app/reports/server_metrics_report.csv"

# Metrics.py dosyasını çalıştır
CMD ["python", "metrics.py"]
