import json

import numpy as np
import requests


class Notion:
    def __init__(self, config):
        self.config = config
        self.token = self.getToken()
        self.contentsID = self.getDatabaseID('contents')
        self.TagsID = self.getDatabaseID('tags')
        self.CategoryID = self.getDatabaseID('category')
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def readDatebase(self, db='contents', save_data=False):
        databaseID = self.contentsID if db == 'contents' else self.TagsID if db == 'tags' else self.CategoryID
        readUrl = f'https://api.notion.com/v1/databases/{databaseID}/query'

        res = requests.request("POST", readUrl, headers=self.headers).json()

        if len(res['results']) == 100:  # Max load num: 100 => deal with more than 100 pages in the database
            pageID = self.getPageID(res['results'][-1])
            payload = {"start_cursor": pageID}
            res_extra = requests.request("POST", readUrl, json=payload, headers=self.headers).json()
            res['results'].extend(res_extra['results'][1:])

        if save_data:
            with open(f'./{db}.json', 'w', encoding='utf8') as f:
                json.dump(res, f, ensure_ascii=False)

        return res['results']

    def getToken(self):
        token = self.config['token_notion']

        return token

    def getDatabaseID(self, db='contents'):
        databaseID = self.config[f'{db}ID']

        return databaseID

    def getPageID(self, page):
        return page['id']

    def getTitle(self, page):
        return page['properties']["Title"]['title'][0]['text']['content']

    def getName(self, page):
        return page['properties']["Name"]['title'][0]['text']['content']

    def getCategory(self, page):
        return page['properties']['Category']['select']['name']

    def getBody(self, page):
        body_parts = [i['text']['content'] for i in page['properties']['Body']['rich_text']]
        return ''.join(body_parts)

    def getSummary(self, page):
        return page['properties']['Summary']['rich_text'][0]['text']['content']

    def getTags(self, page):
        return [i['name'] for i in page['properties']['Tags']['multi_select']]

    def getMainImage(self, page):
        return page['properties']['Main image']['files'][0]['external']['url']

    def getThumbnail(self, page):
        return page['properties']['Thumbnail']['files'][0]['external']['url']

    def getDone(self, page):
        return page['properties']['Done']['checkbox']

    def getFeatured(self, page):
        return page['properties']['Featured']['checkbox']

    def getCategoryLink(self, page):
        return page['properties']['Category_link']['relation'][0]['id']

    def getTagsLink(self, page):
        return [i['id'] for i in page['properties']['Tags_link']['relation']]

    def updateProperty(self, pageID, name, type, contents, archived=False):
        updateUrl = f"https://api.notion.com/v1/pages/{pageID}"
        updateData = {
            "properties": {
                name: self.createDataJson(type, contents)
            },
            "archived": archived
        }

        data = json.dumps(updateData)
        requests.request("PATCH", updateUrl, headers=self.headers, data=data)

    def createDataJson(self, name, contents):
        if name == "text":
            updateData = {
                "rich_text": [
                    {
                        "text": {
                            "content": contents[2000 * i:2000 * (i + 1)]  # maximum available request length: 2000
                        }
                    } for i in range(0, np.ceil(len(contents) / 2000).astype(int))
                ]
            }
        elif name == "files":
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
        elif name == "multi_select":
            updateData = {
                "multi_select": [{"name": i} for i in contents]
            }
        elif name == "checkbox":
            updateData = {
                "checkbox": contents
            }
        elif name == 'relation':
            updateData = {
                'relation': [{"id": i} for i in contents]
            }

        return updateData
