import React from "react";

import SearchResult from "./SearchResult/SearchResult";

import "./SearchResults.css";

const exampleResults = [
    {
        chatName: "Chat 1",
        platform: "instagram",
        message_details: {
            message: "Hello, world! I'm craft",
            sender: "User1",
            timestamp: 1620000000000
        }
    },
    {
        chatName: "Chat 2",
        platform: "whatsapp",
        message_details: {
            message: "Hi, there!",
            sender: "User2",
            timestamp: 1620004444400
        }
    }
];

const SearchResults = () => {
    return (
        <div className="SearchResults">
            <h2>Search Results</h2>
            {exampleResults.map((result, index) => <SearchResult key={index} {...result} />)}
        </div>
    )
}

export default SearchResults;