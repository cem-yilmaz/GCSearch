import pandas as pd


def flask_getNumChatsInGC(GC_name: str) -> int:
    """
    Gets the number of chats in a given group chat (GC) from its name.

    Args:
        GC_name (str): Name of the group chat.

    Returns:
        int: Number of chat records in the specified GC.
    """
    try:
        # Read chat log CSV file
        df = pd.read_csv("chatlog.csv")

        # Ensure column exists
        if "sender" not in df.columns:
            raise ValueError("Column 'sender' not found in chatlog.csv")

        # Count chats in the specified GC
        num_chats = df[df["sender"] == GC_name].shape[0]
        return num_chats
    except Exception as e:
        print(f"Error: {e}")
        return 0


# **调用函数**
result = flask_getNumChatsInGC("Group_name")  # Please fill in the specific group name you want to search
print(f"Number of chats in GC: {result}")

# **If it is a Flask application, start Flask here**
if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)


    @app.route("/")
    def home():
        return "Flask server is running!"


    app.run(debug=True)

