import logging
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import Application, CommandHandler, InlineQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
import math

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token bot dari @BotFather
BOT_TOKEN = "8188917154:AAFW8Vx_e30McMUb7GNvLMs3I0Dynf0wLO0"

def calculate_bmi(weight, height):
    """Menghitung BMI dan memberikan kategori"""
    height_in_meters = height / 100
    bmi = weight / (height_in_meters ** 2)
    
    if bmi < 18.5:
        category = "Kurus"
        recommendation = "⚠️ Disarankan untuk menambah berat badan dengan makanan bergizi tinggi protein dan karbohidrat kompleks"
    elif 18.5 <= bmi < 23:
        category = "Normal (Ideal)"
        recommendation = "✅ Berat badan Anda sudah ideal! Pertahankan pola makan sehat dan olahraga teratur"
    elif 23 <= bmi < 25:
        category = "Kelebihan Berat Badan"
        recommendation = "⚠️ Perhatikan asupan makanan dan tingkatkan aktivitas fisik untuk mencegah obesitas"
    elif 25 <= bmi < 30:
        category = "Obesitas Level 1"
        recommendation = "🚨 Disarankan untuk menurunkan berat badan dengan diet seimbang dan olahraga teratur"
    else:
        category = "Obesitas Level 2"
        recommendation = "🚨 Sangat disarankan untuk konsultasi dengan dokter dan melakukan program penurunan berat badan"
    
    return bmi, category, recommendation

def calculate_ideal_weight(height, gender="pria"):
    """Menghitung berat badan ideal berdasarkan rumus Broca"""
    if gender.lower() == "pria":
        ideal = (height - 100) - ((height - 100) * 0.1)
    else:
        ideal = (height - 100) - ((height - 100) * 0.15)
    return ideal

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"🤖 Selamat datang di IdealWeightBot, {user.first_name}!\n\n"
        "Saya bisa membantu Anda mengecek berat badan ideal dan BMI.\n\n"
        "📝 Cara penggunaan di INLINE MODE:\n"
        "1. Ketik `@ideaIweightbot berat_tinggi` di chat mana saja\n"
        "2. Contoh: `@ideaIweightbot 65_170`\n"
        "3. Atau: `@ideaIweightbot 55_160_wanita`\n\n"
        "💬 Cara penggunaan di PRIVATE CHAT:\n"
        "• Gunakan command: `/bmi berat tinggi gender`\n"
        "• Contoh: `/bmi 65 170 pria`\n"
        "• Atau: `/bmi 55 160 wanita`\n\n"
        "ℹ️ Command lainnya:\n"
        "• `/chart` - Lihat kategori BMI\n"
        "• `/help` - Bantuan lengkap",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /help"""
    await update.message.reply_text(
        "ℹ️ Bantuan IdealWeightBot\n\n"
        "📊 FITUR BMI TERSEDIA!\n\n"
        "1. INLINE MODE (di grup/chat mana saja):\n"
        "• Ketik: `@ideaIweightbot 65_170`\n"
        "• Format: `berat_tinggi_gender`\n"
        "• Gender opsional (default: pria)\n\n"
        "2. PRIVATE CHAT (langsung dengan bot):\n"
        "• `/bmi 65 170 pria`\n"
        "• `/bmi 55 160 wanita`\n"
        "• `/ideal 170 pria` - hitung berat ideal\n\n"
        "3. COMMAND LAIN:\n"
        "• `/chart` - Lihat chart kategori BMI\n"
        "• `/info` - Informasi tentang BMI\n\n"
        "📋 CONTOH PENGGUNAAN:\n"
        "• Inline: `@ideaIweightbot 65_170_pria`\n"
        "• Private: `/bmi 65 170 pria`",
        parse_mode="Markdown"
    )

async def bmi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /bmi di private chat"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Format salah!\n\n"
            "Gunakan: /bmi berat tinggi gender\n"
            "Contoh: /bmi 65 170 pria\n"
            "Atau: /bmi 55 160 wanita"
        )
        return
    
    try:
        weight = float(context.args[0])
        height = float(context.args[1])
        gender = context.args[2].lower() if len(context.args) > 2 else "pria"
        
        # Validasi input
        if weight <= 0 or height <= 0:
            await update.message.reply_text("❌ Berat dan tinggi harus angka positif!")
            return
        
        if weight > 300 or height > 300:
            await update.message.reply_text("❌ Berat/tinggi tidak realistis!")
            return
        
        # Kalkulasi
        bmi, category, recommendation = calculate_bmi(weight, height)
        ideal_weight = calculate_ideal_weight(height, gender)
        weight_diff = weight - ideal_weight
        
        if weight_diff > 2:
            weight_status = f"📈 Kelebihan {abs(weight_diff):.1f} kg"
        elif weight_diff < -2:
            weight_status = f"📉 Kekurangan {abs(weight_diff):.1f} kg"
        else:
            weight_status = "✅ Berat badan ideal"
        
        # Buat response
        message_text = (
            "🏥 HASIL CEK BERAT BADAN & BMI\n\n"
            f"• Berat Badan: {weight} kg\n"
            f"• Tinggi Badan: {height} cm\n"
            f"• Gender: {gender.title()}\n"
            f"• BMI: {bmi:.1f}\n"
            f"• Kategori: {category}\n"
            f"• Berat Ideal: {ideal_weight:.1f} kg\n"
            f"• Status: {weight_status}\n\n"
            f"💡 Saran Kesehatan:\n{recommendation}\n\n"
            f"Hasil ini hanya sebagai referensi, konsultasi dengan dokter untuk hasil yang akurat"
        )
        
        await update.message.reply_text(message_text)
        
    except ValueError:
        await update.message.reply_text(
            "❌ Input tidak valid!\n\n"
            "Pastikan berat dan tinggi berupa angka.\n"
            "Contoh: /bmi 65 170 pria"
        )

async def ideal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /ideal - hitung berat ideal saja"""
    if len(context.args) < 1:
        await update.message.reply_text(
            "❌ Format salah!\n\n"
            "Gunakan: /ideal tinggi gender\n"
            "Contoh: /ideal 170 pria\n"
            "Atau: /ideal 160 wanita"
        )
        return
    
    try:
        height = float(context.args[0])
        gender = context.args[1].lower() if len(context.args) > 1 else "pria"
        
        if height <= 0 or height > 300:
            await update.message.reply_text("❌ Tinggi harus antara 1-300 cm!")
            return
        
        ideal_weight = calculate_ideal_weight(height, gender)
        
        message_text = (
            "🎯 BERAT BADAN IDEAL\n\n"
            f"• Tinggi Badan: {height} cm\n"
            f"• Gender: {gender.title()}\n"
            f"• Berat Ideal: {ideal_weight:.1f} kg\n\n"
            f"Rentang sehat: {ideal_weight-2:.1f} - {ideal_weight+2:.1f} kg\n\n"
            f"💡 Tips: Pertahankan berat badan dalam rentang ini untuk kesehatan optimal"
        )
        
        await update.message.reply_text(message_text)
        
    except ValueError:
        await update.message.reply_text(
            "❌ Input tidak valid!\n\n"
            "Pastikan tinggi berupa angka.\n"
            "Contoh: /ideal 170 pria"
        )

