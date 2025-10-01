import psutil
import time
import csv
import os
from datetime import datetime
import threading

# --- Ayarlar ---
# Metriklerin toplanma aralığı (saniye)
SAMPLING_INTERVAL = 1 
# Rapor dosyasının adı
REPORT_FILE = "server_metrics_report.csv"
# İzleme döngüsünü durdurmak için kullanılacak olay
stop_event = threading.Event()

def get_network_io():
    """Ağ trafiği (giden ve gelen) metriklerini alır."""
    net_io = psutil.net_io_counters()
    return {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv
    }

def monitor_system():
    """Sistem metriklerini toplar ve CSV dosyasına yazar."""
    
    # Rapor dosyasını hazırlama (başlık satırı)
    fieldnames = [
        "timestamp", 
        "cpu_percent", 
        "memory_usage_gb", 
        "memory_percent", 
        "disk_read_mb", 
        "disk_write_mb", 
        "net_sent_mb", 
        "net_recv_mb",
        "open_file_descriptors",
        "process_count"
    ]
    
    # CSV dosyası oluşturma
    with open(REPORT_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # İlk ağ ve disk değerlerini sıfırlama için kaydet
        initial_net_io = get_network_io()
        initial_disk_io = psutil.disk_io_counters()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sunucu metrik takibi başlatıldı. '{REPORT_FILE}' dosyasına yazılıyor...")

        # Stop olayı tetiklenene kadar metrikleri topla
        while not stop_event.is_set():
            
            # --- CPU ve RAM ---
            cpu_usage = psutil.cpu_percent(interval=None) # Interval'ı 0 yapıp kendimiz kontrol ediyoruz
            mem_info = psutil.virtual_memory()
            
            # --- Disk I/O ---
            current_disk_io = psutil.disk_io_counters()
            disk_read_bytes = current_disk_io.read_bytes - initial_disk_io.read_bytes
            disk_write_bytes = current_disk_io.write_bytes - initial_disk_io.write_bytes
            
            # --- Ağ I/O ---
            current_net_io = get_network_io()
            net_sent_bytes = current_net_io["bytes_sent"] - initial_net_io["bytes_sent"]
            net_recv_bytes = current_net_io["bytes_recv"] - initial_net_io["bytes_recv"]
            
            # --- Diğer Metrikler ---
            # Sistemdeki açık dosya tanımlayıcıları (socket limitini görmek için önemli)
            try:
                # psutil'in uygun metodunu kullan
                open_files = psutil.test().num_fds
            except AttributeError:
                # num_fds mevcut değilse (bazı sistemlerde veya psutil sürümlerinde olabilir)
                open_files = "N/A"
            except Exception:
                open_files = "Error"
            
            # Sistemdeki çalışan toplam işlem sayısı
            process_count = len(psutil.pids())

            # --- Verileri Kaydetme ---
            metrics = {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "cpu_percent": cpu_usage,
                "memory_usage_gb": round(mem_info.used / (1024**3), 2),
                "memory_percent": mem_info.percent,
                "disk_read_mb": round(disk_read_bytes / (1024**2) / SAMPLING_INTERVAL, 2), # MB/s
                "disk_write_mb": round(disk_write_bytes / (1024**2) / SAMPLING_INTERVAL, 2), # MB/s
                "net_sent_mb": round(net_sent_bytes / (1024**2) / SAMPLING_INTERVAL, 2), # MB/s
                "net_recv_mb": round(net_recv_bytes / (1024**2) / SAMPLING_INTERVAL, 2), # MB/s
                "open_file_descriptors": open_files,
                "process_count": process_count
            }
            
            # CSV dosyasına satırı yaz
            writer.writerow(metrics)
            csvfile.flush() # Verinin hemen diske yazılmasını sağla
            
            # Sonraki ölçüm için disk ve ağ sıfırlama değerlerini güncelle
            initial_net_io = current_net_io
            initial_disk_io = current_disk_io

            # Belirlenen aralık kadar bekle
            time.sleep(SAMPLING_INTERVAL)

def start_monitor():
    """İzlemeyi ayrı bir iş parçacığında başlatır."""
    monitor_thread = threading.Thread(target=monitor_system)
    monitor_thread.start()
    return monitor_thread

def stop_monitor(thread):
    """İzlemeyi durdurur ve rapor dosyasını kapatır."""
    stop_event.set()
    thread.join()
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sunucu metrik takibi sonlandırıldı.")
    print(f"Rapor '{REPORT_FILE}' dosyasında kaydedildi.")

# --- Kullanım Örneği (SÜREKLİ İZLEME İÇİN DEĞİŞTİRİLDİ) ---
if __name__ == "__main__":
    
    # 1. İzlemeyi başlat
    monitor_thread = start_monitor()
    
    # 2. Metriklerinizi sürekli toplayın
    print("Metrikler toplanmaya başladı. Durdurmak ve raporu kaydetmek için **Ctrl+C** tuşlarına basın.")
    
    try:
        # Ana iş parçacığını, kullanıcı kesintisine (Ctrl+C) yanıt verecek şekilde sürekli aktif tutar.
        while True:
            time.sleep(0.1) 
    except KeyboardInterrupt:
        # Kullanıcı Ctrl+C bastığında bu blok çalışır
        print("\nKullanıcı tarafından durdurma sinyali alındı.")
        pass # Sonlandırma işlemine geç
        

    # 3. İzlemeyi durdur ve dosyayı kaydet
    stop_monitor(monitor_thread)