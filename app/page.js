'use client';

import { useState, useEffect, useRef } from 'react';

const API = '';

function useInitData() {
  const [initData, setInitData] = useState('debug');
  useEffect(() => {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.ready();
      tg.expand();
      setInitData(tg.initData || 'debug');
    }
  }, []);
  return initData;
}

function api(path, opts = {}) {
  return fetch(`${API}${path}`, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      'X-Init-Data': 'debug',
      ...opts.headers,
    },
  }).then(r => r.json());
}

/* ───── CATALOG ───── */
function CatalogTab() {
  const [certs, setCerts] = useState([]);
  const [purchased, setPurchased] = useState(null);

  useEffect(() => {
    api('/api/certificates').then(d => setCerts(d.certificates || []));
  }, []);

  const buy = async (cert) => {
    const res = await api('/api/purchases', {
      method: 'POST',
      body: JSON.stringify({ certificate_id: cert.id }),
    });
    setPurchased({ ...cert, qr_code: res.qr_code });
  };

  if (purchased) {
    return (
      <div className="purchase-success">
        <div className="icon">✅</div>
        <h2>Сертификат приобретён!</h2>
        <p>{purchased.title}</p>
        {purchased.qr_code && (
          <img
            src={`data:image/png;base64,${purchased.qr_code}`}
            alt="QR Code"
            style={{ width: 200, height: 200, margin: '16px auto', display: 'block', borderRadius: 12 }}
          />
        )}
        <p style={{ fontSize: 12, color: '#888' }}>Покажите QR-код для активации</p>
        <button className="btn btn-primary" onClick={() => setPurchased(null)}>
          ← Вернуться
        </button>
      </div>
    );
  }

  return (
    <div>
      {certs.map(c => (
        <div key={c.id} className="card">
          <div className="card-title">{c.title}</div>
          <div className="card-desc">{c.description}</div>
          <div className="card-footer">
            <span className="price">{(c.price / 100).toLocaleString('ru')}₽</span>
            <button className="btn btn-primary" onClick={() => buy(c)}>Купить</button>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ───── MY CERTIFICATES ───── */
function MyCertsTab() {
  const [purchases, setPurchases] = useState([]);

  useEffect(() => {
    api('/api/purchases/my').then(d => setPurchases(d.purchases || []));
  }, []);

  if (!purchases.length) {
    return <div className="loading">У вас пока нет сертификатов</div>;
  }

  return (
    <div>
      {purchases.map(p => (
        <div key={p.id} className="card">
          <div className="card-title">{p.certificate_title}</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <span className="price">{(p.amount / 100).toLocaleString('ru')}₽</span>
            <span style={{ color: p.status === 'paid' ? '#00c853' : '#ffa726' }}>
              {p.status === 'paid' ? '✅ Оплачен' : '⏳ Ожидает'}
            </span>
          </div>
          {p.qr_code && (
            <img
              src={`data:image/png;base64,${p.qr_code}`}
              alt="QR"
              style={{ width: 150, height: 150, margin: '0 auto', display: 'block', borderRadius: 8 }}
            />
          )}
        </div>
      ))}
    </div>
  );
}

/* ───── RAFFLES ───── */
function RafflesTab() {
  const [raffles, setRaffles] = useState([]);
  const [joined, setJoined] = useState({});

  useEffect(() => {
    api('/api/raffles').then(d => setRaffles(d.raffles || []));
  }, []);

  const join = async (id) => {
    await api(`/api/raffles/${id}/join`, { method: 'POST' });
    setJoined(prev => ({ ...prev, [id]: true }));
  };

  if (!raffles.length) {
    return (
      <div className="card raffle-card" style={{ textAlign: 'center' }}>
        <span className="raffle-badge">🎁 Розыгрыши</span>
        <p style={{ color: '#aaa', marginTop: 12 }}>Активных розыгрышей пока нет</p>
      </div>
    );
  }

  return (
    <div>
      {raffles.map(r => (
        <div key={r.id} className="card raffle-card">
          <span className="raffle-badge">🎁 Бесплатный розыгрыш</span>
          <div className="card-title">{r.title}</div>
          <div className="card-desc">{r.description}</div>
          <div className="card-footer">
            <span style={{ color: '#888' }}>👥 {r.entries_count}/{r.max_entries}</span>
            <button
              className={`btn ${joined[r.id] ? 'btn-outline' : 'btn-primary'}`}
              onClick={() => join(r.id)}
            >
              {joined[r.id] ? '✓ Участвую' : 'Участвовать'}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

/* ───── CHARITY ───── */
function CharityTab() {
  const [options, setOptions] = useState([]);
  const [voted, setVoted] = useState(false);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    api('/api/charity').then(d => {
      setOptions(d.options || []);
      setTotal(d.total_votes || 0);
    });
  }, []);

  const vote = async (id) => {
    await api(`/api/charity/${id}/vote`, { method: 'POST' });
    setVoted(true);
    api('/api/charity').then(d => {
      setOptions(d.options || []);
      setTotal(d.total_votes || 0);
    });
  };

  return (
    <div>
      <div className="card" style={{ textAlign: 'center', marginBottom: 16 }}>
        <h3 style={{ marginBottom: 4 }}>🤝 Голосование за благотворительность</h3>
        <p style={{ color: '#888', fontSize: 13 }}>Куда направить часть средств?</p>
      </div>
      {options.map(o => (
        <div key={o.id} className="card">
          <div className="card-title">{o.title}</div>
          <div className="card-desc">{o.description}</div>
          <div style={{ background: '#1a1a2e', borderRadius: 8, height: 8, marginBottom: 8 }}>
            <div style={{
              background: 'linear-gradient(90deg, #6c63ff, #8b83ff)',
              borderRadius: 8,
              height: 8,
              width: `${o.percentage}%`,
              transition: 'width 0.5s',
            }} />
          </div>
          <div className="card-footer">
            <span style={{ color: '#888' }}>{o.votes} голосов ({o.percentage}%)</span>
            {!voted && (
              <button className="btn btn-primary" onClick={() => vote(o.id)}>
                Голосовать
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ───── MAIN APP ───── */
export default function Home() {
  const [tab, setTab] = useState('catalog');

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('tab')) setTab(params.get('tab'));
  }, []);

  const tabs = [
    { id: 'catalog', label: '📜 Каталог' },
    { id: 'my', label: '🎓 Мои' },
    { id: 'raffles', label: '🎲 Розыгрыш' },
    { id: 'charity', label: '🤝 Фонд' },
  ];

  return (
    <div className="container">
      <div className="header">
        <h1>🤖 AI Финансист</h1>
        <p>Цифровые сертификаты на AI-консультации</p>
      </div>
      <div className="tabs">
        {tabs.map(t => (
          <button key={t.id} className={`tab ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>
      {tab === 'catalog' && <CatalogTab />}
      {tab === 'my' && <MyCertsTab />}
      {tab === 'raffles' && <RafflesTab />}
      {tab === 'charity' && <CharityTab />}
    </div>
  );
}
