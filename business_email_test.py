import re
import trafilatura
import trafilatura.sitemaps


def parse_domain(url: str):
    output = url.removeprefix("https://").removeprefix("http://").removeprefix("www.")
    output = output.split("/")[0]
    output_components = output.split(".")
    output = output_components[-2] + "." + output_components[-1]

    return output


url_to_check = input("Website:\n")

domain = parse_domain(url_to_check)
print(f"Email Domain: {domain}")

sitemap = trafilatura.sitemaps.sitemap_search("https://" + domain)
print(sitemap)

contact_pages = list(filter(lambda page: "contact" in page, sitemap))
print(contact_pages)

if len(contact_pages) == 0:
    print("No contact page found, using default URL")
else:
    print("Found contact page(s), using first result")
