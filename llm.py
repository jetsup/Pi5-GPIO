from RPi import GPIO
from langchain_ollama import OllamaLLM
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


def control_led(bulbs: list[str], bulb_states: list[str]):
    for bulb, state in zip(bulbs, bulb_states):
        LED_GPIO = 0
        if bulb == "one":
            LED_GPIO = LED_ONE
        elif bulb == "two":
            LED_GPIO = LED_TWO
        elif bulb == "three":
            LED_GPIO = LED_THREE
        elif bulb == "all":
            if state == "on":
                GPIO.output(LED_ONE, GPIO.HIGH)
                GPIO.output(LED_TWO, GPIO.HIGH)
                GPIO.output(LED_THREE, GPIO.HIGH)
                return
            elif state == "off":
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

        if state == "on":
            GPIO.output(LED_GPIO, GPIO.HIGH)
        elif state == "off":
            GPIO.output(LED_GPIO, GPIO.LOW)
        else:
            print("Invalid bulb state")
            return


LLM_CONTEXT = """\
You are a home automation assistant. You are responsible for controlling the lights in a room. \
There are three bulbs in the room. You are supposed to extract the user prompt and generate a command to control the lights. \
You are supposed to extract the bulb number and the state of the bulb from the user prompt. \
Your response should be a JSON object with the keys "bulbs" and "bulb_states". \
The bulb number can be "one", "two", or "three". \
The state of the bulb(s) can be "on" or "off". \

Example: \
If the user prompt is "Turn on bulb one", you should return {"bulbs": ["one"], "bulb_states": ["on"]}. \
If the user prompt is "Turn off all bulbs", you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["off", "off", "off"]}. \
If the user prompt is "Turn on bulb two and three", you should return {"bulbs": ["two", "three"], "bulb_states": ["on", "on"]}. \
If the user prompt is "Turn off bulb one and three", you should return {"bulbs": ["one", "three"], "bulb_states": ["off", "off"]}. \
If the user prompt is "Turn on all bulbs", you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["on", "on", "on"]}. \
If the user prompt is "Turn off bulb two", you should return {"bulbs": ["two"], "bulb_states": ["off"]}. \
If the user prompt is "Turn on all bulbs except bulb two", you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["on", "off", "on"]}. \
If the user prompt is "Turn off all bulbs except bulb one", you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["on", "off", "off"]}. \
If the user prompt is "Turn on bulb one and two", you should return {"bulbs": ["one", "two"], "bulb_states": ["on", "on"]}. \

You should also be able to understand when users are being general but specific. \
For example: \
If the user prompt is "Turn on the lights", you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["on", "on", "on"]}. \
If the user prompt is "only bulb one should be on", you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["on", "off", "off"]}. \
If the user prompt is "Turn off the lights", you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["off", "off", "off"]}. \

When the user specifies the only bulbs they want on/off, the rest should have the opposite state. \
For example: \
If the user prompt is "only bulb two should be on", you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["off", "on", "off"]}, \
If the user targets only a specific bulb, the other bulbs should be set to the opposite state.i.e. if the user says "only bulb two should be on", you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["off", "on", "off"]}, \
If the user prompt is "only bulb three should be off", you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["on", "on", "off"]}, \
If the user prompt is "only bulb one should be off", you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["off", "on", "on"]} \
and so on. \t

Remember that your response should be a JSON object with the keys "bulbs" and "bulb_states". \
Each key should have a list  strings not less than three elements. \
Even when the user specifies only one bulb, the other bulbs and states should be included in the response with the opposite state of the specified bulb. \

User the current state to keep track of the state of the bulbs. \
This should help you determine the state of the bulbs when the user is being general but specific. \
For example, if the user prompt is "only bulb two should be on", and the current state is "{'bulbs': ['one', 'two', 'three'], 'bulb_states':['on', 'off', 'off']}", \
you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["off", "on", "off"]}. \
If the user prompt is "only bulb three should be off", and the current state is "{'bulbs': ['one', 'two', 'three'], 'bulb_states':['on', 'on', 'on']}", \
you should return {"bulbs": ["one", "two", "three"], "bulb_states": ["on", "on", "off"]} and so on. \

REMEMBER, ALWAYS MAKE SURE TO KEEP TRACK OF THE CURRENT STATE OF THE BULBS AND ALSO REMEMBER THAT "THE RESPONSE SHOULD BE A JSON OBJECT WITH TWO KEYS 'bulbs' and 'bulb_states' AND EACH KEY HAS THREE VALUES". \
\n\n\n\n
"""

llm_history = '{"bulbs": ["one", "two", "three"], "bulb_states": ["off", "off", "off"]}'

# m_llm = Ollama(model="qwen2:0.5b")
m_llm = OllamaLLM(model="gemma2:2b")


if __name__ == "__main__":
    while True:
        try:
            prompt = input("Enter your command: ")
            command = m_llm.invoke(
                f"{LLM_CONTEXT}\nThe current state is: {llm_history}\n\nUser Prompt: {prompt}"
            )

            formatted_response = (
                command.replace("\n", "")
                .strip()
                .replace("```json", "")
                .replace("```", "")
            )
            print(f"Langchain response: {formatted_response}")
            try:
                command_new = json.loads(formatted_response)

                control_led(command_new["bulbs"], command_new["bulb_states"])
                llm_history = f"{'\"{'}'bulbs': {command_new['bulbs']}, 'bulb_states':{command_new['bulb_states']}{'}\"'}\n"
                print(f"\nHistory: {llm_history}")
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e}")
            except KeyError as e:
                print(f"KeyError: {e}")
        except KeyboardInterrupt as e:
            print(f"\nQuitting...")
            break
