import re
import trafilatura
import trafilatura.sitemaps


def naive_email_search(url):
    if url == "Not Available":
        return ""

    domain = parse_domain(url)

    pattern = rf"\b[A-Za-z0-9._%+-]+@{re.escape(domain)}"
    fallback_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{3,}\b"

    sitemap = trafilatura.sitemaps.sitemap_search("https://" + domain)
    contact_pages = list(filter(lambda page: "contact" in page, sitemap))

    res = None
    fallback_res = None

    if len(contact_pages) == 0:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            downloaded = ""

        res = re.search(pattern, downloaded)

        fallback_res = re.search(fallback_pattern, downloaded)
    else:
        downloaded = trafilatura.fetch_url(contact_pages[0])
        if not downloaded:
            downloaded = ""

        res = re.search(pattern, downloaded)

        fallback_res = re.search(fallback_pattern, downloaded)

    if res:
        return res.group(0)

    if fallback_res:
        return fallback_res.group(0)

    return "Not Found"


def parse_domain(url: str):
    output = url.removeprefix("https://").removeprefix("http://").removeprefix("www.")
    output = output.split("/")[0]
    output_components = output.split(".")
    output = output_components[-2] + output_components[-1]

    return output
