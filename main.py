import csv
import ast
import smtplib, ssl
import requests
import helper
from bs4 import BeautifulSoup
from os.path import exists
from time import strftime

supost_baseurl = "https://supost.com"
search_url = supost_baseurl + "/search?&q="
save_path = 'seen_ids.txt'

search_for = ["sublet", "sublease", "https://supost.com/search/sub/66", "rent", "sublicens"]

config = helper.read_config()

port = 587  # For starttls
smtp_server = config['EmailSettings']['smtp_server']
sender_email = config['EmailSettings']['sender_email']
receiver_email = config['EmailSettings']['receiver_email']
password = config['EmailSettings']['password']


def send_results(data):
    if len(data) < 1:
        return None
    message = "Hier die neuen, passenden Angebote:\n\n- " + '\n- '.join(data)

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


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


kick_out_words = ["looking", "wanted", "seeking", "need"]


def scrape_post(url):
    post_id = url.split("/")[-1]
    soup = return_soup(url)
    title = soup.find('h2', id="posttitle").text.strip().replace("\n", ". ").lower()
    content = soup.find('div', class_='post-text').text.strip().replace("\n", ". ").lower()
    on_campus = content.find("on campus") != -1 or title.find("on campus") != -1
    price = soup.find("div", class_="item-price")
    if price is not None:
        price = price.contents[1].text
        try:
            if price == "free" or float(price[1:].replace(",", "")) < 800:
                return None
        except ValueError as e:
            print(e)
    quarter = content.find("quarter") != -1 or title.find("quarter") != -1
    december = content.find("december") != -1 or title.find("december") != -1 or content.find(
        "12/") != -1 or title.find("12/") != -1 or content.find(" dec ") != -1 or title.find(" dec ") != -1
    for kick_out_word in kick_out_words:
        if title.find(kick_out_word) != -1:
            return None
    if on_campus:
        return [post_id, url, title, content, price, quarter, december]
    else:
        return None


def write_to_file(data, folder="results/"):
    filename = strftime("%Y%m%d_data") + '.csv'
    with open(folder + filename, 'w', newline='\n', encoding="UTF-8") as f:
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
    url_list = []
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
            url_list.append(post_url)
    write_to_file(results)
    write_old_ids(old_ids)
    send_results(url_list)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    scrape_supost()
