import requests
import json
from markdown import markdown

class Webflow:
    def __init__(self, config, type="contents"):
        self.config = config
        self.type = type
        self.token = self.getToken()
        self.headers = self.getHeaders()
        self.siteID = self.getSiteId()
        self.domain = self.getDomain()
        self.collectionID = self.getCollectionId()
        self.collection = self.getCollection()
        self.field = self.getField()
        self.cnt = self.getCount()
        self.updated_cnt = 0

    def getInfo(self):
        print(f"This Webflow class is for {self.type}")

    def getToken(self):
        token = self.config['token_webflow']
        return token

    def getHeaders(self):
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.token}"
        }
        return headers

    def getSiteId(self):
        url = "https://api.webflow.com/sites"
        response = requests.get(url, headers=self.headers)
        siteID = response.json()[0]["_id"]

        return siteID

    def getDomain(self):
        domain = self.config['domain']
        return domain

    def getCount(self):
        count = self.config['count']
        return count

    def getSite(self):
        url = f"https://api.webflow.com/sites/{self.siteID}"
        site = requests.request('GET', url, headers=self.headers)

        return site

    def getCollectionId(self):
        url = f"https://api.webflow.com/sites/{self.siteID}/collections"
        collections = requests.request('GET', url, headers=self.headers)

        collections_json = collections.json()
        collections_dict = {i['name']: i['_id'] for i in collections_json}

        cms = f"Blog_{self.type}"
        return collections_dict[cms]

    def getCollection(self):
        url = f"https://api.webflow.com/collections/{self.collectionID}"
        collection = requests.request('GET', url, headers=self.headers)

        return collection

    def getField(self):
        fields = self.collection.json()['fields']
        return {i['name']: i['slug'] for i in fields}

    def getItems(self):
        url = f"https://api.webflow.com/collections/{self.collectionID}/items"
        items = requests.request('GET', url, headers=self.headers)

        return items

    def createItem(self, **kwargs):
        '''
        Create An item in CMS database
        :param collection_id: A collection ID
        :param cms: Target CMS that you craete an item
        :param kwargs: keys()=> {title, [body, summary, image, thumbnail]}
        :return: An ID of the created item
        '''
        url = f"https://api.webflow.com/collections/{self.collectionID}/items"

        data = self.createDataJson(kwargs)

        item = requests.request("POST", url, json=data, headers=self.headers)

        return item.json()['_id']

    def updateItem(self, item_id, field, contents):
        '''
        Update an item in CMS of Webflow
        :param item_id: an ID of the item to be updated
        :param field: A field of the item to be updated
                      Options: [BODY, SUMMARY, IMAGE, THUMBNAIL, TAGS, CATEGORY]
        :param contents:
        :return:
        '''
        url = f"https://api.webflow.com/collections/{self.collectionID}/items/{item_id}"

        if field == self.config["IMAGE"] or field == self.config["THUMBNAIL"]:
            contents = {"url": contents}

        payload = {"fields": {
            f"{self.field[field]}": contents
        }}

        _ = requests.request('PATCH', url, json=payload, headers=self.headers)

    def createDataJson(self, kwargs):
        if self.type == 'contents':
            data = {
                "fields": {
                    "slug": "",
                    "name": f"{kwargs['title']}",
                    "_archived": False,
                    "_draft": False,
                    f"{self.field[self.config['BODY']]}": f"{markdown(kwargs['body'])}",
                    f"{self.field[self.config['SUMMARY']]}": f"{kwargs['summary']}",
                    f"{self.field[self.config['IMAGE']]}": {
                        'url': f"{kwargs['image']}"
                    },
                    f"{self.field[self.config['THUMBNAIL']]}": {
                        'url': f"{kwargs['thumbnail']}"
                    }
                }
            }
        else:  # for tags and categories CMS
            data = {
                "fields": {
                    "slug": "",
                    "name": f"{kwargs['title']}",
                    "_archived": False,
                    "_draft": False
                }
            }
        return data

    def publish(self):
        url = f"https://api.webflow.com/sites/{self.siteID}/publish"
        payload = {"domains": [self.domain]}

        _ = requests.request("POST", url, json=payload, headers=self.headers)

        self.updated_cnt += 1
        if self.updated_cnt == self.cnt:
            return True

        return False
