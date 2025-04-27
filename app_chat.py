import streamlit as st
from streamlit_tags import st_tags
from langchain_core.messages import AIMessage, HumanMessage
from app.chains import instruction_chain, behavioral_chain, technical_chain

st.title("HireBot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "data" not in st.session_state:
    st.session_state.data = {
        'candidate_name': None, 
        'job_title': None, 
        'interview_type': None, 
        'number_of_questions': None
    }

if "instructions" not in st.session_state:
    st.session_state.instructions = ""

roles = {HumanMessage: "user", AIMessage: "assistant"}

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    role = type(message)
    with st.chat_message(roles[role]):
        st.markdown(message.content)


def chat(prompt= None):
    # Append user message to chat history
    if prompt:
        st.session_state.messages.append(HumanMessage(content=prompt))
    else:
        prompt = "Hello"
    
    history = st.session_state.messages
    
    if not history:
        history = [HumanMessage("Hello")]
    
    if st.session_state.data['interview_type'] == "Technical":
        response = technical_chain.invoke({
            "candidate_name": st.session_state.data['candidate_name'],
            "job_title": st.session_state.data['job_title'],
            "number_of_questions": st.session_state.data['number_of_questions'],
            "skills": st.session_state.data['skills'],
            "instructions": st.session_state.instructions,
            "chat_history": history,
        })

    elif st.session_state.data['interview_type'] == "Behavioral":
        response = behavioral_chain.invoke({
            "candidate_name": st.session_state.data['candidate_name'],
            "job_title": st.session_state.data['job_title'],
            "number_of_questions": st.session_state.data['number_of_questions'],
            "skills": st.session_state.data['skills'],
            "instructions": st.session_state.instructions,
            "chat_history": history,
        })
    
    # Append AI response to chat history
    st.session_state.messages.append(AIMessage(content=response))
    
    # Rerun the app to display the new messages
    st.rerun()

# Sidebar for user input
with st.sidebar: # Initialize Side Bar Items
    st.title("Side Panel")
    
    # Collect user input
    name = st.text_input("Candidate Name")
    job_title = st.text_input("Job Title")
    interview_type = st.selectbox("Interview Type", ["Behavioral", "Technical"])
    number_of_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=5)
    skills = st_tags()
    
    # Store user input in session state
    st.session_state.data['candidate_name'] = name
    st.session_state.data['job_title'] = job_title
    st.session_state.data['interview_type'] = interview_type
    st.session_state.data['number_of_questions'] = number_of_questions
    st.session_state.data['skills'] = skills
    
    # Button to start a new interview
    generate = st.button("Start New Interview")


if generate:
    # Empty chat history 
    st.session_state.messages =  []
    
    # Generate instructions
    st.session_state.instructions= instruction_chain.invoke({
                                "candidate_name": st.session_state.data['candidate_name'],
                                "job_title": st.session_state.data['job_title'],
                                "number_of_questions": st.session_state.data['number_of_questions'],
                                "skills": st.session_state.data['skills'],
                                'interview_type': st.session_state.data['interview_type'],
                                })
    
    # Start New Chat
    chat()

prompt = st.chat_input("Chat with HireBot")

if st.session_state.instructions and prompt:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Proceed in chat
    chat(prompt)