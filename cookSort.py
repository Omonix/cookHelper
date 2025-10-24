import cohere, os, dotenv

dotenv.load_dotenv()
AI_KEY = os.getenv('AI_KEY')

co = cohere.Client(AI_KEY)
#print(co.chat(message='Quel jour sommes nous').text)
