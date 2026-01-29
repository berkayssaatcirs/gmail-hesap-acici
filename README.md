# Gmail-Account-Creator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Proxy Support](https://img.shields.io/badge/Proxy-SOCKS5%20%7C%20Residential-orange.svg)](https://img.shields.io/badge/Proxy-SOCKS5%20%7C%20Residential-orange.svg)
[![Captcha](https://img.shields.io/badge/Captcha-2Captcha-red.svg)](https://2captcha.com/)

**Proxy destekli, anti-detection özellikli Gmail hesap oluşturucu. Bulk mode, session persistence ve 2Captcha entegrasyonu ile pentest/red teaming için optimize edildi.**

## ✨ Özellikler

| Özellik | Durum |
|---------|-------|
| **Proxy Rotation** (SOCKS5) | ✅ |
| **2Captcha reCAPTCHA Solver** | ✅ Opsiyonel |
| **Fingerprint Randomization** | ✅ UA, Screen, Language |
| **Anti-Detection** | ✅ `undetected-chromedriver` |
| **Session Persistence** | ✅ Chrome Profiles + Cookies |
| **Bulk Creation** | ✅ ThreadPoolExecutor |
| **Human-like Delays** | ✅ Random timing |
| **Rate Limiting** | ✅ Built-in |

## 📋 Ön Koşullar

- **Python 3.8+**
- **Chrome Browser** (otomatik driver)
- **Residential Proxies** (datacenter proxy'ler banlanır)
- **2Captcha API Key** (opsiyonel, ama önerilir)

## 🛠 Hızlı Kurulum

```bash
# 1. Repository klonla
git clone https://github.com/yourusername/gmail-account-creator.git
cd gmail-account-creator

# 2. Dependencies yükle
pip install -r requirements.txt

# 3. Proxy listesi hazırla (proxies.txt)
# Format: ip:port:username:password

# 4. 2Captcha API key al (isteğe bağlı)
# 2captcha.com -> Dashboard -> API Key

# 5. Çalıştır
python gmail_creator.py
