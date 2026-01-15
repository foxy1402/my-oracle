"""
Telegram notification module for sending alerts.
Uses simple HTTP requests to Telegram Bot API.
"""

import requests
from config import Config


class TelegramNotifier:
    """Send notifications via Telegram Bot API."""
    
    API_URL = "https://api.telegram.org/bot{token}/sendMessage"
    
    def __init__(self, config: Config = None):
        if config is None:
            config = Config()
        self.bot_token = config.telegram_bot_token
        self.chat_id = config.telegram_chat_id
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message via Telegram.
        
        Args:
            message: The message text to send
            parse_mode: Message format (HTML or Markdown)
        
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            url = self.API_URL.format(token=self.bot_token)
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                print("✅ Telegram notification sent successfully")
                return True
            else:
                print(f"❌ Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send Telegram notification: {e}")
            return False
    
    def send_success_message(self, instance_details: dict) -> bool:
        """
        Send a success notification with instance details.
        
        Args:
            instance_details: Dictionary containing instance information
        """
        message = f"""
🎉 <b>Oracle Cloud Instance Created Successfully!</b>

<b>Instance Details:</b>
• <b>Name:</b> {instance_details.get('name', 'N/A')}
• <b>Shape:</b> {instance_details.get('shape', 'N/A')}
• <b>Region:</b> {instance_details.get('region', 'N/A')}
• <b>Availability Domain:</b> {instance_details.get('availability_domain', 'N/A')}
• <b>Public IP:</b> {instance_details.get('public_ip', 'Not yet assigned')}
• <b>State:</b> {instance_details.get('lifecycle_state', 'N/A')}

<b>Instance ID:</b>
<code>{instance_details.get('id', 'N/A')}</code>

🚀 Your free ARM instance is now running!
        """.strip()
        
        return self.send_message(message)
    
    def send_error_message(self, error_message: str) -> bool:
        """
        Send an error notification (for critical errors only).
        
        Args:
            error_message: The error description
        """
        message = f"""
⚠️ <b>Oracle Cloud Auto-Register Error</b>

<b>Error:</b> {error_message}

The script will continue retrying...
        """.strip()
        
        return self.send_message(message)
    
    def send_startup_message(self) -> bool:
        """Send a notification that the script has started."""
        message = """
🚀 <b>Oracle Cloud Auto-Register Started</b>

The script is now running and will attempt to create your VM.Standard.A1.Flex instance.

You will be notified when the instance is created successfully!
        """.strip()
        
        return self.send_message(message)


if __name__ == "__main__":
    # Test Telegram notification
    try:
        notifier = TelegramNotifier()
        notifier.send_message("🧪 Test notification from Oracle Cloud Auto-Register!")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
