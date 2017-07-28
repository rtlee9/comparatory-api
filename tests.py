import unittest
import json
from app import app

class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_peers_200(self):
        r = self.app.get('/companies/peers?ticker=KO')
        self.assertEqual(r.status_code, 200)

    def test_peers_desc_200(self):
        r = self.app.get('/companies/peers/desc?ticker=KO')
        self.assertEqual(r.status_code, 200)

    def test_peers_match_hasno_desc(self):
        r = self.app.get('/companies/peers?ticker=KO')
        body = json.loads(r.get_data())
        self.assertNotIn('business_desc', body['match'])

    def test_peers_desc_match_has_desc(self):
        r = self.app.get('/companies/peers/desc?ticker=KO')
        body = json.loads(r.get_data())
        self.assertIn('business_desc', body['match'])

    def test_peers_desc_results_have_desc(self):
        r = self.app.get('/companies/peers/desc?ticker=KO')
        body = json.loads(r.get_data())
        for sim in body['results']:
            self.assertIn('business_desc', sim)

    def test_peers_response_length(self):
        r = self.app.get('/companies/peers?ticker=KO')
        body = json.loads(r.get_data())
        self.assertEqual(len(body), 2)

    def test_peers_keys(self):
        r = self.app.get('/companies/peers?ticker=KO')
        body = json.loads(r.get_data())
        self.assertListEqual(body.keys(), ['results', 'match'])

    def test_match(self):
        r = self.app.get('/companies/peers?ticker=KO')
        body = json.loads(r.get_data())
        self.assertDictEqual(
            body['match'],
            {'id': u'KO', 'name': u'The Coca-Cola Company (KO)'})

    def test_peers_results_length(self):
        r = self.app.get('/companies/peers?ticker=KO')
        body = json.loads(r.get_data())
        self.assertEqual(len(body['results']), 5)

    def test_plots_200(self):
        r = self.app.get('/plots')
        self.assertEqual(r.status_code, 200)

    def test_plots_response_length(self):
        r = self.app.get('/plots')
        body = json.loads(r.get_data())
        self.assertGreaterEqual(len(body), 50)

    def test_plot_200(self):
        r = self.app.get('/plot')
        self.assertEqual(r.status_code, 200)

    def test_plot_response_length(self):
        r = self.app.get('/plot')
        body = json.loads(r.get_data())
        self.assertGreaterEqual(len(body), 50)

    def test_describe_200(self):
        r = self.app.get('/companies/describe/desc?description=jeans retailer')
        self.assertEqual(r.status_code, 200)

    def test_describe_response_length(self):
        r = self.app.get('/companies/describe/desc?description=jeans retailer')
        body = json.loads(r.get_data())
        self.assertEqual(len(body), 5)

    def test_describe_response_keys(self):
        r = self.app.get('/companies/describe/desc?description=jeans retailer')
        body = json.loads(r.get_data())
        for hit in body:
            self.assertListEqual(
                hit.keys(),
                [u'sim_score', u'business_desc', u'id', u'rank', u'name'])

    def test_desc_200(self):
        r = self.app.get('/companies/describe?description=jeans retailer')
        self.assertEqual(r.status_code, 200)

    def test_desc_response_length(self):
        r = self.app.get('/companies/describe?description=jeans retailer')
        body = json.loads(r.get_data())
        self.assertEqual(len(body), 5)

    def test_desc_response_keys(self):
        r = self.app.get('/companies/describe?description=jeans retailer')
        body = json.loads(r.get_data())
        for hit in body:
            self.assertListEqual(
                hit.keys(),
                [u'sim_score', u'id', u'rank', u'name'])


if __name__ == '__main__':
    unittest.main()
