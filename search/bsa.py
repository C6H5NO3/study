from baidu_serp_api import BaiduPc
import time

pc_serp = BaiduPc()
max_page = 10
max_retry = 5
page = 1
retry = 0

while page <= max_page:
    try:
        results = pc_serp.search('python', pn=page, exclude=['recommend', 'match_count'])
        
        if len(results['data']['results']) == 0:
            if retry < max_retry:
                retry += 1
                time.sleep(5)
                print(f'Retrying... ({retry}/{max_retry})')
                continue
            else:
                print('Max retries reached. Exiting...')
                break
        
        print(f'Page {page}')
        for result in results['data']['results']:
            print(result['title'])

        if results['data']['last_page']:
            break
        page += 1
        retry = 0
        time.sleep(2)
    except Exception as e:
        retry += 1
        print(f'Attempt {retry}/{max_retry} failed: {e}')
        if retry < max_retry:
            time.sleep(5)
        else:
            print('Max retries reached.')
            break