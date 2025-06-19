from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

es = Elasticsearch(hosts=["http://localhost:9200"])

# 创建索引
if not es.indices.exists(index="db"):
    es.indices.create(
        index="db",
        body={
            "settings": {"number_of_shards": 1, "number_of_replicas": 1},
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "author": {"type": "keyword"},
                    "date": {"type": "text"},
                    "content": {"type": "text"}
                }
            }
        }
    )

@app.route('/api/search', methods=['POST'])
def search():
    query = request.json.get('query')
    page = request.json.get('page', 1)
    if not query:
        return jsonify({"error": "Missing query"}), 400

    try:
        res = es.search(
            index="db",
            body={
                "query": {"multi_match": {"query": query, "fields": ["title^2", "content"]}},
                "from": (page - 1) * 10,
                "size": 10
            }
        )
        formatted_results = [
            {
                "id": hit["_id"],
                "title": hit["_source"]["title"],
                "author": hit["_source"]["author"],
                "date": hit["_source"]["date"],
                "snippet": " ".join(hit["_source"]["content"].split()[:30]) + "...",
            }
            for hit in res["hits"]["hits"]
        ]
        total_pages = max(1, (res["hits"]["total"]["value"] + 9) // 10)
        return jsonify({
            "results": formatted_results,
            "total_pages": total_pages,
            "current_page": page,
            "total_results": res["hits"]["total"]["value"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/document/<doc_id>', methods=['GET'])
def get_document(doc_id):
    try:
        result = es.get(index="db", id=doc_id)
        return jsonify({
            "id": doc_id,
            "title": result["_source"]["title"],
            "author": result["_source"]["author"],
            "date": result["_source"]["date"],
            "content": result["_source"]["content"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)