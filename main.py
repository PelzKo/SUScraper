import csv
import ast
from time import strftime

import requests
from bs4 import BeautifulSoup
from os.path import exists

supost_baseurl = "https://supost.com"
search_url = supost_baseurl + "/search?&q="
save_path = 'seen_ids.txt'

search_for = ["sublet", "sublease", "https://supost.com/search/sub/66", "rent"]


def return_soup(url):
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0'
    s.headers[
        'Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    # Making a GET request
    r = s.get(url)
    # Parsing the HTML
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


kick_out_words = ["looking", "wanted", "seeking"]


def scrape_post(url):
    post_id = url.split("/")[-1]
    soup = return_soup(url)
    title = soup.find('h2', id="posttitle").text.strip().replace("\n", ". ").lower()
    content = soup.find('div', class_='post-text').text.strip().replace("\n", ". ").lower()
    on_campus = content.find("on campus") != -1 or title.find("on campus") != -1
    price = soup.find("div", class_="item-price")
    if price is not None:
        price = price.contents[1].text
    quarter = content.find("quarter") != -1 or title.find("quarter") != -1
    december = content.find("december") != -1 or title.find("december") != -1 or content.find(
        "12/") != -1 or title.find("12/") != -1
    for kick_out_word in kick_out_words:
        if title.find(kick_out_word) != -1:
            return None
    if on_campus:
        return [post_id, url, title, content, price, quarter, december]
    else:
        return None


def write_to_file(data):
    filename = strftime("%Y%m%d_data") + '.csv'
    with open(filename, 'w', newline='\n', encoding="UTF-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerows(data)


def write_old_ids(old_ids):
    with open(save_path, 'w') as f:
        f.write(str(old_ids))  # set of numbers & a tuple


def load_old_ids():
    if not exists(save_path):
        return set()
    with open(save_path, 'r') as f:
        return ast.literal_eval(f.read())


def scrape_supost():
    old_ids = load_old_ids()
    results = []
    header = ["post_id", "link", "title", "content", "price", "quarter", "december"]
    results.append(header)
    for keyword in search_for:
        if keyword.startswith("https://"):
            search_url_sublet = keyword
        else:
            search_url_sublet = search_url + keyword
        soup = return_soup(search_url_sublet)
        links = soup.find_all('div', class_='one-result')
        for link in links:
            post_url = supost_baseurl + link.find("a").get("href")
            print(post_url)
            post_id = post_url.split("/")[-1]
            if post_id in old_ids:
                continue
            old_ids.add(post_id)
            res = scrape_post(post_url)
            if res is None:
                continue
            results.append(res)
    write_to_file(results)
    write_old_ids(old_ids)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    scrape_supost()
