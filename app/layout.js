import './globals.css';

export const metadata = {
  title: 'AI Финансист',
  description: 'Цифровые сертификаты на AI-консультации по финансовой грамотности',
};

export default function RootLayout({ children }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
