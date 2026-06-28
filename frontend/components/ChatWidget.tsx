"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, Bot, User, Sparkles, AlertCircle } from "lucide-react";
import axios from "axios";
import { API_BASE } from "../lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatWidgetProps {
  articleText?: string;
  userName?: string;
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({ articleText, userName = "Investor" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: `Hello ${userName}! I'm the E-newspaper Assistant. I can help you understand this article or answer general questions about news and current events. How can I help today?`,
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(`session_${Math.random().toString(36).substring(7)}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    
    // Add user message to UI
    const newMessage: Message = {
      role: "user",
      content: userMessage,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        session_id: sessionId,
        user_message: userMessage,
        article_text: articleText,
        user_profile: { name: userName }
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.ai_reply,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error("Chat Error:", error);
      const detail = error.response?.data?.detail || error.message || "Connection failed";
      const errorMessage: Message = {
        role: "assistant",
        content: `Sorry, I encountered an error connecting to the E-newspaper Intelligence: ${detail}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="mb-4 w-96 max-w-[calc(100vw-3rem)] h-[500px] liquid-glass-dark overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="p-4 border-b border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-[#ED1C24] flex items-center justify-center">
                  <Bot size={18} className="text-white" />
                </div>
                <div>
                  <h3 className="text-white font-medium text-[0.9375rem]">E-newspaper Assistant</h3>
                  <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                    <span className="text-[0.6875rem] text-white/60">Intelligence Unit Online</span>
                  </div>
                </div>
              </div>
              <button 
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-white/10 rounded-lg transition-colors text-white/60 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            {/* Context Notice (if article active) */}
            {articleText && (
              <div className="px-4 py-2 border-b border-white/10 flex items-center gap-2 bg-white/5">
                <Sparkles size={12} className="text-[#ED1C24]" />
                <span className="text-[0.6875rem] text-white/70 font-medium">Analyzing current article context...</span>
              </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div 
                    className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-[0.9375rem] leading-relaxed ${
                      msg.role === "user" 
                        ? "bg-[#ED1C24] text-white rounded-tr-sm" 
                        : "bg-white/10 text-white/90 rounded-tl-sm"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white/10 px-4 py-2.5 rounded-2xl rounded-tl-sm w-2/3 space-y-2">
                    <div className="h-3 bg-white/20 rounded-full animate-pulse w-full"></div>
                    <div className="h-3 bg-white/20 rounded-full animate-pulse w-[60%]"></div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-white/10 bg-white/5">
              <div className="relative flex items-center">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  placeholder="Ask a question..."
                  className="w-full bg-white/10 border border-white/20 rounded-full py-2.5 pl-4 pr-12 text-[0.9375rem] text-white placeholder-white/40 focus:outline-none focus:border-[#ED1C24] transition-colors"
                />
                <button 
                  onClick={handleSendMessage}
                  disabled={isLoading}
                  className="absolute right-1.5 p-2 bg-[#ED1C24] hover:bg-[#c8151b] disabled:bg-white/10 transition-colors rounded-full text-white"
                >
                  <Send size={16} />
                </button>
              </div>
              <p className="mt-2 text-[0.6875rem] text-center text-white/40">
                E-newspaper Assistant can make mistakes. Verify critical information.
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toggle Button (The Orb) */}
      <motion.button
        whileHover={{ y: -4 }}
        whileTap={{ y: 0, scale: 0.99 }}
        transition={{ duration: 0.25, ease: "easeOut" }}
        onClick={() => setIsOpen(!isOpen)}
        className={`w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 ${
          isOpen ? "bg-[#1d1d1f] border border-white/10" : "bg-[#ED1C24] hover:bg-[#c8151b]"
        }`}
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div
              key="close"
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
            >
              <X size={20} className="text-white" />
            </motion.div>
          ) : (
            <motion.div
              key="chat"
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.5, opacity: 0 }}
              className="relative"
            >
              <MessageCircle size={20} className="text-white" />
              <div className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-white rounded-full border-2 border-[#ED1C24] animate-pulse"></div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    </div>
  );
};
