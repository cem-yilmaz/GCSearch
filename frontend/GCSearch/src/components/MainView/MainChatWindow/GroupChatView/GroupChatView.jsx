import React, { useEffect, useRef } from "react";

import Message from "./Message/Message";

import "./GroupChatView.css";

const GroupChatView = ({ messages, isLoadingChatMessages }) => {
    const messagesContainerRef = useRef(null);

    useEffect(() => {
        if (messagesContainerRef.current && !isLoadingChatMessages) {
            const container = messagesContainerRef.current;
            const scrollHeight = container.scrollHeight;
            const height = container.clientHeight;

            const middlePosition = (scrollHeight / 2) - (height / 2);
            container.scrollTo({
                top: middlePosition,
                behavior: "smooth"
            });
        }
    }, [messages, isLoadingChatMessages]);
    
    return (
        <div className="GroupChatView">
            <div className="GroupChatMessages">
                {isLoadingChatMessages ? (
                    <p className="loading">Loading...</p>
                ) : messages.length === 0 ? (
                    <p className="no-messages">Click on a chat/result to view messages!</p>
                ) : (
                    console.log(`Got ${messages.length} messages: ${messages}`),
                    messages.map((message, index) => (
                        <Message
                            key={index}
                            message={message.message}
                            sender={message.sender}
                            timestamp={message.timestamp}
                            image_url={message.image_url}
                            isCurrentUser={message.isCurrentUser}
                        />
                    ))
                )}
            </div>
        </div>
    )
};

export default GroupChatView;