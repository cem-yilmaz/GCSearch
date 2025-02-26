import React from "react";

import "./Message.css";

const Message = (
    {
        message,
        sender,
        time,
        image_url,
        isCurrentUser,
        reactions
    }
) => {
    return (
        <div className={`${isCurrentUser ? "message-right" : "message-left"}`}>
            <div className="message-header">
                <p>{sender} | {time}</p>
            </div>
            <div className="message-content">
                <p>{message}</p>
            </div>
        </div>
    )
}

export default Message;