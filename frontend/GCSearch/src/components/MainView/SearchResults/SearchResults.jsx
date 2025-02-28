import React from "react";

import SearchResult from "./SearchResult/SearchResult";

import "./SearchResults.css";

const SearchResults = ({ results = [], isLoading = false }) => {
    return (
        <div className="SearchResults">
            <h2>Search Results</h2>

            {isLoading ? (
                <p className="loading">Searching...</p>
            ) : results.length > 0 ? (
                console.log(`Got ${results.length} results: ${results}`),
                results.map((result, index) => (
                    <SearchResult key={index} {...result} />
                ))
            ) : (
                <p className="no-results">No results found</p>
            )}
        </div>
    )
}

export default SearchResults;