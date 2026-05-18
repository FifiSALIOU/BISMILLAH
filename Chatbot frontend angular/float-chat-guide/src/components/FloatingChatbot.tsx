import React, { useState } from 'react';
import { MessageCircle, X, Send, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { askQuestionUltra, recordSatisfaction } from '@/lib/chatApi';

interface ChatMessage {
  id: number;
  text: string;
  isBot: boolean;
  time: string;
  feedback: 'like' | 'dislike' | null;
  isWelcomeMessage?: boolean;
  responseId?: string;
}

const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      text: 'Bonjour ! Comment puis-je vous aider ?',
      isBot: true,
      time: '14:30',
      feedback: null,
      isWelcomeMessage: true
    }
  ]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const sendMessage = async () => {
    if (!message.trim() || isLoading) return;

    const userText = message.trim();
    const userMessage: ChatMessage = {
      id: Date.now(),
      text: userText,
      isBot: false,
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
      feedback: null
    };

    setMessages((prev) => [...prev, userMessage]);
    setMessage('');
    setIsLoading(true);

    try {
      const result = await askQuestionUltra(userText);
      const botResponse: ChatMessage = {
        id: Date.now() + 1,
        text: result.answer,
        isBot: true,
        time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        feedback: null,
        isWelcomeMessage: false,
        responseId: result.id
      };
      setMessages((prev) => [...prev, botResponse]);
    } catch {
      const botResponse: ChatMessage = {
        id: Date.now() + 1,
        text: 'Je vous remercie pour votre message. Un de nos conseillers va vous répondre sous peu.',
        isBot: true,
        time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        feedback: null,
        isWelcomeMessage: false
      };
      setMessages((prev) => [...prev, botResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const handleFeedback = (messageId: number, feedbackType: 'like' | 'dislike') => {
    const target = messages.find((msg) => msg.id === messageId);

    setMessages((prevMessages) =>
      prevMessages.map((msg) =>
        msg.id === messageId ? { ...msg, feedback: feedbackType } : msg
      )
    );

    if (target?.responseId) {
      recordSatisfaction({
        response_id: target.responseId,
        is_satisfied: feedbackType === 'like',
      }).catch(() => {
        // L'UI conserve le feedback local même si l'enregistrement échoue
      });
    }
  };

  return (
    <>
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 animate-slide-up">
          <Card className="w-80 h-96 bg-card shadow-chat border-0 overflow-hidden">
            <div className="bg-gradient-primary p-4 text-primary-foreground">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full overflow-hidden">
                    <img 
                      src="/lovable-uploads/Lovable 2.png" 
                      alt="Assistant IA" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm">Assistant IA</h3>
                    <p className="text-xs opacity-90">En ligne</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleChat}
                  className="text-primary-foreground hover:bg-white/20 h-8 w-8 p-0"
                >
                  <X size={16} />
                </Button>
              </div>
            </div>

            <div className="flex-1 p-4 space-y-3 overflow-y-auto h-64">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex flex-col ${msg.isBot ? 'items-start' : 'items-end'}`}>
                  <div className={`max-w-[70%] rounded-lg p-3 ${
                    msg.isBot 
                      ? 'bg-muted text-foreground' 
                      : 'bg-primary text-primary-foreground'
                  }`}>
                    <p className="text-sm">{msg.text}</p>
                    <p className="text-xs opacity-70 mt-1">{msg.time}</p>
                  </div>
                  
                  {msg.isBot && !msg.isWelcomeMessage && (
                    <div className="flex mt-1 space-x-2">
                      <button 
                        onClick={() => handleFeedback(msg.id, 'like')}
                        className={`p-1 rounded-full ${msg.feedback === 'like' ? 'bg-green-100' : 'hover:bg-gray-100'}`}
                        aria-label="J'aime cette réponse"
                      >
                        <ThumbsUp size={16} className={`${msg.feedback === 'like' ? 'text-green-500' : 'text-gray-500'}`} />
                      </button>
                      <button 
                        onClick={() => handleFeedback(msg.id, 'dislike')}
                        className={`p-1 rounded-full ${msg.feedback === 'dislike' ? 'bg-red-100' : 'hover:bg-gray-100'}`}
                        aria-label="Je n'aime pas cette réponse"
                      >
                        <ThumbsDown size={16} className={`${msg.feedback === 'dislike' ? 'text-red-500' : 'text-gray-500'}`} />
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="p-4 border-t">
              <div className="flex gap-2">
                <Input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Tapez votre message..."
                  className="flex-1 text-sm"
                  disabled={isLoading}
                />
                <Button 
                  onClick={sendMessage}
                  size="sm"
                  className="px-3"
                  disabled={isLoading}
                >
                  <Send size={16} />
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      <div className="fixed bottom-6 right-6 z-40">
        <Button
          onClick={toggleChat}
          className="h-14 w-14 rounded-full bg-gradient-primary shadow-elegant hover:scale-105 transition-all duration-200"
          size="sm"
        >
          {isOpen ? (
            <X size={24} className="text-primary-foreground" />
          ) : (
            <MessageCircle size={24} className="text-primary-foreground" />
          )}
        </Button>
        
        {!isOpen && (
          <div className="absolute -top-2 -left-2 w-6 h-6 bg-primary rounded-full animate-pulse">
            <div className="w-full h-full bg-primary rounded-full animate-ping"></div>
          </div>
        )}
      </div>
    </>
  );
};

export default FloatingChatbot;
