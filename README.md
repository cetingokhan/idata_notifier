## IDATA Randevu Bulucu (İtalya, Almanya)

Idata Schengen Vize başvurusu için otomatik olarak açık randevu slotlarını kontrol eder. SendGrid ve Twilio hesaplarına bağlamanız durumunda, açık bir randevu slotu bulduğunda size Email ve SMS gönderir.

Notlar:
- Uygulama mevcut hali ile sadece İtalya randevularını takip etmektedir. Dileyen ilave eklentiler ile Almanya'yı da ekleyebilir.
- İtalya için şuan 3 ofis tanımlanmıştır; İstanbul-Altunizade, İstanbul-Gayrettepe, İzmir
- SendGrid email gönderim hesabı için; https://sendgrid.com/en-us adresi üstünden Free Account ile hesap oluşturabilirsiniz
- Twilio ile SMS gönderimi için; https://www.twilio.com/en-us adresi üstünden Free Account ile hesap oluşturabilirsiniz. **Twilio hesabını oluşturduktan sonra Messaging menüsü altındaki Geo permissions sayfasından Türkiye'ye sms gönderimine izin vermek için işaretlemelisiniz.**
- 2 dakikada bir sorgulama yapmaktadır. idata sistemlerini yormamak adına daha sık istek atmamanızı öneririm(Developerlara iş çıkarmayalım) :) 


### Konfigürasyonlar

docker-compose.yaml dosyası içinde aşağıdaki ENV bilgilerini düzenlemek gerekmektedir.

### Email için SendGrid bilgileri


    AIRFLOW__SMTP__SMTP_HOST: 'smtp.sendgrid.net'
    AIRFLOW__SMTP__SMTP_USER: 'apikey'
    AIRFLOW__SMTP__SMTP_MAIL_FROM: ''
    AIRFLOW__SMTP__SMTP_PASSWORD: ''


### SMS için Twilio bilgileri

    

    TWILIO_ACCOUNT_SID: ''
    TWILIO_AUTH_TOKEN: ''
    TWILIO_FROM_PHONE_NUMBER: ''
    TWILIO_TO_PHONE_NUMBER: ''


### Vize istenen ülke: 
italya, almanya

    IDATA_COUNTRY_VARIABLE_NAME: 'italya'

### Randevu alınmak istenen idata ofisi: 
istanbul_altunizade, istanbul_gayrettepe, izmir

    IDATA_OFFICE_VARIABLE_NAME: 'istanbul_altunizade'

### Alert Modu: Test, Prod

    MODE: 'Test'

### Çalıştırmak için

    docker compose -f docker-compose.yaml build
    docker compose -f docker-compose.yaml up

### Durdurmak için

    docker compose -f docker-compose.yaml down
