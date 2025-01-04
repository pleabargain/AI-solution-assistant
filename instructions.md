instruction

in python
using ollama

each function should be a separate python script to be called by the main script
each function should be logged to catch errors and exceptions

ask user for the large language model they would like to use : ollama list
default ollama 3.2:latest
create a python script that will use the large language model to create a json schema for the decision making process

each interation will of the json file will be date and time stamped yyyy.mm.dd.hh.mm.ss
create a json file 
track the large language model used in the json file
ask user for decision to make

ask user to list pros
ask user to list cons

track the pros and cons in the json file

ask user to estimate the likelihood of each pro and con

track the likelihood of each pro and con in the json file

ask user to estimate the impact of each pro and con

track the impact of each pro and con in the json file

ask user to estimate the cost of each pro and con

track the cost of each pro and con in the json file

ask user if they would like an AI to assist them each step of the way

if yes, take user input and use it to create a prompt for the AI

track the prompt in the json file
if the user likes the result, ask them if they would like to save the result
If yes, save the result to the json file and indicate that the result has been saved to the json file and that it was AI generated

if no, thank the user for their time and exit the program

# File Management and Exit Behavior
- After saving any decision data to a JSON file, notify the user that their file has been saved
- Before exiting the program, display a thank you message to the user
