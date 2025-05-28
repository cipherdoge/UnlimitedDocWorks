import { useState } from "react";

function ChatInput({ onSend })
{
    const [input, setInput] = useState("");

    const handleKeyDown = (e) =>
    {
        if (e.key === "Enter" && !e.shiftKey)
        {
            e.preventDefault();
            onSend(input);
            setInput("");
        }
    };

    return (
        <div className="chat-input">
            <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Send a message"
            />
        </div>
    );
}

export default ChatInput;
