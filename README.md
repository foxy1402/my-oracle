# 🚀 Oracle Cloud VM.Standard.A1.Flex Auto-Register

Automatically claim Oracle Cloud's **free tier ARM instance** when capacity becomes available!

Oracle's free ARM instances (VM.Standard.A1.Flex) are extremely popular and often show "Out of host capacity" errors. This script continuously retries until successful, then notifies you via Telegram.

## ✨ Features

- 🔄 **Continuous retry** with configurable interval
- 📱 **Telegram notification** when instance is created
- 🔐 **Environment-based configuration** for easy deployment
- ☁️ **Deploy anywhere** - locally, Render.com, Railway, etc.
- ✅ **Dry-run mode** to validate configuration

## 📋 Prerequisites

1. **Oracle Cloud Account** (Free Tier)
   - Sign up: [https://www.oracle.com/cloud/free/](https://www.oracle.com/cloud/free/)

2. **Telegram Bot**
   - Create one using [@BotFather](https://t.me/BotFather)

3. **Python 3.8+**
   - Download: [https://www.python.org/downloads/](https://www.python.org/downloads/)

---

## 🔧 Setup Guide

### Step 1: Get Oracle Cloud API Credentials

1. **Log in to Oracle Cloud Console**
   - [https://cloud.oracle.com/](https://cloud.oracle.com/)

2. **Get your User OCID**
   - Click your profile icon (top right) → **My profile**
   - Copy the **OCID** shown under your username
   - Looks like: `ocid1.user.oc1..aaaaaaaaxxxxxxxxxx`

3. **Get your Tenancy OCID**
   - Click your profile icon → **Tenancy: [Your Tenancy Name]**
   - Copy the **OCID** shown on the page
   - Looks like: `ocid1.tenancy.oc1..aaaaaaaaxxxxxxxxxx`

4. **Generate API Keys**
   - Go to **Profile** → **My profile** → **API keys**
   - Direct link: [https://cloud.oracle.com/identity/domains/my-profile/api-keys](https://cloud.oracle.com/identity/domains/my-profile/api-keys)
   - Click **Add API key**
   - Select **Generate API key pair**
   - **Download the private key** (save as `oci_private_key.pem`)
   - Click **Add**
   - Copy the **Fingerprint** shown (e.g., `aa:bb:cc:dd:...`)

### Step 2: Get Instance Configuration Values

1. **Get Compartment OCID**
   - Go to **Identity & Security** → **Compartments**
   - Direct link: [https://cloud.oracle.com/identity/compartments](https://cloud.oracle.com/identity/compartments)
   - Click on your compartment (or root compartment)
   - Copy the **OCID**

2. **Create a VCN (Virtual Cloud Network)** if you don't have one
   - Go to **Networking** → **Virtual cloud networks**
   - Direct link: [https://cloud.oracle.com/networking/vcns](https://cloud.oracle.com/networking/vcns)
   - Click **Start VCN Wizard** → **Create VCN with Internet Connectivity**
   - Use default settings and create

3. **Get Subnet OCID**
   - Go to your VCN → **Subnets**
   - Click on the **public subnet**
   - Copy the **OCID**
   - Looks like: `ocid1.subnet.oc1.ap-singapore-1.aaaaaaaaxxxxxxxxxx`

4. **Get Image OCID**
   - Browse available images: [https://docs.oracle.com/en-us/iaas/images/](https://docs.oracle.com/en-us/iaas/images/)
   - **Important**: Choose an **aarch64** (ARM) image!
   - Popular choices for Singapore (`ap-singapore-1`):
     - **Oracle Linux 8 (aarch64)**: Check the image list
     - **Ubuntu 22.04 (aarch64)**: Check the image list
   - Or go to **Compute** → **Custom images** → **Image OCID catalog**
   - Direct link: [https://cloud.oracle.com/compute/images](https://cloud.oracle.com/compute/images)

5. **Get Availability Domain**
   - Go to **Compute** → **Instances** → **Create instance**
   - Direct link: [https://cloud.oracle.com/compute/instances/create](https://cloud.oracle.com/compute/instances/create)
   - Look at the **Placement** section → **Availability domain** dropdown
   - Copy the full name (e.g., `XXXX:AP-SINGAPORE-1-AD-1`)

### Step 3: Set Up Telegram Bot

1. **Create a Bot**
   - Open Telegram and search for [@BotFather](https://t.me/BotFather)
   - Send `/newbot`
   - Follow the prompts to set name and username
   - Copy the **API token** (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Your Chat ID**
   - Search for [@userinfobot](https://t.me/userinfobot) on Telegram
   - Send `/start`
   - It will reply with your **ID** (e.g., `123456789`)

3. **Start Your Bot**
   - Search for your bot by its username
   - Send `/start` to it (important! Bot can only message you after you start it)

### Step 4: Generate SSH Key

You need an SSH key to access your instance once created.

**Windows (PowerShell):**
```powershell
ssh-keygen -t rsa -b 4096 -f "$HOME\.ssh\oracle_key"
```

**Linux/Mac:**
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/oracle_key
```

Copy the contents of the **public key** file (`oracle_key.pub`).

---

## 🚀 Installation

### Option 1: Run Locally

1. **Clone or download this repository**

2. **Install dependencies**
   ```powershell
   cd free-oracle-cloud
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```powershell
   copy .env.example .env
   ```
   
4. **Edit `.env`** with your values (use Notepad or any text editor)

5. **Copy your private key**
   - Place `oci_private_key.pem` in the project folder

6. **Validate configuration**
   ```powershell
   python main.py --dry-run
   ```

7. **Test Telegram notification**
   ```powershell
   python main.py --test-telegram
   ```

8. **Run the script**
   ```powershell
   python main.py
   ```

### Option 2: Deploy to Render.com (Free, 24/7)

1. **Push code to GitHub**
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/free-oracle-cloud.git
   git push -u origin main
   ```

2. **Create Render.com account**
   - Sign up: [https://render.com/](https://render.com/)

3. **Create new Background Worker**
   - Go to Dashboard → **New** → **Background Worker**
   - Connect your GitHub repository
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

4. **Add Environment Variables**
   - Go to **Environment** tab
   - Add all variables from `.env` file
   - For `OCI_PRIVATE_KEY_PATH`, you'll need to use a different approach (see below)

5. **Handling Private Key on Render**
   
   Modify `config.py` to support key content directly:
   ```python
   # Add this as an alternative to file path
   self.oci_private_key_content = os.getenv("OCI_PRIVATE_KEY_CONTENT")
   ```
   
   Then paste your private key content as an environment variable.

### Option 3: Deploy to Railway.app

1. **Sign up**: [https://railway.app/](https://railway.app/)
2. **New Project** → **Deploy from GitHub repo**
3. Add environment variables in the **Variables** tab
4. Railway will auto-detect Python and run `main.py`

---

## 📖 Usage

### Normal Run
```powershell
python main.py
```

### Validate Configuration (Dry Run)
```powershell
python main.py --dry-run
```

### Test Telegram Notification
```powershell
python main.py --test-telegram
```

---

## 🔧 Configuration Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `OCI_USER_OCID` | Your user OCID | `ocid1.user.oc1..aaa...` |
| `OCI_TENANCY_OCID` | Your tenancy OCID | `ocid1.tenancy.oc1..aaa...` |
| `OCI_FINGERPRINT` | API key fingerprint | `aa:bb:cc:dd:...` |
| `OCI_PRIVATE_KEY_PATH` | Path to private key | `./oci_private_key.pem` |
| `OCI_REGION` | Oracle Cloud region | `ap-singapore-1` |
| `OCI_COMPARTMENT_OCID` | Compartment OCID | `ocid1.compartment.oc1..aaa...` |
| `OCI_SUBNET_OCID` | Subnet OCID | `ocid1.subnet.oc1...` |
| `OCI_IMAGE_OCID` | OS image OCID | `ocid1.image.oc1...` |
| `OCI_AVAILABILITY_DOMAIN` | Availability domain | `XXXX:AP-SINGAPORE-1-AD-1` |
| `OCI_INSTANCE_NAME` | Instance display name | `free-arm-instance` |
| `OCI_OCPUS` | Number of OCPUs (max 4) | `4` |
| `OCI_MEMORY_GB` | Memory in GB (max 24) | `24` |
| `OCI_SSH_PUBLIC_KEY` | SSH public key | `ssh-rsa AAAA...` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | `123456789:ABC...` |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | `123456789` |
| `RETRY_INTERVAL_SECONDS` | Seconds between retries | `60` |

---

## 🌏 Oracle Cloud Regions

| Region | Identifier |
|--------|------------|
| Singapore | `ap-singapore-1` |
| Tokyo | `ap-tokyo-1` |
| Seoul | `ap-seoul-1` |
| Mumbai | `ap-mumbai-1` |
| Sydney | `ap-sydney-1` |
| Frankfurt | `eu-frankfurt-1` |
| London | `uk-london-1` |
| US East (Ashburn) | `us-ashburn-1` |
| US West (Phoenix) | `us-phoenix-1` |

Full list: [https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm](https://docs.oracle.com/en-us/iaas/Content/General/Concepts/regions.htm)

---

## ⚠️ Important Notes

1. **Free Tier Limits**
   - Maximum 4 OCPUs and 24GB RAM total for ARM instances
   - You can split across multiple instances (e.g., 2x 2 OCPU)

2. **Retry Interval**
   - Recommended: 60 seconds
   - Don't set too low to avoid rate limiting

3. **Patience Required**
   - It may take hours or even days for capacity to become available
   - The script will keep trying until successful

4. **One Instance at a Time**
   - Don't run multiple instances of this script simultaneously

---

## 🐛 Troubleshooting

### "Authentication failed"
- Check your API key fingerprint matches
- Ensure private key file is correct and not corrupted
- Verify user OCID and tenancy OCID

### "Authorization failed"
- Ensure your user has permissions to create instances
- Check compartment OCID is correct

### "Invalid parameter"
- Verify all OCIDs are from the same region
- Ensure image OCID is for aarch64 (ARM)

### "LimitExceeded"
- You've reached free tier limits
- Delete existing instances or reduce OCPU/memory

### Telegram not working
- Ensure you've started a chat with your bot
- Verify bot token and chat ID are correct
- Test with `python main.py --test-telegram`

---

## 📄 License

MIT License - feel free to use and modify!

---

## 🔗 Useful Links

- [Oracle Cloud Console](https://cloud.oracle.com/)
- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
- [OCI Python SDK Documentation](https://docs.oracle.com/en-us/iaas/tools/python/latest/)
- [Telegram BotFather](https://t.me/BotFather)
- [Telegram @userinfobot](https://t.me/userinfobot)
