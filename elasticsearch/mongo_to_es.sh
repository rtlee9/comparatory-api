#! /bin/bash

curl -XPUT "http://localhost:9200/" -d'
{
  "settings": {
    "number_of_shards": 3,
    "analysis": {
      "filter": {
        "autocomplete_filter": {
          "type": "edge_ngram",
          "min_gram": 1,
          "max_gram": 20
        }
      },
      "analyzer": {
        "autocomplete": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "autocomplete_filter"
          ]
        }
      }
    }
  }
}'

# mongoexport --db industry --collection dataset --out ten_k.json
curl -XPUT "https://search-comparatory-q63ccyabfwf2hcitoumz3wuuxi.us-east-1.es.amazonaws.com/comparatory" -d'
{
  "settings": {
    "number_of_shards": 3,
    "analysis": {
      "filter": {
        "autocomplete_filter": {
          "type": "edge_ngram",
          "min_gram": 1,
          "max_gram": 20
        }
      },
      "analyzer": {
        "autocomplete": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "autocomplete_filter"
          ]
        }
      }
    }
  }
}'

# curl -XPOST 'https://search-comparatory-q63ccyabfwf2hcitoumz3wuuxi.us-east-1.es.amazonaws.com/comparatory/company/_bulk?pretty' --data-binary '@ten_k.json'
