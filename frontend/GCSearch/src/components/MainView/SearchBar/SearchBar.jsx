import React from "react";

import "./SearchBar.css";

const SearchBar = () => {
    return (
        <div className="SearchBar">
            <img src="/assets/search.png"></img>
            <input type="text" placeholder="Search..."></input>
        </div>
    )
};

export default SearchBar;