# Upwork Job Notifier Bot

## Overview

This project provides a Telegram bot that notifies users of new job postings on Upwork based on their search keywords. The bot uses RSS feeds to fetch job updates and sends notifications to users via Telegram.

## Prerequisites

- Python 3.x
- `pip` (Python package installer)
- A GitHub account
- A Render.com account
- A Telegram account

## Setup Instructions

### 1. **Create a Telegram Bot**

1. **Start a Chat with BotFather**:
   - Open Telegram and search for the [BotFather](https://t.me/botfather).
   - Start a chat with BotFather by clicking the "Start" button or sending `/start`.

2. **Create a New Bot**:
   - Send the command `/newbot` to BotFather.
   - Follow the prompts to set a name and username for your bot.
   - Once created, BotFather will provide you with an API token. Copy this token; you will need it later.

### 2. **Prepare Your Environment**

1. **Clone the Repository**:
   - Clone the repository to your local machine:
     ```bash
     git clone https://github.com/yourusername/your-repository.git
     ```
   - Navigate to the project directory:
     ```bash
     cd your-repository
     ```

2. **Install Dependencies**:
   - Install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

### 3. **Configure Environment Variables**

1. **Create a `.env` File**:
   - In the project directory, create a file named `.env`.

2. **Add Environment Variables**:
   - Open the `.env` file and add the following lines:
     ```
     API_KEY=your_telegram_bot_api_key
     BASE_RSS_URL=https://www.upwork.com/ab/feed/jobs/rss?paging=NaN-undefined&q=
     ```

   - Replace `your_telegram_bot_api_key` with the API token you received from BotFather.

### 4. **Deploy to Render**

1. **Create a New Web Service**:
   - Log in to [Render.com](https://render.com).
   - Click on **"New+"** and select **"Web Service"**.

2. **Connect Your GitHub Repository**:
   - Choose **"GitHub"** as your deployment source.
   - Select the repository containing your code.

3. **Configure the Service**:
   - **Name**: Enter a name for your service.
   - **Region**: Choose a region close to your users.
   - **Branch**: Select the branch to deploy (usually `main` or `master`).

4. **Set Build and Start Commands**:
   - **Build Command**: Specify `pip install -r requirements.txt` to install dependencies.
   - **Start Command**: Specify `python main.py` to start your application.

5. **Add Environment Variables**:
   - Go to the **"Environment"** tab.
   - Add the environment variables from your `.env` file (`API_KEY` and `BASE_RSS_URL`).

6. **Deploy the Service**:
   - Click **"Deploy"** to start the deployment process.

### 5. **Using the Bot**

1. **Start the Bot**:
   - Once deployed, the bot will start running automatically.

2. **Interact with the Bot**:
   - Start a chat with your bot on Telegram (search for the bot's username).
   - Use the following commands:
     - **`/start`**: Shows a welcome message.
     - **`/help`**: Provides a list of available commands.
     - **`/add <search keyword>`**: Adds a new search keyword.
     - **`/view`**: Shows a list of your search keywords.
     - **`/edit <index> <search keyword>`**: Edits an existing keyword.
     - **`/remove <index>`**: Removes a keyword.

### Troubleshooting

- **Check Logs**: View the application logs on Render to debug issues.
- **Verify Environment Variables**: Ensure all required environment variables are correctly set.

---
