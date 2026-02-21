'use client';

import { useEffect, useState } from 'react';

interface Certificate {
  id: number;
  title: string;
  description: string;
  price: number;
}

export default function Home() {
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:3000/api/certificates')
      .then(res => res.json())
      .then(data => {
        setCertificates(data.certificates || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading certificates:', err);
        setLoading(false);
      });
  }, []);

  const handlePurchase = async (certId: number, price: number) => {
    // TODO: Integrate Telegram payment
    alert(`Покупка сертификата #${certId} за ${price}₽. Интеграция платежей в полной версии!`);
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Загрузка...</div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>🎓 AI Finansist</h1>
        <p style={styles.subtitle}>Сертификаты на консультации с AI</p>
      </header>

      <div style={styles.grid}>
        {certificates.map(cert => (
          <div key={cert.id} style={styles.card}>
            <h3 style={styles.cardTitle}>{cert.title}</h3>
            <p style={styles.cardDesc}>{cert.description}</p>
            <div style={styles.cardFooter}>
              <span style={styles.price}>{cert.price}₽</span>
              <button 
                style={styles.button}
                onClick={() => handlePurchase(cert.id, cert.price)}
              >
                Купить
              </button>
            </div>
          </div>
        ))}
      </div>

      <footer style={styles.footer}>
        <p>🎁 Еженедельные бесплатные розыгрыши</p>
        <p>🤖 AI-советник по финансовой грамотности</p>
      </footer>
    </div>
  );
}

const styles = {
  container: {
    padding: '20px',
    maxWidth: '800px',
    margin: '0 auto',
    backgroundColor: '#f5f5f5',
    minHeight: '100vh',
  },
  header: {
    textAlign: 'center' as const,
    marginBottom: '30px',
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#2c3e50',
    margin: '0 0 10px 0',
  },
  subtitle: {
    fontSize: '16px',
    color: '#7f8c8d',
    margin: 0,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '20px',
    marginBottom: '40px',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  cardTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#2c3e50',
    margin: '0 0 10px 0',
  },
  cardDesc: {
    fontSize: '14px',
    color: '#7f8c8d',
    marginBottom: '20px',
  },
  cardFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  price: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#27ae60',
  },
  button: {
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    padding: '10px 20px',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
  },
  footer: {
    textAlign: 'center' as const,
    color: '#7f8c8d',
    marginTop: '40px',
  },
  loading: {
    textAlign: 'center' as const,
    padding: '50px',
    fontSize: '18px',
    color: '#7f8c8d',
  },
};
