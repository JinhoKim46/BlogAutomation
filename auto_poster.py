import utils
from api_notion import Notion
from api_webflow import Webflow

# Get config
config = utils.read_config("Z:\Personal\Projects\BlogAutomation\config.json")

# Get notion api
notion_contents = Notion(config['notion'], 'contents')
contents = notion_contents.readDatebase()

notion_categories = Notion(config['notion'], 'categories')
categories = notion_categories.readDatebase()

notion_tags = Notion(config['notion'], 'tags')
tags = notion_tags.readDatebase()

# Get webflow api
webflow_contents = Webflow(config['webflow'], 'contents')

print("Start to upload blog posts!!")
for page in contents:
    if not notion_contents.getFeatured(page):
        title = notion_contents.getTitle(page)
        category = notion_contents.getCategory(page)
        body = notion_contents.getBody(page)
        summary = notion_contents.getSummary(page)
        image = notion_contents.getMainImage(page)
        thumbnail = notion_contents.getThumbnail(page)

        print(f" - Posting '{title}' ...")
        item_id = webflow_contents.createItem(title=title,
                                              body=body,
                                              summary=summary,
                                              image=image,
                                              thumbnail=thumbnail)
        #
        category_id = notion_categories.getCategoryLink(page)
        category_web_id = utils.get_category_webItemID(categories=categories, category_id=category_id)
        webflow_contents.updateItem(item_id=item_id, field='Category', contents=category_web_id)

        tag_ids = notion_tags.getTagsLink(page)
        tag_web_id = utils.get_tag_webItemID(tags=tags, tag_ids=tag_ids)
        webflow_contents.updateItem(item_id=item_id, field='Tags', contents=tag_web_id)

        notion_contents.updateProperty(page['id'], "Featured", 'checkbox', True)
        isStop = webflow_contents.publish()
        print(f"   Done!\n")

        if isStop:
            break
else:
    _ = webflow_contents.publish()
