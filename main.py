import re
import os
from pytrends.request import TrendReq
from web3 import Web3

from dotenv import load_dotenv
load_dotenv()

# Domain names must be longer than 2 characters
MINIMUM_KEYWORD_LENGTH = 2

pytrends = TrendReq(hl='en-US', tz=360)

# Initialize web3 instance
INFURA_API_KEY = os.environ["INFURA_API_KEY"]
web3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{INFURA_API_KEY}"))

def slugify(value):
    value = str(value)
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()  # Remove all non-alphanumeric characters except spaces, hyphens, and underscores
    value = re.sub(r'[-\s]+', '-', value)  # Replace sequences of spaces or hyphens with a single hyphen
    return value

def get_keyword_from_url(url):
    pattern = re.compile(r'q=([^&]+)')
    match = pattern.search(url)
    keyword = match.group(1).replace('+', ' ') if match else None
    return keyword

def get_trending_keywords():
    trending = pytrends.today_searches(pn='US')
    urls = trending.tolist()
    keywords = [get_keyword_from_url(url) for url in urls]
    return keywords

def get_file_keywords():
    folder_path = "keywords"
    all_lines = []
    files = os.listdir(folder_path)
    for file_name in files:
        if not file_name.endswith(".txt"): continue
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r") as file:
            lines = file.readlines()
            all_lines.extend(lines)
    all_lines = [line.strip() for line in all_lines if line.strip()]
    keywords = list(set(all_lines))
    return keywords

def get_all_keywords():
    trending_keywords = get_trending_keywords()
    file_keywords = get_file_keywords()
    all_keywords = trending_keywords + file_keywords
    all_keywords = list(set(all_keywords))
    return all_keywords

def check_ens_status(domain):
    ens = web3.ens
    owner = ens.owner(domain)
    return owner != '0x0000000000000000000000000000000000000000'

def main():
    keywords = get_all_keywords()
    keywords = [keyword for keyword in keywords if keyword]
    keywords = [slugify(keyword) for keyword in keywords]
    keywords = [keyword for keyword in keywords if len(keyword) > MINIMUM_KEYWORD_LENGTH]
    potential_domains = [f"{keyword}.eth" for keyword in keywords]

    for domain in potential_domains:
        if not check_ens_status(domain):
            print(f'Domain {domain} is unregistered')

if __name__ == '__main__':
    main()

