import asyncio
import json
import base64
import requests
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import os

# Target URL
URL = "https://egypt.blsspainglobal.com/Global/CaptchaPublic/GenerateCaptcha?data=4CDiA9odF2%2b%2bsWCkAU8htqZkgDyUa5SR6waINtJfg1ThGb6rPIIpxNjefP9UkAaSp%2fGsNNuJJi5Zt1nbVACkDRusgqfb418%2bScFkcoa1F0I%3d"

def save_json(data, filename):
    # Ensure outputs directory exists
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Saved {len(data)} items to {filepath}")

def get_base64_from_url(url):
    try:
        if url.startswith("data:image"):
            return url.split(",")[1]
        
        response = requests.get(url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        print(f"Error fetching image {url}: {e}")
    return None

async def main(headed=False):
    print(f"Starting scrape of {URL}")
    print(f"Mode: {'Headed (Visible)' if headed else 'Headless'}")
    
    # 1. Scrape RAW HTML for ALL images (hidden + visible)
    # The page seems to use JS to remove images, so we need the raw response.
    print("Fetching raw HTML...")
    try:
        raw_response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        if raw_response.status_code != 200:
            print(f"Failed to fetch raw URL: {raw_response.status_code}")
            return

        soup = BeautifulSoup(raw_response.text, 'html.parser')
        all_imgs = soup.find_all('img')
        print(f"Found {len(all_imgs)} images in raw HTML.")
        
        all_images_data = []
        for img in all_imgs:
            src = img.get('src')
            if src:
                b64 = get_base64_from_url(src) if not src.startswith("data:image") else src.split(",")[1]
                if b64:
                    all_images_data.append({"src": src, "base64": b64})
        
        save_json(all_images_data, "allimages.json")

    except Exception as e:
        print(f"Error during raw scraping: {e}")

    # 2. Scrape Visible Images & Instructions using Playwright using Z-Index Filtering
    print("Launching browser for visible elements (Z-Index filtering)...")
    async with async_playwright() as p:
        # Launch browser with headed option
        browser = await p.chromium.launch(headless=not headed)
        page = await browser.new_page()
        await page.goto(URL)
        
        try:
            await page.wait_for_selector(".captcha-img", timeout=10000)
        except:
            print("Timeout waiting for content")
            
        # Helper to get element info with z-index
        async def get_element_info(element):
            if not await element.is_visible():
                return None
            box = await element.bounding_box()
            if not box:
                return None
            # Get z-index, default to 0 ('auto' usually computed as 0 in stacking context comparison logic for simple cases, 
            # or we can assume numerical values are present based on debug)
            z_index_str = await element.evaluate("el => window.getComputedStyle(el).zIndex")
            try:
                z_index = int(z_index_str)
            except:
                z_index = 0
            
            return {
                "element": element,
                "x": round(box["x"]),
                "y": round(box["y"]),
                "z_index": z_index
            }

        # --- Filter Images ---
        raw_imgs = await page.query_selector_all(".captcha-img")
        img_candidates = []
        for img in raw_imgs:
            info = await get_element_info(img)
            if info:
                img_candidates.append(info)
                
        # Group by position (x,y)
        from collections import defaultdict
        images_by_pos = defaultdict(list)
        for cand in img_candidates:
            key = (cand["x"], cand["y"])
            images_by_pos[key].append(cand)
            
        print(f"Found {len(img_candidates)} visible image candidates in {len(images_by_pos)} unique positions.")
        
        final_images_data = []
        for pos, candidates in images_by_pos.items():
            # Pick max z-index
            best = max(candidates, key=lambda c: c["z_index"])
            # Extract data
            src = await best["element"].get_attribute("src")
            if src:
                b64 = get_base64_from_url(src) if not src.startswith("data:image") else src.split(",")[1]
                if b64:
                    final_images_data.append({"src": src, "base64": b64})
                    
        save_json(final_images_data, "visible_images_only.json")

        # --- Filter Instructions ---
        raw_instrs = await page.query_selector_all(".box-label")
        instr_candidates = []
        for instr in raw_instrs:
            info = await get_element_info(instr)
            if info:
                text = await instr.inner_text()
                if text.strip():
                    info["text"] = text.strip()
                    instr_candidates.append(info)
        
        if instr_candidates:
            # Pick absolute max z-index
            best_instr = max(instr_candidates, key=lambda c: c["z_index"])
            print(f"Chosen Instruction: '{best_instr['text']}' (Z-Index: {best_instr['z_index']})")
            
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, "visible_instruction.txt")
            
            with open(filepath, "w") as f:
                f.write(best_instr['text'])
        else:
            print("No visible instructions found.")
            
        await browser.close()

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Task 3 DOM Scraper")
    parser.add_argument("--headed", action="store_true", help="Run in headed mode (visible browser) for verification")
    args = parser.parse_args()
    
    asyncio.run(main(headed=args.headed))
