import React from "react";

import PlatformSelector from "./PlatformSelector/PlatformSelector";
import GroupChat from "./GroupChat/GroupChat";

import "./ChatList.css";

const example_groupchat = {
    internal_chat_name: "instagram",
    ChatName: "Instagram Chat",
    last_message: {
        message: "I mean you could really argue for or against applying to Edinburgh",
        sender: "John Doe",
        date: "2021-08-01",
        time: "12:00"
    }
}

const examples_groupchats = [example_groupchat, example_groupchat, example_groupchat, example_groupchat, example_groupchat, example_groupchat, example_groupchat, example_groupchat, example_groupchat, example_groupchat, example_groupchat, example_groupchat, example_groupchat, example_groupchat, example_groupchat]

const ChatList = () => {
    return (
        <div className="ChatList">
            <PlatformSelector />
            <div className="group-chats">
                {examples_groupchats.map((groupchat) => (
                    <GroupChat groupchat={groupchat} />
                ))}
            </div>
        </div>
    )
};

export default ChatList;