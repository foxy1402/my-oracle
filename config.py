"""
Configuration loader for Oracle Cloud VM Auto-Register App.
Loads all settings from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class that loads settings from environment variables."""
    
    def __init__(self):
        # Oracle Cloud Credentials
        self.oci_user_ocid = self._get_required("OCI_USER_OCID")
        self.oci_tenancy_ocid = self._get_required("OCI_TENANCY_OCID")
        self.oci_fingerprint = self._get_required("OCI_FINGERPRINT")
        self.oci_region = os.getenv("OCI_REGION", "ap-singapore-1")
        
        # Support both file path and direct content (for platforms like Render)
        self.oci_private_key_path = os.getenv("OCI_PRIVATE_KEY_PATH")
        self.oci_private_key_content = os.getenv("OCI_PRIVATE_KEY_CONTENT")
        
        if not self.oci_private_key_path and not self.oci_private_key_content:
             raise ValueError("Missing OCI private key. Set OCI_PRIVATE_KEY_PATH or OCI_PRIVATE_KEY_CONTENT.")
        
        # Instance Configuration
        self.compartment_ocid = self._get_required("OCI_COMPARTMENT_OCID")
        self.subnet_ocid = self._get_required("OCI_SUBNET_OCID")
        self.image_ocid = self._get_required("OCI_IMAGE_OCID")
        self.availability_domain = self._get_required("OCI_AVAILABILITY_DOMAIN")
        self.instance_name = os.getenv("OCI_INSTANCE_NAME", "free-arm-instance")
        self.ocpus = int(os.getenv("OCI_OCPUS", "4"))
        self.memory_gb = int(os.getenv("OCI_MEMORY_GB", "24"))
        self.ssh_public_key = self._get_required("OCI_SSH_PUBLIC_KEY")
        
        # Telegram Configuration
        self.telegram_bot_token = self._get_required("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = self._get_required("TELEGRAM_CHAT_ID")
        
        # Retry Configuration
        self.retry_interval = int(os.getenv("RETRY_INTERVAL_SECONDS", "60"))
    
    def _get_required(self, key: str) -> str:
        """Get a required environment variable or raise an error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Missing required environment variable: {key}")
        return value
    
    def get_oci_config(self) -> dict:
        """Return OCI configuration dictionary for SDK."""
        config = {
            "user": self.oci_user_ocid,
            "tenancy": self.oci_tenancy_ocid,
            "fingerprint": self.oci_fingerprint,
            "region": self.oci_region,
        }
        
        if self.oci_private_key_content:
            # Clean up the key content (handle newlines from env vars)
            key_content = self.oci_private_key_content.replace("\\n", "\n")
            if "-----BEGIN RSA PRIVATE KEY-----" not in key_content:
                 # Try to fix if it's just the body or has other formatting issues
                 # This is a basic attempt, user should provide correct format
                 pass
            config["key_content"] = key_content
        else:
            config["key_file"] = self.oci_private_key_path
            
        return config
    
    def validate(self) -> bool:
        """Validate that all required configurations are present."""
        try:
            # Check for private key
            if self.oci_private_key_path and not os.path.exists(self.oci_private_key_path):
                print(f"❌ Private key file not found: {self.oci_private_key_path}")
                return False
            
            if not self.oci_private_key_path and not self.oci_private_key_content:
                print("❌ No private key provided (file or content)")
                return False
            
            # Basic OCID format validation
            required_ocids = [
                ("User OCID", self.oci_user_ocid),
                ("Tenancy OCID", self.oci_tenancy_ocid),
                ("Compartment OCID", self.compartment_ocid),
                ("Subnet OCID", self.subnet_ocid),
                ("Image OCID", self.image_ocid),
            ]
            
            for name, ocid in required_ocids:
                if not ocid.startswith("ocid1."):
                    print(f"❌ Invalid {name} format: {ocid}")
                    return False
            
            print("✅ Configuration validated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False


if __name__ == "__main__":
    # Test configuration loading
    try:
        config = Config()
        config.validate()
        print(f"\n📍 Region: {config.oci_region}")
        print(f"💻 Instance: {config.instance_name}")
        print(f"🔧 OCPUs: {config.ocpus}, Memory: {config.memory_gb}GB")
        print(f"⏱️  Retry interval: {config.retry_interval}s")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
