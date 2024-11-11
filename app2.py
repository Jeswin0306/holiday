import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini AI model using the API key
#api_key = os.environ.get("GOOGLE_API_KEY")  # Ensure your .env file has the Google API key
#if api_key is None:
    #st.error("API key for Google Gemini is not set.")
    #st.stop()

genai.configure(api_key="AIzaSyCTCynB5jDa_0dobkAnBDUbrWzPS9jOumk")
model = genai.GenerativeModel("gemini-1.5-flash")  # Set the Gemini model

# Define the message classes
class AIMessage:
    def __init__(self, content):
        self.content = content

class HumanMessage:
    def __init__(self, content):
        self.content = content

# App config
st.set_page_config(page_title="Holiday.AI", page_icon="🌍")
st.title("Holiday.AI 🧳")

# Define the template outside the function
template = """
You are a travel assistant chatbot your name is Yatra Sevak.AI designed to help users plan their trips and provide travel-related information. Here are some scenarios you should be able to handle:

1. Booking Flights: Assist users with booking flights to their desired destinations. Ask for departure city, destination city, travel dates, and any specific preferences (e.g., direct flights, airline preferences). Check available airlines and book the tickets accordingly.
2. Booking Hotels: Help users find and book accommodations. Inquire about city or region, check-in/check-out dates, number of guests, and accommodation preferences (e.g., budget, amenities).
3. Booking Rental Cars: Facilitate the booking of rental cars for travel convenience. Gather details such as pickup/drop-off locations, dates, car preferences (e.g., size, type), and any additional requirements.
4. Destination Information: Provide information about popular travel destinations. Offer insights on attractions, local cuisine, cultural highlights, weather conditions, and best times to visit.
5. Travel Tips: Offer practical travel tips and advice. Topics may include packing essentials, visa requirements, currency exchange, local customs, and safety tips.
6. Weather Updates: Give current weather updates for specific destinations or regions. Include temperature forecasts, precipitation chances, and any weather advisories.
7. Local Attractions: Suggest local attractions and points of interest based on the user's destination. Highlight must-see landmarks, museums, parks, and recreational activities.
8. Customer Service: Address customer service inquiries and provide assistance with travel-related issues. Handle queries about bookings, cancellations, refunds, and general support.

Please ensure responses are informative, accurate, and tailored to the user's queries and preferences. Use natural language to engage users and provide a seamless experience throughout their travel planning journey.

Chat history: {chat_history}
User question: {user_question}
"""

# Function to get a response from the model
def get_response(user_query, chat_history):
    # Prepare the message history for the model
    messages = [
        {"role": "system", "content": "You are a helpful travel assistant named Holiday.AI."}
    ]

    for message in chat_history:
        if isinstance(message, HumanMessage):
            messages.append({"role": "user", "content": message.content})
        elif isinstance(message, AIMessage):
            messages.append({"role": "assistant", "content": message.content})

    messages.append({"role": "user",
                     "content": template.format(chat_history="\n".join([msg['content'] for msg in messages]),
                                                user_question=user_query)})

    try:
        # Get response from Gemini AI model
        response = model.generate_content(messages[-1]["content"])
        print(response)  # For debugging, you can remove this line after checking

        if response:
            return response.text
        else:
            return "No response from Gemini AI."
    
    except Exception as e:
        st.error(f"Error in generating response: {e}")
        return "Error fetching response from Gemini AI. Please try again later."

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am Holiday.AI. How can I help you?")
    ]

# Display chat history
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# User input
user_query = st.chat_input("Type your message here...")
if user_query:
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("Human"):
        st.markdown(user_query)

    response = get_response(user_query, st.session_state.chat_history)
    st.session_state.chat_history.append(AIMessage(content=response))
    with st.chat_message("AI"):
        st.write(response)
