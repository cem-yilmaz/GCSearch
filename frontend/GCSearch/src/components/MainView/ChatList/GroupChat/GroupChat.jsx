import React from "react";

import "./GroupChat.css";

const GroupChat = (
    {
        groupchat : {
            internal_chat_name,
            ChatName,
            last_message : {
                message,
                sender,
                date,
                time
            }
        }
    }
) => {
    return (
        <div className="group-chat">
            <div className="group-chat-top">
                <h3><span className="chatname">{ChatName}</span></h3>
                <p><span className="date">{date}</span></p>
            </div>
            <div className="group-chat-bottom">
                <p><span className="time">[{time}]</span> <span className="sender">{sender}: </span></p>
                <p><span className="message"><i>{message}</i></span></p>
            </div>
        </div>
    )
}

export default GroupChat;