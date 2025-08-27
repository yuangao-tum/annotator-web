# Data Annotation Tool

A web-based annotation tool for labeling autonomous driving scenarios with GIFs and plots. This tool allows multiple users to annotate driving scenarios with different annotation classes and tracks progress across all users.

## 🖼️ Screenshots

### 🔐 Login Page![login](https://github.com/user-attachments/assets/2eebbf9f-d284-4c44-a3e7-bbc9a6a71476)

### 📂 Scenario Gallery![gallery](https://github.com/user-attachments/assets/cea018a6-0ae9-45d7-afcc-1363f50ab268)

### ✏️ Annotation Interface![annotation](https://github.com/user-attachments/assets/6a89af57-9d22-4650-94bd-fd1addb88b51)

## 🚀 Features

- **Multi-User Support**: Individual user accounts with separate annotation storage
- **Multiple Annotation Classes**:
  - **Target Lanelet Change**: Move existing vehicles to specific lanelets
  - **Behavior Change**: Modify driving behavior (Balanced, Eco, Emergency, Cautious, Aggressive, Speeder)
  - **Insert Actor**: Add new vehicles with start and target lanelets
  - **Delete Agent**: Remove vehicles with collision or other reasons
  - **Impossible**: Mark scenarios as impossible to annotate
- **Media Support**: View GIFs or individual timestep plots
- **Progress Tracking**: Monitor annotation completion across all scenarios
- **User Statistics**: Track login counts, registration dates, and last login times
- **Public Access**: Shareable public URL for remote collaboration
- **Persistent Sessions**: Runs continuously using tmux

## 📁 Project Structure

```
annotator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── login.html        # Login/registration page
│   ├── gallery.html      # Scenario gallery view
│   └── annotator.html    # Main annotation interface
├── data/                 # User annotation data (auto-created)
│   └── {username}/       # User-specific annotation folders
└── .venv/                # Python virtual environment
```

## 🛠️ Prerequisites

- Python 3.8+
- Node.js 16+ (for localtunnel)
- Access to `/home/yuan/Dataset/Frenetix-Motion-Planner/logs_global/`

## 📦 Installation

### 1. Clone/Setup Project
```bash
cd /home/yuan/Dataset
# Your annotation tool should already be in the annotator/ folder
```

### 2. Install Python Dependencies
```bash
cd annotator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Localtunnel (for public access)
```bash
npm install -g localtunnel
```

## 🚀 Running the Application

### 🌐 Public Access Options (Two Tunneling Frameworks)

You can expose the local server on port 8000 to the internet using either of these tunneling tools:

- LocalTunnel (Node.js-based)
  - Pros: Simple, memorable subdomain support (best-effort)
  - Cons: Can be flaky/outages; password flow via `loca.lt` only
  - Start in tmux:
    ```bash
    tmux new-session -d -s tunnel 'lt --port 8000 --subdomain annotator-yuan'
    ```
  - Access URL (example): `https://annotator-yuan.loca.lt`

- localhost.run (SSH-based)
  - Pros: Works over SSH; easy to keep persistent in tmux; identifies you by SSH key
  - Cons: Random URL unless you reserve a custom domain in your account
  - Start in tmux using your SSH key:
    ```bash
    tmux new-session -d -s annotator-tunnel 'ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -R 80:localhost:8000 localhost.run | tee -a /home/yuan/Dataset/.localhost.run.log'
    ```
  - Get current public URL from the log:
    ```bash
    grep -m1 -E "https?://[[:alnum:].-]+" /home/yuan/Dataset/.localhost.run.log
    ```

Both tunnels can run simultaneously; use whichever URL is working best for you.

### Option 1: Quick Start (Recommended for Production)
```bash
# Start Flask server in tmux
tmux new-session -d -s annotator 'cd /home/yuan/Dataset/annotator && source .venv/bin/activate && waitress-serve --host=0.0.0.0 --port=8000 app:app'

# Start Localtunnel in tmux (for public access)
tmux new-session -d -s tunnel 'lt --port 8000 --subdomain annotator-yuan'

# Start localhost.run in tmux (alternative to Localtunnel)
tmux new-session -d -s annotator-tunnel 'ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -R 80:localhost:8000 localhost.run | tee -a /home/yuan/Dataset/.localhost.run.log'
```

