import React, { useState } from 'react';

function App() {
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Send a POST request to the Flask backend
    const response = await fetch('http://localhost:5000/reverse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ string: inputText })
    });
    console.log("response: ", response);
    const data = await response.json();
    setResult(data);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Reverse String App</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Enter text here"
          style={{ width: '300px', padding: '8px' }}
        />
        <button type="submit" style={{ marginLeft: '10px', padding: '8px 12px' }}>
          Submit
        </button>
      </form>
      {result && (
        <div style={{ marginTop: '20px' }}>
          <p><strong>Original:</strong> {result.original}</p>
          <p><strong>Reversed:</strong> {result.reversed}</p>
        </div>
      )}
    </div>
  );
}

export default App;
