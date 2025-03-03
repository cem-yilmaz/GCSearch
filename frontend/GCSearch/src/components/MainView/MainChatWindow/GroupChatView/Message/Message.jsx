import React from "react";

import "./Message.css";

const getDateFromTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toDateString();
}

const getTimeFromTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
}

const Message = (
    {
        message,
        sender,
        timestamp,
        image_url,
        isCurrentUser,
        reactions
    }
) => {
    return (
        <div className={`${isCurrentUser ? "message-right" : "message-left"}`}>
            <div className="message-header">
                <p>{sender} | {timestamp}</p>
            </div>
            <div className="message-content">
                <p>{message}</p>
            </div>
        </div>
    )
}

export default Message;