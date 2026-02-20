# Currency Importer (TCMB Kur Kaydedici)

Bu proje, Türkiye Cumhuriyet Merkez Bankası (TCMB) günlük döviz kurları XML servisine bağlanarak güncel kurları çeken ve bu verileri bir PostgreSQL veritabanına kaydeden bir Python betiğidir. Veritabanında aynı güne ait aynı kur kodu zaten varsa, verileri otomatik olarak günceller.

## Özellikler

- **TCMB Entegrasyonu:** Günlük kurları `today.xml` servisi üzerinden çeker.
- **PostgreSQL Bağlantısı:** Verileri güvenli ve kalıcı bir şekilde ilişkisel veritabanında saklar.
- **Çakışma Yönetimi (Upsert):** Mükerrer kayıtları önlemek için PostgreSQL'in `ON CONFLICT` özelliğini kullanır. Aynı tarih ve kur koduyla gelen yeni veriler eski verinin üzerine yazılır.

## Proje Yapısı

\`\`\`text
KURKAYDEDICI/
├── .gitignore              # Git konfigürasyon dosyası
├── requirements.txt        # Proje bağımlılıkları
├── currency_importer.py    # Ana Python betiği
└── README.md               # Proje dokümantasyonu
\`\`\`

## Kurulum ve Çalıştırma

### 1. Gereksinimler
- Python 3.7 veya üzeri
- PostgreSQL Veritabanı Sunucusu

### 2. Repoyu Klonlayın
\`\`\`bash
git clone https://github.com/Huffz55/Currency_Importer.git
cd Currency_Importer
\`\`\`

### 3. Sanal Ortam (Virtual Environment) Oluşturun ve Aktif Edin
\`\`\`bash
python -m venv venv

# Windows için:
venv\Scripts\activate

# Linux/macOS için:
source venv/bin/activate
\`\`\`

### 4. Gerekli Kütüphaneleri Yükleyin
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 5. Veritabanı Tablosunu Oluşturun
PostgreSQL veritabanınızda aşağıdaki SQL sorgusunu çalıştırarak gerekli tabloyu oluşturun:
\`\`\`sql
CREATE TABLE kurlar (
    tarih DATE,
    kur_kodu VARCHAR(10),
    alis_fiyati NUMERIC,
    satis_fiyati NUMERIC,
    PRIMARY KEY (tarih, kur_kodu)
);
\`\`\`

### 6. Çevresel Değişkenleri Ayarlayın
Proje ana dizininde bir `.env` dosyası oluşturun ve veritabanı bilgilerinizi aşağıdaki formatta girin:
\`\`\`env
DB_HOST=localhost
DB_NAME=veritabani_adiniz
DB_USER=kullanici_adiniz
DB_PASS=sifreniz
\`\`\`

### 7. Betiği Çalıştırın
\`\`\`bash
python currency_importer.py
\`\`\`
İşlem başarıyla tamamlandığında terminalde "Operation complete. X currency rates processed." şeklinde bir bildirim göreceksiniz.
