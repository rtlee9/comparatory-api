#! /bin/bash

curl -XDELETE "localhost:9200/comparatory"


# Create `my_index` with a single primary shard
# and set up the `autocomplete` analyzer using
# edge ngrams
curl -XPUT "localhost:9200/comparatory" -d'
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

# Test the autocomplete analyzer
curl -XGET "localhost:9200/comparatory/_analyze" -d'
{
  "analyzer": "autocomplete",
  "text": "quick brown"
}'

# Set the mapping for the `name` field
# to use the "autocomplete" analyzer at index time
# and the "standard" analyzer at search time
curl -XPUT "localhost:9200/comparatory/company/_mapping" -d'
{
  "company": {
    "properties": {
      "dets": {
        "properties": {
          "COMPANY CONFORMED NAME": {
            "type": "string",
            "analyzer": "autocomplete",
            "search_analyzer": "standard"
          }
        }
      }
    }
  }
}'
