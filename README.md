# 🚀 Oracle Cloud VM.Standard.A1.Flex Auto-Register

Automatically claim Oracle Cloud's **free tier ARM instance** when capacity becomes available!

Oracle's free ARM instances (VM.Standard.A1.Flex) are extremely popular and often show "Out of host capacity" errors. This script continuously retries until successful, then notifies you via Telegram.

## ✨ Features

- 🔄 **Continuous retry** with configurable interval (default: 60 seconds)
- 📱 **Telegram notification** when instance is created successfully
- 🔐 **Environment-based configuration** for easy deployment
- ☁️ **Deploy anywhere** - locally, Render.com, Railway, etc.
- ✅ **Dry-run mode** to validate configuration before running

---

## 📋 What You Need (Checklist)

Before starting, make sure you have:

- [ ] Oracle Cloud Account ([Sign up here](https://www.oracle.com/cloud/free/))
- [ ] Telegram Account
- [ ] Python 3.8+ installed ([Download](https://www.python.org/downloads/))

You will collect these values during setup:

| Item | Example Value |
|------|---------------|
| User OCID | `ocid1.user.oc1..aaaaaaaak3s...` |
| Tenancy OCID | `ocid1.tenancy.oc1..aaaaaaaayr7...` |
| API Key Fingerprint | `a1:b2:c3:d4:e5:f6:g7:h8:i9:j0:k1:l2:m3:n4:o5:p6` |
| Private Key File | `oci_private_key.pem` |
| Compartment OCID | `ocid1.compartment.oc1..aaaaaaaayz...` |
| Subnet OCID | `ocid1.subnet.oc1.ap-singapore-2.aaaaaaaaab...` |
| Image OCID | `ocid1.image.oc1.ap-singapore-2.aaaaaaaacd...` |
| Availability Domain | `OUGC:AP-SINGAPORE-2-AD-1` |
| SSH Public Key | `ssh-rsa AAAAB3NzaC1yc2EAAAA...` |
| Telegram Bot Token | `7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| Telegram Chat ID | `123456789` |

---

## 🔧 Step-by-Step Setup Guide

### Step 1: Log in to Oracle Cloud Console

1. Go to **[https://cloud.oracle.com/](https://cloud.oracle.com/)**
2. Enter your **Cloud Account Name** (tenancy name) and click **Next**
3. Log in with your credentials

---

### Step 2: Get Your User OCID

1. Click the **👤 Profile icon** (top-right corner)
2. Click **My profile**

   ![Profile Menu](https://docs.oracle.com/en-us/iaas/Content/Resources/Images/console_profile_menu.png)

3. On your profile page, find **OCID** under your username
4. Click **Copy** to copy it

**Example User OCID:**
```
ocid1.user.oc1..aaaaaaaak3s7hnvt7gcoqpvxqof6ywn3kgmua7r7cx5nuri6w7l5fa
```

---

### Step 3: Get Your Tenancy OCID

1. Click the **👤 Profile icon** (top-right corner)
2. Click **Tenancy: [Your Tenancy Name]**
3. On the Tenancy Details page, find **OCID**
4. Click **Copy** to copy it

**Example Tenancy OCID:**
```
ocid1.tenancy.oc1..aaaaaaaayr7ht5kh6loqw4a5szdr3pufq7xc5nuri6w7l5fa
```

---

### Step 4: Generate API Key

1. Go to **[https://cloud.oracle.com/identity/domains/my-profile/api-keys](https://cloud.oracle.com/identity/domains/my-profile/api-keys)**
   
   Or: Profile icon → My profile → API keys (left menu)

2. Click **Add API key**

3. Select **Generate API key pair**

4. Click **Download private key** button
   - Save the file as `oci_private_key.pem`
   - **IMPORTANT: Keep this file safe! You cannot download it again.**

5. Click **Add**

6. A popup will show configuration. Copy the **fingerprint** value

**Example Fingerprint:**
```
a1:b2:c3:d4:e5:f6:07:18:29:3a:4b:5c:6d:7e:8f:90
```

---

### Step 5: Get Compartment OCID

1. Go to **[https://cloud.oracle.com/identity/compartments](https://cloud.oracle.com/identity/compartments)**
   
   Or: Menu (☰) → Identity & Security → Compartments

2. Click on your compartment name (usually the **root** compartment with your tenancy name)

3. Copy the **OCID**

**Example Compartment OCID:**
```
ocid1.compartment.oc1..aaaaaaaayzk7hnvt7gcoqpvxqof6ywn3kppzzz
```

> **Note:** If you're using the root compartment, it will have the same OCID as your tenancy.

---

### Step 6: Create VCN (Virtual Cloud Network)

If you don't have a VCN yet:

1. Go to **[https://cloud.oracle.com/networking/vcns](https://cloud.oracle.com/networking/vcns)**
   
   Or: Menu (☰) → Networking → Virtual cloud networks

2. Make sure you're in the **ap-singapore-2** region (check top-right dropdown)

3. Click **Start VCN Wizard**

4. Select **Create VCN with Internet Connectivity** → Click **Start VCN Wizard**

5. Enter a name like `my-vcn` and keep other defaults

6. Click **Next** → **Create**

7. Wait for it to complete (takes ~30 seconds)

---

### Step 7: Get Subnet OCID

1. Go to **[https://cloud.oracle.com/networking/vcns](https://cloud.oracle.com/networking/vcns)**

2. Click on your VCN name (e.g., `my-vcn`)

3. Under **Subnets**, click on the **public subnet** (e.g., `Public Subnet-my-vcn`)

4. Copy the **OCID**

**Example Subnet OCID:**
```
ocid1.subnet.oc1.ap-singapore-2.aaaaaaaab2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7
```

---

### Step 8: Get Image OCID

1. Go to **[https://cloud.oracle.com/compute/instances/create?region=ap-singapore-2](https://cloud.oracle.com/compute/instances/create?region=ap-singapore-2)**

2. Scroll down to **Image and shape** section

3. Click **Change image**

4. Select your preferred OS:
   - **Oracle Linux 8** (recommended, lightweight)
   - **Ubuntu 22.04** (popular choice)
   - **Canonical Ubuntu 24.04** (latest)

5. Make sure **Image type** shows **aarch64** (ARM architecture)

6. Click **Select image**

7. To get the OCID, go to: **[https://docs.oracle.com/en-us/iaas/images/](https://docs.oracle.com/en-us/iaas/images/)**
   - Search for your image
   - Find your region `ap-singapore-2`
   - Copy the OCID

**Example Image OCID (Oracle Linux 8 aarch64):**
```
ocid1.image.oc1.ap-singapore-2.aaaaaaaa5yd4bgiec5zz33hnu6sjzwcze5mcan6z4p6thbd6q
```

> **Alternative:** Go to Menu → Compute → Custom images → All images tab, then filter by OS and copy OCID.

---

### Step 9: Get Availability Domain

1. Go to **[https://cloud.oracle.com/compute/instances/create?region=ap-singapore-2](https://cloud.oracle.com/compute/instances/create?region=ap-singapore-2)**

2. Look at the **Placement** section

3. Click the **Availability domain** dropdown

4. Note the full name (you'll see something like):

**Example Availability Domain:**
```
OUGC:AP-SINGAPORE-2-AD-1
```

> **Note:** The prefix (like `OUGC`) is unique to your tenancy.

---

### Step 10: Generate SSH Key

You need an SSH key to access your instance after it's created.

**Windows (PowerShell):**
```powershell
ssh-keygen -t rsa -b 4096 -f "$HOME\.ssh\oracle_key" -N '""'
```

**Linux/Mac:**
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/oracle_key -N ""
```

Then copy the **public key** content:

**Windows:**
```powershell
Get-Content "$HOME\.ssh\oracle_key.pub"
```

**Linux/Mac:**
```bash
cat ~/.ssh/oracle_key.pub
```

**Example SSH Public Key:**
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDLqp7Xk3Fqpz123abc...very long string...xyz== your-email@example.com
```

---

### Step 11: Create Telegram Bot

1. Open Telegram and search for **[@BotFather](https://t.me/BotFather)**

2. Start a chat and send: `/newbot`

3. Follow the prompts:
   - Enter a **display name** (e.g., `Oracle Notifier`)
   - Enter a **username** ending with `bot` (e.g., `my_oracle_notifier_bot`)

4. BotFather will give you an **API token**

**Example Bot Token:**
```
7123456789:AAHk5hf7J3KLMNopqrstuVWXyz123456789
```

5. **IMPORTANT:** Start a chat with your new bot
   - Search for your bot by its username
   - Click **Start** or send `/start`
   - This allows the bot to send you messages!

---

### Step 12: Get Your Telegram Chat ID

1. Search for **[@userinfobot](https://t.me/userinfobot)** on Telegram

2. Send `/start`

3. It will reply with your **ID**

**Example Chat ID:**
```
123456789
```

---

## 🚀 Installation & Running

### Option 1: Run Locally

1. **Download/Clone this repository**
   ```powershell
   git clone https://github.com/foxy1402/my-oracle.git
   cd my-oracle
   ```

2. **Install Python dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Create your configuration file**
   ```powershell
   copy .env.example .env
   ```

4. **Edit `.env` file** with Notepad or any text editor
   
   Fill in ALL values you collected in the steps above:
   
   ```ini
   # Oracle Cloud Credentials
   OCI_USER_OCID=ocid1.user.oc1..aaaaaaaak3s7hnvt7gcoqpvxqof6ywn3kgmua7r7cx5nuri6w7l5fa
   OCI_TENANCY_OCID=ocid1.tenancy.oc1..aaaaaaaayr7ht5kh6loqw4a5szdr3pufq7xc5nuri6w7l5fa
   OCI_FINGERPRINT=a1:b2:c3:d4:e5:f6:07:18:29:3a:4b:5c:6d:7e:8f:90
   OCI_PRIVATE_KEY_PATH=./oci_private_key.pem
   OCI_REGION=ap-singapore-2
   
   # Instance Configuration
   OCI_COMPARTMENT_OCID=ocid1.compartment.oc1..aaaaaaaayzk7hnvt7gcoqpvxqof6ywn3kppzzz
   OCI_SUBNET_OCID=ocid1.subnet.oc1.ap-singapore-2.aaaaaaaab2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7
   OCI_IMAGE_OCID=ocid1.image.oc1.ap-singapore-2.aaaaaaaa5yd4bgiec5zz33hnu6sjzwcze5mcan6z4p6thbd6q
   OCI_AVAILABILITY_DOMAIN=OUGC:AP-SINGAPORE-2-AD-1
   OCI_INSTANCE_NAME=free-arm-instance
   OCI_OCPUS=4
   OCI_MEMORY_GB=24
   OCI_SSH_PUBLIC_KEY=ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDLqp7Xk3F...
   
   # Telegram Notification
   TELEGRAM_BOT_TOKEN=7123456789:AAHk5hf7J3KLMNopqrstuVWXyz123456789
   TELEGRAM_CHAT_ID=123456789
   
   # Retry Configuration
   RETRY_INTERVAL_SECONDS=60
   ```

5. **Copy your private key file** to the project folder
   - The file you downloaded in Step 4 (`oci_private_key.pem`)
   - Place it in the same folder as `main.py`

6. **Validate your configuration**
   ```powershell
   python main.py --dry-run
   ```
   
   You should see:
   ```
   ✅ Configuration validated successfully
   ✅ OCI credentials validated successfully
   ```

7. **Test Telegram notification**
   ```powershell
   python main.py --test-telegram
   ```
   
   Check your Telegram - you should receive a test message!

8. **Run the auto-register script**
   ```powershell
   python main.py
   ```
   
   The script will keep running and retry every 60 seconds until it creates an instance.

---

### Option 2: Deploy to Render.com (Free 24/7)

Render.com is a free hosting platform that can run your script 24/7.

#### Step 1: Push Code to GitHub (Already Done! ✅)

Your code is at: `https://github.com/foxy1402/my-oracle`

#### Step 2: Create Render Account

1. Go to **[https://render.com/](https://render.com/)**
2. Click **Get Started for Free**
3. Sign up with **GitHub** (recommended for easy connection)

#### Step 3: Create Background Worker

1. Go to **[Render Dashboard](https://dashboard.render.com/)**
2. Click **New +** → **Background Worker**
3. Connect your GitHub account if prompted
4. Select repository: `foxy1402/my-oracle`
5. Configure:
   - **Name:** `oracle-auto-register`
   - **Region:** Singapore (or any)
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
6. Click **Create Background Worker**

#### Step 4: Add Environment Variables

1. In your Background Worker, go to **Environment** tab
2. Click **Add Environment Variable** for each:

| Key | Value |
|-----|-------|
| `OCI_USER_OCID` | Your user OCID |
| `OCI_TENANCY_OCID` | Your tenancy OCID |
| `OCI_FINGERPRINT` | Your API key fingerprint |
| `OCI_PRIVATE_KEY_CONTENT` | **Entire content of your private key** (see below) |
| `OCI_REGION` | `ap-singapore-2` |
| `OCI_COMPARTMENT_OCID` | Your compartment OCID |
| `OCI_SUBNET_OCID` | Your subnet OCID |
| `OCI_IMAGE_OCID` | Your image OCID |
| `OCI_AVAILABILITY_DOMAIN` | Your availability domain |
| `OCI_INSTANCE_NAME` | `free-arm-instance` |
| `OCI_OCPUS` | `4` |
| `OCI_MEMORY_GB` | `24` |
| `OCI_SSH_PUBLIC_KEY` | Your SSH public key |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |
| `RETRY_INTERVAL_SECONDS` | `60` |

#### For the Private Key (OCI_PRIVATE_KEY_CONTENT):

1. Open your `oci_private_key.pem` file in Notepad
2. Select ALL the content (Ctrl+A)
3. Copy it (Ctrl+C)
4. In Render, paste it as the value for `OCI_PRIVATE_KEY_CONTENT`

The content should look like:
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
... (many lines) ...
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
-----END RSA PRIVATE KEY-----
```

#### Step 5: Deploy

1. Click **Save Changes** after adding all environment variables
2. Render will automatically build and deploy your worker
3. Check the **Logs** tab to see if it's running

You should see output like:
```
Loading configuration...
🚀 Starting auto-register loop...
   • Target: VM.Standard.A1.Flex in ap-singapore-2
   • Retry interval: 60 seconds
```

---

## 🔧 Configuration Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `OCI_USER_OCID` | ✅ | Your Oracle Cloud user identifier |
| `OCI_TENANCY_OCID` | ✅ | Your tenancy (account) identifier |
| `OCI_FINGERPRINT` | ✅ | API key fingerprint |
| `OCI_PRIVATE_KEY_PATH` | ⚠️ | Path to private key file (for local use) |
| `OCI_PRIVATE_KEY_CONTENT` | ⚠️ | Private key content (for Render deployment) |
| `OCI_REGION` | ✅ | Oracle Cloud region (default: `ap-singapore-2`) |
| `OCI_COMPARTMENT_OCID` | ✅ | Compartment where VM will be created |
| `OCI_SUBNET_OCID` | ✅ | Network subnet for the VM |
| `OCI_IMAGE_OCID` | ✅ | Operating system image |
| `OCI_AVAILABILITY_DOMAIN` | ✅ | Data center location |
| `OCI_INSTANCE_NAME` | ❌ | Display name (default: `free-arm-instance`) |
| `OCI_OCPUS` | ❌ | Number of CPUs (default: `4`, max: `4`) |
| `OCI_MEMORY_GB` | ❌ | RAM in GB (default: `24`, max: `24`) |
| `OCI_SSH_PUBLIC_KEY` | ✅ | SSH key for accessing the VM |
| `TELEGRAM_BOT_TOKEN` | ✅ | Telegram bot API token |
| `TELEGRAM_CHAT_ID` | ✅ | Your Telegram user ID |
| `RETRY_INTERVAL_SECONDS` | ❌ | Seconds between attempts (default: `60`) |

> ⚠️ Use either `OCI_PRIVATE_KEY_PATH` (local) or `OCI_PRIVATE_KEY_CONTENT` (cloud deployment)

---

## ⚠️ Important Notes

1. **Free Tier Limits**
   - Maximum **4 OCPUs** and **24GB RAM** total for ARM instances
   - You can split across multiple instances (e.g., 2x 2 OCPU, 12GB each)

2. **Patience Required**
   - It may take **hours, days, or even weeks** for capacity to become available
   - The script will keep trying until successful

3. **Don't Run Multiple Instances**
   - Running multiple copies will make more API calls but won't help
   - Stick to one running instance of this script

4. **Render Free Tier**
   - Background workers may spin down after inactivity
   - Use your external cron job to ping the service periodically to keep it alive

---

## 🐛 Troubleshooting

### "Authentication failed"
- Double-check your API key fingerprint
- Ensure private key file content is correct (including `-----BEGIN` and `-----END` lines)
- Verify User OCID and Tenancy OCID match your account

### "Authorization failed"
- Your user might not have permission to create instances
- Try using the root compartment OCID

### "Invalid parameter"
- Ensure all OCIDs are from the **same region** (`ap-singapore-2`)
- Make sure Image OCID is for **aarch64** (ARM) architecture

### "LimitExceeded"
- You've reached free tier limits
- Delete existing ARM instances before trying again

### Telegram not receiving messages
- Make sure you've sent `/start` to your bot first
- Verify bot token and chat ID are correct
- Test with: `python main.py --test-telegram`

---

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| Oracle Cloud Console | [https://cloud.oracle.com/](https://cloud.oracle.com/) |
| Create Instance Page | [https://cloud.oracle.com/compute/instances/create?region=ap-singapore-2](https://cloud.oracle.com/compute/instances/create?region=ap-singapore-2) |
| API Keys | [https://cloud.oracle.com/identity/domains/my-profile/api-keys](https://cloud.oracle.com/identity/domains/my-profile/api-keys) |
| Compartments | [https://cloud.oracle.com/identity/compartments](https://cloud.oracle.com/identity/compartments) |
| VCNs | [https://cloud.oracle.com/networking/vcns](https://cloud.oracle.com/networking/vcns) |
| Image List | [https://docs.oracle.com/en-us/iaas/images/](https://docs.oracle.com/en-us/iaas/images/) |
| Telegram BotFather | [https://t.me/BotFather](https://t.me/BotFather) |
| Telegram userinfobot | [https://t.me/userinfobot](https://t.me/userinfobot) |
| Render Dashboard | [https://dashboard.render.com/](https://dashboard.render.com/) |

---

## 📄 License

MIT License - feel free to use and modify!
