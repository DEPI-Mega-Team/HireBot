from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda

from . import utils, templates
from .models import GeminiModel

model = GeminiModel()
chatbot = model.model


instruction_chain = templates.instructions_template | chatbot | StrOutputParser() | RunnableLambda(utils.clear_markdown)

behavioral_chain = templates.behavioral_template | chatbot | StrOutputParser()
technical_chain = templates.technical_template | chatbot | StrOutputParser()

interview_chains = {
    "behavioral": behavioral_chain,
    "technical": technical_chain
}