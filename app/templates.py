from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from . import messages

instructions_template = ChatPromptTemplate.from_messages(
    [
        ("system", messages.instructions_system_message),
        ("human", messages.instructions_human_message)
    ]
)

behavioral_template = ChatPromptTemplate.from_messages(
    [
        ("system", messages.behavioral_system_message),
        MessagesPlaceholder("chat_history"),
    ]
)

technical_template = ChatPromptTemplate.from_messages(
    [
        ("system", messages.technical_system_message),
        MessagesPlaceholder("chat_history"),
    ]
)