import discord
from discord.ext import commands
import asyncio
import os

# 1. إعداد الصلاحيات الكاملة للبوت
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # تذكري تفعيلها أيضاً من صفحة المطورين ليعمل الترحيب!

# 2. إنشاء البوت مع البريفكس (!) 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'=== Elysia Bot Is Online ===')
    print(f'Logged in as: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'============================')
    # تعيين حالة البوت (Watching)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Elysia Community"))

# 3. أمر الترحيب التلقائي بالأعضاء الجدد
@bot.event
async def on_member_join(member):
    # ابحثي عن اسم روم الترحيب في سيرفركِ (welcome أو الترحيب)
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if channel:
        embed = discord.Embed(
            title="🌸 عضو جديد في ديارنا! 🌸",
            description=f"أهلاً بك يا {member.mention} في سيرفرنا المميز!\nنورتنا بوجودك، أتمنى لك وقتاً ممتعاً معنا.",
            color=discord.Color.from_rgb(255, 182, 193) # لون وردي ناعم يناسب إيليسيا
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"أنت العضو رقم {len(member.guild.members)}")
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            print(f"خطأ: البوت لا يملك صلاحية إرسال الرسائل في روم الترحيب.")

# 4. الأوامر الإدارية (قفل، فتح، طرد، باند، مسح)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """امر مسح الشات: !clear 10"""
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 تم مسح {amount} رسالة بنجاح!")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """امر طرد عضو: !kick @user"""
    try:
        await member.kick(reason=reason)
        await ctx.send(f"👤 تم طرد {member.mention} من السيرفر. السبب: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ لا يمكنني طرد هذا العضو! قد تكون رتبته أعلى من رتبة البوت.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    """امر تبنيد عضو: !ban @user"""
    try:
        await member.ban(reason=reason)
        await ctx.send(f"🚫 تم حظر {member.mention} نهائياً. السبب: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ لا يمكنني حظر هذا العضو! قد تكون رتبته أعلى من رتبة البوت.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def mute_channel(ctx):
    """امر قفل الروم الحالية"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم قفل الروم بنجاح. الكتابة مغلقة الآن!")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unmute_channel(ctx):
    """امر فتح الروم الحالية"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 تم فتح الروم بنجاح. الكتابة متاحة للجميع!")

# 5. أوامر عامة وتفاعلية

@bot.command()
async def ping(ctx):
    """امر فحص سرعة اتصال البوت"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! سرعة الاتصال: {latency}ms")

@bot.command()
async def server(ctx):
    """امر معلومات السيرفر"""
    embed = discord.Embed(title=f"📊 معلومات سيرفر {ctx.guild.name}", color=discord.Color.blue())
    embed.add_field(name="صاحب السيرفر:", value=ctx.guild.owner.mention, inline=True)
    embed.add_field(name="عدد الأعضاء:", value=str(ctx.guild.member_count), inline=True)
    embed.add_field(name="عدد الرومات:", value=str(len(ctx.guild.channels)), inline=True)
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    """امر معلومات الحساب: !userinfo @user"""
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 هوية الحساب: {member.name}", color=discord.Color.green())
    # تم تعديل السطر بالأسفل لإزالة discriminator القديم والاعتماد على الاسم الجديد والاسم المستعار
    embed.add_field(name="الاسم في السيرفر:", value=member.display_name, inline=True)
    embed.add_field(name="تاريخ الانضمام للديسكورد:", value=member.created_at.strftime("%Y-%m-%d"), inline=False)
    embed.add_field(name="تاريخ الانضمام للسيرفر:", value=member.joined_at.strftime("%Y-%m-%d"), inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

# 6. تشغيل البوت بسحب التوكن بشكل آمن من Railway Variables
TOKEN = os.environ.get("TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("خطأ: لم يتم العثور على متغير TOKEN في إعدادات المنصة! تأكدي من إضافته في تبويب Variables.")
