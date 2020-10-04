from services.earthdata.earthdata import get_collection_ids
from services.meilisearch.meilisearch import index_collection

if __name__ == "__main__":
    collection_ids = get_collection_ids(has_granules=True)
    index_collection(collection_ids, has_granules=True)
    collection_ids = get_collection_ids(has_granules=False)
    index_collection(collection_ids, has_granules=False)
