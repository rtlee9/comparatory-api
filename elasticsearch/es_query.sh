curl -XGET "https://search-comparatory-q63ccyabfwf2hcitoumz3wuuxi.us-east-1.es.amazonaws.com/comparatory/_count" -d'
{}'

curl -XGET "https://search-comparatory-q63ccyabfwf2hcitoumz3wuuxi.us-east-1.es.amazonaws.com/comparatory/_search" -d'
{
  "query": {
    "match_phrase_prefix": {
      "dets.COMPANY CONFORMED NAME": {
        "query": "frontier fund",
        "max_expansions": 20
      }
    }
  }, "_source": "dets.COMPANY CONFORMED NAME"
}'

# Get explanation for above query
curl -XGET "https://search-comparatory-q63ccyabfwf2hcitoumz3wuuxi.us-east-1.es.amazonaws.com/comparatory/company/_validate/query?explain" -d'
{
  "query": {
    "match_phrase_prefix": {
      "dets.COMPANY CONFORMED NAME": {
        "query": "International gr",
        "max_expansions": 20
      }
    }
  }
}'

curl -XGET "https://search-comparatory-q63ccyabfwf2hcitoumz3wuuxi.us-east-1.es.amazonaws.com/comparatory/_search" -d'
{
  "query": {
    "match": {
      "dets.COMPANY CONFORMED NAME": "bank of america"
    }
  }, "_source": "dets.COMPANY CONFORMED NAME", "size": 10
}'

# Get explanation for above query
curl -XGET "https://search-comparatory-q63ccyabfwf2hcitoumz3wuuxi.us-east-1.es.amazonaws.com/comparatory/company/_validate/query?explain" -d'
{
  "query": {
    "match": {
      "dets.COMPANY CONFORMED NAME": "American internatio"
    }
  }
}'
