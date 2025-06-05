import re
import math
import numpy as np
from urllib.parse import urlparse
import tldextract

# Tách Features từ tập raw dataset
def calculate_entropy(string):
    prob = [float(string.count(c)) / len(string) for c in set(string)]
    return -sum(p * math.log2(p) for p in prob)

def extract_features_from_url(url):
    features = {}
    parsed = urlparse(url)
    ext = tldextract.extract(url)

    domain = ext.registered_domain or ''
    subdomain = ext.subdomain or ''
    path = parsed.path or ''
    query = parsed.query or ''
    fragment = parsed.fragment or ''

    sub_parts = subdomain.split('.') if subdomain else []

    # 1. URL_based Features
    features['url_length'] = len(url)
    features['number_of_dots_in_url'] = url.count('.')
    features['having_repeated_digits_in_url'] = int(bool(re.search(r'(\d)\1', url)))
    features['number_of_digits_in_url'] = sum(c.isdigit() for c in url)
    features['number_of_special_char_in_url'] = len(re.findall(r'[^\w]', url))
    features['number_of_hyphens_in_url'] = url.count('-')
    features['number_of_underline_in_url'] = url.count('_')
    features['number_of_slash_in_url'] = url.count('/')
    features['number_of_questionmark_in_url'] = url.count('?')
    features['number_of_equal_in_url'] = url.count('=')
    features['number_of_at_in_url'] = url.count('@')
    features['number_of_dollar_in_url'] = url.count('$')
    features['number_of_exclamation_in_url'] = url.count('!')
    features['number_of_hashtag_in_url'] = url.count('#')
    features['number_of_percent_in_url'] = url.count('%')

    # 2. Domain_based Features
    features['domain_length'] = len(domain)
    features['number_of_dots_in_domain'] = domain.count('.')
    features['number_of_hyphens_in_domain'] = domain.count('-')
    features['having_special_characters_in_domain'] = int(bool(re.search(r'[^\w\.]', domain)))
    features['number_of_special_characters_in_domain'] = len(re.findall(r'[^\w\.]', domain))
    features['having_digits_in_domain'] = int(any(c.isdigit() for c in domain))
    features['number_of_digits_in_domain'] = sum(c.isdigit() for c in domain)
    features['having_repeated_digits_in_domain'] = int(bool(re.search(r'(\d)\1', domain)))

    # 3. Subdomain_based Features
    features['number_of_subdomains'] = len(sub_parts)
    features['having_dot_in_subdomain'] = int('.' in subdomain)
    features['having_hyphen_in_subdomain'] = int('-' in subdomain)
    features['average_subdomain_length'] = np.mean([len(p) for p in sub_parts]) if sub_parts else 0
    features['average_number_of_dots_in_subdomain'] = np.mean([s.count('.') for s in sub_parts]) if sub_parts else 0
    features['average_number_of_hyphens_in_subdomain'] = np.mean([s.count('-') for s in sub_parts]) if sub_parts else 0
    features['having_special_characters_in_subdomain'] = int(bool(re.search(r'[^\w\.]', subdomain)))
    features['number_of_special_characters_in_subdomain'] = len(re.findall(r'[^\w\.]', subdomain))
    features['having_digits_in_subdomain'] = int(any(c.isdigit() for c in subdomain))
    features['number_of_digits_in_subdomain'] = sum(c.isdigit() for c in subdomain)
    features['having_repeated_digits_in_subdomain'] = int(bool(re.search(r'(\d)\1', subdomain)))

    # 4. Other Features
    features['having_path'] = int(bool(path))
    features['path_length'] = len(path)
    features['having_query'] = int(bool(query))
    features['having_fragment'] = int(bool(fragment))
    features['having_anchor'] = int('#' in url)
    features['entropy_of_url'] = calculate_entropy(url)
    features['entropy_of_domain'] = calculate_entropy(domain)

    return features