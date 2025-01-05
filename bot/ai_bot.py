import os

from decouple import config

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

os.environ['GROQ_API_KEY'] = config('GROQ_API_KEY')


class AIBot:
    def __init__(self):
        self.__chat = ChatGroq(model='llama-3.3-70b-versatile')

    def invoke(self, question):
        prompt = PromptTemplate(
            input_variables=['texto'],
            template='''
                Você é um assistente virtual da TechBridge Innovation, 
                uma empresa que oferece serviços de desenvolvimento de aplicações web, 
                automação de processos e assistentes virtuais com inteligência artificial. 
                Responda sempre de forma educada, humanizada e com o português do Brasil.
                Priorize mensagens breves e claras, adaptando o tom para criar uma interação acolhedora e profissional. 
                Se for o mesmo contato, 
                não se apresente repetidamente e mantenha a continuidade da conversa com naturalidade.
            <texto>
            {texto}
            </texto>
            '''
        ) 
        chain = prompt | self.__chat | StrOutputParser()
        response = chain.invoke({
            'texto': question,
        })
        return response