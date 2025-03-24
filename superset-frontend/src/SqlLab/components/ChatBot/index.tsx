import { useState, useRef, useEffect } from "react";
import "./ChatBot.css";
import useQueryEditor from "src/SqlLab/hooks/useQueryEditor";
import { JsonObject } from "@superset-ui/core";
import { sendChatMessage } from "src/SqlLab/actions/sqlLab";
import { useDispatch } from 'react-redux';

interface ChatBotProps {
  queryEditorId: any
}

const Chatbot = ({queryEditorId}:ChatBotProps) => {
    const dispatch = useDispatch<(dispatch: any) => Promise<JsonObject>>();
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [messages, setMessages] = useState([{ text: "Hello! How can I help?", sender: "bot" }]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<any>(null); // Reference for last message
    const queryEditor = useQueryEditor(queryEditorId, [
      'dbId',
      'catalog',
      'schema',
    ]);
    // Function to auto-scroll to the latest message
    const scrollToBottom = () => {
      messagesEndRef?.current?.scrollIntoView({ behavior: "smooth" });
    };
  
    useEffect(() => {
      scrollToBottom();
    }, [messages, isTyping]); // Scroll when messages update or bot starts typing
  
    // const handleSendMessage = () => {
    //   if (!input.trim()) return;
  
    //   const userMessage = { text: input, sender: "user" };
    //   setMessages([...messages, userMessage]);
    //   setInput("");
  
    //   setIsTyping(true); // Show "typing" indicator
  
    //   setTimeout(() => {
    //     setIsTyping(false);
    //     const botMessage = { text: "I'm just a demo bot! 😊", sender: "bot" };
    //     setMessages((prevMessages) => [...prevMessages, botMessage]);
    //   }, 2000);
    // };
  
  // const handleSendMessage = async () => {
  //   if (!input.trim()) return;

  //   // Add user message to the chat
  //   const newMessage = { text: input, sender: "user" };
  //   setMessages([...messages, newMessage]);

  //   setIsTyping(true);
  //   sendChatMessage(newMessage).then((response) => {
  //     setIsTyping(false);
  //     const botReply = response.json?.message || "No response from server";
  //     setMessages((prev) => [...prev, { text: botReply, sender: "bot" }]);
  //   }).catch((error) => {
  //     setIsTyping(false);
  //     setMessages((prev) => [...prev, { text: "Error fetching response", sender: "bot" }]);
  //   });

  //   setInput("");
  // };



    const handleSendMessageDispatch = () => {
      if (!input.trim()) return;
      const newMessage = { text: input, sender: "user" };
      setMessages([...messages, newMessage]);
  
      setIsTyping(true);

      dispatch(sendChatMessage(newMessage))
        .then((msg) => {
          setIsTyping(false);
          const botReply: any = msg || "No response from server";
          setMessages((prev) => [...prev, { text: botReply, sender: "bot" }]);
          setInput("");
        })
        .catch((error) => {
          setIsTyping(false);
          setMessages((prev) => [...prev, { text: "Error fetching response", sender: "bot" }]);
          setInput("");
        });
    };


    const handleKeyPress = (e:any) => {
      if (e.key === "Enter") {
        handleSendMessageDispatch();
      }
    };
  

    return (
      <div id="chat-box" className="chat-container">
        {isOpen && (
          <div className="chatbox">
            <div className="chat-header">

              <div style={{flexDirection: 'column'}}>
                <h4>Chatbot</h4>
                <h6>Database ID {queryEditor?.dbId}</h6> 
                <h6>Schema {queryEditor?.schema}</h6>
              </div>

              <button onClick={() => setIsOpen(false)} className="close-btn">✖</button>
            </div>
            <div className="chat-body">
              {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.sender}`}>
                  {msg.text}
                </div>
              ))}
              {isTyping && <div className="typing-indicator">Bot is typing...</div>}
              <div ref={messagesEndRef} /> {/* Invisible div to focus last message */}
            </div>
            <div className="chat-footer">
              <input
                type="text"
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
              />
              <button className="send-btn" onClick={handleSendMessageDispatch}>Send</button>
            </div>
          </div>
        )}
        <button onClick={() => setIsOpen(!isOpen)} className="chat-icon">💬</button>
      </div>
    );
  };

  export default Chatbot
