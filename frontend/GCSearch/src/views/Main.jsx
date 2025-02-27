import React from "react";

import MainChatWindow from "../components/MainView/MainChatWindow/MainChatWindow";
import ChatList from "../components/MainView/ChatList/ChatList";
import SearchResults from "../components/MainView/SearchResults/SearchResults";
import SearchBar from "../components/MainView/SearchBar/SearchBar";

import "./Main.css";

const API_URL = "http://localhost:5000/api";

const canConnectToServer = async () => {
    try {
        const response = await fetch(`${API_URL}/isAlive`);
        return response.status;
    } catch (error) {
        console.error(`Error connecting to server: ${error}`);
        return false;
    } finally {
        
    }
}

const Main = () => {
    console.log(`Can connect to server: ${canConnectToServer()}`);
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