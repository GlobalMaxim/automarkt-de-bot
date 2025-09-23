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

## How it works
### Choose the language
<p align="left">
  <img width="367" height="161" alt="image" src="https://github.com/user-attachments/assets/4879b28d-ee2e-4515-9e87-9f9207e906ab" />
</p>

### Main menu
<p align="left">
  <img width="373" height="125" alt="image" src="https://github.com/user-attachments/assets/c1ce7203-ed2c-4932-841a-22822f8bd3a3" />
</p>

### Select category
<p align="left">
  <img width="373" height="160" alt="image" src="https://github.com/user-attachments/assets/7bf47eeb-a2a5-4782-be59-6a04c7ad4ba0" />
</p>

### Step-by-step creating add
<p align="left">
  <img width="370" height="174" alt="image" src="https://github.com/user-attachments/assets/bcc78b79-b55b-4628-afd7-d0b0a151977f" />

</p>

### Publish final result
<p align="left">
  <img width="308" height="567" alt="image" src="https://github.com/user-attachments/assets/49c44822-0c9e-47a5-a191-fc2e26ae029a" />

</p>





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
---

## Run with Docker Compose 🐳

The project can also be launched using Docker Compose.  
Make sure you have created a **.env** file with all required variables.

### Start the services
```bash
docker compose up -d --build
