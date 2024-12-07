from RPi import GPIO
from ollama import generate
import json

LED_ONE = 14
LED_TWO = 15
LED_THREE = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_ONE, GPIO.OUT)
GPIO.setup(LED_TWO, GPIO.OUT)
GPIO.setup(LED_THREE, GPIO.OUT)

GPIO.output(LED_ONE, GPIO.LOW)
GPIO.output(LED_TWO, GPIO.LOW)
GPIO.output(LED_THREE, GPIO.LOW)


def control_led(bulb_number: str, bulb_state: str):
    LED_GPIO = 0
    if bulb_number == "one":
        LED_GPIO = LED_ONE
    elif bulb_number == "two":
        LED_GPIO = LED_TWO
    elif bulb_number == "three":
        LED_GPIO = LED_THREE
    elif bulb_number == "all":
        if bulb_state == "on":
            GPIO.output(LED_ONE, GPIO.HIGH)
            GPIO.output(LED_TWO, GPIO.HIGH)
            GPIO.output(LED_THREE, GPIO.HIGH)
            return
        elif bulb_state == "off":
            GPIO.output(LED_ONE, GPIO.LOW)
            GPIO.output(LED_TWO, GPIO.LOW)
            GPIO.output(LED_THREE, GPIO.LOW)
            return
        else:
            print("Invalid bulb state")
            return
    else:
        print("Invalid bulb number")
        return

    if bulb_state == "on":
        GPIO.output(LED_GPIO, GPIO.HIGH)
    elif bulb_state == "off":
        GPIO.output(LED_GPIO, GPIO.LOW)
    else:
        print("Invalid bulb state")
        return


LLM_CONTEXT = """\
You are a home automation assistant. You are responsible for controlling the lights in a room. \
You are suposed to extract the user prompt and generate a command to control the lights. \
You are supposed to extract the bulb number and the state of the bulb from the user prompt. \
The bulb number can be "one", "two", "three" or "all" if the user means to select all bulbs. \
The state of the bulb(s) can be "on" or "off". You should not reply with just "on" or "off". \
You should return the response in the form a dictionary with the keys bulb_number and bulb_state. \
When a user prompts with room number, the room number simply means that they are refering to the bulb. \
For example, if the user says "turn on the light in room one", you should interpret that as "turn on bulb one". \
If the user says "only room two should be on", you should interpret that as "turn on bulb two" and so on. \
If the user says "good night", you should interpret that as "turn off all bulbs", "good morning" should interpret as "turn on all bulbs". \
If the user says "turn off the lights", you should interpret that as "turn off all bulbs". \
The command like "shutdown" should interpret as "turn off all bulbs". \
The command like "turn on the lights" should interpret as "turn on all bulbs". \
The worl "light" should be interpreted as "bulb". \
The word "room" and "bulb" should be interpreted as the same thing. Their plural forms should also be interpreted as the same thing. \
You should use the last command executed to generate the next command if the user intend to reverse the last action. \
For example, if the user said "turn on bulb one", then the user says "turn it off", you should interpret that as "turn off bulb one" and so on. \
But some commands that naturally sound like a reversal of the last command should be interpreted as a reversal of the last command. \
Also, the commands that naturally implies to turn on all bulbs should be interpreted as turning on all bulbs and so on. \
You should also be able to handle pluralization, "it" should refer to one bulb, "them" should refer to all bulbs. \
If you don't understand the user prompt, you should reply with "I don't understand". \
\n\n
"""

llm_history = ""


# Ollama interaction (pseudocode)
while True:
    prompt = input("Enter your command: ")
    command = generate(model="gemma2:2b", prompt=LLM_CONTEXT + llm_history + prompt)
    """
    ```json
    {"bulb_number": "one", "bulb_state": "on"}
    ```
    """
    formatted_response = (
        command.response.strip()
        .replace("\n", "")
        .replace("```json", "")
        .replace("```", "")
    )
    print(f"Formatted response: {formatted_response}")
    try:
        command_new = json.loads(formatted_response)

        control_led(command_new["bulb_number"], command_new["bulb_state"])
        llm_history = f"\n\nCommand executed: {command_new['bulb_number']} {command_new['bulb_state']}\n"
        print(f"\n\nHistory: {llm_history}")
    except json.JSONDecodeError as e:
        print("Invalid response")
    print(
        f"Response:{command.response},\n{formatted_response}\n\
            Command executed: {command_new['bulb_number']} {command_new['bulb_state']}\n"
    )
