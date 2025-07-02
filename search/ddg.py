from duckduckgo_search import DDGS
import time

max_retry = 5
start_time = time.time()
ddgs = DDGS(timeout=20)
retry = 0

while retry < max_retry:
    try:
        results = ddgs.text('python', region='cn-zh', max_results=10)
        for result in results:
            print(result['title'])
            print(result['href'])
            print(result['body'])
        time.sleep(2)
        break
    except Exception as e:
        retry += 1
        print(f"Attempt {retry}/{max_retry} failed: {e}")
        time.sleep(5)
        continue
else:
    print("Max retries reached.")