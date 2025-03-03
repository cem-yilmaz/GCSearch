import React from "react";

import GroupChatView from "./GroupChatView/GroupChatView";

import "./MainChatWindow.css";

const MainChatWindow = ({ messages, isLoadingChatMessages, currentUser }) => {
    return (
        <div className="MainChatWindow">
            <GroupChatView messages={messages} isLoadingChatMessages={isLoadingChatMessages} currentUser={currentUser} />
        </div>
    )
};

export default MainChatWindow;