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
    const [currentChatPII, setCurrentChatPII] = useState(null);
    const [offset, setOffset] = useState(0);
    
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

    const handleGetEarlierChats = (pii, doc_id) => {
        const newOffset = offset - 10;
        setOffset(newOffset);
        fetchChatRange(pii, doc_id, newOffset);
    }

    const handleGetLaterChats = (pii, doc_id) => {
        const newOffset = offset + 10;
        setOffset(newOffset);
        fetchChatRange(pii, doc_id, newOffset);
    }

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
        // this function is called when explicitly selecting a chat from the chat list or search results
        console.log(`Fetching chat range for ${pii_name} from ${doc_id} with n=${n}`);
        setIsLoadingChatMessages(true);
        setCurrentChatPII(pii_name);
        setOffset(n);
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
    
    const handleProxSearch = async (searchQuery, range) => {
        if (!searchQuery.trim()) {
            setSearchResults([]);
            console.error(`Recieved empty search query [${searchQuery}]`);
            return;
        }

        setIsSearching(true);
        try {
            const response = await fetch(`${API_URL}/ProximitySearch`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: searchQuery,
                    range: range
                })
            });
            const data = await response.json();
            setSearchResults(data);
        } catch (error) {
            console.error(`Error proxsearching for [${searchQuery}]: ${error}`);
            setSearchResults([]);
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
                fetchCurrentUser={fetchCurrentUser}
            />
            <div className="central-container">
                <h1>GCSearch</h1>
                <SearchBar onSearch={handleSearch} onProxSearch={handleProxSearch} />
                <MainChatWindow 
                    messages={currentChatMessages} 
                    isLoadingChatMessages={isLoadingChatMessages} 
                    currentUser={currentUser}
                    currentPII={currentChatPII}
                    onGetEarlierChats={() => fetchChatRange(currentChatPII, currentChatMessages[0].doc_id, 10)} 
                    onGetLaterChats={() => fetchChatRange(currentChatPII, currentChatMessages[currentChatMessages.length - 1].doc_id, 10)}
                />
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