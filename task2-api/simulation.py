import time
import requests
import sys

API_URL = "http://localhost:8000"

def simulate_customer(target_url: str):
    print(f"🚀 [Customer] Starting simulation for: {target_url}")
    
    # 1. Submit Task
    try:
        response = requests.post(f"{API_URL}/recaptcha/in", json={"url": target_url})
        response.raise_for_status()
        data = response.json()
        task_id = data["task_id"]
        print(f"📥 [Customer] Task Submitted. ID: {task_id}")
    except Exception as e:
        print(f"❌ [Customer] Failed to submit task: {e}")
        return

    # 2. Poll for Results
    start_time = time.time()
    while True:
        try:
            res_response = requests.get(f"{API_URL}/recaptcha/res/{task_id}")
            res_data = res_response.json()
            status = res_data["status"]
            
            if status == "COMPLETED":
                result = res_data["result"]
                print(f"\n✅ [Customer] SUCCESS!")
                print(f"   Score: {result.get('score')}")
                print(f"   Token: {result.get('token')[:50]}...") # Truncate for display
                break
            
            elif status == "FAILED":
                print(f"\n❌ [Customer] FAILED: {res_data.get('error')}")
                break
            
            else:
                elapsed = time.time() - start_time
                sys.stdout.write(f"\r⏳ [Customer] Status: {status} (Elapsed: {elapsed:.1f}s)")
                sys.stdout.flush()
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n🛑 [Customer] Aborted by user.")
            break
        except Exception as e:
            print(f"\n⚠️ [Customer] Connection Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php"
        
    simulate_customer(url)
