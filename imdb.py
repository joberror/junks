import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def search_imdb():
    search_term = input("Enter movie/series name: ").strip()
    encoded_query = quote(search_term)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    search_url = f"https://www.imdb.com/find?q={encoded_query}&s=tt&ttype=ft,tv,vg"

    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"🚨 Connection Error: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for item in soup.select('.ipc-metadata-list-summary-item')[:3]:
        try:
            title_element = item.select_one('a.ipc-metadata-list-summary-item__t')
            title = title_element.text.strip()
            year_element = item.select_one('.ipc-metadata-list-summary-item__li')
            year = year_element.text.strip() if year_element else "Unknown"
            movie_url = "https://www.imdb.com" + title_element['href'].split('?')[0]
            results.append({'title': title, 'year': year, 'url': movie_url})
        except:
            continue

    if not results:
        print("No results found!")
        return

    print("\nTop Results:")
    for idx, result in enumerate(results, 1):
        print(f"{idx}. {result['title']} ({result['year']}) - {result['url']}")

if __name__ == "__main__":
    search_imdb()
