import React, { useState, useEffect } from "react";

import PlatformSelector from "./PlatformSelector/PlatformSelector";
import GroupChat from "./GroupChat/GroupChat";

import "./ChatList.css";

const API_URL = "http://localhost:5000/api";

const ChatList = ({ onSelectChat, fetchCurrentUser }) => {
    const [groupChats, setGroupChats] = useState([]);
    const [selectedPlatform, setSelectedPlatform] = useState("instagram");
    const [isLoading, setIsLoading] = useState(true);

    console.log("Chatlist");
    console.log(selectedPlatform);

    useEffect(() => {
        const fetchGroupChats = async () => {
            setIsLoading(true);
            fetchCurrentUser(selectedPlatform);
            try {
                // get all chat IDs for the selected platform
                const chatIdsResponse = await fetch(`${API_URL}/GetAllParsedChatsForPlatform`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ platform: selectedPlatform })
                });
        
                if (!chatIdsResponse.ok) {
                    throw new Error(`Failed to fetch chat IDs: ${chatIdsResponse.statusText}`);
                }
            
                const chatIds = await chatIdsResponse.json();
        
                // get details for each chat ID
                const chatsData = await Promise.all(chatIds.map(async (chatId) => {
                    try {
                        const chatInfoResponse = await fetch(`${API_URL}/GetInfoForGroupChat`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ chat_name: chatId })
                        });
        
                        if (!chatInfoResponse.ok) {
                            throw new Error(`Failed to fetch info for ${chatId}: ${chatInfoResponse.statusText}`);
                        }
        
                        const chatInfo = await chatInfoResponse.json();
        
                        // Check if the server returned an error in JSON
                        if (chatInfo.error) {
                            return {
                                internal_chat_name: chatId,
                                ChatName: `Error: ${chatInfo.error}`,
                                last_message: null
                            };
                        }
        
                        // Otherwise, format normal data
                        return {
                            internal_chat_name: chatId,
                            ChatName: chatInfo.display_name,
                            last_message: chatInfo.last_message
                        };
                    } catch (error) {
                        console.error(`Error fetching info for chatId ${chatId}:`, error);
                        // Return a fallback chat object
                        return {
                            internal_chat_name: chatId,
                            ChatName: `Error retrieving info for chat ID: ${chatId}`,
                            last_message: null
                        };
                    }
                }));

                // sort chats by timestamp descending
                chatsData.sort((a, b) => {
                    if (a.last_message && b.last_message) {
                        return b.last_message.timestamp - a.last_message.timestamp;
                    } else if (a.last_message) {
                        return -1;
                    } else if (b.last_message) {
                        return 1;
                    } else {
                        return 0;
                    }
                });
        
                setGroupChats(chatsData);
            } catch (error) {
                console.error(`Error fetching group chats: ${error}`);
            } finally {
                setIsLoading(false);
            }
        };

        fetchGroupChats();
    }, [selectedPlatform]);
        
    return (
        <div className="ChatList">
            <PlatformSelector onPlatformSelected={platform => setSelectedPlatform(platform)} />
            <div className="group-chats">
                {isLoading ? (
                    <p>Loading chats...</p>
                ) : (
                    groupChats.map((groupchat, index) => (
                        <div key={index} onClick={() => onSelectChat(groupchat)}>
                            <GroupChat
                                groupchat={groupchat}
                            />
                        </div>
                    ))
                )}
            </div>
        </div>
    )
};

export default ChatList;