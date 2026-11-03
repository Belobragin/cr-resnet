"""POST to an AWS_IAM Function URL with a SigV4 signature: sigv4_post.py <url> [region]."""
import os
import sys

import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.session import Session

url = sys.argv[1]
region = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("AWS_REGION", "us-east-2")

req = AWSRequest(method="POST", url=url, data=b"")
SigV4Auth(Session().get_credentials(), "lambda", region).add_auth(req)
resp = requests.post(url, headers=dict(req.headers), data=b"", timeout=60)
print(resp.text)
sys.exit(0 if resp.ok else 1)
