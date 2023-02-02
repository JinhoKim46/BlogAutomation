import json

import numpy as np
import requests


class Notion:
    def __init__(self, config):
        self.config = config
        self.token = self.getToken()
        self.contentsID = self.getDatabaseID("contents")
        self.tagID = self.getDatabaseID("tags")
        self.categoryID = self.getDatabaseID("categories")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def readDatabase(self, db_type, save_data=False):
        databaseID = self.contentsID if db_type == "contents" else self.tagID if db_type == 'tags' else self.categoryID
        readUrl = f'https://api.notion.com/v1/databases/{databaseID}/query'

        res = requests.request("POST", readUrl, headers=self.headers).json()

        if len(res['results']) == 100:  # Max load num: 100 => deal with more than 100 pages in the database
            pageID = self.getPageID(res['results'][-1])
            payload = {"start_cursor": pageID}
            res_extra = requests.request("POST", readUrl, json=payload, headers=self.headers).json()
            res['results'].extend(res_extra['results'][1:])

        if save_data:
            with open(f'./{db_type}.json', 'w', encoding='utf8') as f:
                json.dump(res, f, ensure_ascii=False)

        return res['results']

    def getToken(self):
        token = self.config['token']

        return token

    def getDatabaseID(self, db_type):
        databaseID = self.config[f'{db_type}ID']

        return databaseID

    def updateProperty(self, pageID, name, field_type, contents, archived=False):
        updateUrl = f"https://api.notion.com/v1/pages/{pageID}"
        updateData = {
            "properties": {
                name: self.createDataJson(field_type, contents)
            },
            "archived": archived
        }

        data = json.dumps(updateData)
        requests.request("PATCH", updateUrl, headers=self.headers, data=data)

    def createDataJson(self, field_type, contents):
        if field_type == "text":
            updateData = {
                "rich_text": [
                    {
                        "text": {
                            "content": contents[2000 * i:2000 * (i + 1)]  # maximum available request length: 2000
                        }
                    } for i in range(0, np.ceil(len(contents) / 2000).astype(int))
                ]
            }
        elif field_type == "files":
            updateData = {
                'files': [
                    {
                        "name": contents[0],
                        "external": {
                            "url": contents[1]
                        }
                    }
                ]
            }
        elif field_type == "multi_select":
            updateData = {
                "multi_select": [{"name": i} for i in contents]
            }
        elif field_type == "checkbox":
            updateData = {
                "checkbox": contents
            }
        elif field_type == 'relation':
            updateData = {
                'relation': [{"id": i} for i in contents]
            }
        else:
            raise

        return updateData

    @staticmethod
    def getPageID(page):
        return page['id']

    @staticmethod
    def getTitle(page):
        return page['properties']["Title"]['title'][0]['text']['content']

    @staticmethod
    def getName(page):
        return page['properties']["Name"]['title'][0]['text']['content']

    @staticmethod
    def getCategory(page):
        return page['properties']['Category']['select']['name']

    @staticmethod
    def getBody(page):
        body_parts = [i['text']['content'] for i in page['properties']['Body']['rich_text']]
        return ''.join(body_parts)

    @staticmethod
    def getSummary(page):
        return page['properties']['Summary']['rich_text'][0]['text']['content']

    @staticmethod
    def getTags(page):
        return [i['name'] for i in page['properties']['Tags']['multi_select']]

    @staticmethod
    def getMainImage(page):
        return page['properties']['Main image']['files'][0]['external']['url']

    @staticmethod
    def getThumbnail(page):
        return page['properties']['Thumbnail']['files'][0]['external']['url']

    @staticmethod
    def getDone(page):
        return page['properties']['Done']['checkbox']

    @staticmethod
    def getFeatured(page):
        return page['properties']['Featured']['checkbox']

    @staticmethod
    def getCategoryLink(page):
        return page['properties']['Category_link']['relation'][0]['id']

    @staticmethod
    def getTagsLink(page):
        return [i['id'] for i in page['properties']['Tags_link']['relation']]

    @staticmethod
    def get_category_id(categories, category_name):
        for category in categories:
            if category['properties']["Name"]['title'][0]['text']['content'] == category_name:
                return [category['id']]  # since tag_ids are stored in the list!!

    @staticmethod
    def get_tag_id(tags, tag_names):
        tag_ids = []
        for tag_name in tag_names:
            for tag in tags:
                if tag['properties']["Name"]['title'][0]['text']['content'] == tag_name:
                    tag_ids.append(tag['id'])
                    break
        return tag_ids

    @staticmethod
    def get_category_webItemID(categories, category_id):
        for category in categories:
            if category['id'] == category_id:
                return category['properties']['Webflow item ID']['rich_text'][0]['text']['content']

    @staticmethod
    def get_tag_webItemID(tags, tag_ids):
        web_ids = []
        for tag_id in tag_ids:
            for tag in tags:
                if tag['id'] == tag_id:
                    web_ids.append(tag['properties']['Webflow item ID']['rich_text'][0]['text']['content'])

        return web_ids