async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /chart"""
    chart_text = (
        "📊 CHART INDEKS MASSA TUBUH (BMI)\n\n"
        "Kategori BMI:\n"
        "• Kurus: BMI < 18.5\n"
        "• Normal (Ideal): BMI 18.5 - 22.9\n" 
        "• Kelebihan Berat Badan: BMI 23.0 - 24.9\n"
        "• Obesitas Level 1: BMI 25.0 - 29.9\n"
        "• Obesitas Level 2: BMI >= 30.0\n\n"
        "Rumus BMI:\n"
        "BMI = Berat (kg) / (Tinggi (m) × Tinggi (m))\n\n"
        "Keterangan:\n"
        "• Kurus: Perlu meningkatkan asupan gizi\n"
        "• Normal: Pertahankan pola hidup sehat\n"
        "• Kelebihan: Waspada, tingkatkan aktivitas fisik\n"
        "• Obesitas: Disarankan konsultasi dokter\n\n"
        "Standard Kementerian Kesehatan Indonesia"
    )
    
    await update.message.reply_text(chart_text)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /info"""
    info_text = (
        "ℹ️ INFORMASI TENTANG BMI\n\n"
        "Apa itu BMI?\n"
        "BMI (Body Mass Index) atau Indeks Massa Tubuh adalah ukuran yang digunakan untuk menilai apakah berat badan seseorang proporsional dengan tinggi badannya.\n\n"
        "Mengapa BMI penting?\n"
        "• Menilai risiko kesehatan terkait berat badan\n"
        "• Memantau status gizi\n"
        "• Sebagai panduan program diet/sehat\n\n"
        "Keterbatasan BMI:\n"
        "• Tidak memperhitungkan massa otot\n"
        "• Tidak membedakan distribusi lemak\n"
        "• Hasil dapat berbeda untuk atlet/lansia\n\n"
        "Konsultasi dengan tenaga kesehatan untuk penilaian yang lebih akurat"
    )
    
    await update.message.reply_text(info_text)

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk inline query"""
    query = update.inline_query.query
    
    if not query:
        # Tampilkan contoh penggunaan saat query kosong
        results = [
            InlineQueryResultArticle(
                id="1",
                title="Contoh Penggunaan - BMI Calculator",
                description="Format: berat_tinggi atau berat_tinggi_gender",
                input_message_content=InputTextMessageContent(
                    "🤖 IdealWeightBot - BMI Calculator\n\n"
                    "📋 Contoh Penggunaan:\n"
                    "• 65_170 - Berat 65kg, Tinggi 170cm\n"
                    "• 55_160_wanita - Berat 55kg, Tinggi 160cm, Wanita\n"
                    "• 70_175_pria - Berat 70kg, Tinggi 175cm, Pria\n\n"
                    "Gunakan format: berat_tinggi_gender"
                )
            )
        ]
        await update.inline_query.answer(results, cache_time=1)
        return
    
    try:
        # Parsing input user
        parts = query.split('_')
        
        if len(parts) < 2:
            results = [
                InlineQueryResultArticle(
                    id="1",
                    title="Format Salah!",
                    description="Gunakan format: berat_tinggi atau berat_tinggi_gender",
                    input_message_content=InputTextMessageContent(
                        "❌ Format Input Salah!\n\n"
                        "Gunakan format: berat_tinggi atau berat_tinggi_gender\n\n"
                        "Contoh:\n"
                        "• 65_170\n"
                        "• 55_160_wanita\n"
                        "• 70_175_pria"
                    )
                )
            ]
        else:
            weight = float(parts[0])
            height = float(parts[1])
            gender = parts[2].lower() if len(parts) > 2 else "pria"
            
            # Validasi input
            if weight <= 0 or height <= 0:
                raise ValueError("Berat dan tinggi harus positif")
            
            if weight > 300 or height > 300:
                raise ValueError("Berat/tinggi tidak realistis")
            
            # Kalkulasi
            bmi, category, recommendation = calculate_bmi(weight, height)
            ideal_weight = calculate_ideal_weight(height, gender)
            weight_diff = weight - ideal_weight
            
            if weight_diff > 2:
                weight_status = f"📈 Kelebihan {abs(weight_diff):.1f} kg"
            elif weight_diff < -2:
                weight_status = f"📉 Kekurangan {abs(weight_diff):.1f} kg"
            else:
                weight_status = "✅ Berat badan ideal"
            
            # Buat hasil
            message_text = (
                "🏥 HASIL CEK BERAT BADAN & BMI\n\n"
                f"• Berat Badan: {weight} kg\n"
                f"• Tinggi Badan: {height} cm\n"
                f"• Gender: {gender.title()}\n"
                f"• BMI: {bmi:.1f}\n"
                f"• Kategori: {category}\n"
                f"• Berat Ideal: {ideal_weight:.1f} kg\n"
                f"• Status: {weight_status}\n\n"
                f"💡 Saran: {recommendation}\n\n"
                f"Hasil oleh @ideaIweightbot • Konsultasi dokter untuk hasil akurat"
            )
            
            results = [
                InlineQueryResultArticle(
                    id="1",
                    title=f"BMI: {bmi:.1f} ({category})",
                    description=f"Berat: {weight}kg, Tinggi: {height}cm, Ideal: {ideal_weight:.1f}kg",
                    input_message_content=InputTextMessageContent(message_text)
                )
            ]
    
    except (ValueError, IndexError) as e:
        # Handle error
        results = [
            InlineQueryResultArticle(
                id="error",
                title="Format Input Salah!",
                description="Gunakan format: berat_tinggi atau berat_tinggi_gender",
                input_message_content=InputTextMessageContent(
                    "❌ Format Input Salah!\n\n"
                    "Gunakan format: berat_tinggi atau berat_tinggi_gender\n\n"
                    "Contoh:\n"
                    "• 65_170\n"
                    "• 55_160_wanita\n"
                    "• 70_175_pria\n\n"
                    "Pastikan berat dan tinggi berupa angka"
                )
            )
        ]
    
    await update.inline_query.answer(results, cache_time=1)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan biasa"""
    await update.message.reply_text(
        "🤖 IdealWeightBot - BMI Calculator\n\n"
        "Gunakan command berikut:\n"
        "• `/bmi berat tinggi gender` - Hitung BMI\n"
        "• `/ideal tinggi gender` - Hitung berat ideal\n"
        "• `/chart` - Lihat kategori BMI\n"
        "• `/info` - Informasi tentang BMI\n"
        "• `/help` - Bantuan lengkap\n\n"
        "💡 Contoh: `/bmi 65 170 pria`",
        parse_mode="Markdown"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk error"""
    logging.error(f"Error: {context.error}")

def main():
    """Main function"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("bmi", bmi_command))
    application.add_handler(CommandHandler("ideal", ideal_command))
    application.add_handler(CommandHandler("chart", chart_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(InlineQueryHandler(inline_query))
    
    # Handler untuk pesan biasa
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    print("🤖 IdealWeightBot sedang berjalan...")
    print("📍 Nama bot: @ideaIweightbot")
    print("📱 Mode: Inline & Private Chat")
    application.run_polling()

if __name__ == "__main__":
    main()