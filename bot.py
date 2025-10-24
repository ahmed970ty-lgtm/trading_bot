from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ta  # مكتبة التحليل الفني

TOKEN = "8366438891:AAGowx9iPvQdYGQ9sNArJ_50lrsaSckrRqk"
TWELVE_DATA_API_KEY = "de24b2541d564eb19684408b7367c6b7"

class ProfessionalTechnicalAnalysis:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.twelvedata.com"
    
    def get_historical_data(self, symbol, interval="15min", outputsize=100):
        """جلب بيانات تاريخية للتحليل الفني"""
        try:
            params = {
                'symbol': symbol,
                'interval': interval,
                'outputsize': outputsize,
                'apikey': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/time_series", params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'values' in data:
                    df = pd.DataFrame(data['values'])
                    # تحويل الأنواع
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df['open'] = df['open'].astype(float)
                    df['high'] = df['high'].astype(float)
                    df['low'] = df['low'].astype(float)
                    df['close'] = df['close'].astype(float)
                    df['volume'] = df['volume'].astype(float) if 'volume' in df.columns else 0
                    return df.sort_values('datetime')
                    
        except Exception as e:
            print(f"خطأ في البيانات التاريخية {symbol}: {e}")
        
        return None
    
    def calculate_technical_indicators(self, df):
        """حساب المؤشرات الفنية المتقدمة"""
        if df is None or len(df) < 20:
            return None
            
        try:
            # مؤشر RSI
            df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
            
            # MACD
            macd = ta.trend.MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            # المتوسطات المتحركة
            df['sma_20'] = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
            df['sma_50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
            df['ema_12'] = ta.trend.EMAIndicator(df['close'], window=12).ema_indicator()
            df['ema_26'] = ta.trend.EMAIndicator(df['close'], window=26).ema_indicator()
            
            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
            df['bb_upper'] = bollinger.bollinger_hband()
            df['bb_middle'] = bollinger.bollinger_mavg()
            df['bb_lower'] = bollinger.bollinger_lband()
            
            # Stochastic
            stochastic = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], window=14, smooth_window=3)
            df['stoch_k'] = stochastic.stoch()
            df['stoch_d'] = stochastic.stoch_signal()
            
            # Support and Resistance
            df['support'] = df['low'].rolling(window=10).min()
            df['resistance'] = df['high'].rolling(window=10).max()
            
            return df
            
        except Exception as e:
            print(f"خطأ في حساب المؤشرات: {e}")
            return None
    
    def analyze_candlestick_patterns(self, df):
        """تحليل أنماط الشموع اليابانية"""
        if df is None or len(df) < 3:
            return []
            
        patterns = []
        current = df.iloc[-1]
        prev = df.iloc[-2]
        prev2 = df.iloc[-3] if len(df) >= 3 else None
        
        # نمط الشهاب (Shooting Star)
        if (current['high'] - max(current['open'], current['close'])) > (2 * abs(current['close'] - current['open'])) and \
           (min(current['open'], current['close']) - current['low']) <= (0.1 * abs(current['close'] - current['open'])):
            patterns.append("🔴 شهاب - انعكاس هابط")
        
        # نمط المطرقة (Hammer)
        elif (min(current['open'], current['close']) - current['low']) > (2 * abs(current['close'] - current['open'])) and \
             (current['high'] - max(current['open'], current['close'])) <= (0.1 * abs(current['close'] - current['open'])):
            patterns.append("🟢 مطرقة - انعكاس صاعد")
        
        # نمط الابتلاع (Engulfing)
        elif current['close'] > current['open'] and prev['close'] < prev['open'] and \
             current['open'] < prev['close'] and current['close'] > prev['open']:
            patterns.append("🟢 ابتلاع صاعد")
        elif current['close'] < current['open'] and prev['close'] > prev['open'] and \
             current['open'] > prev['close'] and current['close'] < prev['open']:
            patterns.append("🔴 ابتلاع هابط")
        
        # نمط النجوم (Doji)
        if abs(current['close'] - current['open']) <= (0.01 * current['close']):
            patterns.append("⚪ دوجي - تردد")
            
        return patterns
    
    def generate_trading_signals(self, df):
        """توليد إشارات تداول احترافية"""
        if df is None or len(df) < 50:
            return None
            
        current = df.iloc[-1]
        signals = []
        confidence = 0
        
        # إشارات RSI
        if current['rsi'] < 30:
            signals.append("🟢 RSI في منطقة ذروة البيع")
            confidence += 25
        elif current['rsi'] > 70:
            signals.append("🔴 RSI في منطقة ذروة الشراء")
            confidence += 25
        
        # إشارات MACD
        if current['macd'] > current['macd_signal'] and df.iloc[-2]['macd'] <= df.iloc[-2]['macd_signal']:
            signals.append("🟢 إشارة شراء من MACD")
            confidence += 20
        elif current['macd'] < current['macd_signal'] and df.iloc[-2]['macd'] >= df.iloc[-2]['macd_signal']:
            signals.append("🔴 إشارة بيع من MACD")
            confidence += 20
        
        # إشارات المتوسطات
        if current['sma_20'] > current['sma_50'] and df.iloc[-2]['sma_20'] <= df.iloc[-2]['sma_50']:
            signals.append("🟢 تقاطع ذهبي للمتوسطات")
            confidence += 15
        elif current['sma_20'] < current['sma_50'] and df.iloc[-2]['sma_20'] >= df.iloc[-2]['sma_50']:
            signals.append("🔴 تقاطع ميت للمتوسطات")
            confidence += 15
        
        # إشارات Bollinger Bands
        if current['close'] <= current['bb_lower']:
            signals.append("🟢 السعر عند الحزام السفلي - شراء")
            confidence += 10
        elif current['close'] >= current['bb_upper']:
            signals.append("🔴 السعر عند الحزام العلوي - بيع")
            confidence += 10
        
        return {
            'signals': signals,
            'confidence': min(confidence, 100),
            'total_signals': len(signals)
        }
    
    def calculate_entry_exit_points(self, df, current_price):
        """حساب نقاط الدخول والخروج بدقة"""
        if df is None:
            return None
            
        current = df.iloc[-1]
        
        # نقاط الدخول
        buy_entry = round(current['bb_lower'] * 0.998, 4)
        sell_entry = round(current['bb_upper'] * 1.002, 4)
        
        # نقاط وقف الخسارة
        buy_stop_loss = round(current['support'] * 0.995, 4)
        sell_stop_loss = round(current['resistance'] * 1.005, 4)
        
        # أهداف الربح
        buy_take_profit = [
            round(current_price * 1.005, 4),
            round(current_price * 1.01, 4),
            round(current['resistance'] * 0.998, 4)
        ]
        
        sell_take_profit = [
            round(current_price * 0.995, 4),
            round(current_price * 0.99, 4),
            round(current['support'] * 1.002, 4)
        ]
        
        return {
            'buy': {
                'entry': buy_entry,
                'stop_loss': buy_stop_loss,
                'take_profit': buy_take_profit,
                'risk_reward': round((buy_take_profit[0] - current_price) / (current_price - buy_stop_loss), 2)
            },
            'sell': {
                'entry': sell_entry,
                'stop_loss': sell_stop_loss,
                'take_profit': sell_take_profit,
                'risk_reward': round((current_price - sell_take_profit[0]) / (sell_stop_loss - current_price), 2)
            }
        }

