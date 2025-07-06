import os
import json
import requests
import re
import http.client
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, redirect
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Initialize Flask app
app = Flask(__name__)

# Debug information
print(f"Current directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

#######################
# FOOTBALL FUNCTIONS #
#######################

# Football API configuration
FOOTBALL_API_KEY = "20f34383c0mshca06042c2349b9ap1295abjsn6bef5ef49cfc"
FOOTBALL_API_HOST = "api-football-v1.p.rapidapi.com"
TEAM_ID = 2932  # Al Hilal team ID
LEAGUE_ID = 504  # Saudi Pro League ID
SEASON = 2024    # Current season

# Saudi Pro League teams
SAUDI_TEAMS = {
    "النصر": 2889,
    "الأهلي": 2933,
    "الاتحاد": 2906,
    "الشباب": 2931,
    "الاتفاق": 2938,
    "الفيصلي": 2940,
    "الفتح": 2939,
    "الرائد": 2942,
    "التعاون": 2937,
    "أبها": 10492,
    "الوحدة": 2941,
    "الفيحاء": 10501,
    "ضمك": 10503,
    "الحزم": 10504,
    "الخليج": 10498,
    "القادسية": 10499
}

# Load football match data from JSON file
def load_football_match_data():
    try:
        with open('match_data.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return empty data if file doesn't exist or is invalid
        return {"matches": []}

# Save football match data to JSON file
def save_football_match_data(data):
    with open('match_data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Get last 5 matches from Football API
def get_last_matches(team_id=TEAM_ID, count=5):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    querystring = {
        "team": str(team_id),
        "last": str(count)
    }
    
    headers = {
        "X-RapidAPI-Key": FOOTBALL_API_KEY,
        "X-RapidAPI-Host": FOOTBALL_API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return response.json()['response']
        else:
            print(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching matches: {e}")
        return []

# Get detailed match statistics from Football API
def get_match_statistics(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
    
    querystring = {
        "fixture": str(fixture_id)
    }
    
    headers = {
        "X-RapidAPI-Key": FOOTBALL_API_KEY,
        "X-RapidAPI-Host": FOOTBALL_API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return response.json()['response']
        else:
            print(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching match statistics: {e}")
        return []

# Get match lineups from Football API
def get_match_lineups(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/lineups"
    
    querystring = {
        "fixture": str(fixture_id)
    }
    
    headers = {
        "X-RapidAPI-Key": FOOTBALL_API_KEY,
        "X-RapidAPI-Host": FOOTBALL_API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return response.json()['response']
        else:
            print(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching match lineups: {e}")
        return []

# Get match events from Football API
def get_match_events(fixture_id):
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures/events"
    
    querystring = {
        "fixture": str(fixture_id)
    }
    
    headers = {
        "X-RapidAPI-Key": FOOTBALL_API_KEY,
        "X-RapidAPI-Host": FOOTBALL_API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return response.json()['response']
        else:
            print(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching match events: {e}")
        return []

# Get next match from Football API
def get_next_match(team_id=TEAM_ID):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    querystring = {
        "team": str(team_id),
        "next": "1"
    }
    
    headers = {
        "X-RapidAPI-Key": FOOTBALL_API_KEY,
        "X-RapidAPI-Host": FOOTBALL_API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            matches = response.json()['response']
            if matches:
                return matches[0]
            return None
        else:
            print(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching next match: {e}")
        return None

# Get team information from Football API
def get_team_info(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"
    
    querystring = {
        "id": str(team_id)
    }
    
    headers = {
        "X-RapidAPI-Key": FOOTBALL_API_KEY,
        "X-RapidAPI-Host": FOOTBALL_API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            teams = response.json()['response']
            if teams:
                return teams[0]
            return None
        else:
            print(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching team info: {e}")
        return None

# Calculate team statistics from match data
def calculate_football_team_stats(matches):
    stats = {
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0
    }
    
    for match in matches:
        is_home = match['teams']['home']['id'] == TEAM_ID
        team_goals = match['goals']['home'] if is_home else match['goals']['away']
        opponent_goals = match['goals']['away'] if is_home else match['goals']['home']
        
        stats["goals_for"] += team_goals
        stats["goals_against"] += opponent_goals
        
        if team_goals > opponent_goals:
            stats["wins"] += 1
        elif team_goals < opponent_goals:
            stats["losses"] += 1
        else:
            stats["draws"] += 1
    
    return stats

# Format matches for frontend display
def format_football_matches_for_display(matches):
    formatted_matches = []
    
    for match in matches:
        is_home = match['teams']['home']['id'] == TEAM_ID
        team_goals = match['goals']['home'] if is_home else match['goals']['away']
        opponent_goals = match['goals']['away'] if is_home else match['goals']['home']
        
        # Determine result
        result = "draw"
        if team_goals > opponent_goals:
            result = "win"
        elif team_goals < opponent_goals:
            result = "loss"
        
        formatted_match = {
            "match_id": match['fixture']['id'],
            "date": match['fixture']['date'].split("T")[0],
            "home_team": match['teams']['home']['name'],
            "away_team": match['teams']['away']['name'],
            "home_score": match['goals']['home'],
            "away_score": match['goals']['away'],
            "team_result": result,
            "opponent": match['teams']['away']['name'] if is_home else match['teams']['home']['name'],
            "goals_for": team_goals,
            "goals_against": opponent_goals
        }
        
        formatted_matches.append(formatted_match)
    
    return formatted_matches

# Format match data for detailed analysis
def format_football_match_data_for_analysis(match, statistics, lineups, events):
    match_data = {
        "match_id": match['fixture']['id'],
        "date": match['fixture']['date'],
        "home_team": match['teams']['home']['name'],
        "away_team": match['teams']['away']['name'],
        "home_score": match['goals']['home'],
        "away_score": match['goals']['away'],
        "venue": match['fixture']['venue']['name'],
        "referee": match['fixture']['referee'],
        "statistics": statistics,
        "lineups": lineups,
        "events": events
    }
    
    return match_data

# Generate threat analysis using OpenAI
def generate_football_threat_analysis(opponent_name):
    # Get opponent team ID
    opponent_id = SAUDI_TEAMS.get(opponent_name)
    if not opponent_id:
        return "لم يتم العثور على الفريق المنافس في قاعدة البيانات."
    
    # Get opponent's last 5 matches
    matches = get_last_matches(opponent_id, 5)
    if not matches:
        return "لا توجد بيانات كافية لإجراء تحليل التهديد."
    
    # Format match data for analysis
    formatted_matches = []
    for match in matches:
        is_home = match['teams']['home']['id'] == opponent_id
        team_goals = match['goals']['home'] if is_home else match['goals']['away']
        opponent_goals = match['goals']['away'] if is_home else match['goals']['home']
        opponent_team = match['teams']['away']['name'] if is_home else match['teams']['home']['name']
        
        formatted_match = {
            "date": match['fixture']['date'].split("T")[0],
            "opponent": opponent_team,
            "result": "فوز" if team_goals > opponent_goals else "تعادل" if team_goals == opponent_goals else "خسارة",
            "score": f"{team_goals} - {opponent_goals}",
            "is_home": is_home
        }
        
        formatted_matches.append(formatted_match)
    
    # Get team info
    team_info = get_team_info(opponent_id)
    
    # Create prompt for OpenAI
    prompt = f"""
    أنت محلل كرة قدم محترف متخصص في تحليل أداء الفرق وتقييم التهديدات.
    
    قم بتحليل الفريق التالي وتقييم مستوى التهديد الذي يشكله على فريق الهلال السعودي:
    
    اسم الفريق: {opponent_name}
    
    نتائج آخر 5 مباريات:
    {json.dumps(formatted_matches, ensure_ascii=False, indent=2)}
    
    معلومات إضافية عن الفريق:
    {json.dumps(team_info, ensure_ascii=False, indent=2) if team_info else "لا توجد معلومات إضافية"}
    
    المطلوب:
    1. تحليل شامل لنقاط القوة والضعف في الفريق
    2. تقييم مستوى التهديد (منخفض، متوسط، عالي، خطير جداً)
    3. اللاعبين المؤثرين الذين يجب الحذر منهم
    4. استراتيجيات مقترحة للتعامل مع هذا الفريق
    
    قدم التحليل بتنسيق Markdown مع عناوين واضحة وفقرات منظمة. استخدم اللغة العربية الفصحى.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "أنت محلل كرة قدم محترف متخصص في تحليل أداء الفرق وتقييم التهديدات."},
                {"role": "user", "content": prompt}
            ],
            
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating threat analysis: {e}")
        return "حدث خطأ أثناء تحليل التهديد. يرجى المحاولة مرة أخرى."

# Generate performance analysis using OpenAI
def generate_football_performance_analysis():
    # Load match data from JSON
    match_data = load_football_match_data()
    if not match_data or not match_data.get("matches"):
        return "لا توجد بيانات كافية لإجراء تحليل الأداء."
    
    # Create prompt for OpenAI
    prompt = f"""
    أنت محلل كرة قدم محترف متخصص في تحليل أداء الفرق بعد المباريات.
    
    قم بتحليل أداء فريق الهلال السعودي بناءً على البيانات التالية:
    
    معلومات المباريات:
    {json.dumps(match_data, ensure_ascii=False, indent=2)}
    
    المطلوب:
    1. ملخص عام لأداء الفريق
    2. تحليل النقاط الإيجابية في الأداء
    3. تحليل النقاط السلبية والجوانب التي تحتاج إلى تحسين
    4. تقييم أداء اللاعبين الأساسيين
    5. توصيات للمباريات القادمة
    
    قدم التحليل بتنسيق Markdown مع عناوين واضحة وفقرات منظمة. استخدم اللغة العربية الفصحى.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "أنت محلل كرة قدم محترف متخصص في تحليل أداء الفرق بعد المباريات."},
                {"role": "user", "content": prompt}
            ],
            
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating performance analysis: {e}")
        return "حدث خطأ أثناء تحليل الأداء. يرجى المحاولة مرة أخرى."

# Generate next match tactics using OpenAI
def generate_football_next_match_tactics(opponent, league):
    # Load match data from JSON
    match_data = load_football_match_data()
    if not match_data or not match_data.get("matches"):
        return "لا توجد بيانات كافية لإجراء تحليل التكتيكات."
    
    # Create prompt for OpenAI
    prompt = f"""
    أنت مستشار تكتيكي محترف لفريق الهلال السعودي.
    
    قم بتقديم نصائح وتوصيات تكتيكية للمباراة القادمة بناءً على البيانات التالية:
    
    الفريق المنافس: {opponent}
    البطولة: {league}
    
    معلومات المباريات السابقة:
    {json.dumps(match_data, ensure_ascii=False, indent=2)}
    
    المطلوب:
    1. التشكيل المقترح
    2. الخطة التكتيكية المناسبة
    3. نقاط القوة التي يجب استغلالها
    4. نقاط الضعف التي يجب الحذر منها
    5. اللاعبين المؤثرين الذين يجب التركيز عليهم
    
    قدم التحليل بتنسيق Markdown مع عناوين واضحة وفقرات منظمة. استخدم اللغة العربية الفصحى.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "أنت مستشار تكتيكي محترف لفريق الهلال السعودي."},
                {"role": "user", "content": prompt}
            ],
            
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating next match tactics: {e}")
        return "حدث خطأ أثناء تحليل التكتيكات. يرجى المحاولة مرة أخرى."

# Generate formation recommendation using OpenAI
def generate_football_formation_recommendation(opponent):
    # Load match data from JSON
    match_data = load_football_match_data()
    if not match_data or not match_data.get("matches"):
        return {
            "formation": "4-3-3",
            "explanation": "لا توجد بيانات كافية لإجراء تحليل التشكيل.",
            "players": []
        }
    
    # Create prompt for OpenAI
    prompt = f"""
    أنت مدرب كرة قدم محترف متخصص في تحليل التشكيلات والتكتيكات.
    
    قم بتوصية تشكيل مناسب لفريق الهلال السعودي في مباراته القادمة ضد {opponent} بناءً على البيانات التالية:
    
    معلومات المباريات السابقة:
    {json.dumps(match_data, ensure_ascii=False, indent=2)}
    
    المطلوب:
    1. التشكيل الموصى به (مثل 4-3-3 أو 4-2-3-1)
    2. شرح سبب اختيار هذا التشكيل
    3. قائمة بـ 11 لاعب أساسي مع أرقامهم ومراكزهم وأدوارهم
    
    قدم التوصية بتنسيق JSON كالتالي:
    {{
        "formation": "4-3-3",
        "explanation": "شرح سبب اختيار هذا التشكيل",
        "players": [
            {{
                "number": 1,
                "name": "اسم اللاعب",
                "position": "المركز",
                "role": "الدور التكتيكي"
            }},
            ...
        ]
    }}
    
    استخدم أسماء لاعبين حقيقيين من فريق الهلال السعودي.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "أنت مدرب كرة قدم محترف متخصص في تحليل التشكيلات والتكتيكات."},
                {"role": "user", "content": prompt}
            ],
            
        )
        
        # Parse JSON response
        result = response.choices[0].message.content
        # Extract JSON part
        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text
            return {
                "formation": "4-3-3",
                "explanation": "حدث خطأ في تحليل التشكيل",
                "players": []
            }
    except Exception as e:
        print(f"Error generating formation recommendation: {e}")
        return {
            "formation": "4-3-3",
            "explanation": "حدث خطأ في تحليل التشكيل",
            "players": []
        }

# Generate match report using OpenAI
def generate_football_match_report(match_id):
    # Load match data from JSON
    match_data = load_football_match_data()
    if not match_data or not match_data.get("matches"):
        return "لا توجد بيانات كافية لإنشاء تقرير المباراة."
    
    # Find the match with the given ID
    match = None
    for m in match_data.get("matches", []):
        if str(m.get("match_id")) == str(match_id):
            match = m
            break
    
    if not match:
        return "لم يتم العثور على المباراة المطلوبة."
    
    # Create prompt for OpenAI
    prompt = f"""
    أنت صحفي رياضي متخصص في كتابة تقارير مباريات كرة القدم.
    
    قم بكتابة تقرير مفصل عن المباراة التالية:
    
    معلومات المباراة:
    {json.dumps(match, ensure_ascii=False, indent=2)}
    
    المطلوب:
    1. عنوان جذاب للتقرير
    2. ملخص المباراة
    3. أهم الأحداث واللحظات المؤثرة
    4. تحليل أداء الفريقين
    5. أبرز اللاعبين وإنجازاتهم
    6. تعليق على قرارات المدرب والتكتيكات المستخدمة
    
    قدم التقرير بتنسيق Markdown مع عناوين واضحة وفقرات منظمة. استخدم اللغة العربية الفصحى واجعل التقرير ممتعاً وجذاباً للقراءة.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "أنت صحفي رياضي متخصص في كتابة تقارير مباريات كرة القدم."},
                {"role": "user", "content": prompt}
            ],
            
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating match report: {e}")
        return "حدث خطأ أثناء إنشاء تقرير المباراة. يرجى المحاولة مرة أخرى."

# Generate next match prediction using OpenAI
def generate_football_next_match_prediction():
    # Get next match
    next_match = get_next_match()
    if not next_match:
        return {
            "home_team": "الهلال",
            "away_team": "الفريق المنافس",
            "predicted_score": "0 - 0",
            "explanation": "لم يتم العثور على معلومات المباراة القادمة."
        }
    
    # Get last 5 matches for both teams
    al_hilal_matches = get_last_matches(TEAM_ID, 5)
    
    # Determine opponent team ID
    is_home = next_match['teams']['home']['id'] == TEAM_ID
    opponent_id = next_match['teams']['away']['id'] if is_home else next_match['teams']['home']['id']
    opponent_matches = get_last_matches(opponent_id, 5)
    
    # Format match data for analysis
    al_hilal_formatted = format_football_matches_for_display(al_hilal_matches)
    opponent_formatted = format_football_matches_for_display(opponent_matches)
    
    home_team = next_match['teams']['home']['name']
    away_team = next_match['teams']['away']['name']
    
    # Create prompt for OpenAI
    prompt = f"""
    أنت محلل كرة قدم محترف متخصص في التنبؤ بنتائج المباريات.
    
    قم بتحليل وتوقع نتيجة المباراة القادمة:
    
    الفريق المضيف: {home_team}
    الفريق الضيف: {away_team}
    الملعب: {next_match['fixture']['venue']['name']}
    التاريخ: {next_match['fixture']['date']}
    
    نتائج آخر 5 مباريات للهلال:
    {json.dumps(al_hilal_formatted, ensure_ascii=False, indent=2)}
    
    نتائج آخر 5 مباريات للفريق المنافس:
    {json.dumps(opponent_formatted, ensure_ascii=False, indent=2)}
    
    المطلوب:
    1. توقع نتيجة المباراة (مثال: "2 - 1")
    2. تحليل مفصل لسبب هذا التوقع
    
    ملاحظة مهمة: يجب أن تكون النتيجة المتوقعة منطقية بناءً على البيانات المتاحة.
    إذا كان أحد الفريقين أقوى بشكل واضح، يجب أن تعكس النتيجة ذلك.
    
    قدم إجابتك بتنسيق JSON كالتالي:
    {{
        "predicted_score": "2 - 1",
        "explanation": "تحليل مفصل باللغة العربية"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "أنت محلل كرة قدم محترف. قم بالرد باللغة العربية وبتنسيق JSON فقط."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Get the response content
        result = response.choices[0].message.content.strip()
        
        # Try to find JSON in the response
        try:
            # First try to parse the entire response as JSON
            prediction_data = json.loads(result)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the response using regex
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                try:
                    prediction_data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    raise ValueError("Could not parse prediction data")
            else:
                raise ValueError("No valid JSON found in response")
        
        # Validate the prediction data
        if not isinstance(prediction_data, dict):
            raise ValueError("Invalid prediction data format")
        
        if "predicted_score" not in prediction_data or "explanation" not in prediction_data:
            raise ValueError("Missing required prediction fields")
        
        # Keep the scores in their original order based on home/away teams
        return {
            "home_team": home_team,
            "away_team": away_team,
            "predicted_score": prediction_data["predicted_score"],
            "explanation": prediction_data["explanation"]
        }
        
    except Exception as e:
        print(f"Error generating prediction: {str(e)}")
        return {
            "home_team": home_team,
            "away_team": away_team,
            "predicted_score": "2 - 1",
            "explanation": "بناءً على البيانات المتوفرة، نتوقع فوز الهلال في هذه المباراة."
        }

# Handle football chat queries using OpenAI
def handle_football_chat_query(query):
    # Load match data for context
    match_data = load_football_match_data()
    
    # Create prompt for OpenAI
    prompt = f"""
    أنت مساعد ذكي لفريق الهلال السعودي. يمكنك الإجابة على الأسئلة المتعلقة بالفريق والمباريات والإحصائيات.
    
    بيانات المباريات للهلال:
    {json.dumps(match_data, ensure_ascii=False, indent=2)}
    
    سؤال المستخدم: {query}
    
    قدم إجابة مفيدة ودقيقة بناءً على البيانات المتاحة. إذا كان السؤال خارج نطاق معرفتك أو لا يتعلق بفريق الهلال، فاشرح ذلك بلطف.
    استخدم اللغة العربية الفصحى في إجابتك.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "أنت مساعد ذكي لفريق الهلال السعودي."},
                {"role": "user", "content": prompt}
            ],
            
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error handling chat query: {e}")
        return "عذراً، حدث خطأ أثناء معالجة سؤالك. يرجى المحاولة مرة أخرى."

########################
# BASKETBALL FUNCTIONS #
########################

# Basketball API configuration
BASKETBALL_API_KEY = "20f34383c0mshca06042c2349b9ap1295abjsn6bef5ef49cfc"
BASKETBALL_API_HOST = "api-basketball.p.rapidapi.com"
NYK_TEAM_ID = 152  # New York Knicks team ID
NBA_LEAGUE_ID = 12  # NBA League ID
CURRENT_SEASON = "2023-2024"  # Current season

# Load basketball data from JSON file
def load_basketball_data():
    try:
        with open('NYK-JAN.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return empty data if file doesn't exist or is invalid
        return []

# Get last 5 games from Basketball API
def get_last_basketball_games(team_id=NYK_TEAM_ID, count=5):
    conn = http.client.HTTPSConnection("api-basketball.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': BASKETBALL_API_KEY,
        'x-rapidapi-host': BASKETBALL_API_HOST
    }
    
    try:
        conn.request("GET", f"/games?league={NBA_LEAGUE_ID}&season={CURRENT_SEASON}&team={team_id}&last={count}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        if res.status == 200:
            return json.loads(data.decode("utf-8"))['response']
        else:
            print(f"API Error: {res.status}")
            return []
    except Exception as e:
        print(f"Error fetching basketball games: {e}")
        return []

# Get team information from Basketball API
def get_basketball_team_info(team_id):
    conn = http.client.HTTPSConnection("api-basketball.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': BASKETBALL_API_KEY,
        'x-rapidapi-host': BASKETBALL_API_HOST
    }
    
    try:
        conn.request("GET", f"/teams?id={team_id}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        if res.status == 200:
            teams = json.loads(data.decode("utf-8"))['response']
            if teams:
                return teams[0]
            return None
        else:
            print(f"API Error: {res.status}")
            return None
    except Exception as e:
        print(f"Error fetching basketball team info: {e}")
        return None

# Get next game from Basketball API
def get_next_basketball_game(team_id=NYK_TEAM_ID):
    conn = http.client.HTTPSConnection("api-basketball.p.rapidapi.com")
    
    headers = {
        'x-rapidapi-key': BASKETBALL_API_KEY,
        'x-rapidapi-host': BASKETBALL_API_HOST
    }
    
    try:
        conn.request("GET", f"/games?league={NBA_LEAGUE_ID}&season={CURRENT_SEASON}&team={team_id}&next=1", headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        if res.status == 200:
            games = json.loads(data.decode("utf-8"))['response']
            if games:
                return games[0]
            return None
        else:
            print(f"API Error: {res.status}")
            return None
    except Exception as e:
        print(f"Error fetching next basketball game: {e}")
        return None

# Format basketball games for frontend display
def format_games_for_display(games):
    formatted_games = []
    
    for game in games:
        home_team = game['teams']['home']
        away_team = game['teams']['away']
        is_knicks_home = home_team == "New York Knicks"
        
        # Determine result from Knicks perspective
        knicks_team = game['box_score']['home_team'] if is_knicks_home else game['box_score']['away_team']
        opponent_team = game['box_score']['away_team'] if is_knicks_home else game['box_score']['home_team']
        knicks_score = knicks_team['team_totals']['pts']
        opponent_score = opponent_team['team_totals']['pts']
        
        result = "draw"
        if knicks_score > opponent_score:
            result = "win"
        elif knicks_score < opponent_score:
            result = "loss"
        
        formatted_game = {
            "match_id": game['game_date'].replace(" ", "-").replace(",", ""),
            "date": game['game_date'],
            "home_team": home_team,
            "away_team": away_team,
            "home_score": knicks_team['team_totals']['pts'] if is_knicks_home else opponent_team['team_totals']['pts'],
            "away_score": opponent_team['team_totals']['pts'] if is_knicks_home else knicks_team['team_totals']['pts'],
            "team_result": result,
            "opponent": opponent_team['team_name'],
            "points_for": knicks_score,
            "points_against": opponent_score
        }
        
        formatted_games.append(formatted_game)
    
    return formatted_games

# Format API basketball games for frontend display
def format_api_basketball_games(games):
    formatted_games = []
    
    for game in games:
        is_knicks_home = game['teams']['home']['id'] == NYK_TEAM_ID
        
        # Determine result from Knicks perspective
        knicks_score = game['scores']['home']['total'] if is_knicks_home else game['scores']['away']['total']
        opponent_score = game['scores']['away']['total'] if is_knicks_home else game['scores']['home']['total']
        
        result = "draw"
        if knicks_score > opponent_score:
            result = "win"
        elif knicks_score < opponent_score:
            result = "loss"
        
        formatted_game = {
            "match_id": game['id'],
            "date": game['date'],
            "home_team": game['teams']['home']['name'],
            "away_team": game['teams']['away']['name'],
            "home_score": game['scores']['home']['total'],
            "away_score": game['scores']['away']['total'],
            "team_result": result,
            "opponent": game['teams']['away']['name'] if is_knicks_home else game['teams']['home']['name'],
            "points_for": knicks_score,
            "points_against": opponent_score
        }
        
        formatted_games.append(formatted_game)
    
    return formatted_games

# Calculate team statistics from game data
def calculate_basketball_team_stats(games):
    stats = {
        "wins": 0,
        "losses": 0,
        "avg_points": 0,
        "rebounds": 0,
        "assists": 0
    }
    
    for game in games:
        home_team = game['teams']['home']
        away_team = game['teams']['away']
        is_knicks_home = home_team == "New York Knicks"
        
        knicks_team = game['box_score']['home_team'] if is_knicks_home else game['box_score']['away_team']
        opponent_team = game['box_score']['away_team'] if is_knicks_home else game['box_score']['home_team']
        
        knicks_score = knicks_team['team_totals']['pts']
        opponent_score = opponent_team['team_totals']['pts']
        
        stats["rebounds"] += knicks_team['team_totals']['reb']
        stats["assists"] += knicks_team['team_totals']['ast']
        
        if knicks_score > opponent_score:
            stats["wins"] += 1
        else:
            stats["losses"] += 1
    
    if games:
        total_points = sum(game['box_score']['home_team']['team_totals']['pts'] if game['teams']['home'] == "New York Knicks" 
                          else game['box_score']['away_team']['team_totals']['pts'] for game in games)
        stats["avg_points"] = round(total_points / len(games), 1)
    
    return stats

# Format game data for detailed analysis
def format_game_data_for_analysis(game):
    home_team = game['teams']['home']
    away_team = game['teams']['away']
    is_knicks_home = home_team == "New York Knicks"
    
    knicks_team = game['box_score']['home_team'] if is_knicks_home else game['box_score']['away_team']
    opponent_team = game['box_score']['away_team'] if is_knicks_home else game['box_score']['home_team']
    
    game_data = {
        "game_id": game['game_date'].replace(" ", "-").replace(",", ""),
        "date": game['game_date'],
        "home_team": home_team,
        "away_team": away_team,
        "home_score": knicks_team['team_totals']['pts'] if is_knicks_home else opponent_team['team_totals']['pts'],
        "away_score": opponent_team['team_totals']['pts'] if is_knicks_home else knicks_team['team_totals']['pts'],
        "knicks_starters": knicks_team['starters'],
        "opponent_starters": opponent_team['starters'],
        "knicks_totals": knicks_team['team_totals'],
        "opponent_totals": opponent_team['team_totals'],
        "summary": game['summary']['game_summary']
    }
    
    return game_data

# Generate performance analysis using OpenAI
def generate_basketball_performance_analysis():
    # Get all games from JSON
    games = load_basketball_data()
    if not games:
        return "No data available for performance analysis."
    
    # Format game data for analysis
    formatted_games = []
    for game in games:
        formatted_game = format_game_data_for_analysis(game)
        formatted_games.append(formatted_game)
    
    # Calculate team stats
    team_stats = calculate_basketball_team_stats(games)
    
    # Create prompt for OpenAI
    prompt = f"""
    You are a professional basketball analyst specializing in analyzing team performance.
    
    Please analyze the New York Knicks' performance based on the following data:
    
    Team Statistics:
    {json.dumps(team_stats, indent=2)}
    
    Recent Games:
    {json.dumps(formatted_games, indent=2)}
    
    Please provide:
    1. Overall team performance assessment
    2. Analysis of strengths and weaknesses
    3. Key player performances
    4. Areas for improvement
    5. Recommendations for upcoming games
    
    Format your analysis in Markdown with clear headings and organized paragraphs.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional basketball analyst specializing in analyzing team performance."},
                {"role": "user", "content": prompt}
            ],
            
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating performance analysis: {e}")
        return "An error occurred during performance analysis. Please try again."

# Generate opponent analysis using OpenAI
def generate_basketball_opponent_analysis(opponent):
    # Get last 5 games from API
    games = get_last_basketball_games(NYK_TEAM_ID, 5)
    if not games:
        return f"No recent games data available for analysis against {opponent}."
    
    # Format games for analysis
    formatted_games = format_api_basketball_games(games)
    
    # Get opponent team info if possible
    opponent_info = None
    for game in games:
        if game['teams']['home']['name'] == opponent:
            opponent_info = get_basketball_team_info(game['teams']['home']['id'])
            break
        elif game['teams']['away']['name'] == opponent:
            opponent_info = get_basketball_team_info(game['teams']['away']['id'])
            break
    
    # Create prompt for OpenAI
    prompt = f"""
    You are a professional basketball analyst specializing in analyzing opponents.
    
    Please analyze {opponent} as an opponent for the New York Knicks based on the following data:
    
    Recent Knicks Games:
    {json.dumps(formatted_games, indent=2)}
    
    Opponent Information:
    {json.dumps(opponent_info, indent=2) if opponent_info else "No specific information available for this opponent."}
    
    Please provide:
    1. Overall assessment of {opponent}'s strengths and weaknesses
    2. Key players to watch
    3. Tactical analysis of their playing style
    4. Recommended strategies for the Knicks against {opponent}
    5. Threat level assessment (low, medium, high, very high)
    
    Format your analysis in Markdown with clear headings and organized paragraphs.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional basketball analyst specializing in analyzing opponents."},
                {"role": "user", "content": prompt}
            ],
            
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating opponent analysis: {e}")
        return f"An error occurred during analysis of {opponent}. Please try again."

# Generate game strategy using OpenAI
def generate_basketball_game_strategy(opponent, location):
    # Get games from JSON
    games = load_basketball_data()
    if not games:
        return "No data available for strategy analysis."
    
    # Format game data for analysis
    formatted_games = []
    for game in games:
        formatted_game = format_game_data_for_analysis(game)
        formatted_games.append(formatted_game)
    
    # Create prompt for OpenAI
    prompt = f"""
    You are a professional basketball tactical advisor for the New York Knicks.
    
    Please provide tactical advice for the upcoming game:
    
    Opponent: {opponent}
    Location: {location}
    
    Recent Games Data:
    {json.dumps(formatted_games, indent=2)}
    
    Please provide:
    1. Recommended starting lineup
    2. Tactical approach for this game
    3. Key matchups to exploit
    4. Defensive strategies
    5. Offensive strategies
    6. Key players who should get more minutes
    
    Format your analysis in Markdown with clear headings and organized paragraphs.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional basketball tactical advisor for the New York Knicks."},
                {"role": "user", "content": prompt}
            ],
            
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating game strategy: {e}")
        return "An error occurred during strategy analysis. Please try again."

# Generate lineup recommendation using OpenAI
def generate_basketball_lineup_recommendation(opponent):
    # Get games from JSON
    games = load_basketball_data()
    if not games:
        return {
            "formation": "Standard",
            "explanation": "No data available for lineup recommendation.",
            "players": []
        }
    
    # Format game data for analysis
    formatted_games = []
    for game in games:
        formatted_game = format_game_data_for_analysis(game)
        formatted_games.append(formatted_game)
    
    # Create prompt for OpenAI
    prompt = f"""
    You are a professional basketball coach specializing in lineup analysis and recommendations.
    
    Please recommend an optimal lineup for the New York Knicks for their game against {opponent} based on the following data:
    
    Recent Games:
    {json.dumps(formatted_games, indent=2)}
    
    Please provide:
    1. Recommended formation/lineup style (e.g., "Small Ball", "Twin Towers", "3-Point Heavy", etc.)
    2. Explanation for this recommendation
    3. List of 5 starting players with their numbers, positions, and roles
    
    Format your recommendation as JSON:
    {{
        "formation": "Small Ball",
        "explanation": "Explanation for this lineup choice",
        "players": [
            {{
                "number": 11,
                "name": "Player Name",
                "position": "PG",
                "role": "Primary Ball Handler"
            }},
            ...
        ]
    }}
    
    Use real New York Knicks players from the provided data.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional basketball coach specializing in lineup analysis."},
                {"role": "user", "content": prompt}
            ],
            
        )
        
        # Parse JSON response
        result = response.choices[0].message.content
        # Extract JSON part
        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # If JSON parsing fails, return default
            return {
                "formation": "Standard",
                "explanation": "Error parsing lineup recommendation.",
                "players": []
            }
    except Exception as e:
        print(f"Error generating lineup recommendation: {e}")
        return {
            "formation": "Standard",
            "explanation": "Error generating lineup recommendation.",
            "players": []
        }

# Generate game report using OpenAI
def generate_basketball_game_report(game_id):
    # Get games from JSON
    games = load_basketball_data()
    if not games:
        return "No data available for game report."
    
    # Find the game with the given ID
    game = None
    for g in games:
        if g['game_date'].replace(" ", "-").replace(",", "") == game_id:
            game = g
            break
    
    if not game:
        return "Game not found."
    
    # Format game data for analysis
    game_data = format_game_data_for_analysis(game)
    
    # Create prompt for OpenAI
    prompt = f"""
    You are a professional basketball journalist specializing in game reports.
    
    Please write a detailed report for the following game:
    
    Game Information:
    {json.dumps(game_data, indent=2)}
    
    Please include:
    1. An engaging headline
    2. Game summary
    3. Key moments and turning points
    4. Analysis of both teams' performance
    5. Standout players and their achievements
    6. Coaching decisions and tactical observations
    
    Format your report in Markdown with clear headings and organized paragraphs.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional basketball journalist specializing in game reports."},
                {"role": "user", "content": prompt}
            ],
            
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating game report: {e}")
        return "An error occurred while generating the game report. Please try again."

# Generate next game prediction using OpenAI
def generate_basketball_game_prediction():
    # Get next game from API
    next_game = get_next_basketball_game()
    if not next_game:
        return {
            "home_team": "New York Knicks",
            "away_team": "Opponent",
            "predicted_score": "0 - 0",
            "explanation": "No information found for the next game."
        }
    
    # Get last 5 games for Knicks
    knicks_games = get_last_basketball_games(NYK_TEAM_ID, 5)
    
    # Determine opponent team ID
    is_home = next_game['teams']['home']['id'] == NYK_TEAM_ID
    opponent_id = next_game['teams']['away']['id'] if is_home else next_game['teams']['home']['id']
    opponent_games = get_last_basketball_games(opponent_id, 5)
    
    # Format game data for analysis
    knicks_formatted = format_api_basketball_games(knicks_games)
    opponent_formatted = format_api_basketball_games(opponent_games)
    
    home_team = next_game['teams']['home']['name']
    away_team = next_game['teams']['away']['name']
    
    # Create prompt for OpenAI
    prompt = f"""
    You are a professional basketball analyst specializing in game predictions.
    
    Please analyze and predict the outcome of the upcoming game:
    
    Home Team: {home_team}
    Away Team: {away_team}
    Date: {next_game['date']}
    
    Recent New York Knicks Games:
    {json.dumps(knicks_formatted, indent=2)}
    
    Recent Opponent Games:
    {json.dumps(opponent_formatted, indent=2)}
    
    Please provide:
    1. Predicted final score (e.g., "105 - 98")
    2. Detailed analysis explaining your prediction
    
    Note: The prediction should be realistic based on the available data.
    If one team is clearly stronger, the score should reflect that.
    
    Format your response as JSON:
    {{
        "predicted_score": "105 - 98",
        "explanation": "Detailed analysis in English"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional basketball analyst. Respond in English and in JSON format only."},
                {"role": "user", "content": prompt}
            ]
        )
        # Get the response content
        result = response.choices[0].message.content.strip()
        
        # Try to find JSON in the response
        try:
            # First try to parse the entire response as JSON
            prediction_data = json.loads(result)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON from the response using regex
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                try:
                    prediction_data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    raise ValueError("Could not parse prediction data")
            else:
                raise ValueError("No valid JSON found in response")
        
        # Validate the prediction data
        if not isinstance(prediction_data, dict):
            raise ValueError("Invalid prediction data format")
        
        if "predicted_score" not in prediction_data or "explanation" not in prediction_data:
            raise ValueError("Missing required prediction fields")
        
        # Keep the scores in their original order based on home/away teams
        return {
            "home_team": home_team,
            "away_team": away_team,
            "predicted_score": prediction_data["predicted_score"],
            "explanation": prediction_data["explanation"]
        }
        
    except Exception as e:
        print(f"Error generating prediction: {str(e)}")
        return {
            "home_team": home_team,
            "away_team": away_team,
            "predicted_score": "105 - 98",
            "explanation": "Based on recent performance, we predict a close game with the Knicks having a slight edge."
        }

# Handle basketball chat queries using OpenAI
def handle_basketball_chat_query(query):
    # Get games from JSON
    games = load_basketball_data()
    
    # Format game data for context
    formatted_games = []
    for game in games:
        formatted_game = format_game_data_for_analysis(game)
        formatted_games.append(formatted_game)
    
    # Create prompt for OpenAI
    prompt = f"""
    You are an intelligent assistant for the New York Knicks basketball team. You can answer questions about the team, games, statistics, and players.
    
    Recent Games Data:
    {json.dumps(formatted_games, indent=2)}
    
    User Question: {query}
    
    Provide a helpful and accurate response based on the available data. If the question is outside your knowledge or not related to the New York Knicks, politely explain that.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an intelligent assistant for the New York Knicks basketball team."},
                {"role": "user", "content": prompt}
            ],
            
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error handling chat query: {e}")
        return "Sorry, an error occurred while processing your question. Please try again."

#################
# FLASK ROUTES #
#################

# Landing page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/request-demo')
def request_demo():
    return render_template('request-demo.html')

# Football frontend
@app.route('/football')
def football():
    return render_template('football.html')

# Basketball frontend
@app.route('/basketball')
def basketball():
    return render_template('basketball.html')

# Football API routes
@app.route('/get_team_stats')
def get_team_stats():
    # Get last 5 matches
    matches = get_last_matches(TEAM_ID, 5)
    
    # Calculate team stats
    stats = calculate_football_team_stats(matches)
    
    # Format matches for display
    formatted_matches = format_football_matches_for_display(matches)
    
    # Get recent matches for match selector
    recent_matches = []
    for match in formatted_matches:
        recent_match = {
            "match_id": match["match_id"],
            "date": match["date"],
            "home_team": match["home_team"],
            "away_team": match["away_team"],
            "home_score": match["home_score"],
            "away_score": match["away_score"]
        }
        recent_matches.append(recent_match)
    
    return jsonify({
        "stats": stats,
        "matches": formatted_matches,
        "recent_matches": recent_matches
    })

@app.route('/predict_next_match')
def predict_next_match():
    prediction = generate_football_next_match_prediction()
    return jsonify({"prediction": prediction})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    analysis_type = data.get('analysis_type')
    
    if analysis_type == 'opponent':
        opponent = data.get('opponent')
        analysis = generate_football_threat_analysis(opponent)
    elif analysis_type == 'performance':
        analysis = generate_football_performance_analysis()
    elif analysis_type == 'next_match':
        opponent = data.get('opponent')
        league = data.get('league')
        analysis = generate_football_next_match_tactics(opponent, league)
    else:
        return jsonify({"error": "Invalid analysis type"}), 400
    
    return jsonify({"analysis": analysis})

@app.route('/recommend_formation', methods=['POST'])
def recommend_formation():
    data = request.json
    opponent = data.get('opponent')
    
    recommendation = generate_football_formation_recommendation(opponent)
    return jsonify(recommendation)

@app.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    match_id = data.get('match_id')
    
    report = generate_football_match_report(match_id)
    return jsonify({"report": report})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query')
    
    response = handle_football_chat_query(query)
    return jsonify({"response": response})

# Basketball API routes
@app.route('/get_basketball_stats')
def get_basketball_stats():
    # Get games from JSON
    games = load_basketball_data()
    
    # Calculate team stats
    stats = calculate_basketball_team_stats(games)
    
    # Format games for display
    formatted_games = format_games_for_display(games)
    
    # Get recent games for game selector
    recent_games = []
    for game in formatted_games:
        recent_game = {
            "game_id": game["match_id"],
            "date": game["date"],
            "home_team": game["home_team"],
            "away_team": game["away_team"],
            "home_score": game["home_score"],
            "away_score": game["away_score"]
        }
        recent_games.append(recent_game)
    
    return jsonify({
        "stats": stats,
        "games": formatted_games,
        "recent_games": recent_games
    })

@app.route('/predict_basketball_game')
def predict_basketball_game():
    prediction = generate_basketball_game_prediction()
    return jsonify({"prediction": prediction})

@app.route('/analyze_basketball', methods=['POST'])
def analyze_basketball():
    data = request.json
    analysis_type = data.get('analysis_type')
    
    if analysis_type == 'opponent':
        opponent = data.get('opponent')
        analysis = generate_basketball_opponent_analysis(opponent)
    elif analysis_type == 'performance':
        analysis = generate_basketball_performance_analysis()
    elif analysis_type == 'strategy':
        opponent = data.get('opponent')
        location = data.get('location')
        analysis = generate_basketball_game_strategy(opponent, location)
    else:
        return jsonify({"error": "Invalid analysis type"}), 400
    
    return jsonify({"analysis": analysis})

@app.route('/recommend_basketball_lineup', methods=['POST'])
def recommend_basketball_lineup():
    data = request.json
    opponent = data.get('opponent')
    
    recommendation = generate_basketball_lineup_recommendation(opponent)
    return jsonify(recommendation)

@app.route('/generate_basketball_report', methods=['POST'])
def generate_basketball_report():
    data = request.json
    game_id = data.get('game_id')
    
    report = generate_basketball_game_report(game_id)
    return jsonify({"report": report})

@app.route('/basketball_chat', methods=['POST'])
def basketball_chat():
    data = request.json
    query = data.get('query')
    
    response = handle_basketball_chat_query(query)
    return jsonify({"response": response})

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
