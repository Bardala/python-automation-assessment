# Task 1 — Q2: Research on reCAPTCHA v3

## 1. Different Types of reCAPTCHA v3

reCAPTCHA v3 is primarily a single "silent" type, but it is implemented and configured in different ways depending on the use case and action type.

### Types by Implementation
- **V3 Standard**: Silent verification. Returns a score (0.0 - 1.0).
- **V3 Enterprise**: Includes additional features like "Reason Codes" (e.g., `AUTOMATION`, `UNEXPECTED_ENVIRONMENT`) and "Transaction Protection".
- **Action-based**: Specifically tagged interactions (e.g., `login`, `checkout`, `social_post`).

### Parameter-Issue-Solution Report

| Parameter | Issue | Solution |
|---|---|---|
| **Action Name** | Using the same action name for multiple distinct events confuses the risk engine. | Define specific action names for each significant interaction (e.g., `homepage_view`, `form_submit`). |
| **User Session** | Frequent actions from the same session can lower the score. | Maintain realistic session lengths and intermittent interactions to mimic human browsing. |
| **Site Key Type** | Using a v2 site key with v3 logic (or vice versa) results in errors or 0.1 scores. | Ensure the `sitekey` implementation explicitly matches the reCAPTCHA version registered in the console. |
| **Execution Delay** | Executing `grecaptcha.execute` immediately on page load is often flagged. | Trigger execution after human-like interaction (scroll, mouse move, button click). |

---

## 2. Two Ways to Inject Tokens

When automating a site that uses reCAPTCHA v3, the goal is often to obtain a valid token and "inject" it into the target form or request.

### Method A: DOM Manipulation (Hidden Input Injection)
Most reCAPTCHA integrations involve a hidden input field (often named `g-recaptcha-response`) that is populated by the script.
- **Process**: 
  1. Obtain a token (either via browser automation or a solving service).
  2. Use JavaScript to set the value of the hidden input in the DOM.
  3. Trigger the form submission.
- **Example**:
  ```javascript
  document.getElementById('g-recaptcha-response').value = 'CAPTCHA_TOKEN_HERE';
  ```

### Method B: Request Interception & Modification (POST Payload Injection)
If the site sends the token via an AJAX/Fetch request (as seen in our target site), you can intercept the request before it reaches the server.
- **Process**:
  1. Intercept the outgoing network request (e.g., using Playwright `route` or a proxy).
  2. Substitute the `token` parameter in the POST body with your valid high-score token.
  3. Allow the request to continue to the server.
- **Example**: Using Playwright `page.route()`, you can modify the `postData` of the request to include the high-score token.
