import React from "react";

import MainChatWindow from "../components/MainView/MainChatWindow/MainChatWindow";
import ChatList from "../components/MainView/ChatList/ChatList";
import SearchResults from "../components/MainView/SearchResults/SearchResults";
import SearchBar from "../components/MainView/SearchBar/SearchBar";

import "./Main.css";

const Main = () => {
    return (
        <>
            <ChatList />
            <div className="central-container">
                <h1>GCSearch</h1>
                <SearchBar />
                <MainChatWindow />
            </div>
            <SearchResults />
        </>
    )
}

export default Main;