# Run a test server.
import argparse
from app import app

p = argparse.ArgumentParser()
p.add_argument('--port', type=int, default=5000)
p.add_argument('--no-debug', action='store_true')
args = p.parse_args()
app.run(host='0.0.0.0', port=args.port, debug=(not args.no_debug))
