import requests
import json
import meilisearch

earthdata_endpoint = "https://cmr.earthdata.nasa.gov"
img_url_prefix = "https://cmr.earthdata.nasa.gov/browse-scaler/browse_images/datasets/"

indexing_batch_size = 50

def get_collection_ids():
    batch_size = 2000
    params = {
        "page_size": batch_size,
        "offset": 0,
    }
    collection_ids = []
    
    print("Gathering collections IDs from CMR Earth Data API")
    response = requests.get(
        earthdata_endpoint + "/search/collections/",
        headers={"Accept": "application/json"},
        params=params,
    )
    if (response.status_code == 200):
        results = json.loads(response.text)['feed']['entry']
    else:
        raise Exception("Couldn't access CMR Earth Data API")
    while (len(results) > 0):

        for dataset in results:
            collection_ids.append(dataset['id'])

        params['offset'] += batch_size
        response = requests.get(
            earthdata_endpoint + "/search/collections/",
            headers={"Accept": "application/json"},
            params=params,
        )
        if (response.status_code == 200):
            results = json.loads(response.text)['feed']['entry']

        break
    print("Collections IDs retrieved")
    return collection_ids


client  = meilisearch.Client("http://localhost:7700/", "")
index = client.get_or_create_index("nasa", options={"primaryKey": "id"})

results = []
collection_ids = get_collection_ids()

for collection_id in collection_ids:
    try:
        
        response = requests.get(
            earthdata_endpoint + "/search/concepts/" + str(collection_id),
            headers={"Accept": "application/json"},
        )
        if (response.status_code == 200):
            result = json.loads(response.text)
            document = {}
            document['id'] = collection_id
            document['img_url'] = img_url_prefix + collection_id
            document['title'] = result['title']
            document['summary'] = result['summary']
            document['short_name'] = result['short_name']
            document['original_format'] = result['original_format']
            document['organizations'] = result['organizations']
            document['data_center'] = result['data_center']
            if "links" in result:
                document['links'] = result['links']
            if "time_start" in result:
                document['time_start'] = result['time_start']
            if "time_end" in result:
                document['time_end'] = result['time_end']
            results.append(document)
        else:
            raise Exception("Couldn't access CMR Earth Data API")
        print(collection_id, "success", len(results))
        
    except Exception as e:
        print("ERROR:", e)
        print(collection_id, document, len(results))
    if (len(results) >= indexing_batch_size):
        index.add_documents(results)
        results = []
