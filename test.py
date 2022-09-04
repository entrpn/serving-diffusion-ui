import base64
import json

# retval = []
# retval.append(base64.b64encode('foo'))
# retval.append(base64.b64encode(u'fee'))
# print(retval)
with open('/Users/jfacevedo/Downloads/response.json') as json_file:
    data = json.load(json_file)
    images = data.get('predictions',None)[0]
    for i in range(len(images)):
        with open(f"imageToSave-{i}.png", "wb") as fh:
            fh.write(base64.b64decode(images[i]))