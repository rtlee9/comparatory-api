# Comparatory
## Commercial intelligence API

[Comparatory](https://comparatory.io/) is a web application that provides novel insights about public companies based on free text data from regulatory filings. It uses deep learning to understand a company's business model, and provides several channels to explore the competitive landscape.

Start using the Comparatory [web application](https://comparatory.io/) for free today, or host this open source Comparatory API following the usage instructions below. API specifications can be found in `api.raml` (rendered into interactive HTML [here](https://comparatory.io/api-about)).

## Usage (Python 2.7)
1. Set environment variables:
	* `CONFIG`: configuration type (`config.ProductionConfig`, `config.DevelopmentConfig`)
	* `ES_HOST=`:  URL of ElasticSearch server
	* `AWS_ACCESS_KEY_ID`:  AWS ID for downloading pretrained model
	* `AWS_SECRET_ACCESS_KEY`:  AWS key for downloading pretrained model
1. Initialize ElasticSearch (one time) with company descriptions: `python index_descriptions.py`
1. Set up virtualenv: `virtualenv venv && source venv/bin/activate`
1. Install requirements: `pip install -r requirements.txt`
1. Run web application: `python run.py` or `gunicorn app:app`
1. Profit: `curl -G -XGET 'localhost:5000/companies/describe' --data-urlencode 'description=commercial insurance brokerage'`
