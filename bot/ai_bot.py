import logging
import os
from collections import defaultdict

from decouple import config

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

os.environ['GROQ_API_KEY'] = config('GROQ_API_KEY')

logger = logging.getLogger(__name__)

MAX_HISTORY = 10


class AIBot:
    def __init__(self):
        self.__chat = ChatGroq(model='llama-3.3-70b-versatile')
        self.__memory = defaultdict(list)
        self.__retriever = None
        self._init_retriever()

    def _init_retriever(self):
        try:
            from langchain_chroma import Chroma
            from langchain_huggingface import HuggingFaceEmbeddings

            persist_directory = '/app/chroma_data'
            embedding = HuggingFaceEmbeddings()
            vector_store = Chroma(
                embedding_function=embedding,
                persist_directory=persist_directory,
            )
            self.__retriever = vector_store.as_retriever(search_kwargs={'k': 3})
            logger.info('Retriever RAG inicializado com sucesso')
        except Exception as e:
            logger.warning('RAG não disponível, operando sem contexto: %s', e)

    def _get_context(self, question):
        if not self.__retriever:
            return ''
        try:
            docs = self.__retriever.invoke(question)
            return '\n'.join(d.page_content for d in docs)
        except Exception as e:
            logger.warning('Erro ao buscar contexto RAG: %s', e)
            return ''

    def _build_history(self, chat_id):
        history = self.__memory.get(chat_id, [])
        if not history:
            return ''
        lines = []
        for role, text in history[-MAX_HISTORY:]:
            prefix = 'Cliente' if role == 'user' else 'Assistente'
            lines.append(f'{prefix}: {text}')
        return '\n'.join(lines)

    def invoke(self, question, chat_id='default'):
        context = self._get_context(question)
        history = self._build_history(chat_id)

        template = '''Você é um assistente virtual da TechBridge Innovation, uma empresa que oferece serviços de desenvolvimento de aplicações web, automação de processos e assistentes virtuais com inteligência artificial. Responda sempre de forma educada, humanizada e com o português do Brasil. Priorize mensagens breves e claras, adaptando o tom para criar uma interação acolhedora e profissional. Não se apresente repetidamente para o mesmo contato.

{context}

Histórico da conversa:
{history}

Cliente: {question}
Assistente:'''

        prompt = PromptTemplate(
            input_variables=['context', 'history', 'question'],
            template=template,
        )
        chain = prompt | self.__chat | StrOutputParser()
        response = chain.invoke({
            'context': f'Contexto relevante:\n{context}' if context else '(sem contexto adicional)',
            'history': history or '(início da conversa)',
            'question': question,
        })

        self.__memory[chat_id].append(('user', question))
        self.__memory[chat_id].append(('assistant', response))
        if len(self.__memory[chat_id]) > MAX_HISTORY * 2:
            self.__memory[chat_id] = self.__memory[chat_id][-MAX_HISTORY * 2:]

        return response