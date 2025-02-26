import React from "react";

import GroupChatView from "./GroupChatView/GroupChatView";

import "./MainChatWindow.css";

const MainChatWindow = () => {
    return (
        <div className="MainChatWindow">
            <GroupChatView />
        </div>
    )
};

export default MainChatWindow;