# إنشاء المحلل الفني
technical_analyzer = ProfessionalTechnicalAnalysis(TWELVE_DATA_API_KEY)

# رموز الأصول
ASSETS = {
    "الذهب": {"symbol": "XAU/USD", "emoji": "🪙"},
    "الفضة": {"symbol": "XAG/USD", "emoji": "⚪"}, 
    "النفط": {"symbol": "USOIL", "emoji": "🛢️"},
    "يورو/دولار": {"symbol": "EUR/USD", "emoji": "💶"},
    "جنيه/دولار": {"symbol": "GBP/USD", "emoji": "💷"},
    "دولار/ين": {"symbol": "USD/JPY", "emoji": "💴"},
    "بتكوين": {"symbol": "BTC/USD", "emoji": "₿"},
    "إيثريوم": {"symbol": "ETH/USD", "emoji": "🔷"}
}

def get_main_keyboard():
    """لوحة المفاتيح الرئيسية"""
    keyboard = []
    
    # الصف الأول: الذهب والفضة والنفط
    keyboard.append([
        InlineKeyboardButton("🪙 الذهب", callback_data="asset_الذهب"),
        InlineKeyboardButton("⚪ الفضة", callback_data="asset_الفضة"),
        InlineKeyboardButton("🛢️ النفط", callback_data="asset_النفط")
    ])
    
    # الصف الثاني: الفوركس
    keyboard.append([
        InlineKeyboardButton("💶 يورو/دولار", callback_data="asset_يورو/دولار"),
        InlineKeyboardButton("💷 جنيه/دولار", callback_data="asset_جنيه/دولار"),
        InlineKeyboardButton("💴 دولار/ين", callback_data="asset_دولار/ين")
    ])
    
    # الصف الثالث: العملات الرقمية
    keyboard.append([
        InlineKeyboardButton("₿ بتكوين", callback_data="asset_بتكوين"),
        InlineKeyboardButton("🔷 إيثريوم", callback_data="asset_إيثريوم")
    ])
    
    # الصف الرابع: أوامر إضافية
    keyboard.append([
        InlineKeyboardButton("📊 جميع الأسعار", callback_data="all_prices"),
        InlineKeyboardButton("🆘 المساعدة", callback_data="help")
    ])
    
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context):
    """بدء البوت وعرض القائمة الرئيسية"""
    welcome_text = """
🎯 **مرحباً بك في بوت التحليل الفني المتقدم!**

📊 **اختر الأصل الذي تريد تحليله:**

• 🪙 **الذهب** - XAU/USD
• ⚪ **الفضة** - XAG/USD  
• 🛢️ **النفط** - USOIL
• 💶 **يورو/دولار** - EUR/USD
• 💷 **جنيه/دولار** - GBP/USD
• 💴 **دولار/ين** - USD/JPY
• ₿ **بتكوين** - BTC/USD
• 🔷 **إيثريوم** - ETH/USD

🎯 **ما تحصل عليه:**
✓ تحليل فني كامل بالمؤشرات
✓ نقاط دخول وخروج دقيقة
✓ توصيات تداول مبررة
✓ إدارة مخاطر محسوبة

**اختر أحد الأصول بالأسفل 👇**
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )

async def handle_button_click(update: Update, context):
    """معالجة النقر على الأزرار"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("asset_"):
        asset_name = data.replace("asset_", "")
        await send_detailed_analysis(query, asset_name)
    
    elif data == "all_prices":
        await send_all_prices(query)
    
    elif data == "help":
        await send_help(query)

