import React, { useState, useEffect } from "react";

import PlatformSelector from "./PlatformSelector/PlatformSelector";
import GroupChat from "./GroupChat/GroupChat";

import "./ChatList.css";

const API_URL = "http://localhost:5000/api";

const ChatList = () => {
    const [groupChats, setGroupChats] = useState([]);
    const [selectedPlatform, setSelectedPlatform] = useState("instagram");
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchGroupChats = async () => {
            setIsLoading(true);
            try {
                // get all chat IDs for the selected platform
                const chatIdsResponse = await fetch(`${API_URL}/GetAllParsedChatsForPlatform`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({platform: selectedPlatform})
                });
                const chatIds = await chatIdsResponse.json();

                // get details for each chat ID
                const chatsData = await Promise.all(chatIds.map(async (chatId) => {
                    const chatInfoResponse = await fetch(`${API_URL}/GetInfoForGroupChat`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ chat_name: chatId })
                    });
                    const chatInfo = await chatInfoResponse.json();

                    //format data
                    return {
                        internal_chat_name: chatId,
                        ChatName: chatInfo.display_name,
                        last_message: chatInfo.last_message
                    };
                }));

                setGroupChats(chatsData);
            } catch (error) {
                console.error(`Error fetching group chats: ${error}`);
            } finally {
                setIsLoading(false);
            }
        };

        fetchGroupChats();
    }, [selectedPlatform]);

    

    const handlePlatformChange = (platform) => {
        setSelectedPlatform(platform);
    }

    return (
        <div className="ChatList">
            <PlatformSelector />
            <div className="group-chats">
                {isLoading ? (
                    <p>Loading chats...</p>
                ) : (
                    groupChats.map((groupchat, index) => {
                        <GroupChat
                            key={index}
                            groupchat={groupchat}
                        />
                    })
                )}
            </div>
        </div>
    )
};

export default ChatList;