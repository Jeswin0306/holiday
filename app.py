import os
import requests
import streamlit as st
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variables
class AIMessage:
    def __init__(self, content):
        self.content = content

# Define the message classes
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
    # Prepare the message history for OpenAI
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
    
    # Initialize the OpenAI API
    api_key = os.environ.get("OPENAI_API_KEY")
    print("API Key Loaded:", api_key)  # For debugging, remove after checking
    if api_key is None:
        st.error("API key for OpenAI is not set.")
        return "API key is missing. Please check the .env file."

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": "gpt-3.5-turbo-0125",
                "messages": messages,
                "temperature": 0,
                "max_tokens": 4095,
            }
        )
        print("OpenAI response:", response.json())


        # Check if the response was successful
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("choices"):
                return response_data["choices"][0]["message"]["content"]
            else:
                return "No response from OpenAI."
        else:
            # Show error message in Streamlit for non-200 responses
            st.error(f"OpenAI API error {response.status_code}: {response.text}")
            return "Error fetching response from OpenAI. Please try again later."
    
    except requests.exceptions.RequestException as e:
        st.error("Failed to connect to OpenAI API. Please check your network connection.")
        return "Network error. Unable to connect to OpenAI."

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
