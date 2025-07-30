import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://abav.com.br"
LIST_URL = BASE_URL + "/associados-abav/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_agency_links():
    response = requests.get(LIST_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    # Os links das agências geralmente estão dentro de 'a' com classe específica ou dentro de cards/listas
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Ajuste este filtro conforme a estrutura real dos links de agências
        if "/associado/" in href:
            full_link = href if href.startswith("http") else BASE_URL + href
            links.append(full_link)
    return list(set(links))  # remove duplicatas

def get_agency_details(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Nome da agência
    name = soup.find("h1")
    name = name.get_text(strip=True) if name else ""
    
    # Busca por telefone, email e website em possíveis campos
    phone = ""
    email = ""
    website = ""
    for text in soup.stripped_strings:
        if "Telefone:" in text:
            phone = text.split("Telefone:")[-1].strip()
        if "E-mail:" in text or "Email:" in text:
            email = text.split(":")[-1].strip()
        if "Site:" in text or "Website:" in text:
            website = text.split(":")[-1].strip()
    
    # Alternativamente, procurar por links mailto ou tel
    for a in soup.find_all('a', href=True):
        if a['href'].startswith('mailto:'):
            email = a['href'].replace('mailto:', '').strip()
        if a['href'].startswith('tel:'):
            phone = a['href'].replace('tel:', '').strip()
        if a['href'].startswith('http') and "abav.com.br" not in a['href']:
            website = a['href']
    
    return {
        'name': name,
        'phone': phone,
        'email': email,
        'website': website,
    }

def main():
    agency_links = get_agency_links()
    print(f"Encontradas {len(agency_links)} agências.")
    with open("agencias_abav.csv", "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(["Nome", "Telefone", "Email", "Website"])
        for url in agency_links:
            details = get_agency_details(url)
            writer.writerow([details['name'], details['phone'], details['email'], details['website']])
            print(f"Raspada: {details['name']}")
            time.sleep(1)  # Evite sobrecarregar o servidor

if __name__ == "__main__":
    main()