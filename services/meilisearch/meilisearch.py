import requests
import json
import meilisearch
from bs4 import BeautifulSoup

from services.earthdata.earthdata import img_url_prefix, earthdata_endpoint

# MeiliSearch Config
meilisearch_client = meilisearch.Client("https://localhost:7700", "")
index = meilisearch_client.get_or_create_index(
    "earthdata",
    options={"primaryKey": "id"}
)
indexing_batch_size = 100


def build_document(result, collection_id, has_granules=None):



    # Count granules if present
    granules = 0
    try:
        if has_granules:
            response = requests.get(
                earthdata_endpoint + "/search/granules?collection_concept_id=" + collection_id,
            )
            if (response.status_code == 200):
                from xml.dom import minidom
                xmldoc = minidom.parseString(response.text)
                items = xmldoc.getElementsByTagName('hits')[0]
                granules = int(items.childNodes[0].data)
    except Exception:
        print("Couldn't get granules")


    # Scrapping Categories and Geopraphic location
    categories = []
    subcategories = {}
    continents = []
    countries = []

    response = requests.get(
        earthdata_endpoint + "/search/concepts/" + collection_id,
        headers={'Accept':'text/html'}
    )
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            keywords_div = soup.find_all('div', class_='science-keywords-preview')
            for div in keywords_div:
                lists = div.find_all('ul', class_='arrow-tag-group-list')
                for list in lists:
                    elem = list.find_all('li', class_='arrow-tag-group-item')
                    if not elem[1].string in categories:
                        categories.append(elem[1].string)
                    if not elem[1].string in subcategories:
                        subcategories[elem[1].string] = []
                    if (len(elem) >= 3):
                        subcategories[elem[1].string].append(elem[2].string)
        except Exception:
            print("Couldn't scrape categories")

        try:
            location_div = soup.find_all('ul', class_='location-keywords-preview')
            for div in location_div:
                lists = div.find_all('ul', class_='arrow-tag-group-list')
                for list in lists:
                    elements = list.find_all('li', class_='arrow-tag-group-item')
                    for i in range(len(elements)):
                        if elements[i].string == 'CONTINENT':
                            if not elements[i+1].string in continents:
                                continents.append(elements[i+1].string)
                            if not elements[-1].string in countries:
                                countries.append(elements[-1].string)
                            break
        except Exception:
            print("Couldn't scrape location data")


    document= {}
    document['id'] = collection_id
    document['img_url'] = img_url_prefix + collection_id
    document['title'] = result['title']
    document['summary'] = result['summary']
    document['short_name'] = result['short_name']
    document['original_format'] = result['original_format']
    document['organizations'] = result['organizations']
    document['data_center'] = result['data_center']
    document['categories'] = categories
    document['subcategories'] = subcategories
    document['continents'] = continents
    document['countries'] = countries
    if 'updated' in result:
        document['updated'] = result['updated']
    if "links" in result:
        document['links'] = result['links']
    if "time_start" in result:
        document['time_start'] = result['time_start']
    if "time_end" in result:
        document['time_end'] = result['time_end']
    document['granules'] = granules
    return document


def index_collection(collection_ids, has_granules=None):
    results = []

    for collection_id in collection_ids:

        try:
            response = requests.get(
                earthdata_endpoint + "/search/concepts/" + str(collection_id),
                headers={"Accept": "application/json"},
            )

            if (response.status_code == 200):
                result = json.loads(response.text)
                document = build_document(result, collection_id, has_granules)

                results.append(document)
            else:
                print(response.status_code)
                raise Exception("Couldn't access CMR Earth Data API")
            print(collection_id, "success", len(results))

        except Exception as e:
            print("ERROR:", e)
        if (len(results) >= indexing_batch_size):
            index.add_documents(results)
            results = []
    index.add_documents(results)
