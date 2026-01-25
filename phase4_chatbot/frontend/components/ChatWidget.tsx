"use client";

import { useState, useRef, useEffect } from "react";
import { chatApi } from "@/lib/api";
import { MessageCircle, X, Send, Loader2 } from "lucide-react";
import { useTaskRefresh } from "@/contexts/TaskRefreshContext";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [userId, setUserId] = useState<number | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Use the task refresh context
  const { refreshTasks } = useTaskRefresh();

  // Function to check authentication
  const checkAuth = () => {
    try {
      console.log("ChatWidget: Checking authentication...");
      if (typeof window === "undefined") {
        console.log("ChatWidget: Window not available, skipping auth check");
        return;
      }

      const storedUserId = localStorage.getItem("user_id");
      const token = localStorage.getItem("auth_token");

      console.log("ChatWidget: storedUserId =", storedUserId);
      console.log("ChatWidget: token exists =", !!token);

      if (storedUserId && token) {
        console.log("ChatWidget: User authenticated with ID:", storedUserId);
        setUserId(parseInt(storedUserId, 10));
        setIsAuthenticated(true);
      } else {
        console.log("ChatWidget: Not authenticated - missing userId or token");
        setIsAuthenticated(false);
      }
    } catch (err) {
      console.error("Error checking auth:", err);
      setError("Failed to initialize chat widget");
    }
  };

  // Check auth on mount and when storage changes
  useEffect(() => {
    checkAuth();

    // Listen for storage changes (in case other tabs update localStorage)
    const handleStorageChange = () => {
      console.log("ChatWidget: Storage changed, rechecking auth...");
      checkAuth();
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !userId) return;

    const userMessage = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(userId, userMessage, conversationId);

      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.message },
      ]);

      // Check if the response indicates a task was modified and trigger refresh
      const responseText = response.message.toLowerCase();
      if (
        responseText.includes('[completed]') ||
        responseText.includes('[done]') ||
        responseText.includes('[updated]') ||
        responseText.includes('[removed]') ||
        responseText.includes('added') ||
        responseText.includes('deleted') ||
        responseText.includes('completed') ||
        responseText.includes('updated')
      ) {
        // Small delay to ensure backend operations are complete
        setTimeout(() => {
          refreshTasks();
        }, 1000);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to send message";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${errorMessage}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (error) {
    console.error("ChatWidget error:", error);
    return null; // Don't show chatbot if there's an error
  }

  if (!isAuthenticated) {
    return null; // Don't show chatbot if not logged in
  }

  return (
    <>
      {/* Floating Chat Icon Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center hover:scale-110 active:scale-95"
        title="Open Chat"
      >
        {isOpen ? (
          <X className="w-6 h-6" />
        ) : (
          <>
            <MessageCircle className="w-6 h-6" />
            <span className="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
          </>
        )}
      </button>

      {/* Chat Widget Modal */}
      {isOpen && (
        <div className="fixed bottom-20 right-6 z-50 w-96 max-h-96 rounded-2xl shadow-2xl bg-white dark:bg-gray-900 border border-white/20 overflow-hidden flex flex-col animate-scale-in">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-lg">TaskFlow Chat</h3>
              <p className="text-xs text-white/80">Powered by AI</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="hover:bg-white/20 p-1 rounded transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50 dark:bg-gray-800/50">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center text-center">
                <div className="text-sm text-muted-foreground">
                  <p className="font-semibold mb-2">👋 Hi there!</p>
                  <p className="text-xs">Try: "Add a task to buy groceries"</p>
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-xs rounded-lg px-3 py-2 text-sm ${
                      msg.role === "user"
                        ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-br-none"
                        : "bg-white dark:bg-gray-700 text-foreground rounded-bl-none border border-gray-200 dark:border-gray-600"
                    }`}
                  >
                    <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-700 rounded-lg px-3 py-2 flex gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-3 bg-white dark:bg-gray-900">
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <input
                type="text"
                placeholder="Ask me anything..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading}
                className="flex-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-purple-600 disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="p-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-lg transition-all disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
