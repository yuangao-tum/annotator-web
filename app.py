import os
import json
import re
from pathlib import Path
from flask import Flask, jsonify, send_file, request, render_template, abort, redirect, url_for, session
from datetime import datetime
from collections import Counter
from werkzeug.utils import secure_filename

APP_ROOT = Path(__file__).parent
# Allow dataset path to be configured via environment variable
LOGS_ROOT = Path(os.environ.get('DATASET_PATH', "/home/yuan/Dataset/Frenetix-Motion-Planner/logs_annotation")).resolve()
DATA_ROOT = APP_ROOT / "data"
DATA_ROOT.mkdir(parents=True, exist_ok=True)

# Log the dataset path being used
print(f"🔍 Dataset path configured as: {LOGS_ROOT}")
if not LOGS_ROOT.exists():
    print(f"⚠️  WARNING: Dataset path does not exist: {LOGS_ROOT}")
    print(f"   Please set DATASET_PATH environment variable or update the code")
else:
    print(f"✅ Dataset path exists and is accessible")

# User management
USERS_FILE = DATA_ROOT / "users.json"

def load_users():
    """Load registered users from file"""
    if not USERS_FILE.exists():
        return {}
    try:
        with USERS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    """Save users to file"""
    try:
        with USERS_FILE.open("w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def normalize_username(username):
    """Normalize username to lowercase for case-insensitive comparison"""
    return username.lower().strip()

def get_user_data_path(username):
    """Get the data path for a specific user"""
    normalized_name = normalize_username(username)
    return DATA_ROOT / normalized_name

def ensure_user_folder(username):
    """Ensure user folder exists"""
    user_path = get_user_data_path(username)
    user_path.mkdir(exist_ok=True)
    return user_path


app = Flask(__name__, template_folder=str(APP_ROOT / "templates"), static_folder=str(APP_ROOT / "static"))
app.secret_key = 'your-secret-key-here'  # In production, use a secure random key


def load_annotation_status(scenario_name: str, username: str = None):
    if not username:
        return {
            "annotated": False,
            "total": 0,
            "by_class": {},
            "last_updated": None,
        }
    
    user_data_path = get_user_data_path(username)
    out_path = user_data_path / f"{scenario_name}_annotations.jsonl"
    
    if not out_path.exists():
        return {
            "annotated": False,
            "total": 0,
            "by_class": {},
            "last_updated": None,
        }
    
    counts = Counter()
    last_updated = None
    
    try:
        # Read file in chunks for better performance
        with out_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    cls = rec.get("class")
                    if cls:
                        counts[cls] += 1
                    ts = rec.get("timestamp")
                    if ts:
                        try:
                            dt = datetime.fromisoformat(ts)
                            if last_updated is None or dt > last_updated:
                                last_updated = dt
                        except Exception:
                            pass
                except Exception:
                    continue
    except Exception as e:
        print(f"⚠️  Error reading annotation file for {scenario_name}: {e}")
        return {
            "annotated": False,
            "total": 0,
            "by_class": {},
            "last_updated": None,
        }
    
    return {
        "annotated": sum(counts.values()) > 0,
        "total": int(sum(counts.values())),
        "by_class": dict(counts),
        "last_updated": last_updated.isoformat() if last_updated else None,
    }


def find_scenarios(username: str = None):
    scenarios = []
    if not LOGS_ROOT.exists():
        return scenarios
    
    # Get all scenario directories first
    scenario_dirs = [item for item in LOGS_ROOT.iterdir() if item.is_dir()]
    total_scenarios = len(scenario_dirs)
    
    print(f"🔍 Processing {total_scenarios} scenarios for user: {username}")
    
    for i, item in enumerate(sorted(scenario_dirs)):
        if i % 50 == 0:  # Log progress every 50 scenarios
            print(f"📊 Progress: {i}/{total_scenarios} scenarios processed ({i/total_scenarios*100:.1f}%)")
            
        name = item.name
        gif_path = item / f"{name}.gif"
        plots_dir = item / "plots"
        has_gif = gif_path.exists()
        has_plots = plots_dir.exists()
        
        if has_gif or has_plots:
            # Get first plot for cover (optimized)
            first_plot = None
            if has_plots:
                try:
                    # Use listdir instead of iterdir for better performance
                    plot_files = [p for p in plots_dir.iterdir() if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}]
                    if plot_files:
                        # Sort by name and take first (most scenarios have timestep-based naming)
                        plot_files.sort(key=lambda x: x.name)
                        first_plot = plot_files[0].name
                except Exception as e:
                    print(f"⚠️  Error reading plots for {name}: {e}")
                    first_plot = None
            
            # Load annotation status
            status = load_annotation_status(name, username)
            
            scenarios.append({
                "name": name,
                "has_gif": has_gif,
                "has_plots": has_plots,
                "first_plot": first_plot,
                "status": status,
            })
    
    print(f"✅ Completed processing {len(scenarios)} valid scenarios")
    return scenarios


