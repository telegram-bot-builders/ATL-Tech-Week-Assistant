from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from telegram import Bot
from dotenv import load_dotenv
import pprint, os
# from crewai.json_tools import JSONSearchTool  # Updated import path

# # General JSON content search
# # This approach is suitable when the JSON path is either known beforehand or can be dynamically identified.
# tool = JSONSearchTool()

# # Restricting search to a specific JSON file
# # Use this initialization method when you want to limit the search scope to a specific JSON file.
# tool = JSONSearchTool(json_path='../atl_tech_week_events.json')
load_dotenv()
TOKEN = os.getenv('TELEGRAM_API_KEY')



async def send_msg_to_telegram(msg, chat_id):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=chat_id, text=msg, parse_mode="MarkdownV2")


@tool("get_response")
def get_response(question):
  """The mechanism to get the user's response. Takes in a question and returns the user's response."""
  print(question)
  value = input("Enter your response: ")
  return value

def on_boarding_callback(step_output):
  
  for step in step_output:
    print(step)
    

conversational_agent = Agent(
    role='Atlanta Tech Week Sign Up Assistant',
    goal='Engage in a friendly conversation to gather attendee preferences for Atlanta Tech Week 2024.',
    memory=True,
    backstory=(
        "You are a friendly assistant for Atlanta Tech Week 2024. Your goal is to learn about attendees' preferences "
        "to help create a unique schedule for them among the many events happening during the week."
        "You need to ask them about their interests, availability, and preferred event types to make the best recommendations."
        "You are smooth in your conversation. Almost make them want to tell you a story. You make them speak more than you do."
        "Your goal is to keep being as engaging as possible as you gather information to help them have a great experience."
        "You are here to make them feel welcome and excited about the upcoming events."
        "It is pertentinet that you gather the following information: Interests, Availability, Preferred Event Types, Outcomes"
        """
        You will output a json object with the following structure:
        {
            "interests": ["Technology", "Business"],
            "availability": ["Monday", "Wednesday"],
            "preferred_event_types": ["Workshops", "Networking"],
            "outcomes": ["Meet new people", "Learn about new technologies"]
        }
        """
    ),
    tools=[],
    allow_delegation=False,
    # step_callback=on_boarding_callback
)


on_boarding_task= Task(
    description="Begin the onboarding process for Atlanta Tech Week 2024 attendees. Start with an engaging opener that automatically makes the user feel welcome and excited about the upcoming events. Say something smooth that makes them open up. You will use get the user responses to your questions by using the get_response(question) function, where the question is what you need the user to respond to.",
    expected_output='A json response of the parsed answers from the user.',
    tools=[get_response],
    agent=conversational_agent,
)

on_boarding_crew = Crew(
    agents=[conversational_agent],
    tasks=[on_boarding_task],
    process=Process.sequential,  # Sequential task execution
)


# result = on_boarding_crew.kickoff()
# pprint.pprint(result)