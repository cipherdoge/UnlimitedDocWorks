import React, { useState } from "react";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

function ChatWindow() {
    const [messages, setMessages] = useState([]);
    const [mode, setMode] = useState("document"); // default mode

    const handleSend = (text) => {
        if (text.trim()) {
            setMessages((prev) => [...prev, { sender: "user", text }]);

            fetch("http://localhost:5000/run", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ text, mode }), // send mode along with text
            })
            .then((response) => response.json())
            .then((data) => {
                setMessages((prev) => [...prev, { sender: "bot", text: data.response }]);
            })
            .catch((error) => {
                console.error("Error:", error);
                setMessages((prev) => [...prev, { sender: "bot", text: "Something went wrong!" }]);
            });
        }
    };

    return (
        <div className="chat-window">
            {/* Dropdown Menu */}
            <div className="mode-selector" style={{ marginBottom: "10px" }}>
                <label htmlFor="mode">Select mode: </label>
                <select
                    id="mode"
                    value={mode}
                    onChange={(e) => setMode(e.target.value)}
                >
                    <option value="document">document</option>
                    <option value="csv">csv</option>
                    <option value="document+csv">document+csv</option>
                </select>
            </div>

            {/* Chat Messages */}
            <div className="chat-history">
                {messages.map((msg, idx) => (
                    <ChatMessage key={idx} sender={msg.sender} text={msg.text} />
                ))}
            </div>

            {/* Chat Input */}
            <ChatInput onSend={handleSend} />
        </div>
    );
}

export default ChatWindow;