async def send_detailed_analysis(query, asset_name):
    """إرسال تحليل مفصل للأصل المختار"""
    asset_info = ASSETS.get(asset_name)
    
    if not asset_info:
        await query.message.reply_text("❌ هذا الأصل غير متوفر")
        return
    
    symbol = asset_info["symbol"]
    emoji = asset_info["emoji"]
    
    # رسالة الانتظار
    processing_msg = await query.message.reply_text(f"⏳ جاري تحليل {emoji} {asset_name}...")
    
    try:
        # جلب البيانات والتحليل
        df = technical_analyzer.get_historical_data(symbol, "15min", 100)
        
        if df is None or len(df) < 50:
            await processing_msg.edit_text(f"❌ لا توجد بيانات كافية لتحليل {asset_name}")
            return
        
        # حساب المؤشرات الفنية
        df = technical_analyzer.calculate_technical_indicators(df)
        
        if df is None:
            await processing_msg.edit_text(f"❌ خطأ في تحليل {asset_name}")
            return
        
        current_data = df.iloc[-1]
        current_price = current_data['close']
        
        # تحليل أنماط الشموع
        candlestick_patterns = technical_analyzer.analyze_candlestick_patterns(df)
        
        # توليد إشارات التداول
        trading_signals = technical_analyzer.generate_trading_signals(df)
        
        # حساب نقاط الدخول والخروج
        entry_exit_points = technical_analyzer.calculate_entry_exit_points(df, current_price)
        
        # بناء التقرير المفصل
        message = f"🎯 **التقرير الفني المتقدم**\n"
        message += f"📊 **{emoji} {asset_name}**\n\n"
        
        # السعر والمؤشرات السريعة
        message += f"💰 **السعر الحالي:** `{current_price:.{4 if '/' in symbol else 2}f}`\n"
        message += f"📈 **RSI (14):** `{current_data['rsi']:.1f}` {'🔴' if current_data['rsi'] > 70 else '🟢' if current_data['rsi'] < 30 else '⚪'}\n"
        message += f"📊 **MACD:** `{current_data['macd']:.4f}` {'🟢' if current_data['macd'] > current_data['macd_signal'] else '🔴'}\n\n"
        
        # أنماط الشموع
        if candlestick_patterns:
            message += "🕯️ **أنماط الشموع:**\n"
            for pattern in candlestick_patterns:
                message += f"• {pattern}\n"
            message += "\n"
        
        # إشارات التداول
        if trading_signals and trading_signals['signals']:
            message += f"📢 **إشارات التداول ({trading_signals['confidence']}% ثقة):**\n"
            for signal in trading_signals['signals'][:5]:  # أول 5 إشارات فقط
                message += f"• {signal}\n"
            message += "\n"
        
        # نقاط الدخول والخروج
        if entry_exit_points:
            # تحديد التوصية الرئيسية
            if trading_signals['confidence'] >= 60:
                main_action = "🟢 الشراء"
                main_entry = entry_exit_points['buy']['entry']
                main_stop = entry_exit_points['buy']['stop_loss']
                main_targets = entry_exit_points['buy']['take_profit']
                risk_reward = entry_exit_points['buy']['risk_reward']
            else:
                main_action = "🔴 البيع" 
                main_entry = entry_exit_points['sell']['entry']
                main_stop = entry_exit_points['sell']['stop_loss']
                main_targets = entry_exit_points['sell']['take_profit']
                risk_reward = entry_exit_points['sell']['risk_reward']
            
            message += f"🎯 **التوصية:** {main_action}\n"
            message += f"📍 **نقطة الدخول:** `{main_entry}`\n"
            message += f"🛡️ **وقف الخسارة:** `{main_stop}`\n"
            message += f"🎯 **أهداف الربح:**\n"
            for i, target in enumerate(main_targets, 1):
                message += f"   {i}. `{target}`\n"
            message += f"⚖️ **نسبة المخاطرة:** 1:`{risk_reward}`\n\n"
        
        # المعلومات الإضافية
        message += f"⏰ **الإطار الزمني:** 15 دقيقة\n"
        message += f"🕒 **وقت التحليل:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += "---\n"
        message += "⚠️ *هذا تحليل فني للمساعدة في اتخاذ القرار وليس نصيحة استثمارية*"
        
        # حذف رسالة الانتظار وإرسال النتيجة
        await processing_msg.delete()
        await query.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        
    except Exception as e:
        await processing_msg.edit_text(f"❌ حدث خطأ أثناء تحليل {asset_name}: {str(e)}")

