from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # Launch browser (headless=False to see it working)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Navigating to target URL...")
        page.goto("https://cd.captchaaiplus.com/recaptcha-v3-2.php")
        
        # Wait for page load
        page.wait_for_load_state("networkidle")
        print("Page loaded successfully.")
        
        # Keep browser open for a moment to verify visually
        page.wait_for_timeout(2000)
        
        browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    run()
