import pymongo
import urllib.request
from bs4 import BeautifulSoup

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["crawler_db"]
pages_collection = db["pages"]
professors_collection = db["professors"]

professors_collection.create_index('email', unique=True)

target_url = 'https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml'

print("Downloading the Permanent Faculty List")
try:
    response = urllib.request.urlopen(target_url)
    html_data = response.read().decode('utf-8')
except Exception as e:
    print(f"Failed to retrieve the page: {e}")
    exit(1)

soup = BeautifulSoup(html_data, 'html.parser')

faculty_section = soup.find('section', class_='text-images')

if not faculty_section:
    print("Faculty section not found.")
    exit(1)

h2_tags = faculty_section.find_all('h2')

if not h2_tags:
    print("No faculty profiles found.")
    exit(1)


def get_label_value(strong_tag):
    label = strong_tag.get_text(strip=True).lower().rstrip(':')
    current = strong_tag.next_sibling
    while current and (isinstance(current, str) and current.strip() in ['', ':'] or current.name == 'br'):
        current = current.next_sibling
    value_parts = []
    while current and not (hasattr(current, 'name') and current.name == 'strong'):
        if isinstance(current, str):
            text = current.strip()
            if text and text != ':':
                value_parts.append(text)
        elif current.name == 'a':
            if label == 'email':
                value_parts.append(current.get_text(strip=True))
            elif label == 'web':
                value_parts.append(current.get('href', '').strip())
            else:
                value_parts.append(current.get_text(strip=True))
        elif current.name == 'br':
            pass  
        else:
            value_parts.append(current.get_text(strip=True))
        current = current.next_sibling
    value = ' '.join(value_parts).strip()
    return label, value


processed_emails = set()

for name_tag in h2_tags:
    name = name_tag.get_text(strip=True)

    title = office = phone = email = website = None

    p_tag = name_tag.find_next_sibling('p')

    if p_tag:
        strong_tags = p_tag.find_all('strong')
        for strong_tag in strong_tags:
            label, value = get_label_value(strong_tag)
            if label == 'title':
                title = value
            elif label == 'office':
                office = value
            elif label == 'phone':
                phone = value
            elif label == 'email':
                email = value
            elif label == 'web':
                website = value

    if not name or not email:
        print(
            f"Missing critical information for a faculty member ({name}). Skipping.")
        continue

    if email in processed_emails:
        print(f"Duplicate email found in HTML for {
              name} ({email}). Skipping duplicate.")
        continue
    processed_emails.add(email)

    professor_data = {
        'name': name,
        'title': title,
        'office': office,
        'phone': phone,
        'email': email,
        'website': website
    }

    try:
        professors_collection.insert_one(professor_data)
        print(f"Name: {name}")
        print(f"Title: {title}")
        print(f"Office: {office}")
        print(f"Phone: {phone}")
        print(f"Email: {email}")
        print(f"Website: {website}")
        print("   ")
    except pymongo.errors.DuplicateKeyError:
        print(f"Professor with email {
              email} already exists in MongoDB. Skipping.")

print(f"Total unique professors inserted: {len(processed_emails)}")