async def send_all_prices(query):
    """إرسال جميع الأسعار الحية"""
    processing_msg = await query.message.reply_text("📡 جاري جرب جميع الأسعار...")
    
    message = "💹 **الأسعار الحية لجميع الأصول**\n\n"
    
    for asset_name, asset_info in ASSETS.items():
        symbol = asset_info["symbol"]
        emoji = asset_info["emoji"]
        
        try:
            # جلب السعر الحالي
            df = technical_analyzer.get_historical_data(symbol, "1min", 2)
            if df is not None and len(df) > 0:
                current_price = df.iloc[-1]['close']
                prev_price = df.iloc[-2]['close'] if len(df) > 1 else current_price
                
                change = ((current_price - prev_price) / prev_price) * 100
                change_emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                
                message += f"{emoji} **{asset_name}:** `{current_price:.{4 if '/' in symbol else 2}f}` {change_emoji} {change:+.2f}%\n"
            else:
                message += f"{emoji} **{asset_name}:** ❌ غير متوفر\n"
                
        except:
            message += f"{emoji} **{asset_name}:** ❌ خطأ\n"
    
    message += f"\n🕒 **آخر تحديث:** {datetime.now().strftime('%H:%M:%S')}"
    
    await processing_msg.delete()
    await query.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

async def send_help(query):
    """إرسال رسالة المساعدة"""
    help_text = """
🆘 **كيفية استخدام البوت:**

🎯 **التحليل الفني المتقدم:**
1. اختر الأصل الذي تريد تحليله
2. انتظر قليلاً لجلب البيانات
3. احصل على تحليل كامل بالمؤشرات

📊 **المؤشرات المتضمنة:**
• RSI - مؤشر القوة النسبية
• MACD - تقارب/تباعد المتوسطات  
• المتوسطات المتحركة
• Bollinger Bands
• أنماط الشموع اليابانية

🎯 **ما تحصل عليه:**
• توصيات تداول مبررة
• نقاط دخول وخروج دقيقة
• إدارة مخاطر محسوبة
• نسبة مكافأة/مخاطرة

⚠️ **ملاحظة مهمة:**
هذا التحليل للمساعدة في اتخاذ القرار وليس نصيحة استثمارية. always do your own research!

📞 **للتواصل والدعم:** @[اسم_حسابك]
"""
    
    await query.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

def main():
    if TWELVE_DATA_API_KEY == "مفتاحك_هنا":
        print("❌ ضع مفتاح Twelve Data في المتغير TWELVE_DATA_API_KEY")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button_click))
    
    print("🎯 بوت التحليل الفني مع الواجهة التفاعلية شغال!")
    print("📱 يحتوي على أزرار سهلة الاستخدام")
    print("📊 يجلب تحليلات فنية متقدمة")
    
    app.run_polling()

if __name__ == '__main__':
    main()