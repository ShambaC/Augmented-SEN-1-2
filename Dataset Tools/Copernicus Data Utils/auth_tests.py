from AuthClient import getOAuth
from pprint import pp
from time import time

import json

oauth, token = getOAuth()
print(f"token: {token}")
print(f'Time Now: {time()}, token expire: {token["expires_at"]}')

# res = oauth.get("https://sh.dataspace.copernicus.eu/configuration/v1/wms/instances")
# print(f"Response: {res.content}")

catalog_url = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/collections/byoc-3c662330-108b-4378-8899-525fd5a225cb"
res = oauth.get(catalog_url)
json_Res = json.loads(res.content)
pp(json_Res)