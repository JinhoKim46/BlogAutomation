from api_notion import Notion
from api_openai import Openai
from api_webflow import Webflow

import utils

# Get config
config = utils.read_config("Z:\Personal\Projects\BlogAutomation\config.json")

# Get openai api
openai = Openai(config['openai'])

# Get notion api
notion_contents = Notion(config['notion'], 'contents')
contents = notion_contents.readDatebase()

notion_categories = Notion(config['notion'], 'categories')
categories = notion_categories.readDatebase()

notion_tags = Notion(config['notion'], 'tags')
tags = notion_tags.readDatebase()

# Get webflow api
webflow_tags = Webflow(config['webflow'], 'tags')
webflow_categories = Webflow(config['webflow'], 'categories')

print("Start blog posts generation!!\n")
for page in contents:
    if not notion_contents.getDone(page):
        title = notion_contents.getTitle(page)
        category = notion_contents.getCategory(page)

        print(f"Blog auto-generation starts for ...\n - Title: {title}\n - Category: {category}")
        print("==============================================")
        # %% Body
        print("Generate the blog body")
        body = openai.run("Body", max_tokens=3800, title=title, category=category)

        # %% Summary
        print("Generate a summary")
        summary = openai.run("Summary", max_tokens=1000, body=body, temperature=0.7)

        # %% Tags
        print("Generate tags")
        tag_names = openai.run("Tags", summary=summary, tags=tags, temperature=0.4)
        tag_ids = utils.get_tag_id(tags, tag_names)

        # %% Main image
        print("Generate an image")
        image = openai.run("Image", title=title, summary=summary, temperature=0.1)

        # %% Thumbnail image
        print("Generate a thumbnail image")
        thumbnail = openai.run("Thumbnail", title=title, temperature=0.1)

        # %% Get category ID
        category_id = utils.get_category_id(categories, category)

        notion_contents.updateProperty(page['id'], "Body", 'text', body)
        notion_contents.updateProperty(page['id'], "Summary", 'text', summary)
        notion_contents.updateProperty(page['id'], "Main image", 'files', ("Image", image))
        notion_contents.updateProperty(page['id'], "Thumbnail", 'files', ("Thumbnail", thumbnail))
        notion_contents.updateProperty(page['id'], "Tags_link", 'relation', tag_ids)
        notion_contents.updateProperty(page['id'], "Category_link", 'relation', category_id)
        notion_contents.updateProperty(page['id'], "Done", 'checkbox', True)

        print("Done!\n\n")

print("Generating blog posts is done!")
print("Start to create tags and categories in Webflow")
for page in tags:
    if not notion_tags.getFeatured(page):
        tag = notion_tags.getName(page)
        print(f" Uploading Tag: {tag} ... ")
        item_id = webflow_tags.createItem(title=tag)
        notion_tags.updateProperty(page['id'], 'Webflow item ID', 'text', item_id)
        notion_tags.updateProperty(page['id'], "Featured", 'checkbox', True)
        print("  Done!\n")

for page in categories:
    if not notion_categories.getFeatured(page):
        category = notion_categories.getName(page)
        print(f" Uploading Tag: {category} ... ")
        item_id = webflow_categories.createItem(title=category)
        notion_categories.updateProperty(page['id'], 'Webflow item ID', 'text', item_id)
        notion_categories.updateProperty(page['id'], "Featured", 'checkbox', True)
        print("  Done!\n")
