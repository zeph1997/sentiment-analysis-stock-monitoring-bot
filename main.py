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
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    headlines = soup.find_all("a", class_="tab-link-news")
    return headlines

def get_sentiment_score(ticker):
    score = 0
    num = 0
    vader = SentimentIntensityAnalyzer()
    headlines = get_headlines(ticker)
    for i in headlines:
        score += vader.polarity_scores(i.text)["compound"]
        num += 1
    print(score)
    return score/num

@bot.message_handler(commands=["start"])
def start_message(m):
    bot.send_message(m.from_user.id,"Hello! I am a bot that will look through all the news of the stock ticker you have given me on finviz and determine if the news in recent days are good or bad.")

@bot.message_handler(func=lambda m: "$" in m.text)
def search_stock(m):
    userText = m.text.split("$")
    tickers = []
    for i in range(1,len(userText)):
        tickers.append(userText[i].split(" ")[0].upper())
    for j in tickers:
        bot.send_message(m.from_user.id,f"Sentiment Analysis for ${j}: {get_sentiment_score(j)}\n\n")

bot.polling()