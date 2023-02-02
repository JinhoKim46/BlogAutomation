from api_notion import Notion
from api_webflow import Webflow
import json

# Get config
config = json.load(open("Z:\Personal\Projects\BlogAutomation\config.json"))

# Get notion api
notion = Notion(config['notion'])

contents = notion.readDatabase('contents')
categories = notion.readDatabase('categories')
tags = notion.readDatabase('tags')

# Get webflow api
webflow_contents = Webflow(config['webflow'], 'contents')

print("Start to upload blog posts!!")
for page in contents:
    if not Notion.getFeatured(page):
        title = Notion.getTitle(page)
        category = Notion.getCategory(page)
        body = Notion.getBody(page)
        summary = Notion.getSummary(page)
        image = Notion.getMainImage(page)
        thumbnail = Notion.getThumbnail(page)

        print(f" - Posting '{title}' ...")
        item_id = webflow_contents.createItem(title=title,
                                              body=body,
                                              summary=summary,
                                              image=image,
                                              thumbnail=thumbnail)
        #
        category_id = Notion.getCategoryLink(page)
        category_web_id = Notion.get_category_webItemID(categories=categories, category_id=category_id)
        webflow_contents.updateItem(item_id=item_id, field='Category', contents=category_web_id)

        tag_ids = Notion.getTagsLink(page)
        tag_web_id = Notion.get_tag_webItemID(tags=tags, tag_ids=tag_ids)
        webflow_contents.updateItem(item_id=item_id, field='Tags', contents=tag_web_id)

        isStop = webflow_contents.publish()
        notion.updateProperty(page['id'], "Featured", 'checkbox', True)
        print(f"   Done!\n")

        if isStop:
            break
else:
    _ = webflow_contents.publish()
