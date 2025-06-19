from elasticsearch import Elasticsearch
import json
es = Elasticsearch(hosts=["http://localhost:9200"])
with open("people_health_articles.json", "r", encoding="utf-8") as f:
    documents = json.load(f)


for doc in documents:
    es.index(index="health", id=doc["_id"], body=doc["_source"])