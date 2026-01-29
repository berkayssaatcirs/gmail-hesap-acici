import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import random
import string
from faker import Faker
import socks
import socket
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChain
import base64
import os
from datetime import datetime

fake = Faker()

class CaptchaSolver:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
    
    def solve_recaptcha(self, site_key, page_url):
        """2Captcha reCAPTCHA v2 solver"""
        try:
            # Sitekey ve pageurl ile request oluştur
            submit_url = f"{self.base_url}/in.php"
            params = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'pageurl': page_url,
                'json': 1
            }
            
            resp = requests.get(submit_url, params=params)
            result = resp.json()
            
            if result['status'] != 1:
                return None
            
            request_id = result['request']
            
            # Poll for solution
            for _ in range(30):  # 5 dakika bekle
                time.sleep(10)
                check_url = f"{self.base_url}/res.php"
                params = {'key': self.api_key, 'action': 'get', 'id': request_id, 'json': 1}
                resp = requests.get(check_url, params=params)
                result = resp.json()
                
                if result['status'] == 1:
                    return result['request']
            
            return None
        except:
            return None
    
    def submit_captcha_token(self, driver, token):
        """CAPTCHA token'ını sayfaya inject et"""
        script = f"""
        var recaptcha = document.querySelector('.g-recaptcha');
        if (recaptcha) {{
            recaptcha.setAttribute('data-sitekey', '{token}');
        }}
        document.getElementById('g-recaptcha-response').innerHTML = '{token}';
        """
        driver.execute_script(script)

