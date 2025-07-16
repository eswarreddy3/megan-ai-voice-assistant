import os, time, re
import pyttsx3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

load_dotenv()

def speak(text):
    print("Megan:", text)
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("TTS Error:", e)

def login(driver):
    driver.get("https://www.linkedin.com/login")
    driver.find_element(By.ID, "username").send_keys(os.getenv("LINKEDIN_EMAIL"))
    driver.find_element(By.ID, "password").send_keys(os.getenv("LINKEDIN_PASSWORD"))
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(5)

def linkedin_job_flow(voice_cmd):
    match = re.search(r"for (.+?)(?: job| jobs|$)", voice_cmd)
    keyword = match.group(1).strip() if match else "python developer"

    if "hyderabad" in voice_cmd:
        location = "Hyderabad"
    else:
        location = "Bengaluru"

    speak(f"Looking for {keyword} jobs in {location} with Easy Apply posted in last 1 day…")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    login(driver)
    job_links = search_jobs(driver, keyword, location)
    for link in job_links[:5]:
        apply_one(driver, link)
    driver.quit()

def search_jobs(driver, keyword, location):
    url = (
        f"https://www.linkedin.com/jobs/search/?keywords={keyword}"
        f"&location={location}&f_AL=true&f_TPR=r86400"
    )
    driver.get(url)
    time.sleep(3)
    links = [a.get_attribute("href") for a in driver.find_elements(By.CSS_SELECTOR, "a.job-card-container__link")]
    return links

def apply_one(driver, job_url):
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    import speech_recognition as sr

    def get_voice_input(prompt_text):
        speak(prompt_text)
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = r.listen(source, timeout=6, phrase_time_limit=6)
                return r.recognize_google(audio, language='en-in')
            except:
                speak("I didn't catch that. Skipping this field.")
                return ""

    try:
        driver.get(job_url)
        time.sleep(2)

        # Click Easy Apply button
        easy_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jobs-apply-button"))
        )
        easy_btn.click()
        time.sleep(2)

        while True:
            time.sleep(1)
            # Fill any input fields
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[aria-required='true']")
            for field in inputs:
                try:
                    label = field.get_attribute("aria-label")
                    if not field.get_attribute("value"):
                        user_input = get_voice_input(f"Please provide {label}")
                        field.clear()
                        field.send_keys(user_input)
                except Exception as e:
                    print("Input fill error:", e)

            # Check for Next or Submit button
            buttons = driver.find_elements(By.CSS_SELECTOR, "button")
            next_btn = None
            for b in buttons:
                text = b.text.strip().lower()
                if text == "next":
                    next_btn = b
                    break
                elif "submit application" in text:
                    b.click()
                    speak("✅ Job application submitted.")
                    return

            if next_btn:
                next_btn.click()
                time.sleep(2)
            else:
                # No next or submit -> assume done
                break

    except Exception as e:
        print("Error during application:", e)
        speak("Could not auto-apply; skipped.")
        # Try closing modal if open
        try:
            driver.find_element(By.CSS_SELECTOR, "button[aria-label='Dismiss']").click()
            time.sleep(1)
            driver.find_element(By.XPATH, "//button/span[text()='Discard']/..").click()
        except:
            pass
