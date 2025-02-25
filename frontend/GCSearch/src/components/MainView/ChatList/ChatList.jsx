import React from "react";

import PlatformSelector from "./PlatformSelector/PlatformSelector";

import "./ChatList.css";

const ChatList = () => {
    return (
        <div className="ChatList">
            <PlatformSelector />
            <p>GroupChatList</p>
        </div>
    )
};

export default ChatList;