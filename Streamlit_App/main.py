import InvokeAgent as agenthelper
import streamlit as st

#to run --> python3 -m streamlit run main.py                                            

st.title("AnyCompany Support Agent :robot_face:")

prompt = st.sidebar.text_area(label="What is your question?", max_chars=2000)

event = {
  "sessionId": "MYSESSION",
  "question": prompt
}

endevent = {
  "sessionId": "MYSESSION",
  "question": "placeholder to end session",
  "endSession": True
}

endsessionprompt = st.sidebar.button("END SESSION", key=None, help=None, on_click=None, args=None, kwargs=None, type="secondary", disabled=False, use_container_width=False)

if prompt:
    response = agenthelper.lambda_handler(event, None)
    st.write("Support AI: ",response['body'])

if endsessionprompt:
    st.write("Thank you for using AnyCompany Support Agent!")
    response = agenthelper.lambda_handler(endevent, None)

    
###Example Prompts
#searchQuery(QUESTON HERE)
#What do you know about flux3000 based on what's in your knowledge base?
#what are some flux3000 features?
#I enrich profiles with third-party data?
#What does Guaranteed Connect do?
#Can you create a feature request named "Support AWS SNS Integration for Guaranteed Connect" from the company named AnyCompanyCustomer14