import React from "react";

import GroupChatView from "./GroupChatView/GroupChatView";

import "./MainChatWindow.css";

const MainChatWindow = ({ messages, isLoadingChatMessages }) => {
    return (
        <div className="MainChatWindow">
            <GroupChatView messages={messages} isLoadingChatMessages={isLoadingChatMessages}/>
        </div>
    )
};

export default MainChatWindow;