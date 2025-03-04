import React from "react";

import GroupChatView from "./GroupChatView/GroupChatView";

import "./MainChatWindow.css";

const MainChatWindow = ({ messages, isLoadingChatMessages, currentUser, currentPII, onGetEarlierChats, onGetLaterChats }) => {
    return (
        <div className="MainChatWindow">
            <GroupChatView 
                messages={messages} 
                isLoadingChatMessages={isLoadingChatMessages} 
                currentUser={currentUser} 
                currentPII={currentPII} 
                onGetEarlierChats={onGetEarlierChats} 
                onGetLaterChats={onGetLaterChats} 
            />
        </div>
    )
};

export default MainChatWindow;