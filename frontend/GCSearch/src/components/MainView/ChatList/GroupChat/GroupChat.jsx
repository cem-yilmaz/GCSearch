import React from "react";

import "./GroupChat.css";

const getDateFromTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toDateString();
}

const getTimeFromTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
}



const GroupChat = (
    {
        groupchat : {
            internal_chat_name,
            ChatName,
            last_message : {
                doc_id,
                message,
                sender,
                timestamp
            }
        }
    }
) => {
    return (
        <div className="group-chat" title={message}>
            <div className="group-chat-top">
                <h3><span className="chatname">{ChatName}</span></h3>
                <p><span className="date">{getDateFromTimestamp(timestamp)}</span></p>
            </div>
            <div className="group-chat-bottom">
                <p><span className="time">[{getTimeFromTimestamp(timestamp)}]</span> <span className="sender">{sender}: </span></p>
                <p><span className="message"><i>{message}</i></span></p>
            </div>
        </div>
    )
}

export default GroupChat;