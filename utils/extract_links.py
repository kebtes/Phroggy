import re
from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning
import warnings

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

async def extract_links(text: str):
    # html hyperlinks
    soup = BeautifulSoup(text, "html.parser")
    html_links = [a["href"] for a in soup.find_all("a", href=True)]

    # plain text URLs
    regex_links = re.findall(r'(https?://[^\s<>"]+|www\.[^\s<>"]+)', text)

    all_links = list(set(html_links + regex_links))
    return all_links
