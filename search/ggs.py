from googlesearch import search
import time

max_retry = 3
retry = 0

while retry < max_retry:
    try:
        results = search("python", lang='zh', num_results=10, advanced=True)
        for result in results:
            print(result.title)
            print(result.url)
            print(result.description)
        break
    except Exception as e:
        retry += 1
        print(f"Attempt {retry}/{max_retry} failed: {e}")
        if retry < max_retry:
            time.sleep(5)
        else:
            print("Max retries reached. Exiting...")