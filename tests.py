import unittest
import json
from app import app

class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_peers_200(self):
        r = self.app.get('/companies/peers?company-name=Coca Cola Co')
        self.assertEqual(r.status_code, 200)

    def test_peers_desc_200(self):
        r = self.app.get('/companies/peers/desc?company-name=Coca Cola Co')
        self.assertEqual(r.status_code, 200)

    def test_peers_desc_has_desc(self):
        r = self.app.get('/companies/peers/desc?company-name=Coca Cola Co')
        body = json.loads(r.get_data())
        for sim in body['results']:
            self.assertIn('business_desc', sim)

    def test_peers_response_length(self):
        r = self.app.get('/companies/peers?company-name=Coca Cola Co')
        body = json.loads(r.get_data())
        self.assertEqual(len(body), 2)

    def test_peers_keys(self):
        r = self.app.get('/companies/peers?company-name=Coca Cola Co')
        body = json.loads(r.get_data())
        self.assertListEqual(body.keys(), ['results', 'match'])

    def test_match(self):
        r = self.app.get('/companies/peers?company-name=Coca Cola Co')
        body = json.loads(r.get_data())
        self.assertDictEqual(
            body['match'],
            {
                u'sic_cd': u'2080',
                u'id': u'21344_10-K_2015-02-25.txt',
                u'name': u'Coca Cola Co',
            })

    def test_peers_results_length(self):
        r = self.app.get('/companies/peers?company-name=Coca Cola Co')
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


if __name__ == '__main__':
    unittest.main()
