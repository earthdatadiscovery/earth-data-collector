import requests
import json
import meilisearch

from services.earthdata.earthdata import img_url_prefix, earthdata_endpoint

# MeiliSearch Config
meilisearch_client = meilisearch.Client("http://localhost:7700", "")
index = meilisearch_client.get_or_create_index(
    "earthdata",
    options={"primaryKey": "id"}
)
indexing_batch_size = 50


def build_document(result, collection_id, has_granules=None):

    document = {}

    # Count granules if present
    granules = 0
    if has_granules:
        response = requests.get(
            earthdata_endpoint + "/search/granules?collection_concept_id=" + collection_id,
        )
        if (response.status_code == 200):
            from xml.dom import minidom
            xmldoc = minidom.parseString(response.text)
            items = xmldoc.getElementsByTagName('hits')[0]
            granules = int(items.childNodes[0].data)


    document['id'] = collection_id
    document['img_url'] = img_url_prefix + collection_id
    document['title'] = result['title']
    document['summary'] = result['summary']
    document['short_name'] = result['short_name']
    document['original_format'] = result['original_format']
    document['organizations'] = result['organizations']
    document['data_center'] = result['data_center']
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
