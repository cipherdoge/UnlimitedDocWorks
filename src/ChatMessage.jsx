
function ChatMessage({ sender, text })
{
    return (
        <div className={`chat-message ${sender}`}>
            <div className="message-content">{text}</div>
        </div>
    );
}

export default ChatMessage;