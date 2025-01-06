import asyncio
import aiohttp
from threading import Thread
from flask import Flask, request, jsonify
from admission_info_spider import WebScraper
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

async def send_webhook(url: str, data: dict):
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        raise ValueError("WEBHOOK_URL environment variable is not set")
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=data) as response:
            return await response.json()

def process_scraping_and_notify(url: str):
    try:
        scraper = WebScraper(url)
        links = scraper.scrape()
        
        webhook_data = {
            'status': 'success',
            'url': url,
            'links': links
        }
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_webhook(url, webhook_data))
        loop.close()
        
    except Exception as e:
        print(f"Error during scraping and notification: {str(e)}")
        return jsonify({'error': 'Server error'}), 500

@app.route('/ok', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

@app.route('/scrape', methods=['POST'])
def scrape_endpoint():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url'].strip()
    
    Thread(target=process_scraping_and_notify, args=(url,)).start()
    
    return jsonify({
        'status': 'processing',
        'message': 'Request accepted'
    }), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000) 