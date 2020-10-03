from earthdata_tools.earthdata_tools import get_collection_ids
from meilisearch_tools.meilisearch_tools import index_collection

if __name__ == "__main__":
    collection_ids = get_collection_ids(has_granules=True)
    index_collection(collection_ids, has_granules=True)
    collection_ids = get_collection_ids(has_granules=False)
    index_collection(collection_ids, has_granules=False)