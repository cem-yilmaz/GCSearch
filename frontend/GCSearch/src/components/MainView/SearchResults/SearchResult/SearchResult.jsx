import React from "react";


import "./SearchResult.css";

const getDateFromTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toDateString();
}

const getTimeFromTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
}

const getTitle = (sender, message) => {
    return `${sender}: ${message}`;
}

const SearchResult = (
    {
        chatName,
        platform,
        message_details : {
            message,
            sender,
            timestamp
        }
    }
) => {
    return (
        <div className="search-result">
            <div className="platform-image">
                <img src={`assets/platform_logos/${platform}.png`} alt={platform} />
            </div>
            <div className="message-details" title={getTitle(sender, message)}>
                <div className="message-top">
                    <h3><span className="chatname">{chatName}</span></h3>
                    <p><span className="date">{getDateFromTimestamp(timestamp)}</span></p>
                </div>
                <div className="message-bottom">
                    <p><span className="time">[{getTimeFromTimestamp(timestamp)}]</span> <span className="sender">{sender}: </span></p>
                    <p><span className="message"><i>{message}</i></span></p>
                </div>
            </div>
        </div>
    )
}

export default SearchResult;