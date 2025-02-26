import React from "react";

import Message from "./Message/Message";

import "./GroupChatView.css";

const messages = [
    {
        message: "Hello! Long time see old pal. It's been 700 years since we last talked.",
        sender: "User1",
        time: "12:10",
        image_url: "",
        isCurrentUser: true,
        reactions: []
    },
    {
        message: "Hi! How are things with the family?",
        sender: "User2",
        time: "12:11",
        image_url: "",
        isCurrentUser: false,
        reactions: []
    },
    {
        message: "How are you?",
        sender: "User1",
        time: "12:12",
        image_url: "",
        isCurrentUser: true,
        reactions: []
    },
    {
        message: "I'm good! I've been working on this project recently, and I think you'd be really interested.",
        sender: "User2",
        time: "12:13",
        image_url: "",
        isCurrentUser: false,
        reactions: []
    },
    {
        message: "What about you?",
        sender: "User2",
        time: "12:14",
        image_url: "",
        isCurrentUser: false,
        reactions: []
    },
    {
        message: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        sender: "User1",
        time: "12:15",
        image_url: "",
        isCurrentUser: true,
        reactions: []
    }
];

const GroupChatView = () => {
    return (
        <div className="GroupChatView">
            <div className="GroupChatMessages">
                {messages.map((message, index) => (
                    <Message
                        key={index}
                        message={message.message}
                        sender={message.sender}
                        time={message.time}
                        image_url={message.image_url}
                        isCurrentUser={message.isCurrentUser}
                    />
                ))}
            </div>
        </div>
    )
};

export default GroupChatView;