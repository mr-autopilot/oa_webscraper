import re
import trafilatura
import trafilatura.sitemaps


def naive_email_search(url):
    # Skip if there's no usable website (redundant per filtering, but better to be safe)
    if url == "Not Available":
        return ""

    # Parse the domain (e.g. 'example.com') from the URL
    domain = parse_domain(url)

    # Regex to match emails tied to that exact domain
    pattern = rf"\b[A-Za-z0-9._%+-]+@{re.escape(domain)}"
    # Fallback pattern: match any email-like string (used if no domain match found)
    fallback_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{3,}\b"

    # Use trafilatura to find sitemap URLs and locate any 'contact' pages
    sitemap = trafilatura.sitemaps.sitemap_search("https://" + domain)
    contact_pages = list(filter(lambda page: "contact" in page, sitemap))

    res = None
    fallback_res = None

    if len(contact_pages) == 0:
        # If no contact page found, download homepage
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            downloaded = ""

        # Try finding email tied to domain
        res = re.search(pattern, downloaded)
        # Fallback: try finding any email
        fallback_res = re.search(fallback_pattern, downloaded)
    else:
        # If contact page found, prefer that
        downloaded = trafilatura.fetch_url(contact_pages[0])
        if not downloaded:
            downloaded = ""

        res = re.search(pattern, downloaded)

        fallback_res = re.search(fallback_pattern, downloaded)

    # Return first matching domain-specific email
    if res:
        return res.group(0)
    # Else return general match
    if fallback_res:
        return fallback_res.group(0)

    return "Not Found"


def parse_domain(url: str):
    # Clean and parse out bare domain name for use in regex
    output = url.removeprefix("https://").removeprefix("http://").removeprefix("www.")
    output = output.split("/")[0]
    output_components = output.split(".")
    output = output_components[-2] + output_components[-1]

    return output
