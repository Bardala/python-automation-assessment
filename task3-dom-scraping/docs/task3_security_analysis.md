# Task 3: Security Analysis & Code Implementation Review

## 1. Security Vulnerability Analysis

The target captcha system exhibits a fundamental **client-side security flaw** in its implementation of "hidden" elements.

### The Vulnerability: Client-Side Obfuscation vs. True Hiding
The application attempts to create a captcha challenge by displaying a subset of images (9 visible) and a single instruction text while keeping a larger set of "decoy" elements in the DOM. However, it relies entirely on **visual stacking (z-index)** rather than securely delivering only the necessary data to the client.

*   **Data Leakage**: The raw HTML response contains **all** 54+ images and ~35 instruction variations. A secure implementation should only deliver the specific images and instruction required for the current challenge session from the server.
*   **Weak Hiding Mechanism**: Instead of using standard visibility toggles (`display: none`, `visibility: hidden`) or removing elements from the DOM, the application stacks multiple elements at the same screen coordinates. The "visible" element is simply the one with the **highest z-index**.
*   **Deterministic Bypass**: Because the visibility logic is purely CSS-based (z-index) and present in the client's computed styles, it can be programmatically deterministic. An automation script can query these properties just as a browser renders them, completely bypassing the intended visual obfuscation.

### Real-World Implication
This design allows a bot to scrape the **entire dataset** (all potential answers) in a single request and deterministically identify the correct challenge parameters without human interaction. This defeats the primary purpose of a CAPTCHA (Completely Automated Public Turing test to tell Computers and Humans Apart).

---

## 2. Implementation Walkthrough

The solution employs a **hybrid scraping strategy** to exploit the data leakage and deterministic rendering described above.

### A. Raw HTML Extraction (Data Leakage Exploitation)
**Goal:** Capture the full dataset of images, including those potentially removed by subsequent JavaScript execution.

```python
raw_response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(raw_response.text, 'html.parser')
all_imgs = soup.find_all('img')
```
*   **Engineering Reasoning**: We bypass the browser's rendering engine initially to capture the `response.text` directly. This ensures we get every `<img>` tag delivered by the server, creating a comprehensive dataset (`allimages.json`) that represents the full scope of leaked data.

### B. DOM Rendering & Visibility Logic (The Bypass)
**Goal:** replicate the "human" view to identify the 9 active images and 1 active instruction.

```python
# Grouping Logic
images_by_pos = defaultdict(list)
for cand in img_candidates:
    key = (cand["x"], cand["y"]) # Group by screen coordinates
    images_by_pos[key].append(cand)

# Filtering Logic
for pos, candidates in images_by_pos.items():
    best = max(candidates, key=lambda c: c["z_index"]) # Select top-most element
```
*   **Engineering Reasoning**:
    1.  **Coordinate Grouping**: By grouping elements that share the exact same bounding box `(x, y)`, we isolate the "stacks" of decoy images.
    2.  **Z-Index Filtering**: We explicitly query the computed `zIndex` style of every element. The `max()` function mathematically determines which element renders on top, effectively simulating the human visual cortex's occlusion processing.

### C. Base64 Handling
**Goal:** Normalize image data for storage.

```python
def get_base64_from_url(url):
    if url.startswith("data:image"):
        return url.split(",")[1]
    # ... fetch and encode remote URLs ...
```
*   **Engineering Reasoning**: The DOM contains a mix of inline `data:` URIs and remote URLs. This utility normalizes both formats into a consistent Base64 string, ensuring `allimages.json` and `visible_images_only.json` follow a strict schema regardless of the source format.

---

## 3. Conclusion

The solution successfully automates the captcha challenge not by breaking a cryptographic protection, but by **reading the open state of the client-side render**. The provided script demonstrates that visual obfuscation without server-side data segregation is insufficient for security controls.
