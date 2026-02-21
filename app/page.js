'use client';

import { useState, useEffect, useRef } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

function CatalogTab() {
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [purchased, setPurchased] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/certificates`)
      .then(res => res.json())
      .then(data => {
        setCertificates(data.certificates || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const handlePurchase = (cert) => {
    setPurchased(cert);
  };

  if (purchased) {
    return (
      <div className="purchase-success">
        <div className="icon">✅</div>
        <h2>Сертификат приобретён!</h2>
        <p>{purchased.title}</p>
        <button className="btn btn-primary" onClick={() => setPurchased(null)}>
          ← Вернуться к каталогу
        </button>
      </div>
    );
  }

  if (loading) {
    return <div className="loading"><span className="dot-pulse">Загрузка...</span></div>;
  }

  return (
    <div>
      {certificates.map(cert => (
        <div key={cert.id} className="card">
          <div className="card-title">{cert.title}</div>
          <div className="card-desc">{cert.description}</div>
          <div className="card-footer">
            <span className="price">{cert.price.toLocaleString()}₽</span>
            <button className="btn btn-primary" onClick={() => handlePurchase(cert)}>
              Купить
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

function RaffleTab() {
  const [timeLeft, setTimeLeft] = useState(86400);
  const [joined, setJoined] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => Math.max(0, prev - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
  };

  return (
    <div>
      <div className="card raffle-card">
        <span className="raffle-badge">🎁 Бесплатный розыгрыш</span>
        <div className="card-title">Инвестиции для начинающих</div>
        <div className="card-desc">
          Выиграйте бесплатный сертификат на AI-консультацию по инвестициям!
        </div>
        <div className="card-footer">
          <div className="timer">⏰ {formatTime(timeLeft)}</div>
          <button 
            className={`btn ${joined ? 'btn-outline' : 'btn-primary'}`}
            onClick={() => setJoined(!joined)}
          >
            {joined ? '✓ Участвую' : 'Участвовать'}
          </button>
        </div>
      </div>

      <div className="card" style={{ textAlign: 'center', color: '#888' }}>
        <p style={{ fontSize: '14px' }}>
          👥 12 участников · Шанс: 8.3%
        </p>
      </div>
    </div>
  );
}

function ChatTab() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Привет! Я AI-Финансист. Задайте мне вопрос о личных финансах, инвестициях или налогах.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEnd = useRef(null);

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ certificate_id: 1, message: userMsg })
      });

      if (!res.ok) {
        throw new Error('AI service unavailable');
      }

      const data = await res.json();
      setMessages(prev => [...prev, { role: 'ai', content: data.response }]);
    } catch {
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: 'Функция AI-консультаций доступна в полной версии. Приобретите сертификат для доступа к персональным консультациям.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {loading && (
          <div className="message ai">
            <span className="dot-pulse">Думаю...</span>
          </div>
        )}
        <div ref={messagesEnd} />
      </div>
      <div className="chat-input">
        <input
          type="text"
          placeholder="Задайте вопрос..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
        />
        <button className="btn btn-primary" onClick={sendMessage}>→</button>
      </div>
    </div>
  );
}

export default function Home() {
  const [activeTab, setActiveTab] = useState('catalog');

  return (
    <div className="container">
      <div className="header">
        <h1>🤖 AI Финансист</h1>
        <p>Цифровые сертификаты на AI-консультации</p>
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'catalog' ? 'active' : ''}`}
          onClick={() => setActiveTab('catalog')}
        >
          📜 Каталог
        </button>
        <button 
          className={`tab ${activeTab === 'raffle' ? 'active' : ''}`}
          onClick={() => setActiveTab('raffle')}
        >
          🎲 Розыгрыш
        </button>
        <button 
          className={`tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          💬 AI Чат
        </button>
      </div>

      {activeTab === 'catalog' && <CatalogTab />}
      {activeTab === 'raffle' && <RaffleTab />}
      {activeTab === 'chat' && <ChatTab />}
    </div>
  );
}
