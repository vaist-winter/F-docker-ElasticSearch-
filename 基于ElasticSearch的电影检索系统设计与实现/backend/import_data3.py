from elasticsearch import Elasticsearch
import json
es = Elasticsearch(hosts=["http://localhost:9200"])
with open("douban_top250_movies.json", "r", encoding="utf-8") as f:
    documents = json.load(f)


for doc in documents:
    es.index(index="db", id=doc["_id"], body=doc["_source"])