class GmailAccountCreator:
    def __init__(self, proxy_file=None, captcha_api_key=None, max_workers=3):
        self.proxy_list = []
        self.captcha_solver = CaptchaSolver(captcha_api_key) if captcha_api_key else None
        self.max_workers = max_workers
        self.accounts = []
        self.session_profiles = {}
        self.account_queue = queue.Queue()
        self.load_proxies(proxy_file)
    
    def load_proxies(self, filename):
        if filename and os.path.exists(filename):
            with open(filename, 'r') as f:
                self.proxy_list = [line.strip() for line in f if line.strip()]
            print(f"✅ Loaded {len(self.proxy_list)} proxies")
    
    def generate_fingerprint(self):
        """Random browser fingerprint"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        screen_res = random.choice(["1920,1080", "1366,768", "1440,900"])
        timezone = random.choice(["America/New_York", "Europe/London", "Asia/Tokyo"])
        
        return {
            'user_agent': random.choice(user_agents),
            'screen': screen_res,
            'timezone': timezone,
            'language': random.choice(['en-US', 'en-GB', 'tr-TR'])
        }
    
    def create_chrome_profile(self, profile_id):
        """Session persistence için Chrome profile oluştur"""
        profile_path = f"./chrome_profiles/profile_{profile_id}"
        os.makedirs(profile_path, exist_ok=True)
        return profile_path
    
    def setup_driver(self, proxy=None, profile_id=None):
        """Undetected Chrome + Fingerprint + Proxy"""
        options = uc.ChromeOptions()
        
        # Fingerprint
        fingerprint = self.generate_fingerprint()
        options.add_argument(f'--user-agent={fingerprint["user_agent"]}')
        options.add_argument(f'--window-size={fingerprint["screen"]}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Profile persistence
        if profile_id:
            profile_path = self.create_chrome_profile(profile_id)
            options.add_argument(f'--user-data-dir={profile_path}')
        
        # Proxy setup
        if proxy:
            proxy_host, proxy_port, proxy_user, proxy_pass = proxy.split(':')
            options.add_argument(f'--proxy-server=socks5://{proxy_host}:{proxy_port}')
            
            # Proxy auth extension (simplified)
            options.add_argument('--proxy-bypass-list=<-loopback>')
        
        # Anti-detection
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        driver = uc.Chrome(options=options, version_main=None)
        
        # Extra anti-detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        
        return driver
    
    def human_like_delay(self, min_sec=1, max_sec=3):
        """İnsan benzeri random delay"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def solve_captcha_if_present(self, driver):
        """CAPTCHA tespit edip çöz"""
        try:
            # reCAPTCHA kontrol et
            recaptcha = driver.find_elements(By.CLASS_NAME, "g-recaptcha")
            if recaptcha:
                site_key = recaptcha[0].get_attribute("data-sitekey")
                page_url = driver.current_url
                
                print("🔍 CAPTCHA detected, solving...")
                token = self.captcha_solver.solve_recaptcha(site_key, page_url)
                
                if token:
                    self.captcha_solver.submit_captcha_token(driver, token)
                    self.human_like_delay(2, 4)
                    return True
        except:
            pass
        return False
    
    def create_single_account(self, task_id):
        """Tek hesap oluşturma worker"""
        proxy = self.get_random_proxy()
        profile_id = f"{task_id}_{int(time.time())}"
        
        try:
            print(f"🚀 Starting task {task_id} with proxy: {proxy[:20]}...")
            
            driver = self.setup_driver(proxy, profile_id)
            self.session_profiles[profile_id] = driver
            
            # Gmail signup sayfası
            driver.get('https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp')
            self.human_like_delay(3, 5)
            
            wait = WebDriverWait(driver, 20)
            
            # 1. İsimler
            first_name = wait.until(EC.presence_of_element_located((By.ID, "firstName")))
            first_name.send_keys(fake.first_name())
            self.human_like_delay()
            
            last_name = driver.find_element(By.ID, "lastName")
            last_name.send_keys(fake.last_name())
            self.human_like_delay()
            
            driver.find_element(By.ID, "collectNameNext").click()
            self.human_like_delay(2, 4)
            
            # 2. Doğum tarihi
            month = wait.until(EC.presence_of_element_located((By.ID, "month")))
            month.send_keys(str(random.randint(1, 12)))
            
            day = driver.find_element(By.ID, "day")
            day.send_keys(str(random.randint(1, 28)))
            
            year = driver.find_element(By.ID, "year")
            year.send_keys(str(random.randint(1980, 2005)))
            
            gender = driver.find_element(By.ID, "gender")
            ActionChain(driver).move_to_element(gender).click().send_keys("Rather not say").perform()
            
            driver.find_element(By.ID, "birthdaygenderNext").click()
            self.human_like_delay(3, 5)
            
            # CAPTCHA çöz
            self.solve_captcha_if_present(driver)
            
            # 3. Username & Password
            username = fake.user_name() + str(random.randint(1000, 9999))
            password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%^&*', k=16))
            
            username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
            username_field.send_keys(username)
            
            password_field = driver.find_element(By.ID, "passwd")
            password_field.send_keys(password)
            
            confirm_password = driver.find_element(By.ID, "confirm-passwd")
            confirm_password.send_keys(password)
            
            driver.find_element(By.ID, "accountDetailsNext").click()
            self.human_like_delay(5, 8)
            
            # CAPTCHA/Phone verification
            self.solve_captcha_if_present(driver)
            
            try:
                # Skip phone
                skip_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Skip') or contains(text(), 'Atla')]")))
                skip_btn.click()
            except:
                print("📱 Phone verification - manual intervention needed")
                time.sleep(30)
            
            self.human_like_delay(5, 10)
            
            # Mail kontrolü ve cookie alma
            driver.get(f'https://mail.google.com/mail/u/0/#inbox')
            self.human_like_delay(8, 12)
            
            cookies = driver.get_cookies()
            
            account_info = {
                'email': f"{username}@gmail.com",
                'password': password,
                'cookies': json.dumps(cookies, indent=2),
                'proxy': proxy,
                'profile_id': profile_id,
                'status': 'success',
                'created_at': datetime.now().isoformat()
            }
            
            self.accounts.append(account_info)
            print(f"✅ SUCCESS: {account_info['email']}")
            
            # Session kaydet
            session_file = f"sessions/{profile_id}.json"
            os.makedirs("sessions", exist_ok=True)
            with open(session_file, 'w') as f:
                json.dump({'cookies': cookies, 'profile': profile_id}, f)
            
            return account_info
            
        except Exception as e:
            error_info = {
                'task_id': task_id,
                'error': str(e),
                'proxy': proxy,
                'status': 'failed',
                'created_at': datetime.now().isoformat()
            }
            self.accounts.append(error_info)
            print(f"❌ FAILED task {task_id}: {str(e)[:100]}")
            return None
        
        finally:
            if profile_id in self.session_profiles:
                self.session_profiles[profile_id].quit()
                del self.session_profiles[profile_id]
    
    def get_random_proxy(self):
        return random.choice(self.proxy_list) if self.proxy_list else None
    
    def bulk_create_accounts(self, count=10):
        """Bulk account creation queue"""
        print(f"🔥 Starting bulk creation of {count} accounts...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for i in range(count):
                future = executor.submit(self.create_single_account, i+1)
                futures.append(future)
                time.sleep(random.uniform(2, 5))  # Rate limiting
            
            for future in futures:
                future.result()
        
        self.save_accounts()
        print(f"📊 Bulk creation completed. {len([a for a in self.accounts if a['status']=='success'])} successful accounts")
    
    def save_accounts(self, filename='gmail_accounts.json'):
        os.makedirs("accounts", exist_ok=True)
        filename = f"accounts/{filename}"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)
        print(f"💾 Accounts saved: {filename}")

# KULLANIM
if __name__ == "__main__":
    # 2Captcha API key (zorunlu değil)
    CAPTCHA_API_KEY = "YOUR_2CAPTCHA_API_KEY_HERE"  # Boş bırakılabilir
    
    creator = GmailAccountCreator(
        proxy_file='proxies.txt',  # proxy_listesi_dosyasi
        captcha_api_key=CAPTCHA_API_KEY,
        max_workers=2  # Eşzamanlı thread sayısı
    )
    
    # 10 hesap oluştur
    creator.bulk_create_accounts(count=10)
