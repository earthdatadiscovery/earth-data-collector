import json
import requests

# Earth Data Config
earthdata_endpoint = "https://cmr.earthdata.nasa.gov"
img_url_prefix = "https://cmr.earthdata.nasa.gov/browse-scaler/browse_images/datasets/"


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
    print("Collections IDs retrieved")
    return collection_ids
