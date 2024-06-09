from crewai import Agent
from crewai.json_tools import JSONSearchTool  # Updated import path

# General JSON content search
# This approach is suitable when the JSON path is either known beforehand or can be dynamically identified.
tool = JSONSearchTool()

# Restricting search to a specific JSON file
# Use this initialization method when you want to limit the search scope to a specific JSON file.
tool = JSONSearchTool(json_path='../atl_tech_week_events.json')




agent = Agent(
  role='Data Analyst',
  goal='Extract actionable insights',
  backstory="""You're a data analyst at a large company.
  You're responsible for analyzing data and providing insights
  to the business.
  You're currently working on a project to analyze the
  performance of our marketing campaigns.""",
  tools=[tool],  # Optional, defaults to an empty list
  max_iter=15,  # Optional
  max_rpm=None, # Optional
  verbose=True,  # Optional
  allow_delegation=True,  # Optional
  cache=True  # Optional
)