### Option 2: Manual Start (for Development)
```bash
cd annotator
source .venv/bin/activate
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

In another terminal:
```bash
lt --port 8000 --subdomain annotator-yuan
```

## 🌐 Access URLs

- **Local Access**: http://localhost:8000
- **Public Access**: https://annotator-yuan.loca.lt
- **Tunnel Password**: 129.187.64.171

### 📡 localhost.run Public URL (alternative)
- Anonymous URLs rotate. Check the current URL printed by the tunnel with:
```bash
grep -m1 -E "https?://[[:alnum:].-]+" /home/yuan/Dataset/.localhost.run.log
tail -n 50 /home/yuan/Dataset/.localhost.run.log
```
- For a more stable subdomain, create an account and add your key at `https://localhost.run`.

### 🚀 **Public Access Instructions:**
1. **Open** https://annotator-yuan.loca.lt in your browser
2. **Enter the password**: 129.187.64.171
3. **You should see your annotation tool's login page!**

**Note**: The tunnel password is your server's public IP address. If it changes, get the new password with:
```bash
curl https://loca.lt/mytunnelpassword
```

## 👥 User Management

### Registration
1. Visit the login page
2. Click "Register" tab
3. Enter a unique username
4. Usernames are case-insensitive (e.g., "Yuan" and "yuan" are the same)

### Login
1. Enter your registered username
2. Click "Login"
3. You'll be redirected to the scenario gallery

## 📊 Annotation Process

### 1. Browse Scenarios
- View all available scenarios in the gallery
- See annotation progress for each scenario
- Use search to find specific scenarios

### 2. Select Scenario
- Click on any scenario card to open the annotation interface
- View the main media (GIF or plot) on the left
- See timestep plots below the main viewer

#### Required per scenario
- Complete all four required annotation classes for every scenario:
  1) Target Lanelet Change
  2) Behavior Change
  3) Insert Actor
  4) Delete Agent
- You may submit them in any order.

### 3. Annotate
- Choose annotation class from dropdown
- Fill in required fields based on the class
- Add optional notes
- Click "Save Annotation" or "Impossible to Annotate"

Note on re-annotation:
- If you are not satisfied with a previous submission for a class, you can re-annotate the same class for the same scenario. The most recent submission will overwrite the previous one.

### 4. Track Progress
- Monitor overall completion percentage
- View individual scenario status
- Check annotation history
- View user statistics (login counts, registration dates)

## 🔧 Configuration

### Environment Variables
- `DATASET_PATH`: Path to scenario data (default: `/home/yuan/Dataset/Frenetix-Motion-Planner/logs_global/`)
- `DATA_ROOT`: Path to store annotations (default: `/home/yuan/Dataset/annotator/data/`)

**To change the dataset path:**
```bash
# Method 1: Set environment variable before starting
export DATASET_PATH="/path/to/your/new/dataset"
tmux new-session -d -s annotator 'cd /home/yuan/Dataset/annotator && source .venv/bin/activate && waitress-serve --host=0.0.0.0 --port=8000 app:app'

# Method 2: Set in the same command
tmux new-session -d -s annotator 'cd /home/yuan/Dataset/annotator && export DATASET_PATH="/path/to/your/new/dataset" && source .venv/bin/activate && waitress-serve --host=0.0.0.0 --port=8000 app:app'
```

### Port Configuration
- Flask server runs on port 8000 by default
- Localtunnel automatically forwards to this port

## 📝 Annotation Classes

### Target Lanelet Change
```json
{
  "class": "target lanelet change",
  "veh_id": "3228",
  "target_lanelet": "7181",
  "difficulty": "easy",
  "scenario_name": "ARG_Carcarana-4_4_T-1"
}
```

**Difficulty Levels:**
- **Easy**: Close or directly connected to original lanelet
- **Medium**: Lane changing in same direction
- **Hard**: Far away, completely new target

