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
    const [isLoadingChatMessages, setIsLoadingChatMessages] = useState(false);
    const [currentChatMessages, setCurrentChatMessages] = useState([]);
    const [currentUser, setCurrentUser] = useState(null);
    
    useEffect(() => {
        const checkServer = async () => {
            try {
                const response = await fetch(`${API_URL}/isAlive`);
                setServerStatus(`Connected (${response.status})`);
                fetchCurrentUser();
            } catch (error) {
                console.error(`Error connecting to server: ${error}`);
                setServerStatus("Failed to connect");
            }
        };
        
        checkServer();
    }, []);

    const fetchCurrentUser = async () => {
        try {
            const response = await fetch(`${API_URL}/GetCurrentUser`);
            const data = await response.json();
            setCurrentUser(data.current_user);
            console.log(`Current User: ${data.current_user}`);
        } catch (error) {
            console.error(`Error fetching current user: ${error}`);
            setCurrentUser(null);
        }
    }

    console.log(`Server status: ${serverStatus}`);

    const fetchChatRange = async (pii_name, doc_id, n) => {
        console.log(`Fetching chat range for ${pii_name} from ${doc_id} with n=${n}`);
        setIsLoadingChatMessages(true);
        try {
            const body = {
                pii_name: pii_name,
                doc_id: doc_id,
                n: n
            };
            const response = await fetch(`${API_URL}/GetChatsBetweenRangeForChatGivenPIIName`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            });
            const data = await response.json();
            setIsLoadingChatMessages(false);
            setCurrentChatMessages(data);
        } catch (error) {
            console.error(`Error fetching chat range: ${error}`);
            setIsLoadingChatMessages(false);
            setCurrentChatMessages([]);
        }
    };

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
            <ChatList 
                onSelectChat={
                    (groupchat) => fetchChatRange(
                        groupchat.internal_chat_name,
                        groupchat.last_message.doc_id,
                        10
                    )
                }
            />
            <div className="central-container">
                <h1>GCSearch</h1>
                <SearchBar onSearch={handleSearch}/>
                <MainChatWindow messages={currentChatMessages} isLoadingChatMessages={isLoadingChatMessages} currentUser={currentUser} />
            </div>
            <SearchResults 
                results={searchResults}
                isLoading={isSearching} 
                onSelectSearchResult={
                    (res) => fetchChatRange(
                        res.internal_chat_name,
                        res.message_details.doc_id,
                        10
                    )
                }/>
        </>
    );
};

export default Main;