@app.route("/")
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("gallery.html", username=session['username'])


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            # Check if user exists (case-insensitive)
            users = load_users()
            normalized_name = normalize_username(username)
            
            if normalized_name in users:
                # User exists, update login stats and set session
                # Ensure login_count field exists for existing users
                if 'login_count' not in users[normalized_name]:
                    users[normalized_name]['login_count'] = 0
                if 'last_login' not in users[normalized_name]:
                    users[normalized_name]['last_login'] = None
                
                users[normalized_name]['login_count'] += 1
                users[normalized_name]['last_login'] = datetime.now().isoformat()
                save_users(users)  # Save updated login stats
                
                session['username'] = username  # Keep original case
                session['login_time'] = datetime.now().isoformat()
                return redirect(url_for('index'))
            else:
                return jsonify({"error": "User not found. Please register first."}), 404
        return jsonify({"error": "Please enter a username"}), 400
    return render_template("login.html")


@app.route("/register", methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    if not username:
        return jsonify({"error": "Please enter a username"}), 400
    
    # Check if username already exists (case-insensitive)
    users = load_users()
    normalized_name = normalize_username(username)
    
    if normalized_name in users:
        return jsonify({"error": "Username already registered. Please choose another name."}), 409
    
    # Register new user
    users[normalized_name] = {
        "username": username,  # Keep original case
        "registered_at": datetime.now().isoformat(),
        "normalized_name": normalized_name,
        "login_count": 0,
        "last_login": None
    }
    
    if save_users(users):
        # Create user folder
        ensure_user_folder(username)
        return jsonify({"message": "Registration successful"}), 200
    else:
        return jsonify({"error": "Failed to save user data"}), 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/annotate/<scenario_name>")
def annotate_scenario(scenario_name):
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template("annotator.html", username=session['username'], scenario_name=scenario_name)


@app.get("/api/scenarios")
def api_scenarios():
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify(find_scenarios(session['username']))


@app.get("/media/<path:scenario>/<path:filename>")
def serve_media(scenario: str, filename: str):
    # Restrict to intended directory
    base = LOGS_ROOT / scenario
    target = (base / filename).resolve()
    if not str(target).startswith(str(base.resolve())):
        abort(403)
    if not target.exists():
        abort(404)
    return send_file(str(target))


@app.get("/api/plots/<path:scenario>")
def list_plots(scenario: str):
    plots_dir = LOGS_ROOT / scenario / "plots"
    if not plots_dir.exists():
        return jsonify([])
    
    # Get all plot files and extract timesteps
    plot_files = []
    for p in plots_dir.iterdir():
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
            # Extract timestep from filename (e.g., "ARG_Carcarana-4_4_T-1_0.png" -> 0)
            match = re.match(r'.*_(\d+)\.(png|jpg|jpeg|gif)$', p.name)
            if match:
                timestep = int(match.group(1))
                plot_files.append((timestep, p.name))
    
    # Sort by timestep number
    plot_files.sort(key=lambda x: x[0])
    
    # Return only the filenames in sorted order
    files = [p[1] for p in plot_files]
    return jsonify(files)


@app.post("/api/annotate")
def annotate():
    print(f"=== ANNOTATION REQUEST RECEIVED ===")
    print(f"Session username: {session.get('username', 'NOT SET')}")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    
    if 'username' not in session:
        print("ERROR: No username in session")
        return jsonify({"error": "Not logged in"}), 401
        
    try:
        payload = request.get_json(force=True)
        print(f"Received payload: {payload}")
    except Exception as e:
        print(f"ERROR parsing JSON: {e}")
        return jsonify({"error": "Invalid JSON"}), 400

    required_keys = {"scenario_name", "class"}
    if not required_keys.issubset(payload.keys()):
        missing = sorted(required_keys - set(payload.keys()))
        print(f"ERROR: Missing required keys: {missing}")
        return jsonify({"error": f"Missing keys: {missing}"}), 400

    # Add user info to annotation
    payload['username'] = session['username']
    payload['timestamp'] = datetime.now().isoformat()
    print(f"Final payload with user info: {payload}")

    scenario = payload.get("scenario_name")
    user_path = get_user_data_path(session['username'])
    out_path = user_path / f"{scenario}_annotations.jsonl"
    print(f"Saving to: {out_path}")

    try:
        # Read existing annotations
        existing_annotations = []
        if out_path.exists():
            with out_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            ann = json.loads(line)
                            existing_annotations.append(ann)
                        except Exception:
                            continue
        
        # Remove existing annotation for the same class
        existing_annotations = [ann for ann in existing_annotations if ann.get('class') != payload.get('class')]
        
        # Add the new annotation
        existing_annotations.append(payload)
        
        # Write all annotations back to file
        with out_path.open("w", encoding="utf-8") as f:
            for ann in existing_annotations:
                f.write(json.dumps(ann, ensure_ascii=False) + "\n")
                
        print(f"SUCCESS: Annotation saved to {out_path}")
        return jsonify({"status": "ok", "path": str(out_path)})
    except Exception as e:
        print(f"ERROR saving file: {e}")
        return jsonify({"error": f"Failed to save: {e}"}), 500


@app.get("/api/annotations/<path:scenario_name>")
def get_annotations(scenario_name: str):
    """Get all annotations for a specific scenario and user"""
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    user_path = get_user_data_path(session['username'])
    out_path = user_path / f"{scenario_name}_annotations.jsonl"
    
    if not out_path.exists():
        return jsonify({"annotations": []})
    
    annotations = []
    try:
        with out_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        ann = json.loads(line)
                        annotations.append(ann)
                    except Exception:
                        continue
    except Exception:
        return jsonify({"error": "Error reading annotations"}), 500
    
    return jsonify({"annotations": annotations})


@app.get("/api/users/stats")
def get_user_stats():
    """Get user statistics including login counts"""
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    users = load_users()
    user_stats = []
    
    for normalized_name, user_data in users.items():
        user_stats.append({
            "username": user_data["username"],
            "registered_at": user_data["registered_at"],
            "login_count": user_data.get("login_count", 0),
            "last_login": user_data.get("last_login"),
            "normalized_name": user_data["normalized_name"]
        })
    
    # Sort by login count (descending)
    user_stats.sort(key=lambda x: x.get("login_count", 0), reverse=True)
    
    return jsonify({"users": user_stats})


@app.get("/api/progress")
def get_overall_progress():
    """Get overall annotation progress for all scenarios for the current user"""
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    scenarios = find_scenarios(session['username'])
    total_scenarios = len(scenarios)
    completed_scenarios = 0
    impossible_scenarios = 0
    
    for scenario in scenarios:
        status = scenario['status']
        if status['annotated']:
            # Check if all three main classes are annotated or marked as impossible
            by_class = status['by_class']
            main_classes = ['target lanelet change', 'behavior change', 'insert actor', 'delete agent']
            has_all_main = all(cls in by_class for cls in main_classes)
            has_impossible = 'impossible' in by_class
            
            if has_all_main or has_impossible:
                completed_scenarios += 1
                if has_impossible:
                    impossible_scenarios += 1
    
    progress_percentage = (completed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
    
    return jsonify({
        "total_scenarios": total_scenarios,
        "completed_scenarios": completed_scenarios,
        "impossible_scenarios": impossible_scenarios,
        "progress_percentage": round(progress_percentage, 1)
    })


if __name__ == "__main__":
    # For quick local run. In production, prefer waitress below
    app.run(host="0.0.0.0", port=8000, debug=True)
