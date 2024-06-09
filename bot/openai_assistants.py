from openai import OpenAI
import os, json
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)


# Get Scheduling Assistant
def get_scheduling_assistant():
    assistant = client.beta.assistants.retrieve("asst_335DCSiN4q59OM2OYIDOXbHH")
    return assistant

# create ATL Tech Week Schedule for attendees
def create_atl_tech_week_schedule(data):
    scheduling_assistant = get_scheduling_assistant()
    # create a thread
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="assistant",
        content=f"Create a schedule for an attendee of Atlanta Tech Week 2024. The attendee is has the following data about themselves. They really need your assistance to tailor this schedule to their needs.:\n\n{data}",
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=scheduling_assistant.id,
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        return messages.data[0].content[0].text.value
    else:
        print(run.status)
        return None
    

# Create Sign Up Assistant
def create_sign_up_assistant():
    my_assistant = client.beta.assistants.create(
        instructions=(
            "You are a friendly assistant for Atlanta Tech Week 2024. Your goal is to learn about attendees' preferences "
            "to help create a unique schedule for them among the many events happening during the week."
            "You need to ask them about their interests, availability, and preferred event types to make the best recommendations."
            "You are smooth in your conversation. Almost make them want to tell you a story. You make them speak more than you do."
            "Your goal is to keep being as engaging as possible as you gather information to help them have a great experience."
            "You are here to make them feel welcome and excited about the upcoming events."
            "It is pertentinet that you gather the following information: Interests, Availability, Preferred Event Types, Outcomes"
            """
           When you believe you have gathered enough info, ask the user if the information is correct and if they would like to continue.
           You should tell them that if they like it, then use the /end_onboarding command to end the onboarding process.
           Keep asking questions and engaging until you get all of the answers you needs.
            """
        ),
        name="Atlanta Tech Week Sign Up Assistant",
        tools=[{"type": "code_interpreter"}],
        model="gpt-4o",
    )
    return my_assistant

# get assistant
def get_sign_up_assistant():
    my_assistant = client.beta.assistants.retrieve("asst_qlAeOl4anjCujklp78k2OfLQ")
    return my_assistant

# send initial onboarding message
def send_initial_onboarding_message():
    onboarding_thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        onboarding_thread.id,
        role="assistant",
        content="Engage the user into a conversation to gather information about their interests, availability, and preferred event types for Atlanta Tech Week 2024. Make sure that when you believe you have everything, you ask the user if the information is correct and if they would like to continue. If they are happy with the information, tell them to use the /end_onboarding command to end the onboarding process. Keep asking questions and engaging until you get all of the answers you need. Do not show the user any JSON data. Just show them what we have in a nice format with a message that says 'Here is what I have so far. If you are happy with this, type /end_onboarding to end the onboarding process.'",
    )

    sign_up_assistant = get_sign_up_assistant()


    run = client.beta.threads.runs.create_and_poll(
        thread_id=onboarding_thread.id,
        assistant_id=sign_up_assistant.id,
    )

    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=onboarding_thread.id
        )
        return messages.data[0].content[0].text.value, onboarding_thread.id
    else:
        print(run.status)
        return None

# run onboarding assistant
def send_follow_up_onboarding_message(thread_id, message):

    onboarding_thread = client.beta.threads.retrieve(thread_id)


    sign_up_assistant = get_sign_up_assistant()

    message = client.beta.threads.messages.create(
        onboarding_thread.id,
        role="assistant",
        content=message,
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=onboarding_thread.id,
        assistant_id=sign_up_assistant.id,
    )

    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=onboarding_thread.id
        )
        return messages.data[0].content[0].text.value
    else:
        print(run.status)
        return None

# get the last message from the thread
def get_json_data_from_last_onboarding_message(thread_id):
    onboarding_thread = client.beta.threads.retrieve(thread_id)
    messages = client.beta.threads.messages.list(
        thread_id=onboarding_thread.id
    )
    message = messages.data[-1].content[0].text.value

    message = client.beta.threads.messages.create(
        onboarding_thread.id,
        role="assistant",
        content=f"Give me the JSON data from this last message. DO NOT WRITE ANYTHING OTHER THAN JSON.JUST STRING JSON):/n{message}\n\n\nKeys to remember: interests, availability, preferred_event_types, outcomes and they all should be arrays.",
    )
    sign_up_assistant = get_sign_up_assistant()

    run = client.beta.threads.runs.create_and_poll(
        thread_id=onboarding_thread.id,
        assistant_id=sign_up_assistant.id,
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=onboarding_thread.id
        )
        string_data = messages.data[0].content[0].text.value
        print(string_data)
        return json.loads(string_data)
    else:
        print(run.status)
        return None



def get_json_data_of_last_message(thread_id, message):
    pass


if __name__ == '__main__':
    # run_onboarding_assistant()
    pass