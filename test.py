import json; story = {"attachments": [{"filename": "test.png", "size": 1000}]}; print(json.dumps(story)); print(story["attachments"][0].get("filename"))
