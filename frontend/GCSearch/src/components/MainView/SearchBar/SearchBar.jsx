import React, { useState, useEffect } from "react";

import "./SearchBar.css";

const SearchBar = ({ onSearch }) => {
    const [query, setQuery] = useState("");

    /* //debounce
    useEffect(() => {
        const timeoutId = setTimeout(() => {
            if (query.trim()) {
                onSearch(query);
            }
        }, 500)

        return () => clearTimeout(timeoutId)
    }, [query, onSearch]) 
    
    This causes the server to automatically search after 500ms of inactivity in the search bar. This could be a nice feature, but I imagine users will want to press enter to search.

    */

    const handleInputChange = (e) => {
        setQuery(e.target.value);
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            console.log("Performing Search")
            onSearch(query);
        }
    }

    return (
        <div className="SearchBar">
            <img src="/assets/search.png"></img>
            <input
                type="text"
                placeholder="Search..."
                value={query}
                onChange={handleInputChange}
                onKeyDown={handleKeyPress}
            />
        </div>
    )
};

export default SearchBar;