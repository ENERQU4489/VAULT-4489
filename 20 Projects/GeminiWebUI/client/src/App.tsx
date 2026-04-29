import React, { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import ReactMarkdown from 'react-markdown';
import { Send, Terminal, Bot, User, Loader2 } from 'lucide-react';
import stripAnsi from 'strip-ansi';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
}

const socket: Socket = io('http://localhost:3001');

function App() {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'system', content: 'Połączono z mostkiem Gemini CLI.' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    socket.on('output', (data: string) => {
      const cleanData = stripAnsi(data);
      if (!cleanData.trim()) return;

      setMessages(prev => {
        const lastMsg = prev[prev.length - 1];
        // Jeśli ostatnia wiadomość jest od asystenta, doklejamy do niej strumień
        if (lastMsg && lastMsg.role === 'assistant') {
          return [
            ...prev.slice(0, -1),
            { ...lastMsg, content: lastMsg.content + cleanData }
          ];
        } else {
          // Nowa wiadomość od asystenta
          return [...prev, { id: Date.now().toString(), role: 'assistant', content: cleanData }];
        }
      });
      setIsTyping(false);
    });

    return () => {
      socket.off('output');
    };
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMsg]);
    socket.emit('input', input);
    setInput('');
    setIsTyping(true);
  };

  return (
    <div className="flex flex-col h-screen bg-zinc-950 text-zinc-100 font-sans">
      {/* Header */}
      <header className="border-b border-zinc-800 p-4 flex items-center justify-between bg-zinc-900/50 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <div className="bg-emerald-500/10 p-2 rounded-lg">
            <Bot className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h1 className="font-bold text-sm tracking-tight">GEMINI WEB UI</h1>
            <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-medium">Local Bridge Active</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          <Terminal className="w-4 h-4 text-zinc-500" />
        </div>
      </header>

      {/* Chat Area */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth"
      >
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((msg) => (
            <div 
              key={msg.id}
              className={cn(
                "flex gap-4 group transition-all duration-300",
                msg.role === 'user' ? "flex-row-reverse" : "flex-row"
              )}
            >
              <div className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
                msg.role === 'user' 
                  ? "bg-zinc-800 border-zinc-700" 
                  : msg.role === 'system' 
                    ? "bg-emerald-500/10 border-emerald-500/20"
                    : "bg-blue-600 border-blue-500"
              )}>
                {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>
              
              <div className={cn(
                "max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed",
                msg.role === 'user' 
                  ? "bg-zinc-800 text-zinc-100 rounded-tr-none" 
                  : msg.role === 'system'
                    ? "bg-emerald-500/5 text-emerald-300 italic border border-emerald-500/10"
                    : "bg-zinc-900 border border-zinc-800 rounded-tl-none"
              )}>
                <ReactMarkdown 
                  className="prose prose-invert prose-sm max-w-none prose-pre:bg-zinc-950 prose-pre:border prose-pre:border-zinc-800"
                >
                  {msg.content}
                </ReactMarkdown>
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex gap-4 items-center text-zinc-500 animate-pulse">
              <div className="w-8 h-8 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center">
                <Loader2 className="w-4 h-4 animate-spin" />
              </div>
              <span className="text-xs font-medium">Gemini myśli...</span>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-zinc-800 bg-zinc-900/50 backdrop-blur-md">
        <form 
          onSubmit={sendMessage}
          className="max-w-3xl mx-auto relative"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Napisz coś do Gemini..."
            className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl py-4 pl-6 pr-14 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500/50 transition-all placeholder:text-zinc-500"
          />
          <button
            type="submit"
            disabled={!input.trim()}
            className="absolute right-2 top-2 bottom-2 px-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-700 disabled:opacity-50 text-white rounded-xl transition-all shadow-lg shadow-emerald-900/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="text-center text-[10px] text-zinc-600 mt-3 uppercase tracking-tighter">
          Połączono lokalnie przez node-pty bridge
        </p>
      </div>
    </div>
  );
}

export default App;
