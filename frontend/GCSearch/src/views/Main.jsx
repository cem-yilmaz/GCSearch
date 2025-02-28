import React, { useState, useEffect } from "react";

import MainChatWindow from "../components/MainView/MainChatWindow/MainChatWindow";
import ChatList from "../components/MainView/ChatList/ChatList";
import SearchResults from "../components/MainView/SearchResults/SearchResults";
import SearchBar from "../components/MainView/SearchBar/SearchBar";

import "./Main.css";

const API_URL = "http://localhost:5000/api";

const Main = () => {
    const [serverStatus, setServerStatus] = useState("Checking...");
    const [searchResults, setSearchResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    
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

    console.log(`Server status: ${serverStatus}`);

    const handleSearch = async (searchQuery) => {
        if (!searchQuery.trim()) {
            setSearchResults([]);
            console.error(`Recieved empty search query [${searchQuery}]`);
            return;
        }

        setIsSearching(true);

        try {
            const response = await fetch(`${API_URL}/GetTopNResultsFromSearch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: searchQuery,
                    n: 25
                })
            });

            if (!response.ok) {
                console.error(`Error searching for [${searchQuery}]: ${response.statusText}`);
                setSearchResults([]);
                console.error(`Ending Search`)
                setIsSearching(false);
            }

            const data = await response.json();
            setSearchResults(data);
        } catch (error) {
            console.error(`Error searching for [${searchQuery}]: ${error}`);
            setSearchResults([]);
            console.error(`Ending Search`)
            setIsSearching(false);
        } finally {
            setIsSearching(false);
        }
    }
    
    return (
        <>
            <ChatList />
            <div className="central-container">
                <h1>GCSearch</h1>
                <SearchBar onSearch={handleSearch}/>
                <MainChatWindow />
            </div>
            <SearchResults results={searchResults} isLoading={isSearching}/>
        </>
    );
};

export default Main;