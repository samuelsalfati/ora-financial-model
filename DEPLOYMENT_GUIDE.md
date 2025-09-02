# Deployment Guide - Ora Living Financial Model

## Option 1: Streamlit Community Cloud (RECOMMENDED - Free & Easy)

### Steps:
1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit deployment"
   git push origin main
   ```

2. **Sign up for Streamlit Community Cloud**
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - It's completely free for public repos (or private with limited apps)

3. **Deploy your app**
   - Click "New app"
   - Select your GitHub repo: `ora-va-step1`
   - Branch: `main`
   - Main file path: `app_simple.py`
   - Click "Deploy"

4. **Share with your team**
   - You'll get a URL like: `https://ora-financial-model.streamlit.app`
   - Share this URL with your team
   - Add password protection if needed (in Streamlit settings)

### Advantages:
- ✅ Free hosting
- ✅ Automatic updates when you push to GitHub
- ✅ Easy sharing with custom URL
- ✅ Built-in authentication options
- ✅ No server management

---

## Option 2: Local Network Sharing (Quick Testing)

Run this command and share your local IP:
```bash
streamlit run app_simple.py --server.address 0.0.0.0 --server.port 8501
```

Your team can access it at: `http://YOUR_IP:8501`
(Find your IP: Mac = `ifconfig | grep inet`, Windows = `ipconfig`)

---

## Option 3: Ngrok Tunnel (Temporary Sharing)

1. **Install ngrok**
   ```bash
   brew install ngrok  # Mac
   # Or download from https://ngrok.com
   ```

2. **Run Streamlit**
   ```bash
   streamlit run app_simple.py
   ```

3. **Create tunnel**
   ```bash
   ngrok http 8501
   ```

4. **Share the ngrok URL** (looks like: https://abc123.ngrok.io)

---

## Option 4: Cloud Platforms (Production Ready)

### Heroku (Low cost)
1. Create `Procfile`:
   ```
   web: streamlit run app_simple.py --server.port $PORT --server.address 0.0.0.0
   ```

2. Create `runtime.txt`:
   ```
   python-3.11.8
   ```

3. Deploy:
   ```bash
   heroku create ora-financial-model
   git push heroku main
   ```

### AWS EC2 / Google Cloud / Azure
- More complex but gives full control
- Costs ~$5-20/month for small instance
- Need to set up SSL certificates for HTTPS

---

## Security Considerations for Team Sharing

### Add Basic Password Protection
Create a `.streamlit/secrets.toml` file:
```toml
[passwords]
team_password = "OraLiving2024!"
```

Add to your app_simple.py at the top:
```python
import streamlit as st

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["passwords"]["team_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

if not check_password():
    st.stop()  # Do not continue if check_password is not True
```

---

## Recommended Approach for Your Team

1. **Use Streamlit Community Cloud** - It's free and professional
2. **Make your repo private** on GitHub if the data is sensitive
3. **Add password protection** using the code above
4. **Get a custom subdomain** like `ora-living.streamlit.app`

## Quick Start Commands

```bash
# Make sure everything works locally first
streamlit run app_simple.py

# Create/update requirements.txt
pip freeze > requirements.txt

# Push to GitHub
git add .
git commit -m "Ready for team deployment"
git push origin main

# Then deploy on Streamlit Cloud
```

## Sharing with Investors Later

Once tested with your team, for investors you might want:
1. Custom domain (e.g., model.oraliving.com)
2. Enhanced security/authentication
3. Analytics to track usage
4. Backup deployment on AWS/Google Cloud

Need help with any of these options? Let me know!