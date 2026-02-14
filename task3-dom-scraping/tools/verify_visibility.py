import asyncio
from playwright.async_api import async_playwright

URL = "https://egypt.blsspainglobal.com/Global/CaptchaPublic/GenerateCaptcha?data=4CDiA9odF2%2b%2bsWCkAU8htqZkgDyUa5SR6waINtJfg1ThGb6rPIIpxNjefP9UkAaSp%2fGsNNuJJi5Zt1nbVACkDRusgqfb418%2bScFkcoa1F0I%3d"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL)
        
        try:
            await page.wait_for_selector(".captcha-img", timeout=10000)
        except:
            print("Timeout waiting for content")
            
        # Inspect Images
        imgs = await page.query_selector_all(".captcha-img")
        print(f"Total .captcha-img found: {len(imgs)}")
        
        visible_imgs = []
        for i, img in enumerate(imgs):
            is_vis = await img.is_visible()
            box = await img.bounding_box()
            if is_vis:
                print(f"Img {i}: Visible=True, Box={box}")
                visible_imgs.append(img)
            else:
                # print(f"Img {i}: Visible=False")
                pass
                
        print(f"Total Visible Images (is_visible): {len(visible_imgs)}")
        
        # Inspect Instructions
        instrs = await page.query_selector_all(".box-label")
        print(f"Total .box-label found: {len(instrs)}")
        
        for i, instr in enumerate(instrs):
            is_vis = await instr.is_visible()
            if is_vis:
                text = await instr.inner_text()
                box = await instr.bounding_box()
                style = await instr.evaluate("el => window.getComputedStyle(el).zIndex")
                print(f"Instr {i}: Visible=True, Text='{text.strip()}', Box={box}, Z-Index={style}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
