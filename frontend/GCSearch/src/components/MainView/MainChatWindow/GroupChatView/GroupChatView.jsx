import React, { useEffect, useRef } from "react";

import Message from "./Message/Message";

import "./GroupChatView.css";

const GroupChatView = ({ messages, isLoadingChatMessages, currentUser, currentPII, onGetEarlierChats, onGetLaterChats }) => {
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
        <div className="GroupChatView" ref={messagesContainerRef}>
            {isLoadingChatMessages || currentPII == null ? <div></div> : (
                <button onClick={onGetEarlierChats}>Later Messages</button>
            )}
            <div className="GroupChatMessages">
                {isLoadingChatMessages ? (
                    <p className="loading">Loading...</p>
                ) : messages.length === 0 ? (
                    <p className="no-messages">Click on a chat/result to view messages!</p>
                ) : (
                    messages.map((message, index) => (
                        <Message
                            key={index}
                            message={message.message}
                            sender={message.sender}
                            timestamp={message.timestamp}
                            image_url={message.image_url}
                            isCurrentUser={
                                currentUser !== null && message.sender === currentUser
                            }
                        />
                    ))
                )}
            </div>
            {isLoadingChatMessages || currentPII == null ? <div></div> : (
                <button onClick={onGetLaterChats}>Previous Messages</button>
            )}
        </div>
    )
};

export default GroupChatView;