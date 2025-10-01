# Server Metrics Monitor Docker

Bu Docker container'ı, sunucu kaynak kullanımını (CPU, RAM, Disk I/O, Network I/O) izler ve CSV formatında raporlar.

## Kullanım

### 1. Docker ile Çalıştırma

```bash
# Docker image'ı oluştur
docker build -t metrics-monitor .

# Container'ı çalıştır
docker run -v $(pwd)/reports:/app/reports metrics-monitor
```

### 2. Docker Compose ile Çalıştırma (Önerilen)

```bash
# Container'ı başlat
docker-compose up --build

# Arka planda çalıştırmak için
docker-compose up -d --build

# Container'ı durdur
docker-compose down
```

### 3. Manuel Durdurma

Container çalışırken `Ctrl+C` ile durdurabilirsiniz.

## Rapor Dosyası

- Rapor dosyası `./reports/server_metrics_report.csv` olarak kaydedilir
- Container durdurulduğunda rapor host sistemde kalır
- Her çalıştırmada yeni bir rapor dosyası oluşturulur (mevcut dosya üzerine yazılır)

## Metrikler

- **timestamp**: Zaman damgası
- **cpu_percent**: CPU kullanım yüzdesi
- **memory_usage_gb**: RAM kullanımı (GB)
- **memory_percent**: RAM kullanım yüzdesi
- **disk_read_mb**: Disk okuma hızı (MB/s)
- **disk_write_mb**: Disk yazma hızı (MB/s)
- **net_sent_mb**: Ağ gönderme hızı (MB/s)
- **net_recv_mb**: Ağ alma hızı (MB/s)
- **open_file_descriptors**: Açık dosya tanımlayıcı sayısı
- **process_count**: Çalışan işlem sayısı