import openai

class Openai:
    def __init__(self, config):
        self.config = config
        openai.api_key = self.getToken()
        self.model = 'text-davinci-003'

    def getToken(self):
        token = self.config['token']
        return token

    def run(self, target, max_tokens=256, temperature=0.8, prompt=None, **kwargs):
        if prompt is None:
            getPrompt = getattr(Openai, f"getPrompt{target}")
            prompt = getPrompt(self, **kwargs)

        output = openai.Completion.create(prompt=prompt, model=self.model, max_tokens=max_tokens,
                                          temperature=temperature).choices[0].text

        # Remove \n in front of the string
        temp = output[:4]
        cnt = sum("\n" == i for i in temp)

        output = output[cnt:]
        if target == "Tags":
            return output.split(', ')

        if target == "Image" or target == "Thumbnail":
            return 'https' + output.split("https")[-1].replace(" ", "")

        return output

    def getPromptBody(self, title, category):
        prompt_body = f''' 
            Write a blog post about "{title}." Its category is {category}. 
            Write a blog article of around 2000 words in the markdown format, and include subtitles and detailed descriptions, but do not include the main title.
            '''
        return prompt_body

    def getPromptSummary(self, body):
        prompt_summary = f"""
        First, read the blog post below.
        {body}
        
        Then, generate a summary of the article in one sentence within 20 words.        
            """
        return prompt_summary

    def getPromptTags(self, summary, tags):
        tag_names = [i['properties']["Name"]['title'][0]['text']['content'] for i in tags]
        prompt_tags = f"""
        First, read the blog below.
        {summary}
        
        Then, choose 3 best tags from the list [{tag_names}]. 
        You must choose tags only in the given list.        
        
        Return your choices with a comma separation. 
            """
        return prompt_tags

    def getPromptImage(self, title, summary):
        prompt_image = f"""
        Read the tile of the blog, "{title}" and its summary, "{summary}" first.
        
        [INFO: Use the Unsplash API (https://source.unsplash.com/1600x900/?<PUT YOUR QUERY HERE>). 
        The query is tags that describe the title and the summary very well. 
        Each tag consists of only one word.
        Reorder the query in descending order in terms of importance.
        Write the final image URL.] ## DO NOT RESPOND TO INFO BLOCK ##
            """
        return prompt_image

    def getPromptThumbnail(self, title):
        prompt_image = f"""
        This is a blog title, "{title}."

        [INFO: Use the Unsplash API (https://source.unsplash.com/1600x900/?<PUT YOUR QUERY HERE>). 
        The query is tags that describe the aforementioned title very well. 
        Each tag consists of only one word.
        Reorder the query in descending order in terms of importance related to the title.
        Write the final image URL.] ## DO NOT RESPOND TO INFO BLOCK ##
            """
        return prompt_image
