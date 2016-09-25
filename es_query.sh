curl -XGET "***REMOVED***comparatory/_count" -d'
{}'

curl -XGET "***REMOVED***comparatory/_search" -d'
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
curl -XGET "***REMOVED***comparatory/company/_validate/query?explain" -d'
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

curl -XGET "***REMOVED***comparatory/_search" -d'
{
  "query": {
    "match": {
      "dets.COMPANY CONFORMED NAME": "bank of america"
    }
  }, "_source": "dets.COMPANY CONFORMED NAME", "size": 10
}'

# Get explanation for above query
curl -XGET "***REMOVED***comparatory/company/_validate/query?explain" -d'
{
  "query": {
    "match": {
      "dets.COMPANY CONFORMED NAME": "American internatio"
    }
  }
}'
