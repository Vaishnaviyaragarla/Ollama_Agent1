import requests

print("🤖 Chat with Gemma (type 'exit' to quit)")
print("-----------------------------------------")

chat_history = []  # this will store all previous messages

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("👋 Bye! Have a great day.")
        break

    # Add user input to history
    chat_history.append(f"User: {user_input}")

    # Combine full chat as a single prompt
    full_prompt = "\n".join(chat_history) + "\nAI:"

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma3",
            "prompt": full_prompt,
            "stream": False
        }
    )

    try:
        ai_response = response.json()["response"].strip()
        print("Gemma:", ai_response)

        # Add AI response to history
        chat_history.append(f"AI: {ai_response}")

    except Exception as e:
        print("⚠️ Error:", e)
        print("Response text:", response.text)

