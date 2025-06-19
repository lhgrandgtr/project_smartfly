from groq import Groq
import src.utils.configs as c
from google import genai


class Model:
    def __init__(self, *, platform: str="google", model_id: str="gemini-2.0-flash"):
        self.platform = platform
        self.model = None
        self.model_id = model_id
        self.get_model()
    
    def get_model(self):
        if self.platform == "google":
            self.model = genai.Client(api_key=c.GOOGLE_API_KEY)
        elif self.platform == "groq":
            self.model = Groq(
                api_key=c.GROQ_API_KEY,
            )
        else:
            raise ValueError("Unsupported platform. Please use 'google' or 'groq'.")
    
    def invoke(self, promp):
        frame = c.FRAME_PATH
        if self.platform == "google":
            self.model.files.upload(file=frame)
            response = self.model.models.generate_content(
                model="gemini-2.0-flash",
                contents=[frame, "Caption this image."],
            )
            return response.text
        
        elif self.platform == "groq":
            response = self.model.chat.completions.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "what is this?"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": frame
                                }
                            }
                        ]
                    }
                ],
                temperature=0,
                max_tokens=1024,
                top_p=1,
                stream=False,
            )
            return response.choices[0].message.content
        

if __name__ == "__main__":
    model = Model(platform='groq', model_id='meta-llama/llama-4-scout-17b-16e-instruct')
    response = model.invoke("What is machine learning?")
    print(response)