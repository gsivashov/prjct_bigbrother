import random
from bs4 import BeautifulSoup
from requests_html import HTMLSession


def get_response(url):
    user_agent_list = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        # Chrome Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        # Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        # Firefox on Linux
        "Mozilla/5.0 (X11; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
    ]

    user_agent = random.choice(user_agent_list)
    headers = {"User-Agent": user_agent}
    # headers = nature_header()

    session = HTMLSession()
    try:
        response = session.get(
            url.strip(),
            headers=headers,
            timeout=10)
        if response.status_code == 200:
            print(url.strip())
            return response
        else:
            print(
                f'-----Skipped {url.strip()} because {response.status_code}-----')
            return url
    except:
        print(f'-----{url.strip()} timed out-----')


def main():
    response = get_response(
        'https://www.ebay.ch/sch/schweiz/107706/i.html?_oac=1&_ssc=1&_nkw=radierung&_mprrngcbx=1&_fosrp=1')
    h1 = response.html.xpath('//h1')

    try:
        article = response.html
    except:
        return None

    soup = BeautifulSoup(article.html, features='lxml')

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.body.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    print(text)


if __name__ == '__main__':
    main()
