import telebot
from bs4 import BeautifulSoup
import secrets
import requests
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

bot = telebot.TeleBot(secrets.get_secret())

def get_headlines(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    response = requests.get(url, headers=headers, allow_redirects=False)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        headlines = soup.find_all("a", class_="tab-link-news")
        return headlines
    return False

def get_sentiment_score(ticker):
    score = 0
    num = 0
    vader = SentimentIntensityAnalyzer()
    headlines = get_headlines(ticker)
    if headlines:
        for i in headlines:
            score += vader.polarity_scores(i.text)["compound"]
            num += 1
        return score/num
    return False

@bot.message_handler(commands=["start"])
def start_message(m):
    bot.send_message(m.from_user.id,"👋 Hello! I am a bot that will look through all the news of the stock ticker you have given me on finviz and determine if the news in recent days are good or bad.\n\nHere is an example of how to use me\n'$C $V $FB'\n\nIf you have any issues, use the /help command!")

@bot.message_handler(commands=["help"])
def help_message(m):
    bot.send_message(m.from_user.id,"🆘 Hey there! Let me help you with using this bot!\n\nTo send in a code, please ensure that the stock ticker is prefixed with the '$' sign. E.g. $C or $FB.\n\nNext, ensure that there is a space after the ticker number!\n'$FB stock' ✅\n'$FBstock' ❌\n\nYou can send me multiple stock tickers in one message, just ensure that you follow the rules above!\nThat's all there is to it! Happy investing!")

@bot.message_handler(func=lambda m: "$" in m.text)
def search_stock(m):
    userText = m.text.split("$")
    tickers = []
    for i in range(1,len(userText)):
        tickers.append(userText[i].split(" ")[0].upper())
    for j in tickers:
        score = get_sentiment_score(j)
        if score:
            sentiment = "Neutral / Mixed 😐"
            if score < -1:
                sentiment = "Negative 🔻😢"
            elif score > 1:
                sentiment = "Positive 🔼😄"
            bot.send_message(m.from_user.id,f"🧮 Sentiment Score for ${j}: {score:.3f}\nThe sentiment is *{sentiment}*\n\n",parse_mode="Markdown")
        else:
            bot.send_message(m.from_user.id,f"Hey, it seems like ${j} does not exist. Please modify it before I search again!")

bot.polling()