import requests
from bs4 import BeautifulSoup
from datetime import datetime

def getSoup(response):
    soup = BeautifulSoup(response.text, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    return soup

def getToken(content):
    start = content.index('ssrAccessToken')
    content = content[start + 17:]
    end = content.index('",')
    token = content[:end]
    return token


session = requests.session()
url = 'https://www.dice.com/dashboard/login'

payload={
    'email' : 'davidsmith2024dev@gmail.com',
    'password' : 'Dev@2024!@'
    }
# headers = {
#   'authority': 'www.dice.com',
#   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#   'accept-language': 'en-US,en;q=0.9',
#   'cache-control': 'max-age=0',
#   'content-type': 'application/x-www-form-urlencoded',
#   'origin': 'https://www.dice.com',
#   'referer': 'https://www.dice.com/dashboard/login',
#   'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
#   'sec-ch-ua-mobile': '?0',
#   'sec-ch-ua-platform': '"Windows"',
#   'sec-fetch-dest': 'document',
#   'sec-fetch-mode': 'navigate',
#   'sec-fetch-site': 'same-origin',
#   'sec-fetch-user': '?1',
#   'upgrade-insecure-requests': '1',
#   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
# }

response = session.request("POST", url,  data=payload)


soup = getSoup(response)



q = 'devops Engineers'
l = ''
e = "CONTRACTS|THIRD_PARTY"
p = 'SEVEN'

start = 0



url = f" https://www.dice.com/jobs?q={q}&location={l}&filters.employmentType={e}&filters.postedDate={p}&radius=30&radiusUnit=mi&page={start}&pageSize=20&filters.easyApply=true&language=en"

print(url)

response = session.get(url)

soup = getSoup(response)

cards = soup.find_all('dhi-search-card')

print(len(cards))

apply_urls = []

for card in cards:
    job_id = card.find('a',attrs={'data-cy':'card-title-link'})['id']
    if 'applied' in card.text:
        print('alrady applied')
    else:
        job_url = f'https://www.dice.com/job-detail/{job_id}'
        apply_urls.append(job_url)

for apply_url in apply_urls:
    response = session.get(apply_url)
    content = str(response.content)
    token = getToken(content)
    print(token)
    url = f'https://www.dice.com/apply?{token}'
    response = session.get(url)
    soup = getSoup(response.text)
    print(soup.text)
    url = f'https://www.dice.com/application-submitted?{token}'
    response = session.get(url)
    soup = getSoup(response.text)
    print(soup.text)










