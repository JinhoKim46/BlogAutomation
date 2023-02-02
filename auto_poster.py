import utils
from api_notion import Notion
from api_webflow import Webflow

config = utils.read_config("Z:\Personal\Projects\BlogAutomation\config.json")

notion = Notion(config['notion'])
contents = notion.readDatebase(db='contents')
categories = notion.readDatebase(db='categories')
tags = notion.readDatebase(db='tags')

webflow_contents = Webflow(config['webflow'], 'contents')
webflow_tags = Webflow(config['webflow'], 'tags')
webflow_categories = Webflow(config['webflow'], 'categories')

for page in contents:
    if not notion.getFeatured(page):
        title = notion.getTitle(page)
        category = notion.getCategory(page)
        body = notion.getBody(page)
        summary = notion.getSummary(page)
        image = notion.getMainImage(page)
        thumbnail = notion.getThumbnail(page)

        print(f" - Posting '{title}' ...")
        item_id = webflow_contents.createItem(title=title,
                                              body=body,
                                              summary=summary,
                                              image=image,
                                              thumbnail=thumbnail)
        #
        category_id = notion.getCategoryLink(page)
        category_web_id = utils.get_category_webItemID(categories=categories, category_id=category_id)
        webflow_contents.updateItem(item_id=item_id, field='Category', contents=category_web_id)

        tag_ids = notion.getTagsLink(page)
        tag_web_id = utils.get_tag_webItemID(tags=tags, tag_ids=tag_ids)
        webflow_contents.updateItem(item_id=item_id, field='Tags', contents=tag_web_id)

        notion.updateProperty(page['id'], "Featured", 'checkbox', True)
        isStop = webflow_contents.publish()
        print(f"   Done!\n")

        if isStop:
            break
else:
    _ = webflow_contents.publish()
