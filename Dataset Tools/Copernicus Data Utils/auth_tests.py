from AuthClient import SessionData
from pprint import pp

import json

oauth, token = SessionData

# res = oauth.get("https://sh.dataspace.copernicus.eu/configuration/v1/wms/instances")
# print(f"Response: {res.content}")

catalog_url = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/collections/byoc-3c662330-108b-4378-8899-525fd5a225cb"
res = oauth.get(catalog_url)
json_Res = json.loads(res.content)
pp(json_Res)