import React, { useState, useEffect } from "react";

import "./SearchBar.css";

const SearchBar = ({ onSearch, onProxSearch }) => {
    const [query, setQuery] = useState("");
    const [isProxSearch, setIsProxSearch] = useState(false);
    const [rangeValue, setRangeValue] = useState(10);

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
            if (isProxSearch) {
                console.log(`Proximity search with range: ${rangeValue}, and query: ${query}`);
                onProxSearch(query, rangeValue);
            } else {
                console.log(`Normal search with query: ${query}`);
                onSearch(query);                
            }
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
            <label>
                <input
                    type="checkbox"
                    checked={isProxSearch}
                    onChange={() => setIsProxSearch(!isProxSearch)}
                />
                Proximity Search
            </label>
            {isProxSearch && (
                <input
                    type="number"
                    min={1}
                    max={25}
                    value={rangeValue}
                    onChange={(e) => setRangeValue(e.target.value)}
                    style={{ width: "50px", marginLeft: "10px" }}
                />
            )}
        </div>
    )
};

export default SearchBar;