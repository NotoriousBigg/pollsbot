# 📚 Alan Turing Quiz Bot  

A Telegram bot that automatically sends quiz polls from an external API. The bot can be added to any group or channel and will send periodic quiz polls.  

## 🚀 Features  
✅ Fetches quiz questions from [quizapi.io](https://quizapi.io/)  
✅ Sends quiz-style polls with multiple-choice answers  
✅ Auto-reposts polls every 30 minutes  
✅ Works in both **groups** and **channels**   

# DEMO
You can view a demo bot on telegram here: [@AlanTuringBot](https://t.me/AlanTuringBot)

## 🛠️ Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/your-repo/quiz-bot.git
cd quiz-bot
```
### Install Dependencies
```bash
pip install -r requirements.txt
```
### Rename sample.env to .env and add the following values
```angular2html
BOT_TOKEN=your-telegram-bot-token
QUIZ_API_KEY=your-quizapi-key

```
### Run The Bot.
```bash
python3 main.py
```
## 🔧 Usage  

### ➤ Start Command  
Send `/start` to receive a welcome message.  

### ➤ Manual Quiz Poll  
Use `/poll` to fetch and send a quiz poll manually. This will send a new poll after 30 minutes 

### ➤ Auto-Posting  
The bot **automatically sends quiz polls** every 30 minutes in **any group or channel** it is added to.  


### Contact me on Telegram @RealOptimusPrime for any question.