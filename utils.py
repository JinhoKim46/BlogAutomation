import json


def print_response(res, indent=2):
    print(json.dumps(res.json(), indent=indent))


def get_category_id(categories, category_name):
    for category in categories:
        if category['properties']["Name"]['title'][0]['text']['content'] == category_name:
            return [category['id']]  # since tag_ids are stored in the list!!


def get_tag_id(tags, tag_names):
    tag_ids = []
    for tag_name in tag_names:
        for tag in tags:
            if tag['properties']["Name"]['title'][0]['text']['content'] == tag_name:
                tag_ids.append(tag['id'])
                break
    return tag_ids


def get_category_webItemID(categories, category_id):
    for category in categories:
        if category['id'] == category_id:
            return category['properties']['Webflow item ID']['rich_text'][0]['text']['content']


def get_tag_webItemID(tags, tag_ids):
    web_ids = []
    for tag_id in tag_ids:
        for tag in tags:
            if tag['id'] == tag_id:
                web_ids.append(tag['properties']['Webflow item ID']['rich_text'][0]['text']['content'])

    return web_ids


def read_config(path):
    return json.load(open(path))