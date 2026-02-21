require('dotenv').config();
const { Bot, InlineKeyboard } = require('grammy');
const sqlite3 = require('sqlite3').verbose();

const bot = new Bot(process.env.BOT_TOKEN);
const db = new sqlite3.Database('./data.db');

// Helper: Get or create user
function getOrCreateUser(ctx, callback) {
  const { id, username, first_name } = ctx.from;
  
  db.get('SELECT * FROM users WHERE telegram_id = ?', [id], (err, user) => {
    if (user) {
      callback(user);
    } else {
      db.run(
        'INSERT INTO users (telegram_id, username, first_name) VALUES (?, ?, ?)',
        [id, username, first_name],
        function() {
          db.get('SELECT * FROM users WHERE id = ?', [this.lastID], (err, newUser) => {
            callback(newUser);
          });
        }
      );
    }
  });
}

// /start command
bot.command('start', async (ctx) => {
  getOrCreateUser(ctx, (user) => {
    const keyboard = new InlineKeyboard()
      .webApp('🎓 Открыть каталог', process.env.MINI_APP_URL || 'https://example.com')
      .row()
      .text('🎲 Участвовать в розыгрыше', 'join_raffle');

    ctx.reply(
      `Привет, ${ctx.from.first_name}! 👋\n\n` +
      `Я AI-Финансист — твой помощник в мире финансовой грамотности.\n\n` +
      `📜 Покупай сертификаты на консультации с AI\n` +
      `🎁 Участвуй в бесплатных розыгрышах\n` +
      `💡 Получай персональные финансовые советы`,
      { reply_markup: keyboard }
    );
  });
});

// /catalog command
bot.command('catalog', async (ctx) => {
  db.all('SELECT * FROM certificates WHERE active = 1', [], (err, certs) => {
    if (!certs || certs.length === 0) {
      return ctx.reply('Пока нет доступных сертификатов');
    }

    let message = '📜 *Доступные сертификаты:*\n\n';
    certs.forEach(cert => {
      message += `*${cert.title}*\n`;
      message += `${cert.description}\n`;
      message += `💰 Цена: ${cert.price}₽\n\n`;
    });

    const keyboard = new InlineKeyboard()
      .webApp('🛒 Открыть каталог', process.env.MINI_APP_URL || 'https://example.com');

    ctx.reply(message, { 
      parse_mode: 'Markdown',
      reply_markup: keyboard 
    });
  });
});

// Join raffle callback
bot.callbackQuery('join_raffle', async (ctx) => {
  await ctx.answerCallbackQuery('Функция розыгрыша будет доступна в полной версии');
  ctx.reply(
    '🎲 *Розыгрыш сертификатов*\n\n' +
    'В полной версии здесь будут:\n' +
    '• Еженедельные бесплатные розыгрыши\n' +
    '• Автоматический выбор победителей\n' +
    '• Уведомления о новых розыгрышах',
    { parse_mode: 'Markdown' }
  );
});

// Error handler
bot.catch((err) => {
  console.error('Bot error:', err);
});

// Start bot
console.log('🤖 Bot starting...');
bot.start();
console.log('✅ Bot is running!');
