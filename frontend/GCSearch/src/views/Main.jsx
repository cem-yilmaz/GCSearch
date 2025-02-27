import React, { useState, useEffect } from "react";

import MainChatWindow from "../components/MainView/MainChatWindow/MainChatWindow";
import ChatList from "../components/MainView/ChatList/ChatList";
import SearchResults from "../components/MainView/SearchResults/SearchResults";
import SearchBar from "../components/MainView/SearchBar/SearchBar";

import "./Main.css";

const API_URL = "http://localhost:5000/api";

const Main = () => {
    const [serverStatus, setServerStatus] = useState("Checking...");
    
    useEffect(() => {
        const checkServer = async () => {
            try {
                const response = await fetch(`${API_URL}/isAlive`);
                setServerStatus(`Connected (${response.status})`);
            } catch (error) {
                console.error(`Error connecting to server: ${error}`);
                setServerStatus("Failed to connect");
            }
        };
        
        checkServer();
    }, []);
    
    return (
        <>
            <ChatList />
            <div className="central-container">
                <h1>GCSearch</h1>
                <p>Server status: {serverStatus}</p>
                <SearchBar />
                <MainChatWindow />
            </div>
            <SearchResults />
        </>
    );
};

export default Main;