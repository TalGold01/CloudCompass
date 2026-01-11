import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Loader2, BookOpen } from 'lucide-react';
import { motion } from 'framer-motion';

// --------------------------------------------------------
// CONFIGURATION
// --------------------------------------------------------
// Lambda URL
const API_URL = "https://6lrbg5ifbqyos4rbt5nyp4ecnm0dbebf.lambda-url.us-east-1.on.aws/";

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Hello! I am CloudCompass. Ask me anything about the DevOps syllabus." }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(scrollToBottom, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // 1. Add User Message
    const userMessage = { role: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // 2. Call the API (Your Lambda)
      const response = await axios.post(API_URL, { question: input });
      
      // 3. Add AI Message
      const botMessage = { 
        role: 'assistant', 
        text: response.data.answer,
        citations: response.data.citations 
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', text: "⚠️ Error connecting to the brain. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100 font-sans">
      
      {/* Sidebar (Simple) */}
      <div className="w-64 bg-gray-800 p-6 hidden md:block border-r border-gray-700">
        <div className="flex items-center gap-2 mb-8 text-blue-400">
          <BookOpen className="w-6 h-6" />
          <h1 className="text-xl font-bold tracking-wider">CLOUD COMPASS</h1>
        </div>
        <div className="text-sm text-gray-400">
          <p className="mb-4">Use this tool to search the syllabus.</p>
          <div className="p-3 bg-gray-700/50 rounded-lg border border-gray-600">
            <p className="text-xs text-gray-300 font-semibold mb-1">Try asking:</p>
            <ul className="list-disc list-inside space-y-1 text-xs text-gray-400">
              <li>"What is Module 14?"</li>
              <li>"Is there a final project?"</li>
              <li>"Do we learn Python?"</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative bg-gray-900">
        
        {/* Messages List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-gray-700">
          {messages.map((msg, index) => (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              key={index} 
              className={`flex gap-4 max-w-3xl mx-auto ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'assistant' ? 'bg-blue-600' : 'bg-green-600'}`}>
                {msg.role === 'assistant' ? <Bot size={18} /> : <User size={18} />}
              </div>

              {/* Message Bubble */}
              <div className={`rounded-2xl px-5 py-3 max-w-[80%] shadow-lg leading-relaxed ${
                msg.role === 'user' 
                  ? 'bg-green-600 text-white rounded-tr-sm' 
                  : 'bg-gray-800 text-gray-100 border border-gray-700 rounded-tl-sm'
              }`}>
                <p className="whitespace-pre-wrap">{msg.text}</p>
                
                {/* Citations (Evidence) */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-400">
                    <p className="font-semibold text-blue-400 mb-1 flex items-center gap-1">
                      <BookOpen size={12} /> Source Found:
                    </p>
                    {msg.citations[0].retrievedReferences[0].content.text.slice(0, 150)}...
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          
          {/* Loading Indicator */}
          {loading && (
            <div className="flex gap-4 max-w-3xl mx-auto">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <Loader2 size={18} className="animate-spin" />
              </div>
              <div className="bg-gray-800 px-5 py-3 rounded-2xl rounded-tl-sm border border-gray-700">
                <span className="animate-pulse text-gray-400">Thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-gray-900 border-t border-gray-800">
          <div className="max-w-3xl mx-auto relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask a question about the DevOps course..."
              className="w-full bg-gray-800 text-gray-100 border border-gray-700 rounded-xl pl-4 pr-12 py-4 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-xl placeholder-gray-500"
              disabled={loading}
            />
            <button 
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="absolute right-2 top-2 p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
          <p className="text-center text-xs text-gray-600 mt-2">
            Cloud Compass AI can make mistakes. Check syllabus for official info.
          </p>
        </div>

      </div>
    </div>
  );
}

export default App;