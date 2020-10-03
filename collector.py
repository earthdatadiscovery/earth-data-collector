import requests
import json
import meilisearch

earthdata_endpoint = "https://cmr.earthdata.nasa.gov"
img_url_prefix = "https://cmr.earthdata.nasa.gov/browse-scaler/browse_images/datasets/"

indexing_batch_size = 50

def get_collection_ids(has_granules=None):
    batch_size = 2000
    params = {
        "page_size": batch_size,
        "offset": 0,
    }
    collection_ids = []
    
    print("Gathering collections IDs from CMR Earth Data API")
    earthdata_url = earthdata_endpoint + "/search/collections/"
    if has_granules is not None:
        earthdata_url += "?has_granules=" + str(has_granules).lower()
    response = requests.get(
        earthdata_url,
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


client  = meilisearch.Client("https://sandbox-pool-xi7fypa-3bsbgmeayb75w.ovh-fr-2.platformsh.site", "zdeGjerpSEiKBJZSMBZb")
index = client.get_or_create_index("nasa", options={"primaryKey": "id"})



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
                if has_granules is not None:
                    if has_granules:
                        document['granules'] = 1
                    else:
                        document['granules'] = 0
                results.append(document)
            else:
                raise Exception("Couldn't access CMR Earth Data API")
            print(collection_id, "success", len(results))
            
        except Exception as e:
            print("ERROR:", e)
        if (len(results) >= indexing_batch_size):
            index.add_documents(results)
            results = []
    index.add_documents(results)

collection_ids = get_collection_ids(has_granules=True)
index_collection(collection_ids, has_granules=True)
collection_ids = get_collection_ids(has_granules=False)
index_collection(collection_ids, has_granules=False)
