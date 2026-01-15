"""
Oracle Cloud VM.Standard.A1.Flex Auto-Register Application

Continuously attempts to create a free tier ARM instance until successful,
then sends a Telegram notification.

Usage:
    python main.py              # Run normally
    python main.py --dry-run    # Validate config without creating instance
    python main.py --test-telegram  # Send a test Telegram message
"""

import sys
import time
import argparse
from datetime import datetime

from config import Config
from oci_client import OCIClient
from telegram_notifier import TelegramNotifier


def get_timestamp() -> str:
    """Get current timestamp for logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def print_banner():
    """Print application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║     Oracle Cloud VM.Standard.A1.Flex Auto-Register            ║
║     Automatically claim your free ARM instance!               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def dry_run(config: Config, oci_client: OCIClient, notifier: TelegramNotifier):
    """Validate configuration without creating an instance."""
    print("\n🔍 Running in DRY-RUN mode (no instance will be created)\n")
    
    # Validate configuration
    print("Validating configuration...")
    if not config.validate():
        print("❌ Configuration validation failed")
        return False
    
    # Validate OCI credentials
    print("\nValidating OCI credentials...")
    if not oci_client.validate_credentials():
        print("❌ OCI credential validation failed")
        return False
    
    print("\n✅ All validations passed! Ready to run.")
    print(f"\n📋 Configuration Summary:")
    print(f"   • Region: {config.oci_region}")
    print(f"   • Availability Domain: {config.availability_domain}")
    print(f"   • Instance Name: {config.instance_name}")
    print(f"   • Shape: VM.Standard.A1.Flex")
    print(f"   • OCPUs: {config.ocpus}")
    print(f"   • Memory: {config.memory_gb} GB")
    print(f"   • Retry Interval: {config.retry_interval} seconds")
    
    return True


def test_telegram(notifier: TelegramNotifier):
    """Send a test Telegram notification."""
    print("\n📱 Sending test Telegram notification...")
    success = notifier.send_message("🧪 Test notification from Oracle Cloud Auto-Register!\n\nIf you see this message, your Telegram configuration is correct.")
    
    if success:
        print("✅ Test notification sent successfully!")
    else:
        print("❌ Failed to send test notification. Check your bot token and chat ID.")
    
    return success


def run_main_loop(config: Config, oci_client: OCIClient, notifier: TelegramNotifier):
    """Main application loop - continuously attempt to create instance."""
    print(f"\n🚀 Starting auto-register loop...")
    print(f"   • Target: VM.Standard.A1.Flex in {config.oci_region}")
    print(f"   • Retry interval: {config.retry_interval} seconds")
    print(f"   • Press Ctrl+C to stop\n")
    
    # Send startup notification
    notifier.send_startup_message()
    
    attempt = 0
    
    while True:
        attempt += 1
        print(f"[{get_timestamp()}] Attempt #{attempt} - Trying to create instance...")
        
        result = oci_client.create_instance()
        
        if result["success"]:
            # SUCCESS! Instance created
            print(f"\n🎉 SUCCESS! Instance created on attempt #{attempt}")
            print(f"   Instance ID: {result['instance']['id']}")
            print(f"   Public IP: {result['instance']['public_ip']}")
            
            # Send Telegram notification
            notifier.send_success_message(result["instance"])
            
            print("\n✅ Telegram notification sent. Exiting...")
            return True
        
        elif result["is_capacity_error"]:
            # Expected capacity error - keep trying
            print(f"[{get_timestamp()}] ⏳ Out of capacity. Retrying in {config.retry_interval}s...")
        
        else:
            # Other error - log but continue
            print(f"[{get_timestamp()}] ❌ Error: {result['message']}")
            print(f"[{get_timestamp()}] ⏳ Will retry in {config.retry_interval}s...")
        
        # Wait before next attempt
        time.sleep(config.retry_interval)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Oracle Cloud VM.Standard.A1.Flex Auto-Register"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without creating an instance"
    )
    parser.add_argument(
        "--test-telegram",
        action="store_true",
        help="Send a test Telegram notification"
    )
    args = parser.parse_args()
    
    print_banner()
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = Config()
        
        # Initialize clients
        oci_client = OCIClient(config)
        notifier = TelegramNotifier(config)
        
        if args.dry_run:
            success = dry_run(config, oci_client, notifier)
            sys.exit(0 if success else 1)
        
        if args.test_telegram:
            success = test_telegram(notifier)
            sys.exit(0 if success else 1)
        
        # Run main loop
        run_main_loop(config, oci_client, notifier)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user. Exiting...")
        sys.exit(0)
    
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
