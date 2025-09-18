# Car Sale Telegram Bot 🚗  

This project is a **Telegram bot** that allows users to easily create and submit advertisements for selling their cars.  
Once an ad is submitted, it is automatically published to a specified Telegram channel.  

---

## Features  

- Simple and user-friendly interface for submitting car sale ads.  
- Step-by-step form for filling out ad details:  
  - Car brand and model  
  - Year of manufacture  
  - Mileage  
  - Price  
  - Description  
  - Contact information  
  - Photos of the car  
- Automatic posting of ads to a **Telegram channel**.  
- Admins can moderate ads before publishing (optional).  
- Built with **aiogram** (async framework for Telegram bots).  

---

## Installation  

### 1. Clone the repository  
```bash
git clone https://github.com/GlobalMaxim/automarkt-de-bot.git
```
```
cd automarkt-de-bot
```
### Local setup:

1. Use python3.11 
2. Create virtual enviroment
```bash
`python3.11 -m venv .venv`
```
```bash
`source .venv/bin/activate`
```
3. Install requirements
 ```bash
`pip install -r requirements.txt`
```
4. Create a .env file in the root directory
```env
TOKEN=your_telegram_bot_token
ADMIN_ID=123456789,987654321
CHANEL_ID=987654321
MYSQL_URI=mysql+pymysql://user:password@localhost:3306/dbname
```
5. Run bot with
```bash
python3 run.py
```
