# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
)
from botbuilder.schema import Activity
import traceback
import json
import sys

# Bot Configuration
APP_ID = ""
APP_PASSWORD = ""

SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Error Handling
async def on_error(context: TurnContext, error: Exception):
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    await context.send_activity("The bot encountered an error.")
    await context.send_activity("Please fix the bot source code.")

ADAPTER.on_turn_error = on_error


# Main Bot Logic
class SimpleChatBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == "message":

            user_message = turn_context.activity.text.lower().strip()

            # Greeting
            if user_message in ["hello", "hi", "hey"]:
                response = "Hello! Welcome to the Simple Chatbot."

            # Help Command
            elif user_message == "help":
                response = (
                    "I can perform the following tasks:\n"
                    "1. Greet users\n"
                    "2. Reverse text\n"
                    "3. Tell a joke\n"
                    "4. Respond to simple questions\n"
                    "5. Handle invalid input\n\n"
                    "Commands:\n"
                    "- hello\n"
                    "- reverse your_text\n"
                    "- joke\n"
                    "- bye"
                )

            # Reverse String
            elif user_message.startswith("reverse"):
                text = user_message.replace("reverse", "").strip()

                if text:
                    response = text[::-1]
                else:
                    response = "Please provide text to reverse."

            # Joke Feature
            elif user_message == "joke":
                response = "Why do programmers prefer dark mode? Because light attracts bugs!"

            # Goodbye
            elif user_message == "bye":
                response = "Goodbye! Have a wonderful day."

            # Invalid Input
            else:
                response = (
                    "Sorry, I did not understand your request.\n"
                    "Type 'help' to see available commands."
                )

            await turn_context.send_activity(response)


BOT = SimpleChatBot()


# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:

    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)

    auth_header = (
        req.headers["Authorization"]
        if "Authorization" in req.headers
        else ""
    )

    response = await ADAPTER.process_activity(
        activity, auth_header, BOT.on_turn
    )

    if response:
        return json_response(data=response.body, status=response.status)

    return Response(status=201)


# Create Web Application
APP = web.Application()
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=3978)

    except Exception as error:
        raise errora