### Behavior Change
```json
{
  "class": "behavior change",
  "veh_id": "3244",
  "target_behavior": "eco_driver",
  "scenario_name": "ARG_Carcarana-4_4_T-1"
}
```

### Insert Actor
```json
{
  "class": "insert actor",
  "veh_id": "11",
  "begin_lanelet": "7181",
  "target_lanelet": "6122",
  "scenario_name": "ARG_Carcarana-4_4_T-1"
}
```

### Delete Agent
```json
{
  "class": "delete agent",
  "veh_id": "1234",
  "delete_reason": "Rear collision with ego - no fault from ego",
  "scenario_name": "ARG_Carcarana-4_4_T-1"
}
```

### Impossible
```json
{
  "class": "impossible",
  "scenario_name": "ARG_Carcarana-4_4_T-1"
}
```

## 🛠️ Troubleshooting

### Server Won't Start
```bash
# Check if port is in use
fuser -k 8000/tcp

# Restart Flask server
tmux kill-session -t annotator
tmux new-session -d -s annotator 'cd /home/yuan/Dataset/annotator && source .venv/bin/activate && waitress-serve --host=0.0.0.0 --port=8000 app:app'
```

### Localtunnel Issues
```bash
# Restart tunnel
tmux kill-session -t tunnel
tmux new-session -d -s tunnel 'lt --port 8000 --subdomain annotator-yuan'

# Get tunnel password
curl https://loca.lt/mytunnelpassword
```

### localhost.run Tunnel
```bash
# Restart localhost.run tunnel
tmux kill-session -t annotator-tunnel
tmux new-session -d -s annotator-tunnel 'ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -R 80:localhost:8000 localhost.run | tee -a /home/yuan/Dataset/.localhost.run.log'

# Check current public URL
grep -m1 -E "https?://[[:alnum:].-]+" /home/yuan/Dataset/.localhost.run.log
tail -n 50 /home/yuan/Dataset/.localhost.run.log
```

### View Logs
```bash
# Attach to Flask session
tmux attach-session -t annotator

# Attach to tunnel session
tmux attach-session -t tunnel

# Detach (keep running): Ctrl+B, then D
```

```bash
# Attach to localhost.run session
tmux attach-session -t annotator-tunnel

# Tail localhost.run log
tail -n 100 /home/yuan/Dataset/.localhost.run.log
```

### Check Running Sessions
```bash
tmux list-sessions
```

## 📊 Data Storage

### Annotation Files
- Location: `/home/yuan/Dataset/annotator/data/{username}/`
- Format: JSONL (one JSON object per line)
- Naming: `{scenario_name}_annotations.jsonl`

### User Data
- Location: `/home/yuan/Dataset/annotator/users.json`
- Contains: Username registration information

## 🔒 Security Notes

- Basic username-based authentication
- No password required (intended for internal/trusted use)
- Public access via Localtunnel (use with caution)
- All data stored locally on the server

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs in tmux sessions
3. Check browser console for frontend errors
4. Verify file permissions and paths

## 🚀 Quick Commands Reference

```bash
# Start everything
tmux new-session -d -s annotator 'cd /home/yuan/Dataset/annotator && source .venv/bin/activate && waitress-serve --host=0.0.0.0 --port=8000 app:app'
tmux new-session -d -s tunnel 'lt --port 8000 --subdomain annotator-yuan'
tmux new-session -d -s annotator-tunnel 'ssh -i ~/.ssh/id_ed25519 -o StrictHostKeyChecking=no -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -R 80:localhost:8000 localhost.run | tee -a /home/yuan/Dataset/.localhost.run.log'

# Stop everything
tmux kill-session -t annotator
tmux kill-session -t tunnel
tmux kill-session -t annotator-tunnel

# Check status
tmux list-sessions
curl http://localhost:8000

# View logs
tmux attach-session -t annotator
tmux attach-session -t tunnel
tmux attach-session -t annotator-tunnel
tail -n 100 /home/yuan/Dataset/.localhost.run.log
```

---

**Happy Annotating! 🎯✨**
