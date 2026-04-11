# Oracle Cloud Always Free (Ubuntu) deploy

Bu bot **long polling** ishlatadi, shuning uchun VPS'da 24/7 ishlatish qulay.

## 1) VM yaratish
- Oracle Cloud: **Compute → Instances → Create instance**
- Image: Ubuntu 22.04/24.04
- Shape: Always Free (mavjud bo'lsa)
- SSH key qo'shing

## 2) SSH bilan kirish
```bash
ssh ubuntu@<PUBLIC_IP>
```

## 3) Docker o'rnatish
```bash
sudo apt update
sudo apt -y install ca-certificates curl git
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
exit
```
So'ng qayta SSH qilib kiring.

## 4) Botni joylash
### Variant A: 1 ta buyruq bilan (tavsiya)
```bash
REPO_URL=<repo_url> BOT_TOKEN=<token> bash -c "$(curl -fsSL <RAW_BOOTSTRAP_URL>)"
```
Eslatma: `RAW_BOOTSTRAP_URL` sifatida `deploy/bootstrap_ubuntu.sh` faylingizning GitHub “raw” linkini qo'ying.

### Variant B: qo'lda
```bash
sudo mkdir -p /opt/ustaqidir
sudo chown -R $USER:$USER /opt/ustaqidir
cd /opt/ustaqidir
git clone <repo_url> .
cp .env.example .env
mkdir -p data
```
`.env` ichida kamida `BOT_TOKEN` ni kiriting.
SQLite DB hostda `./data/ustaqidir.db` sifatida saqlanadi.

## 5) Ishga tushirish
```bash
docker compose up -d --build
docker compose logs -f
```

## 6) Avto-start (ixtiyoriy, systemd)
```bash
sudo cp deploy/systemd/ustaqidir.service /etc/systemd/system/ustaqidir.service
sudo systemctl daemon-reload
sudo systemctl enable --now ustaqidir.service
sudo systemctl status ustaqidir.service
```

## Portlar (faqat web panel kerak bo'lsa)
- Telegram bot uchun odatda port ochish shart emas (long polling).
- Web panelni public qilmoqchi bo'lsangiz:
  1) `.env`: `WEB_ENABLED=true`
  2) `docker-compose.yml` da `ports:` qismida `127.0.0.1:` ni olib tashlang
  3) Oracle VCN Security List/NSG'da `WEB_PORT` (masalan 8000) uchun ingress qo'shing
