import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import openai
import os
import feedparser
import random

# ============ DATA CACHING HELPERS ============
def cache_with_expiry(key, data, hours=24):
    """Cache data with expiration timestamp"""
    st.session_state[key] = {
        'data': data,
        'cached_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(hours=hours)
    }

def get_cached_data(key):
    """Get cached data if not expired"""
    if key in st.session_state:
        cache = st.session_state[key]
        if isinstance(cache, dict) and 'expires_at' in cache:
            if datetime.now() < cache['expires_at']:
                return cache['data']
            else:
                del st.session_state[key]
    return None

# Initialize session state only
if "current_platform" not in st.session_state:
    st.session_state.current_platform = "Home"


# Initialize session state only
if "current_platform" not in st.session_state:
    st.session_state.current_platform = "Home"

# Initialize current page for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Case Search"

# Configure Streamlit page
st.set_page_config(
  page_title="Shorthand Studios - Content Intelligence Platform",
  layout="wide"
)

# Enhanced CSS for Shorthand Studios website styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:wght@600;700&family=Inter:wght@300;400;500;600;700;800;900&display=swap');
            
:root {
  --primary-text: #221F1F;
  --accent-red: #DC143C;  /* CHANGED: From #DC143C (light blue) to #DC143C (bold red) */
  --secondary-red: #ff9797;
  --background: #FFFFFF;
  --footer-grey: #666666;
}

/* Global styles */
* {
  color: var(--primary-text);
}

body {
  background-color: var(--background);
}

.main .block-container {
  padding-top: 0.5rem;
  max-width: 1200px;
  padding-left: 4rem;
  padding-right: 4rem;
}

/* Hero section */
.hero-section {
  min-height: 70vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: 1rem 0;
  background: var(--background);
  margin-bottom: 1rem;
  margin-top: 0;
}

.hero-headline {
  font-family: 'Inter', sans-serif;
  font-size: 130px;
  font-weight: 900;
  text-transform: uppercase;
  color: var(--primary-text);
  line-height: 0.9;
  letter-spacing: -4px;
  margin-bottom: 1rem;
}

.hero-headline .accent {
  color: var(--accent-red);  /* CHANGED: Now uses red */
}
            
.tagline {
  font-family: 'Inter', sans-serif;
  font-size: 30px;
  font-weight: 300;
  color: var(--primary-text);
  line-height: 1.4;
  margin-bottom: 2rem;  /* CHANGED: Reduced from 3rem */
  max-width: 600px;
}

/* Content Intelligence Platform section */
.content-intelligence-section {
  margin-top: 1rem;  /* ADDED: Control spacing above this section */
  margin-bottom: 2rem;  /* ADDED: Control spacing below */
}

.content-intelligence-header {
  font-family: 'Inter', sans-serif;
  font-size: 48px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--primary-text);
  letter-spacing: -1px;
  margin-bottom: 1rem;  /* ADDED: Reduce spacing after header */
}

/* CTA Buttons */
.stButton > button {
  background: #A0A0A0;  /* Gray background by default */
  color: #FFFFFF;  /* White text */
  border: none;
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 4px;
  padding: 1rem 2rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stButton > button:hover {
  background: var(--accent-red);  /* Red background on hover */
  color: #FFFFFF;  /* White text on red */
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
            
/* Section headings */
h1, h2, h3 {
  font-family: 'Crimson Text', serif;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--primary-text);
  letter-spacing: -1px;
}

h2 {
  font-size: 35px;
  margin-bottom: 2rem;
}

h3 {
  font-size: 35px;
  margin-bottom: 1.5rem;
}

/* Numbered lists */
.numbered-list {
  counter-reset: section;
  margin: 2rem 0;
}

.numbered-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.numbered-item::before {
  counter-increment: section;
  content: "0" counter(section);
  font-family: 'Inter', sans-serif;
  font-size: 44px;
  font-weight: 800;
  color: var(--accent-red);
  margin-right: 2rem;
  min-width: 80px;
}

/* Body text */
p, .stMarkdown {
  font-family: 'Inter', sans-serif;
  font-size: 19px;
  font-weight: 300;
  line-height: 1.6;
  color: var(--primary-text);
}

/* Two column layout */
.two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  margin: 4rem 0;
  align-items: center;
}

/* Hexagon shapes for ecosystem */
.hexagon {
  width: 120px;
  height: 120px;
  background: var(--secondary-red);
  position: relative;
  margin: 60px auto;
  display: flex;
  align-items: center;
  justify-content: center;
  clip-path: polygon(30% 0%, 70% 0%, 100% 50%, 70% 100%, 30% 100%, 0% 50%);
}

.hexagon.blue {
  background: var(--accent-red);
}

/* AI Analysis box - updated style */
.ai-analysis {
  background: #f8f9fa;
  border-left: 4px solid var(--accent-red);
  border-radius: 0;
  padding: 2rem;
  margin: 2rem 0;
  font-family: 'Inter', sans-serif;
}

/* Expander style */
.stExpander {
  border: 1px solid #e0e0e0;
  border-radius: 0;
  margin-bottom: 1rem;
}

/* Footer */
.footer {
  background: #000000;  /* Changed to black */
  color: #FFFFFF;  /* Changed to white */
  padding: 4rem 2rem;
  margin: 4rem -4rem -2rem -4rem;
  text-align: left;
  font-family: 'Inter', sans-serif;
}

.footer .brand {
  font-size: 24px;
  font-weight: 800;
  text-transform: uppercase;
  color: #FFFFFF;  /* Changed to white */
  margin-bottom: 1rem;
}

/* Sidebar styling */
.css-1d391kg {
  background-color: #fafafa;
}
            
/* Sidebar styling - black background with white text */
section[data-testid="stSidebar"] {
    background-color: #000000 !important;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] .stRadio label {
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #FFFFFF !important;
}

/* Radio button styling */
section[data-testid="stSidebar"] [data-baseweb="radio"] {
    background-color: #000000 !important;
}

/* Make radio button circles visible on black background */
section[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    background-color: #000000 !important;
}

/* Selected radio button - RED */
section[data-testid="stSidebar"] [aria-checked="true"] > div:first-child > div {
    background-color: #DC143C !important;
    border-color: #DC143C !important;
}

/* Selected radio button inner circle - RED */
section[data-testid="stSidebar"] [aria-checked="true"] > div:first-child > div > div {
    background-color: #DC143C !important;
}

/* Unselected radio buttons */
section[data-testid="stSidebar"] [aria-checked="false"] > div:first-child > div {
    background-color: #000000 !important;
    border-color: #666666 !important;
}         

/* Input fields */
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-family: 'Inter', sans-serif;
  font-size: 16px;
}

/* Metrics */
.metric-container {
  background: var(--background);
  border: 1px solid #e0e0e0;
  padding: 1.5rem;
  border-radius: 4px;
  text-align: center;
}

/* Info boxes */
.stInfo {
  background-color: rgba(188, 229, 247, 0.1);
  border: 1px solid var(--accent-red);
  border-radius: 4px;
}

/* Success messages */
.stSuccess {
  background-color: rgba(188, 229, 247, 0.1);
  color: var(--primary-text);
  border: 1px solid var(--accent-red);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 2rem;
  border-bottom: 2px solid #e0e0e0;
}

.stTabs [data-baseweb="tab"] {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--primary-text);
  padding: 1rem 0;
}

.stTabs [aria-selected="true"] {
  color: var(--accent-red);
  border-bottom: 3px solid var(--accent-red);
}

/* White space and layout */
.section-spacing {
  margin: 6rem 0;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

/* Make subreddit button text smaller */
div[data-testid="column"] button p {
  font-size: 12px !important;
  line-height: 1.2 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}
</style>
""", unsafe_allow_html=True)


# ============ API KEY MANAGEMENT ============

def get_api_keys():
    """Get API keys from environment variables"""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    youtube_key = os.getenv("YOUTUBE_API_KEY", "")
    spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
    spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    tmdb_key = os.getenv("TMDB_API_KEY", "")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    serper_api_key = os.getenv("SERPER_API_KEY", "")
    perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
    courtlistener_token = os.getenv("COURTLISTENER_API_TOKEN", "")  

    return openai_key, youtube_key, spotify_client_id, spotify_client_secret, tmdb_key, gemini_api_key, serper_api_key, perplexity_api_key, courtlistener_token  # ADD courtlistener_token

# Get API keys from environment variables
api_key, youtube_api_key, spotify_client_id, spotify_client_secret, tmdb_key, gemini_api_key, serper_api_key, perplexity_api_key, courtlistener_token = get_api_keys()

# Hardcode Bailey Sarian as the creator
creator_name = "Bailey Sarian"

# Get API keys from environment variables
api_key, youtube_api_key, spotify_client_id, spotify_client_secret, tmdb_key, gemini_api_key, serper_api_key, perplexity_api_key, courtlistener_token = get_api_keys()

# Hardcode Bailey Sarian as the creator
creator_name = "Bailey Sarian"

# ============ ADD LOGIN PAGE HERE ============

# Add this after your API keys initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Login page
if not st.session_state.authenticated:
    # Custom CSS for the login page
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap');
    
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 300px;
        text-align: center;
    }
    
    .cursive-text {
        font-family: 'Dancing Script', cursive;
        font-size: 32px;
        font-weight: 700;
        color: #666666;
        margin-bottom: 0;
    }
    
    .bailey-text {
        font-family: 'Crimson Text', serif;
        font-size: 60px;
        font-weight: 700;
        color: #000000;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: -10px;
        margin-bottom: 0;
    }
    
    .crime-lab-text {
        font-family: 'Crimson Text', serif;
        font-size: 60px;
        font-weight: 700;
        color: #DC143C;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: -20px;
        margin-bottom: 30px;
    }
    
    .stTextInput > div > div > input {
        text-align: center;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create centered login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <p class="cursive-text">You are about to enter</p>
            <h1 class="bailey-text">BAILEY SARIAN'S</h1>
            <h1 class="crime-lab-text">CRIME LAB</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Password input
        password = st.text_input(
            "Enter Password", 
            type="password", 
            placeholder="Enter password to continue...",
            key="login_password",
            label_visibility="collapsed"
        )
        
        # Center the button
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_b:
            if st.button("ENTER", type="primary", use_container_width=True):
                if password == "baileysarian":
                    st.session_state.authenticated = True
                    st.success("Access granted! Welcome to Bailey's Crime Lab")
                    st.rerun()
                else:
                    st.error("Incorrect password. Please try again.")
        
        # Add a subtle hint or footer
        st.markdown("""
        <div style="text-align: center; margin-top: 30px; color: #999;">
            <small>Authorized personnel only</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# ============ SIDEBAR NAVIGATION ============

# Initialize current_page if it doesn't exist
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Case Search"  # Default page

# Main navigation selection
st.sidebar.markdown("""
<p style="font-family: 'Crimson Text', serif; font-size: 30px; font-weight: 600; color: #FFFFFF; margin-bottom: 0.5rem;">
WORKSPACE
</p>
""", unsafe_allow_html=True)

main_section = st.sidebar.radio(
    "",  # Empty label since we're using custom markdown
    ["Research", "Production"],
    key="main_nav",
    label_visibility="collapsed"  # Hide the empty label
)

st.sidebar.markdown("---")

# Sub-navigation based on main selection
if main_section == "Research":
    st.sidebar.markdown("""
    <p style="font-family: 'Crimson Text', serif; font-size: 30px; font-weight: 600; color: #FFFFFF; margin-bottom: 0.5rem;">
    TOOLS
    </p>
    """, unsafe_allow_html=True)
    
    research_pages = ["Case Search", "Trending Cases", "True Crime Podcasts", "YouTube Competitors", "Movies & TV Shows", "Court Documents"]
    
    # Ensure current_page is valid for Research section
    if st.session_state.current_page not in research_pages and st.session_state.current_page != "Privacy Policy":
        st.session_state.current_page = "Case Search"
    
    selected_page = st.sidebar.radio(
        "",
        research_pages,
        key="research_nav",
        index=research_pages.index(st.session_state.current_page) if st.session_state.current_page in research_pages else 0,
        label_visibility="collapsed"
    )
    st.session_state.current_page = selected_page
    
else:  # PRODUCTION
    st.sidebar.markdown("""
    <p style="font-family: 'Crimson Text', serif; font-size: 30px; font-weight: 600; color: #FFFFFF; margin-bottom: 0.5rem;">
    TOOLS
    </p>
    """, unsafe_allow_html=True)
    
    production_pages = ["Saved Ideas", "Script Builder", "Episode Calendar"]
    
    # Ensure current_page is valid for Production section
    if st.session_state.current_page not in production_pages and st.session_state.current_page != "Privacy Policy":
        st.session_state.current_page = "Saved Ideas"
    
    selected_page = st.sidebar.radio(
        "",
        production_pages,
        key="production_nav",
        index=production_pages.index(st.session_state.current_page) if st.session_state.current_page in production_pages else 0,
        label_visibility="collapsed"
    )
    st.session_state.current_page = selected_page


st.sidebar.markdown("---")

# ============ MAIN CONTENT ============

def get_relevant_subreddits_for_creator(creator_name, api_key):
    """Use AI to find 12 most relevant subreddits for a creator"""
    if not api_key:
        return None
    
    prompt = f"""Analyze the creator "{creator_name}" and suggest the 12 most relevant subreddits for their content.

Focus on:
1. Subreddits that match their content niche/topic
2. Communities with good audience size (avoid tiny subreddits with <10k members)
3. Active communities where their content would be relevant
4. Mix of primary niche + related/crossover communities
5. Use actual existing subreddit names (check they exist)

For example, if analyzing "Bailey Sarian":
- Primary niche: TrueCrime, serialkillers, UnresolvedMysteries
- Beauty crossover: MakeupAddiction, beauty, SkinCareAddiction  
- Storytelling: nosleep, LetsNotMeet, creepy
- General: AskReddit, todayilearned, videos

Return ONLY a Python list of subreddit names (without r/ prefix), exactly like this format:
["TrueCrime", "serialkillers", "UnresolvedMysteries", "MakeupAddiction", "beauty", "nosleep", "LetsNotMeet", "creepy", "AskReddit", "todayilearned", "videos", "entertainment"]

Creator: {creator_name}"""

    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            timeout=30
        )
        
        # Parse the AI response to extract the list
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract the list from the response
        import ast
        try:
            # Look for a list in the response
            start = response_text.find('[')
            end = response_text.find(']') + 1
            if start != -1 and end != 0:
                list_text = response_text[start:end]
                subreddits = ast.literal_eval(list_text)
                if isinstance(subreddits, list) and len(subreddits) <= 12:
                    return subreddits[:12]  # Ensure max 12
        except:
            pass
            
        # Fallback: extract subreddit names manually using regex
        import re
        subreddits = re.findall(r'"([^"]+)"', response_text)
        if subreddits:
            return subreddits[:12]
        
        # Final fallback: try to extract words that look like subreddit names
        words = response_text.replace('[', '').replace(']', '').replace('"', '').split(',')
        clean_subreddits = []
        for word in words:
            clean_word = word.strip()
            if clean_word and len(clean_word) > 2 and len(clean_word) < 25:
                clean_subreddits.append(clean_word)
        
        return clean_subreddits[:12] if clean_subreddits else None
            
    except Exception as e:
        st.error(f"Error getting relevant subreddits: {str(e)}")
        return None

# Simple header for the True Crime Research Hub
st.markdown("""
<div style="padding: 2rem 0 1rem 0; border-bottom: 2px solid #e0e0e0; margin-bottom: 2rem;">
    <h1 style="font-family: 'Crimson Text', serif; font-size: 60px; font-weight: 700; margin: 0; text-transform: none;">
        BAILEY'S <span style="color: #DC143C;">CRIME LAB</span>
    </h1>
    <p style="font-size: 18px; color: #666; margin-top: 0.5rem;">Research cases, uncover trends, and create killer content</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'saved_posts' not in st.session_state:
  st.session_state.saved_posts = []
if 'show_concepts' not in st.session_state:
  st.session_state.show_concepts = []
if 'selected_subreddit' not in st.session_state:
  st.session_state.selected_subreddit = "TrueCrime"

# Reddit API headers
HEADERS = {
  'User-Agent': 'web:shorthand-reddit-analyzer:v1.0.0 (by /u/Ruhtorikal)',
  'Accept': 'application/json',
}

# ============ REDDIT FUNCTIONS ============

def save_post(post_data, analysis, creator_name, subreddit):
  """Save a post with its analysis for show planning"""
  saved_post = {
    'id': f"{post_data['id']}_{creator_name}",
    'title': post_data['title'],
    'score': post_data['score'],
    'num_comments': post_data['num_comments'],
    'subreddit': subreddit,
    'creator': creator_name,
    'analysis': analysis,
    'permalink': post_data['permalink'],
    'saved_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
    'image_url': post_data.get('image_url', ''),
    'content': post_data.get('selftext', '')[:200] + '...' if post_data.get('selftext') else ''
  }
  
  existing_ids = [p['id'] for p in st.session_state.saved_posts]
  if saved_post['id'] not in existing_ids:
    st.session_state.saved_posts.append(saved_post)
    return True
  return False

def get_reddit_posts(subreddit, category="hot", limit=5):
  """Get posts from specified subreddit and category"""
  urls_to_try = [
    f"https://www.reddit.com/r/{subreddit}/{category}.json",  # Removed ?limit from URL
    f"https://old.reddit.com/r/{subreddit}/{category}.json",
    f"https://np.reddit.com/r/{subreddit}/{category}.json",
  ]
  
  headers_variants = [
    {
      'User-Agent': 'web:shorthand-reddit-analyzer:v1.0.0 (by /u/Ruhtorikal)',
      'Accept': 'application/json',
    },
    {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      'Accept': 'application/json',
    }
  ]
  
  for url in urls_to_try:
    for headers in headers_variants:
      try:
        time.sleep(2)
        params = {'limit': limit, 'raw_json': 1}
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
          data = response.json()
          if 'data' in data and 'children' in data['data'] and data['data']['children']:
            return data['data']['children'][:limit]  # Force slice to limit
        elif response.status_code == 429:
          time.sleep(5)
          continue
      except:
        continue
  
  return []

def get_top_comments(subreddit, post_id, limit=3):
  """Get top comments for a specific post"""
  url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
  
  try:
    time.sleep(2)
    response = requests.get(url, headers=HEADERS, timeout=15)
    
    if response.status_code == 200:
      data = response.json()
      if len(data) > 1 and 'data' in data[1] and 'children' in data[1]['data']:
        comments = []
        for comment in data[1]['data']['children'][:limit]:
          if comment['kind'] == 't1' and 'body' in comment['data']:
            comments.append({
              'body': comment['data']['body'],
              'score': comment['data']['score'],
              'author': comment['data'].get('author', '[deleted]')
            })
        return comments
  except:
    pass
  
  return []

def search_with_serper(query, api_key, search_type="search", num_results=10):
    """Search the web using Serper API for real-time information"""
    if not api_key:
        return None
    
    try:
        # Serper API endpoint
        if search_type == "news":
            url = "https://google.serper.dev/news"
        else:
            url = "https://google.serper.dev/search"
        
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        # For true crime searches, add context
        enhanced_query = f"{query} murder case crime true crime"
        
        payload = {
            'q': enhanced_query,
            'num': num_results,
            'gl': 'us',
            'hl': 'en'
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            results = {
                'organic': [],
                'news': [],
                'answer_box': data.get('answerBox', {}),
                'knowledge_graph': data.get('knowledgeGraph', {}),
            }
            
            # Process organic results
            for item in data.get('organic', []):
                results['organic'].append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', ''),
                    'date': item.get('date', ''),
                    'source': item.get('source', '')
                })
            
            # Also get news results
            news_response = requests.post(
                "https://google.serper.dev/news",
                headers=headers,
                json={'q': enhanced_query, 'num': 5},
                timeout=10
            )
            
            if news_response.status_code == 200:
                news_data = news_response.json()
                for item in news_data.get('news', []):
                    results['news'].append({
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'link': item.get('link', ''),
                        'date': item.get('date', ''),
                        'source': item.get('source', '')
                    })
            
            return results
        else:
            return None
            
    except Exception as e:
        print(f"Serper search error: {e}")
        return None

def search_with_perplexity(query, api_key, search_type="comprehensive"):
    """
    Use Perplexity AI to search and analyze information about a case
    search_type: "comprehensive", "quick", "news", "academic"
    """
    if not api_key:
        return None
    
    try:
        from openai import OpenAI
        
        # Initialize Perplexity client
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )
        
        # Craft the prompt based on search type
        if search_type == "comprehensive":
            prompt = f"""
            Provide a comprehensive summary about: {query}
            
            Include:
            1. Overview of the case/incident
            2. Key dates and timeline
            3. People involved (victims, suspects, investigators)
            4. Current status or resolution
            5. Recent developments or updates
            6. Media coverage and public interest
            7. Controversies or mysteries
            8. Related cases or connections
            
            Focus on factual, verified information from reliable sources.
            Include source citations where possible.
            """
        elif search_type == "news":
            prompt = f"""
            Find the latest news and updates about: {query}
            
            Focus on:
            - Recent developments (last 30 days)
            - Breaking news
            - New evidence or revelations
            - Legal proceedings updates
            - Media coverage
            
            Cite your sources with dates.
            """
        elif search_type == "quick":
            prompt = f"""
            Provide a brief summary about: {query}
            
            Include only the most essential facts:
            - What happened
            - When and where
            - Who was involved
            - Current status
            
            Keep it concise but informative.
            """
        else:  # academic
            prompt = f"""
            Provide an analytical overview of: {query}
            
            Include:
            - Scholarly analysis
            - Psychological profiles if applicable
            - Forensic details
            - Legal precedents
            - Comparative analysis with similar cases
            
            Use academic and professional sources.
            """
        
        # Make the API call to Perplexity
        response = client.chat.completions.create(
            model="sonar",  # Correct model name from Perplexity docs
            messages=[
                {
                    "role": "system",
                    "content": "You are a true crime researcher helping Bailey Sarian research cases for Murder, Mystery & Makeup. Provide accurate, detailed information with sources."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,  # Lower temperature for more factual responses
            max_tokens=2000
        )
        
        return {
            'summary': response.choices[0].message.content,
            'model': response.model,
            'usage': response.usage
        }
        
    except Exception as e:
        st.error(f"Perplexity API Error: {str(e)}")
        return None

def get_perplexity_case_analysis(case_name, perplexity_api_key):
    """Get comprehensive case analysis using Perplexity's online model"""
    if not perplexity_api_key:
        return None
    
    try:
        import requests
        import json
        import re
        
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "sonar",
            "messages": [{
                "role": "user",
                "content": f"""Search for information about "{case_name}" ONLY in the context of:
                - Murder cases
                - Homicides
                - Serial killers
                - Missing persons (presumed dead)
                - Unsolved mysteries involving death
                - True crime cases
                
                DO NOT include:
                - Political cases
                - Civil lawsuits
                - Corporate fraud
                - Non-violent crimes
                - Living people (unless they are perpetrators/suspects in murder cases)
                
                IMPORTANT CITATION RULES:
                - DO NOT use numbered citations like [1][2][3] in your response
                - Instead, use inline source attribution like "according to FBI records" or "as reported by CNN"
                - At the very end, add a "Sources:" section listing the sources you referenced
                
                If "{case_name}" is NOT associated with any murder/death/true crime case, respond with:
                "No true crime case found for this name. This may be a political figure, civil case, or living person not associated with murder cases."
                
                If you find a TRUE CRIME case, include:
                1. What happened (the murder/crime)
                2. When and where it occurred
                3. Victim(s) - full names and ages if available
                4. Suspect(s)/Perpetrator(s)
                5. Current status (solved/unsolved/convicted)
                6. Key evidence or mysteries
                7. Recent updates
                
                End with:
                Sources:
                - List your sources here
                
                Remember: This is for a true crime podcast. ONLY return information about murders, deaths, or violent crimes."""
            }],
            "temperature": 0.2,
            "max_tokens": 2000
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Remove any remaining numbered citations like [1][2][3]
            content = re.sub(r'\[\d+\](\[\d+\])*', '', content)
            
            # Check if no crime case was found
            if "no true crime case found" in content.lower():
                return {
                    'overview': f"❌ **No True Crime Case Found**\n\n{content}\n\nTry searching for:\n- A different spelling\n- Adding context (e.g., 'victim' or 'murder')\n- Including location or year"
                }
            
            return {
                'overview': content
            }
        else:
            print(f"Perplexity API error: {response.status_code} - {response.text}")
            st.error(f"Perplexity API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Perplexity API error: {str(e)}")
        st.error(f"Perplexity API error: {str(e)}")
        return None
            
def search_reddit_by_keywords(query, subreddits, limit=5):
  """Search Reddit for posts containing specific keywords"""
  all_results = []
  
  # Search all of Reddit if specified
  if subreddits == ["all"]:
    try:
      search_url = "https://www.reddit.com/search.json"
      params = {
        'q': query,
        'sort': 'top',
        't': 'day',
        'limit': limit * 2,
        'type': 'link'
      }
      time.sleep(2)
      response = requests.get(search_url, headers=HEADERS, params=params, timeout=15)
      
      if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'children' in data['data']:
          posts = data['data']['children']
          for post in posts:
            post['data']['source_subreddit'] = post['data']['subreddit']
          all_results.extend(posts)
    except:
      # Fallback to popular subreddits if all Reddit search fails
      subreddits = ["Conservative", "Politics", "News", "WorldNews", "AskReddit", "PublicFreakout"]
  
  # Search specific subreddits
  if subreddits != ["all"]:
    for subreddit in subreddits:
      try:
        search_url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
          'q': query,
          'restrict_sr': 'true',
          'sort': 'top',
          't': 'day',
          'limit': limit
        }
        time.sleep(2)
        response = requests.get(search_url, headers=HEADERS, params=params, timeout=15)
        
        if response.status_code == 200:
          data = response.json()
          if 'data' in data and 'children' in data['data']:
            posts = data['data']['children']
            for post in posts:
              post['data']['source_subreddit'] = subreddit
            all_results.extend(posts)
      except:
        continue
  
  # Sort by score and return top results
  all_results.sort(key=lambda x: x['data']['score'], reverse=True)
  return all_results[:limit * 3]

def calculate_trending_score(upvotes, comments, created_utc):
  """Calculate a trending score based on upvotes, comments, and recency"""
  # Convert created_utc to hours ago
  hours_ago = (datetime.now() - datetime.fromtimestamp(created_utc)).total_seconds() / 3600
  
  # Prevent division by zero and give recent posts a boost
  time_factor = 1 / (hours_ago + 2) # +2 to prevent extreme values for very new posts
  
  # Engagement score
  engagement = upvotes + (comments * 2) # Comments weighted more heavily
  
  # Calculate trending score
  trending_score = engagement * time_factor
  
  return int(trending_score)

# ============ TRUE CRIME RESEARCH API FUNCTIONS ============

def search_wikidata(query, limit=25):
    """Search Wikidata for people, cases, or events"""
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "format": "json",
        "type": "item",
        "limit": limit,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            all_results = []
            
            # Collect all results without filtering
            for hit in data.get("search", []):
                all_results.append({
                    "id": hit.get("id"),
                    "label": hit.get("label", ""),
                    "description": hit.get("description", ""),
                    "url": f"https://www.wikidata.org/wiki/{hit.get('id')}"
                })
            
            # Return all results - let Bailey decide what's relevant
            return all_results[:limit]
            
    except Exception as e:
        print(f"Wikidata search error: {e}")
    
    return []

def get_wikipedia_content(article_title, max_chars=3000):
    """Fetch actual Wikipedia article content"""
    import urllib.parse
    
    # Use Wikipedia API to get article extract
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": article_title,
        "prop": "extracts",
        "exintro": True,  # Only the introduction
        "explaintext": True,  # Plain text, no HTML
        "exsectionformat": "plain",
        "exchars": max_chars  # Limit characters
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if "extract" in page_data:
                    return page_data["extract"]
    except Exception as e:
        print(f"Error fetching Wikipedia content: {e}")
    
    return ""

def search_with_gemini(query, gemini_api_key):
    """Use Gemini with grounding to search the real-time web"""
    if not gemini_api_key:
        return None
    
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        
        # Use Gemini 1.5 with grounding enabled
        model = genai.GenerativeModel(
            'gemini-1.5-flash-latest',
            tools=['google_search_retrieval']  # This enables grounding!
        )
        
        # Create a search prompt
        search_prompt = f"""Search the current internet for information about: {query}

Please search for and provide:
1. Latest information and facts about this person/case
2. Recent news articles or reports
3. Wikipedia or other biographical information
4. Court records or police reports if available
5. Timeline of events
6. Current status or recent developments

Focus on true crime, murder cases, or criminal activities if applicable.
Include specific dates, locations, and verified facts from your web search."""

        # Generate with grounding enabled
        response = model.generate_content(search_prompt)
        
        return response.text
        
    except Exception as e:
        print(f"Gemini search error: {e}")
        # Try without grounding if it fails
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            fallback_prompt = f"""Based on available information, tell me about: {query}
            
Focus on any criminal cases, murders, or true crime connections."""
            
            response = model.generate_content(fallback_prompt)
            return f"(Using cached knowledge, not live web search)\n\n{response.text}"
            
        except Exception as e2:
            return f"Error: {str(e2)}"    
def search_courtlistener(query, limit=20):
    """Search CourtListener for court documents and opinions"""
    url = "https://www.courtlistener.com/api/rest/v3/search/"
    params = {
        "q": query,
        "order_by": "dateFiled desc",
        "page_size": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = []
            for r in data.get("results", []):
                results.append({
                    "court": r.get("court", ""),
                    "date_filed": r.get("dateFiled", ""),
                    "case_name": r.get("caseName", ""),
                    "url": f"https://www.courtlistener.com{r.get('absolute_url', '')}",
                    "citation": r.get("citation", "")
                })
            return results
    except:
        pass
    return []

def count_youtube_videos(query, youtube_key):
    """Count YouTube videos about a topic"""
    if not youtube_key:
        return 0
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": youtube_key,
        "part": "id",
        "q": query,
        "type": "video",
        "maxResults": 50  # Just to get a count
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Total results gives us an estimate
            return data.get("pageInfo", {}).get("totalResults", 0)
    except:
        pass
    return 0

def calculate_real_case_score(case_data):
    """Calculate case score based on real data"""
    score = 50  # Base score
    
    # Wikipedia trend (weighted heavily)
    if case_data.get("wikipedia_trend"):
        trend = case_data["wikipedia_trend"]
        if trend > 50:  # Trending up significantly
            score += 20
        elif trend > 10:
            score += 10
        elif trend < -30:  # Trending down
            score -= 10
    
    # Media freshness (how recent is coverage)
    if case_data.get("days_since_coverage"):
        days = case_data["days_since_coverage"]
        if days < 7:
            score += 15  # Very fresh
        elif days < 30:
            score += 10
        elif days > 180:
            score -= 5  # Stale
    
    # YouTube saturation
    if case_data.get("youtube_count"):
        count = case_data["youtube_count"]
        if count < 10:
            score += 15  # Lots of room for content
        elif count < 50:
            score += 5
        elif count > 200:
            score -= 20  # Oversaturated
    
    # News mentions
    if case_data.get("news_mentions"):
        mentions = case_data["news_mentions"]
        if 5 < mentions < 30:
            score += 10  # Good amount of coverage
        elif mentions > 100:
            score -= 10  # Overexposed
    
    # Case characteristics
    if case_data.get("is_unsolved"):
        score += 15
    if case_data.get("has_mystery"):
        score += 10
    if case_data.get("good_era"):  # 1920s-1990s
        score += 10
    
    # Sensitivity penalties
    if case_data.get("involves_minors"):
        score -= 40
    if case_data.get("too_recent"):
        score -= 25
    
    return max(0, min(100, score))

def analyze_with_ai(post_title, post_content, comments, api_key, creator_name, image_url=None):
  """Analyze post and comments with OpenAI"""
  if not api_key:
    return None
  
  # Use legacy OpenAI method for Railway compatibility
  import openai
  openai.api_key = api_key
  
  # Prepare content for analysis
  content = f"Post Title: {post_title}\n"
  if post_content and post_content != post_title:
    content += f"Post Content: {post_content[:500]}...\n"
  
  content += "Top Comments:\n"
  for i, comment in enumerate(comments[:3], 1):
    content += f"{i}. {comment['body'][:200]}...\n"
  
  creator_prompt = f"""Analyze this Reddit post for {creator_name}'s content strategy. First, consider what you know about {creator_name}'s personality, political positions, communication style, and typical takes. Then analyze the content accordingly:

{content}

Provide analysis in this format:

SUMMARY: What this post is really about (1-2 sentences)

COMMENTER SENTIMENT: How the commenters in this thread are feeling (angry, excited, confused, etc.)

NEWS CONTEXT: Connect this to current events, trending topics, or recent news stories

NORMAL TAKE: What {creator_name} would typically say about this topic, based on their known positions and style

HOT TAKE: {creator_name}'s most provocative, exaggerated take designed for viral content - stay true to their personality but make it bold and shareable

SOCIAL CONTENT: Specific YouTube titles and social media content ideas that {creator_name} would actually use

CONTROVERSY LEVEL: How polarizing this content would be for {creator_name} (1-10 scale)

Important: Base your analysis on {creator_name}'s actual known personality, political positions, and communication style."""

  try:
    response = openai.ChatCompletion.create(
      model="gpt-4.1-nano",
      messages=[{"role": "user", "content": creator_prompt}],
      max_tokens=600,
      timeout=20
    )
    return response.choices[0].message.content
  except Exception as e:
    return f"AI Analysis Error: {str(e)}"

def generate_hashtags(title, subreddit, creator_name):
  """Generate relevant hashtags for social media"""
  # Clean creator name for hashtag
  creator_tag = creator_name.replace(" ", "")
  
  # Extract key words from title (simple approach)
  words = title.lower().split()
  stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 'were'}
  key_words = [w for w in words if w not in stop_words and len(w) > 3][:3]
  
  hashtags = [
    f"#{creator_tag}",
    f"#{subreddit}",
    "#reaction",
    "#commentary"
  ]
  
  for word in key_words:
    hashtags.append(f"#{word}")
  
  return " ".join(hashtags[:8]) # Limit to 8 hashtags

def display_posts(posts, subreddit, api_key=None, creator_name="Bailey Sarian"):
  """Display posts with analysis"""
  if not posts:
    st.warning("⚠️ No posts found. Try a different subreddit.")
    return
  
  for i, post in enumerate(posts):
    post_data = post['data']
    title = post_data.get('title', 'No title')
    score = post_data.get('score', 0)
    num_comments = post_data.get('num_comments', 0)
    author = post_data.get('author', '[deleted]')
    created = datetime.fromtimestamp(post_data.get('created_utc', 0))
    permalink = post_data.get('permalink', '')
    post_id = post_data.get('id', '')
    selftext = post_data.get('selftext', '')
    url = post_data.get('url', '')
    
    # Check if this is an image post
    image_url = None
    is_image = False
    if url and any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
      image_url = url
      is_image = True
    elif 'preview' in post_data and post_data['preview'] is not None and 'images' in post_data['preview']:
      try:
        image_url = post_data['preview']['images'][0]['source']['url'].replace('&amp;', '&')
        is_image = True
      except:
        pass
    
    post_data['image_url'] = image_url
    
    with st.expander(f"{i+1:02d} | {title[:80]}{'...' if len(title) > 80 else ''}", expanded=False):
      # Clean metrics display
      st.markdown(f"""
      <div style="display: flex; gap: 3rem; margin-bottom: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 8px;">
        <div style="text-align: center;">
          <p style="font-size: 32px; font-weight: 800; color: #DC143C; margin: 0;">{score:,}</p>
          <p style="font-size: 14px; text-transform: uppercase; color: #666;">Upvotes</p>
        </div>
        <div style="text-align: center;">
          <p style="font-size: 32px; font-weight: 800; color: #DC143C; margin: 0;">{num_comments:,}</p>
          <p style="font-size: 14px; text-transform: uppercase; color: #666;">Comments</p>
        </div>
        <div style="text-align: center;">
          <p style="font-size: 32px; font-weight: 800; color: #DC143C; margin: 0;">{int((datetime.now() - created).total_seconds() / 3600)}</p>
          <p style="font-size: 14px; text-transform: uppercase; color: #666;">Hours Ago</p>
        </div>
      </div>
      """, unsafe_allow_html=True)

      
      st.write(f"**Author:** u/{author}")
      
      # Display content based on type
      if is_image and image_url:
        st.write("**Image Post:**")
        st.image(image_url, width=400)
      elif selftext and len(selftext) > 50:
        st.write("**Post Content:**")
        st.write(selftext[:400] + "..." if len(selftext) > 400 else selftext)
      elif url and url != f"https://www.reddit.com{permalink}":
        st.write(f"**Link:** {url}")
      
      # Get comments
      with st.spinner("Fetching comments..."):
        comments = get_top_comments(subreddit, post_id, 3)
      
      if comments:
        st.write("**Top Comments:**")
        for j, comment in enumerate(comments, 1):
          st.write(f"{j}. **{comment['author']}** ({comment['score']} points):")
          st.write(f"  {comment['body'][:200]}{'...' if len(comment['body']) > 200 else ''}")
      
      # AI Analysis
      if api_key:
        with st.spinner("🤖 AI analyzing content..."):
          analysis = analyze_with_ai(title, selftext, comments, api_key, creator_name, image_url if is_image else None)
        
        if analysis and not analysis.startswith("AI Analysis Error"):
          st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
          st.markdown("""
          <h3 style="font-size: 24px; font-weight: 800; text-transform: uppercase; margin-bottom: 1.5rem;">
            AI Analysis <span style="color: #DC143C;">Results</span>
          </h3>
          """, unsafe_allow_html=True)
          
          if is_image:
            st.info("Image analysis included")
          
          st.write(analysis)

          # Add hashtags
          hashtags = generate_hashtags(title, subreddit, creator_name)
          st.markdown(f"**Suggested Hashtags:** `{hashtags}`")
          
          # Export button - LEFT ALIGNED
          trending = calculate_trending_score(score, num_comments, post_data.get('created_utc', 0))
          export_data = f"""# {creator_name} Analysis for Reddit Post

**Post:** {title}
**Subreddit:** r/{subreddit}
**Score:** {score:,} upvotes
**Comments:** {num_comments:,}
**Trending Score:** {trending:,}
**Author:** u/{author}
**Reddit Link:** https://reddit.com{permalink}
**Hashtags:** {hashtags}

## AI Analysis:
{analysis}

## Post Content:
{selftext[:500] if selftext else 'No text content'}

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

          # Add to session state for batch export
          if 'analyzed_posts' not in st.session_state:
            st.session_state.analyzed_posts = []
          if export_data not in st.session_state.analyzed_posts:
            st.session_state.analyzed_posts.append(export_data)
          
          st.download_button(
            label="📄 Export Analysis",
            data=export_data,
            file_name=f"{creator_name.replace(' ', '_')}_{title[:30].replace(' ', '_')}_analysis.txt",
            mime="text/plain",
            key=f"export_{post_id}_{i}",
            help="Download this analysis as a text file"
          )

          st.markdown('</div>', unsafe_allow_html=True)
        elif analysis:
          st.error(analysis)
      else:
        st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
        st.markdown("""
        <h3 style="font-size: 24px; font-weight: 800; text-transform: uppercase; margin-bottom: 1.5rem;">
          AI Analysis <span style="color: #DC143C;">Results</span>
        </h3>
        """, unsafe_allow_html=True)
        st.markdown(f"### 🤖 AI Analysis for {creator_name}")
        st.info("⚠️ AI analysis unavailable - configure API keys in environment variables")
        st.markdown('</div>', unsafe_allow_html=True)
      
      st.write(f"[View on Reddit](https://reddit.com{permalink})")

# ============ YOUTUBE API FUNCTIONS ============

def get_youtube_trending(api_key=None, region='US', max_results=15):
  """Get trending videos from YouTube"""
  if not api_key:
    # Return sample trending topics without API
    sample_trending = [
      {
        "title": "BREAKING: Major Political Development Shakes Washington", 
        "channel": "Political News Network", 
        "views": "2.3M views", 
        "published": "2 hours ago", 
        "description": "Latest updates on the developing political situation that could change everything...",
        "video_id": "sample1",
        "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
      },
      {
        "title": "SHOCKING Truth About Latest Government Scandal EXPOSED", 
        "channel": "Truth Commentary", 
        "views": "1.8M views", 
        "published": "4 hours ago", 
        "description": "Deep dive investigation reveals concerning details about recent government actions...",
        "video_id": "sample2",
        "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
      },
      {
        "title": "This Changes EVERYTHING - Full Analysis & Breakdown", 
        "channel": "Conservative Analysis", 
        "views": "956K views", 
        "published": "1 day ago", 
        "description": "Complete breakdown of recent events and their long-term implications...",
        "video_id": "sample3",
        "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
      }
    ]
    st.info("Showing sample trending videos (Configure YouTube API key for live data)")
    return sample_trending
  
  try:
    # YouTube API v3 trending videos endpoint
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
      'part': 'snippet,statistics',
      'chart': 'mostPopular',
      'regionCode': region,
      'maxResults': max_results,
      'key': api_key,
      'videoCategoryId': '25' # News & Politics category
    }
    
    response = requests.get(url, params=params, timeout=15)
    
    if response.status_code == 200:
      data = response.json()
      trending_videos = []
      
      for item in data.get('items', []):
        snippet = item.get('snippet', {})
        stats = item.get('statistics', {})
        
        video_data = {
          'title': snippet.get('title', 'No title'),
          'channel': snippet.get('channelTitle', 'Unknown Channel'),
          'views': f"{int(stats.get('viewCount', 0)):,} views" if stats.get('viewCount') else 'No views',
          'published': snippet.get('publishedAt', 'Unknown'),
          'video_id': item.get('id', ''),
          'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
          'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
        }
        trending_videos.append(video_data)
      
      st.success("✅ Retrieved live YouTube trending data")
      return trending_videos
    elif response.status_code == 403:
      st.warning("⚠️ YouTube API key invalid or quota exceeded. Showing sample data.")
      return get_youtube_trending()
    elif response.status_code == 400:
      st.warning("⚠️ YouTube API request error. Check your API key permissions.")
      return get_youtube_trending()
    else:
      st.warning(f"⚠️ YouTube API error {response.status_code}. Using sample data.")
      return get_youtube_trending()
      
  except Exception as e:
    st.warning(f"⚠️ YouTube API temporarily unavailable: {str(e)[:50]}... Using sample data.")
    return get_youtube_trending()
  
def get_relevant_channels_for_creator(creator_name, api_key):
    """Use AI to find 5 most relevant YouTube channels for a creator"""
    if not api_key:
        return None
    
    prompt = f"""Analyze the creator "{creator_name}" and suggest 5 YouTube channels that are most relevant/similar to their content.

Focus on:
1. Channels that create similar content types
2. Channels in the same niche or related niches
3. Channels with good audience overlap
4. Popular channels that the creator's audience would also watch
5. Use actual existing YouTube channel names

For example, if analyzing "Bailey Sarian":
- Similar true crime: Kendall Rae, Eleanor Neale, Stephanie Harlowe
- Beauty crossover: James Charles, Jeffree Star
- Storytelling: MrBallen, That Chapter

Return ONLY a Python list of YouTube channel names, exactly like this format:
["Kendall Rae", "Eleanor Neale", "Stephanie Harlowe", "MrBallen", "That Chapter"]

Make sure these are real, active YouTube channels. Do not include the original creator in the list.

Creator: {creator_name}"""

    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            timeout=30
        )
        
        # Parse the AI response to extract the list
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract the list from the response
        import ast
        try:
            # Look for a list in the response
            start = response_text.find('[')
            end = response_text.find(']') + 1
            if start != -1 and end != 0:
                list_text = response_text[start:end]
                channels = ast.literal_eval(list_text)
                if isinstance(channels, list) and len(channels) <= 5:
                    return channels[:5]  # Ensure max 5
        except:
            pass
            
        # Fallback: extract channel names manually using regex
        import re
        channels = re.findall(r'"([^"]+)"', response_text)
        if channels:
            return channels[:5]
        
        # Final fallback: try to extract words that look like channel names
        words = response_text.replace('[', '').replace(']', '').replace('"', '').split(',')
        clean_channels = []
        for word in words:
            clean_word = word.strip()
            if clean_word and len(clean_word) > 2 and len(clean_word) < 30:
                clean_channels.append(clean_word)
        
        return clean_channels[:5] if clean_channels else None
            
    except Exception as e:
        st.error(f"Error getting relevant channels: {str(e)}")
        return None


def search_youtube_videos(query, api_key=None, max_results=10, timeframe="week", search_type="video"):
  """Search YouTube for videos by topic/keywords with timeframe, or search by channel"""
  if not api_key:
    # Return sample search results with timeframe context
    timeframe_text = {
      "2days": "last 2 days",
      "week": "last week", 
      "month": "last month"
    }.get(timeframe, "recent")
    
    if search_type == "channel":
      sample_results = [
        {
          "title": f"Latest Upload from {query}", 
          "channel": query, 
          "views": "523K views", 
          "published": "1 day ago", 
          "description": f"Recent content from {query} channel...",
          "video_id": "sample1",
          "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
        },
        {
          "title": f"Popular Video from {query}", 
          "channel": query, 
          "views": "1.2M views", 
          "published": "3 days ago", 
          "description": f"Top performing content from {query}...",
          "video_id": "sample2",
          "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
        }
      ]
      st.info(f"Showing sample videos from '{query}' channel (Configure YouTube API key for live search)")
    else:
      sample_results = [
        {
          "title": f"BREAKING: Latest Analysis on {query}", 
          "channel": "Political Commentary Pro", 
          "views": "523K views", 
          "published": "1 day ago", 
          "description": f"In-depth analysis of {query} and its implications from {timeframe_text}...",
          "video_id": "sample1",
          "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
        },
        {
          "title": f"URGENT UPDATE: {query} - What You Need to Know", 
          "channel": "News Analysis Channel", 
          "views": "1.2M views", 
          "published": "3 hours ago", 
          "description": f"Breaking developments regarding {query} from {timeframe_text}...",
          "video_id": "sample2",
          "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
        }
      ]
      st.info(f"Showing sample search results for '{query}' from {timeframe_text} (Configure YouTube API key for live search)")
    
    return sample_results
  
  try:
    if search_type == "channel":
      # First, search for the channel
      search_url = "https://www.googleapis.com/youtube/v3/search"
      channel_params = {
        'part': 'snippet',
        'q': query,
        'type': 'channel',
        'maxResults': 1,
        'key': api_key
      }
      
      channel_response = requests.get(search_url, params=channel_params, timeout=15)
      
      if channel_response.status_code == 200:
        channel_data = channel_response.json()
        if channel_data.get('items'):
          channel_id = channel_data['items'][0]['id']['channelId']
          
          # Now get videos from this channel
          video_params = {
            'part': 'snippet',
            'channelId': channel_id,
            'type': 'video',
            'order': 'date',
            'maxResults': max_results,
            'key': api_key
          }
          
          # Add timeframe filter
          if timeframe == "2days":
            published_after = (datetime.now() - timedelta(days=2)).isoformat() + 'Z'
          elif timeframe == "week":
            published_after = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
          elif timeframe == "month":
            published_after = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
          else:
            published_after = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
          
          video_params['publishedAfter'] = published_after
          
          video_response = requests.get(search_url, params=video_params, timeout=15)
          
          if video_response.status_code == 200:
            video_data = video_response.json()
            search_results = []
            
            for item in video_data.get('items', []):
              snippet = item.get('snippet', {})
              
              video_data_item = {
                'title': snippet.get('title', 'No title'),
                'channel': snippet.get('channelTitle', 'Unknown Channel'),
                'published': format_youtube_date(snippet.get('publishedAt', 'Unknown')),
                'video_id': item.get('id', {}).get('videoId', ''),
                'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                'views': get_video_views(item.get('id', {}).get('videoId', ''), api_key)
              }
              search_results.append(video_data_item)
            
            st.success(f"✅ Found live videos from '{query}' channel from {timeframe}")
            return search_results
    else:
      # Calculate publishedAfter based on timeframe
      if timeframe == "2days":
        published_after = (datetime.now() - timedelta(days=2)).isoformat() + 'Z'
      elif timeframe == "week":
        published_after = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
      elif timeframe == "month":
        published_after = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
      else:
        published_after = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
      
      # YouTube API v3 search endpoint
      url = "https://www.googleapis.com/youtube/v3/search"
      params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'order': 'relevance',
        'maxResults': max_results,
        'key': api_key,
        'publishedAfter': published_after
      }
      
      response = requests.get(url, params=params, timeout=15)
      
      if response.status_code == 200:
        data = response.json()
        search_results = []
        
        for item in data.get('items', []):
          snippet = item.get('snippet', {})
          
          video_data = {
            'title': snippet.get('title', 'No title'),
            'channel': snippet.get('channelTitle', 'Unknown Channel'),
            'published': format_youtube_date(snippet.get('publishedAt', 'Unknown')),
            'video_id': item.get('id', {}).get('videoId', ''),
            'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
            'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
            'views': get_video_views(item.get('id', {}).get('videoId', ''), api_key)
          }
          search_results.append(video_data)
        
        st.success(f"✅ Found live YouTube results for '{query}' from {timeframe}")
        return search_results
      
      elif response.status_code == 403:
        # Rate limit or quota exceeded
        try:
          error_data = response.json()
          error_reason = error_data.get('error', {}).get('errors', [{}])[0].get('reason', '')
          
          if 'quotaExceeded' in error_reason or 'rateLimitExceeded' in error_reason:
            st.error("🚫 YouTube API rate limit reached. The daily quota has been exceeded. Please wait until midnight Pacific Time for the quota to reset.")
          else:
            st.error("YouTube API access error. Please check your API key permissions.")
        except:
          st.error("🚫 YouTube API quota exceeded. Please wait until midnight Pacific Time for the quota to reset.")
        
        return []  # Return empty list, no sample data
      
      else:
        st.warning(f"YouTube API error (Status: {response.status_code}). Unable to fetch videos.")
        return []  # Return empty list, no sample data
    
    # Remove the fallback section that shows sample data
    # Just return empty list if we get here
    return []
      
  except Exception as e:
    st.error(f"YouTube search error: {str(e)}")
    return []  # Return empty list, no sample data
    
def get_video_views(video_id, api_key):
    """Get view count for a specific video"""
    if not api_key or not video_id or video_id.startswith('sample'):
        return "N/A"
    
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items') and len(data['items']) > 0:
                stats = data['items'][0].get('statistics', {})
                view_count = stats.get('viewCount')
                if view_count:
                    views = int(view_count)
                    if views >= 1000000:
                        return f"{views/1000000:.1f}M views"
                    elif views >= 1000:
                        return f"{views/1000:.0f}K views"
                    else:
                        return f"{views:,} views"
        return "N/A"
    except:
        return "N/A"

def format_youtube_date(date_string):
    """Convert YouTube API date to MM/DD/YY format"""
    if not date_string or date_string in ['Unknown', 'N/A']:
        return date_string
    
    try:
        from datetime import datetime
        if 'T' in date_string:
            clean_date = date_string.replace('Z', '').split('T')[0]
            dt = datetime.strptime(clean_date, '%Y-%m-%d')
        else:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%m/%d/%y')
    except:
        return date_string

def get_youtube_comments(video_id, api_key=None, max_results=20):
  """Get comments from a YouTube video"""
  if not api_key:
    # Return sample comments
    sample_comments = [
      {"author": "TruthSeeker2024", "text": "This is exactly what I've been saying! Finally someone gets it.", "likes": 127},
      {"author": "SkepticalViewer", "text": "I disagree with this take. Here's why this analysis is flawed...", "likes": 89},
      {"author": "CasualObserver", "text": "Great breakdown! Really helps me understand the situation better.", "likes": 45},
      {"author": "ControversialTakes", "text": "This is going to trigger so many people but it's the truth", "likes": 203},
      {"author": "ThoughtfulCritic", "text": "While I appreciate the perspective, I think there are some nuances missing here", "likes": 67}
    ]
    st.info("Showing sample comments (Configure YouTube API key for live comment data)")
    return sample_comments
  
  try:
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
      'part': 'snippet',
      'videoId': video_id,
      'maxResults': max_results,
      'order': 'relevance',
      'key': api_key
    }
    
    response = requests.get(url, params=params, timeout=15)
    
    if response.status_code == 200:
      data = response.json()
      comments = []
      
      for item in data.get('items', []):
        snippet = item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {})
        
        comment_data = {
          'author': snippet.get('authorDisplayName', 'Unknown'),
          'text': snippet.get('textDisplay', 'No text'),
          'likes': int(snippet.get('likeCount', 0))
        }
        comments.append(comment_data)
      
      st.success(f"✅ Retrieved {len(comments)} live comments")
      return comments
    elif response.status_code == 403:
      st.warning("⚠️ Comments disabled or API quota exceeded. Showing sample comments.")
      return [
        {"author": "TruthSeeker2024", "text": "This is exactly what I've been saying! Finally someone gets it.", "likes": 127},
        {"author": "SkepticalViewer", "text": "I disagree with this take. Here's why this analysis is flawed...", "likes": 89},
        {"author": "CasualObserver", "text": "Great breakdown! Really helps me understand the situation better.", "likes": 45},
        {"author": "ControversialTakes", "text": "This is going to trigger so many people but it's the truth", "likes": 203},
        {"author": "ThoughtfulCritic", "text": "While I appreciate the perspective, I think there are some nuances missing here", "likes": 67}
      ]
    else:
      st.warning(f"⚠️ Comments API error {response.status_code}. Using sample comments.")
      return [
        {"author": "TruthSeeker2024", "text": "This is exactly what I've been saying! Finally someone gets it.", "likes": 127},
        {"author": "SkepticalViewer", "text": "I disagree with this take. Here's why this analysis is flawed...", "likes": 89},
        {"author": "CasualObserver", "text": "Great breakdown! Really helps me understand the situation better.", "likes": 45},
        {"author": "ControversialTakes", "text": "This is going to trigger so many people but it's the truth", "likes": 203},
        {"author": "ThoughtfulCritic", "text": "While I appreciate the perspective, I think there are some nuances missing here", "likes": 67}
      ]
      
  except Exception as e:
    st.warning(f"⚠️ Comments temporarily unavailable: {str(e)[:50]}... Using sample data.")
    return [
      {"author": "TruthSeeker2024", "text": "This is exactly what I've been saying! Finally someone gets it.", "likes": 127},
      {"author": "SkepticalViewer", "text": "I disagree with this take. Here's why this analysis is flawed...", "likes": 89},
      {"author": "CasualObserver", "text": "Great breakdown! Really helps me understand the situation better.", "likes": 45},
      {"author": "ControversialTakes", "text": "This is going to trigger so many people but it's the truth", "likes": 203},
      {"author": "ThoughtfulCritic", "text": "While I appreciate the perspective, I think there are some nuances missing here", "likes": 67}
    ]
def get_video_by_id(video_id, api_key=None):
  """Get a specific YouTube video by ID"""
  if not api_key:
    return None
  
  try:
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
      'part': 'snippet,statistics',
      'id': video_id,
      'key': api_key
    }
    
    response = requests.get(url, params=params, timeout=15)
    
    if response.status_code == 200:
      data = response.json()
      if data.get('items'):
        item = data['items'][0]
        snippet = item.get('snippet', {})
        stats = item.get('statistics', {})
        
        return {
          'title': snippet.get('title', 'No title'),
          'channel': snippet.get('channelTitle', 'Unknown Channel'),
          'published': format_youtube_date(snippet.get('publishedAt', 'Unknown')),
          'views': get_video_views(item.get('id', ''), youtube_api_key),
          'video_id': video_id,
          'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
          'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
        }
  except:
    return None

def analyze_video_for_creator_auto(video, comments, creator_name, api_key):
    """Auto-analyze video + comments for creator - Reddit style"""
    if not api_key:
        return None
    
    # Prepare comment text
    comment_text = ""
    if comments:
        top_comments = []
        for comment in comments[:5]:  # Top 5 comments
            top_comments.append(f"• {comment['author']}: {comment['text'][:100]}...")
        comment_text = "\n".join(top_comments)
    
    prompt = f"""Analyze this YouTube video for {creator_name}:

Video: "{video['title']}" by {video['channel']} ({video.get('views', 'N/A')})

Top Comments:
{comment_text}

Brief analysis for {creator_name}:

REACTION ANGLE: How {creator_name} should approach this
KEY POINTS: 2-3 main points to address
AUDIENCE SENTIMENT: What viewers are saying
CONTENT IDEA: Specific video concept for {creator_name}

Keep concise and actionable."""

    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"

def analyze_video_comments_with_ai(comments, video_title, creator_name, api_key):
  """Analyze YouTube video comments for creator insights"""
  if not api_key:
    return None
  
  import openai
  openai.api_key = api_key
  
  # Prepare top comments for analysis
  comment_texts = []
  for i, comment in enumerate(comments[:10], 1):
    comment_texts.append(f"{i}. {comment['author']} ({comment['likes']} likes): {comment['text'][:150]}...")
  
  comments_text = "\n".join(comment_texts)
  
  prompt = f"""Analyze these YouTube video comments for {creator_name}'s content strategy:

Video: "{video_title}"
Top Comments:
{comments_text}

Provide analysis for {creator_name}:

AUDIENCE SENTIMENT: Overall mood and feelings in the comments (angry, supportive, confused, etc.)
CONTROVERSIAL POINTS: What aspects are people most divided on?
{creator_name.upper()} OPPORTUNITY: How {creator_name} could address these comments or create follow-up content
COMMENT THEMES: Top 3 recurring themes or talking points in the comments
AUDIENCE QUESTIONS: What questions are viewers asking that {creator_name} could answer?
ENGAGEMENT STRATEGY: How {creator_name} could respond to maximize engagement
CONTENT IDEAS: 2-3 video ideas based on what the audience is discussing

Focus on what the audience is actually saying and how {creator_name} could use these insights."""
  
  try:
    response = openai.ChatCompletion.create(
      model="gpt-4.1-nano",
      messages=[{"role": "user", "content": prompt}],
      max_tokens=800,
      timeout=30
    )
    return response.choices[0].message.content
  except Exception as e:
    return f"Comment Analysis Error: {str(e)}"

def analyze_youtube_trends_with_ai(trending_videos, creator_name, api_key):
  """Analyze YouTube trending videos for content opportunities"""
  if not api_key:
    return None
  
  import openai
  openai.api_key = api_key
  
  # Prepare trending video data for analysis
  video_titles = []
  for i, video in enumerate(trending_videos[:8], 1):
    video_titles.append(f"{i}. \"{video['title']}\" by {video['channel']} ({video['views']})")
  
  videos_text = "\n".join(video_titles)
  
  prompt = f"""Analyze these trending YouTube videos for {creator_name}'s content opportunities:

{videos_text}

For the top 3 most relevant trends, provide:

TRENDING VIDEO TOPIC: [Main topic/theme]
{creator_name.upper()} ANGLE: How {creator_name} could respond, react, or create similar content
CONTENT IDEA: Specific video title for {creator_name}'s channel
FORMAT: Best format (Reaction, Analysis, Response, Original Take)
URGENCY: How time-sensitive this trend is (1-10)
HOOK: Opening line or angle to grab attention
SERIES POTENTIAL: Could this become multiple videos?"""
  
  try:
    response = openai.ChatCompletion.create(
      model="gpt-4.1-nano",
      messages=[{"role": "user", "content": prompt}],
      max_tokens=800,
      timeout=30
    )
    return response.choices[0].message.content
  except Exception as e:
    return f"AI Analysis Error: {str(e)}"
  
def get_youtube_podcast_channels(api_key=None, category="general", max_results=20):
    """Get popular podcast channels from YouTube"""
    if not api_key:
        return None
    
    # Define search queries for different podcast categories
    podcast_queries = {
        "general": "podcast channel",
        "true crime": "true crime podcast",
        "comedy": "comedy podcast",
        "business": "business podcast",
        "news": "news podcast daily",
        "technology": "tech podcast",
        "health": "health wellness podcast",
        "sports": "sports podcast",
        "education": "educational podcast",
        "music": "music podcast",
        "politics": "political podcast"
    }
    
    query = podcast_queries.get(category, "podcast channel")
    
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'channel',
            'order': 'relevance',
            'maxResults': max_results,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            channels = []
            
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                
                # Filter to ensure it's actually a podcast
                title = snippet.get('title', '').lower()
                description = snippet.get('description', '').lower()
                
                if 'podcast' in title or 'podcast' in description or 'show' in title:
                    channel_data = {
                        'channel_id': item.get('id', {}).get('channelId', ''),
                        'title': snippet.get('title', 'Unknown'),
                        'description': snippet.get('description', '')[:200] + '...',
                        'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                    }
                    channels.append(channel_data)
            
            return channels
    except:
        return None
    
# ============ COURTLISTENER API FUNCTIONS ============

    
def search_courtlistener_cases(query, api_token, limit=10):
    """Search CourtListener - optimized for their API structure"""
    if not api_token:
        return None
        
    headers = {'Authorization': f'Token {api_token}'}
    
    results = {
        'dockets': [],
        'opinions': [],
        'total_found': 0
    }
    
    all_opinions = []
    seen_ids = set()
    
    try:
        # Search the opinions endpoint with basic query
        # The API searches the full text, not just case names
        opinions_url = "https://www.courtlistener.com/api/rest/v4/search/"
        
        # Try different search strategies
        search_queries = [
            query,  # Plain search
            f'"{query}"',  # Exact phrase
        ]
        
        for search_term in search_queries:
            params = {
                'q': search_term,
                'type': 'o',  # opinions type
                'order_by': 'score desc',
                'page_size': 50  # Get more results since we need to filter
            }
            
            response = requests.get(opinions_url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # The API returns results differently than expected
                # Let's check the actual structure
                if 'results' in data:
                    for item in data.get('results', []):
                        # Get all text fields to search
                        case_name = item.get('caseName', '') or ''
                        case_name_full = item.get('caseNameFull', '') or ''
                        snippet = item.get('snippet', '') or ''
                        text = item.get('text', '') or ''
                        
                        # Combine all searchable text
                        all_text = f"{case_name} {case_name_full} {snippet} {text}".lower()
                        
                        # Check if our search query appears anywhere
                        if query.lower() in all_text:
                            item_id = item.get('id') or item.get('resource_uri', '').split('/')[-2]
                            
                            if item_id and item_id not in seen_ids:
                                seen_ids.add(item_id)
                                
                                # Extract docket number if available
                                docket_num = ''
                                if 'docket' in item:
                                    if isinstance(item['docket'], dict):
                                        docket_num = item['docket'].get('docket_number', '')
                                    elif isinstance(item['docket'], str):
                                        # It might be a URL, extract the docket number
                                        docket_num = item['docket'].split('/')[-2] if '/' in item['docket'] else ''
                                
                                all_opinions.append({
                                    'case_name': case_name or case_name_full or 'Unknown Case',
                                    'court': item.get('court', '') or item.get('court_citation_string', ''),
                                    'date_filed': item.get('dateFiled', '') or item.get('date_filed', ''),
                                    'docket_number': docket_num,
                                    'citation': item.get('citation', []),
                                    'summary': snippet[:500] if snippet else text[:500] if text else '',
                                    'url': f"https://www.courtlistener.com{item.get('absolute_url', '')}" if item.get('absolute_url') else '',
                                    'judge': item.get('judge', '') or item.get('panel', ''),
                                    'status': item.get('status', 'Published')
                                })
            
            # If we found results, stop searching
            if all_opinions:
                break
                
    except Exception as e:
        print(f"Search error: {str(e)}")
    
    # Also try the dockets endpoint with a simpler search
    try:
        dockets_url = "https://www.courtlistener.com/api/rest/v4/dockets/"
        params = {
            'q': query,
            'page_size': 20
        }
        
        response = requests.get(dockets_url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            dockets = []
            for docket in data.get('results', []):
                case_name = docket.get('case_name', '')
                
                # Only include if the query appears in the case name
                if query.lower() in case_name.lower():
                    dockets.append({
                        'id': docket.get('id'),
                        'case_name': case_name,
                        'court': docket.get('court_id', ''),
                        'docket_number': docket.get('docket_number', ''),
                        'date_filed': docket.get('date_filed', ''),
                        'date_terminated': docket.get('date_terminated', ''),
                        'nature_of_suit': docket.get('nature_of_suit', ''),
                        'cause': docket.get('cause', ''),
                        'assigned_to': docket.get('assigned_to_str', ''),
                        'url': f"https://www.courtlistener.com{docket.get('absolute_url', '')}" if docket.get('absolute_url') else '',
                        'pacer_case_id': docket.get('pacer_case_id', '')
                    })
            
            results['dockets'] = dockets
            
    except Exception as e:
        print(f"Docket search error: {str(e)}")
    
    results['opinions'] = all_opinions
    results['total_found'] = len(all_opinions) + len(results['dockets'])
    
    # If no results, provide helpful message with direct link
    if not all_opinions and not results['dockets']:
        results['no_results_message'] = f"""
No cases found for "{query}" via API.

**This is likely because:**
- The case title doesn't contain the exact name (e.g., "Associated Press v. Second Judicial District")
- The case is in state court (not federal)
- The API search works differently than the website

**Search directly on CourtListener:**
[Click here to search on their website](https://www.courtlistener.com/?q={query.replace(' ', '+')}&type=o)

The website search is more comprehensive than the API.
"""
    
    return results
def is_name_match(search_query, case_text):
    """
    Smart matching that handles middle names and initials
    Returns True if the search query matches the case text
    """
    search_query = search_query.lower().strip()
    case_text = case_text.lower()
    
    # Split search query into parts
    search_parts = search_query.split()
    
    if len(search_parts) == 2:
        first_name, last_name = search_parts
        
        # Pattern 1: Exact match (Bryan Kohberger in Bryan Kohberger)
        if search_query in case_text:
            return True
        
        # Pattern 2: With middle initial (Bryan Kohberger matches Bryan C. Kohberger)
        import re
        # Look for: first_name [middle_initial]. last_name
        pattern_with_initial = f"{first_name}\\s+\\w\\.?\\s+{last_name}"
        if re.search(pattern_with_initial, case_text):
            return True
        
        # Pattern 3: With middle name (Bryan Kohberger matches Bryan Christopher Kohberger)
        # Look for: first_name [middle_name] last_name
        pattern_with_middle = f"{first_name}\\s+\\w+\\s+{last_name}"
        if re.search(pattern_with_middle, case_text):
            return True
        
        # Pattern 4: Both first and last name present, but not necessarily adjacent
        # (for cases like "Kohberger, Bryan C.")
        if first_name in case_text and last_name in case_text:
            # Make sure they're close enough (within 50 characters)
            first_pos = case_text.find(first_name)
            last_pos = case_text.find(last_name)
            if abs(first_pos - last_pos) < 50:
                return True
    
    elif len(search_parts) == 3:
        # User provided middle name/initial - require exact match
        if search_query in case_text:
            return True
        
        # Also try without middle (in case court record doesn't have it)
        first_name = search_parts[0]
        last_name = search_parts[-1]
        simple_name = f"{first_name} {last_name}"
        if simple_name in case_text:
            return True
    
    else:
        # Single name or more than 3 parts - require exact match
        if search_query in case_text:
            return True
    
    return False

def get_docket_entries(docket_id, api_token, limit=20):
    """
    Get docket entries (individual filings) for a specific case
    """
    headers = {
        'Authorization': f'Token {api_token}'
    }
    
    try:
        url = f"https://www.courtlistener.com/api/rest/v4/docket-entries/"
        params = {
            'docket': docket_id,
            'order_by': '-date_filed',
            'page_size': limit,
            'fields': 'id,date_filed,entry_number,description,recap_documents'  # Exclude plain_text for speed
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            entries = []
            
            for entry in data.get('results', []):
                entries.append({
                    'entry_number': entry.get('entry_number', ''),
                    'date_filed': entry.get('date_filed', ''),
                    'description': entry.get('description', ''),
                    'document_count': len(entry.get('recap_documents', []))
                })
            
            return entries
    except Exception as e:
        print(f"Error getting docket entries: {e}")
        return []

def get_case_parties(docket_id, api_token):
    """
    Get parties involved in a case (defendants, plaintiffs, etc.)
    """
    headers = {
        'Authorization': f'Token {api_token}'
    }
    
    try:
        url = f"https://www.courtlistener.com/api/rest/v4/parties/"
        params = {
            'docket': docket_id,
            'filter_nested_results': 'true'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            parties = []
            
            for party in data.get('results', []):
                party_info = {
                    'name': party.get('name', 'Unknown'),
                    'type': '',
                    'extra_info': party.get('extra_info', '')
                }
                
                # Get party type from nested data
                party_types = party.get('party_types', [])
                if party_types:
                    party_info['type'] = party_types[0].get('name', '')
                    
                    # For criminal cases, get criminal counts
                    if party_types[0].get('criminal_counts'):
                        party_info['criminal_counts'] = party_types[0].get('criminal_counts', [])
                    if party_types[0].get('highest_offense_level_opening'):
                        party_info['offense_level'] = party_types[0].get('highest_offense_level_opening', '')
                
                parties.append(party_info)
            
            return parties
    except Exception as e:
        print(f"Error getting parties: {e}")
        return []

  
# ============ SPOTIFY API FUNCTIONS ============

def get_spotify_token(client_id, client_secret):
    """Get Spotify access token using Client Credentials Flow"""
    if not client_id or not client_secret:
        return None
    
    try:
        import base64
        
        # Encode credentials
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Get token
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials"
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            st.error(f"❌ Spotify Auth Error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ Spotify Token Error: {str(e)}")
        return None

def search_podcasts_by_genre(token, genre="all", limit=10):
    """Get popular podcasts by genre"""
    if not token:
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Build search query based on genre
        if genre == "all":
            # For 'all', search for popular podcast shows
            search_query = "podcast"  # Simple generic search
            params = {
                "q": search_query,
                "type": "show",
                "limit": 50,  # Get more results to filter from
                "market": "US"
            }

        else:
            # For specific genres, use the genre in the search
            # Remove the "genre:" prefix as it's not supported for shows
            search_query = genre
            params = {
                "q": search_query,
                "type": "show", 
                "limit": 50,  # Get more results to filter from
                "market": "US"
            }
        
        url = "https://api.spotify.com/v1/search"
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            shows = []
            
            items = data.get('shows', {}).get('items', [])
            
            # If we have items, process them
            for show in items[:limit]:  # Limit to requested number
                # Skip if no images
                if not show.get('images'):
                    continue
                    
                show_data = {
                    'id': show['id'],
                    'name': show['name'],
                    'publisher': show['publisher'],
                    'description': show['description'][:200] + '...' if len(show['description']) > 200 else show['description'],
                    'total_episodes': show.get('total_episodes', 0),
                    'image': show['images'][0]['url'] if show['images'] else None,
                    'explicit': show.get('explicit', False),
                    'url': show['external_urls']['spotify']
                }
                shows.append(show_data)
            
            # If no results found with genre search, try a different approach
            if not shows and genre != "all":
                # Try searching for "<genre> podcast"
                search_query = f"{genre} podcast"
                params['q'] = search_query
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('shows', {}).get('items', [])
                    
                    for show in items[:limit]:
                        if not show.get('images'):
                            continue
                            
                        show_data = {
                            'id': show['id'],
                            'name': show['name'],
                            'publisher': show['publisher'],
                            'description': show['description'][:200] + '...' if len(show['description']) > 200 else show['description'],
                            'total_episodes': show.get('total_episodes', 0),
                            'image': show['images'][0]['url'] if show['images'] else None,
                            'explicit': show.get('explicit', False),
                            'url': show['external_urls']['spotify']
                        }
                        shows.append(show_data)
            
            return shows
        else:
            st.error(f"❌ Spotify Search Error: {response.status_code}")
            # Try to get error details
            if response.text:
                st.error(f"Error details: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error searching podcasts: {str(e)}")
        return None

def get_show_episodes(token, show_id, limit=10):
    """Get recent episodes from a podcast show"""
    if not token:
        return []  # <- Return empty list instead of None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.spotify.com/v1/shows/{show_id}/episodes"
        params = {
            "limit": limit,
            "market": "US"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            episodes = []
            
            for ep in data.get('items', []):
                episode_data = {
                    'id': ep['id'],
                    'name': ep['name'],
                    'description': ep['description'][:200] + '...' if len(ep['description']) > 200 else ep['description'],
                    'release_date': ep['release_date'],
                    'duration_ms': ep['duration_ms'],
                    'duration_min': ep['duration_ms'] // 60000,
                    'url': ep['external_urls']['spotify']
                }
                episodes.append(episode_data)
            
            return episodes
        else:
            return []  # <- Return empty list
            
    except Exception as e:
        return []  # <- Return empty list

def search_podcasts_by_topic(token, topic, limit=20):
    """Search for podcast episodes about a specific topic"""
    if not token:
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://api.spotify.com/v1/search"
        params = {
            "q": topic,
            "type": "episode",
            "limit": limit,
            "market": "US"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            episodes = []
            
            items = data.get('episodes', {}).get('items', [])
            
            # First, collect all episodes with their show IDs
            episode_list = []
            show_ids = set()
            
            for ep in items:
                # Extract show ID from the episode href
                # The href looks like: "https://api.spotify.com/v1/episodes/6FjEzvYK4hXVhV1X5hh2XP"
                # We need to get the show ID by fetching the full episode details
                episode_id = ep.get('id', '')
                
                episode_data = {
                    'id': episode_id,
                    'name': ep.get('name', 'Unknown Episode'),
                    'description': ep.get('description', '')[:200] + '...' if len(ep.get('description', '')) > 200 else ep.get('description', ''),
                    'release_date': ep.get('release_date', 'Unknown'),
                    'duration_min': ep.get('duration_ms', 0) // 60000,
                    'url': ep.get('external_urls', {}).get('spotify', ''),
                    'image': ep.get('images', [{}])[0].get('url', '') if ep.get('images') else None,
                    'show_id': None,
                    'show_name': 'Loading...'
                }
                episode_list.append(episode_data)
            
            # Now fetch full episode details to get show IDs
            for i, ep_data in enumerate(episode_list):
                if ep_data['id']:
                    ep_url = f"https://api.spotify.com/v1/episodes/{ep_data['id']}"
                    ep_response = requests.get(ep_url, headers=headers, params={"market": "US"})
                    
                    if ep_response.status_code == 200:
                        full_episode = ep_response.json()
                        if 'show' in full_episode:
                            show_id = full_episode['show'].get('id')
                            show_name = full_episode['show'].get('name', 'Unknown Show')
                            episode_list[i]['show_id'] = show_id
                            episode_list[i]['show_name'] = show_name
                        
                        # Small delay to respect rate limits
                        time.sleep(0.1)
            
            return episode_list
            
        else:
            st.error(f"❌ Spotify Episode Search Error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error searching episodes: {str(e)}")
        return None
            
def get_new_episodes_today(token, limit=20):
    """Get podcast episodes released today"""
    if not token:
        return None
    
    # Search for episodes with today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://api.spotify.com/v1/search"
        params = {
            "q": f"tag:new",  # This gets recently added content
            "type": "episode",
            "limit": limit,
            "market": "US"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            episodes = []
            
            for ep in data.get('episodes', {}).get('items', []):
                # Filter for today's episodes
                if ep['release_date'] == today:
                    episode_data = {
                        'id': ep['id'],
                        'name': ep['name'],
                        'show_name': ep['show']['name'],
                        'description': ep['description'][:200] + '...' if len(ep['description']) > 200 else ep['description'],
                        'release_date': ep['release_date'],
                        'duration_min': ep['duration_ms'] // 60000,
                        'url': ep['external_urls']['spotify'],
                        'image': ep['images'][0]['url'] if ep['images'] else None
                    }
                    episodes.append(episode_data)
            
            return episodes
        else:
            return None
            
    except Exception as e:
        return None
    
def get_itunes_top_podcasts(genre_id=None, limit=20):
    """Get top podcasts from iTunes/Apple Podcasts"""
    try:
        # iTunes genre IDs for podcasts
        genre_map = {
            "all": None,
            "business": 1321,
            "comedy": 1303,
            "education": 1304,
            "fiction": 1483,
            "government": 1511,
            "health": 1512,
            "history": 1487,
            "kids": 1305,
            "leisure": 1502,
            "music": 1310,
            "news": 1489,
            "religion": 1314,
            "science": 1533,
            "society": 1324,
            "sports": 1545,
            "technology": 1318,
            "true_crime": 1488,
            "tv_film": 1309
        }
        
        # Use the lookup URL for top podcasts
        if genre_id:
            url = f"https://itunes.apple.com/us/rss/toppodcasts/limit={limit}/genre={genre_id}/json"
        else:
            url = f"https://itunes.apple.com/us/rss/toppodcasts/limit={limit}/json"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            podcasts = []
            
            entries = data.get('feed', {}).get('entry', [])
            
            for i, entry in enumerate(entries, 1):
                # Extract podcast data
                podcast_data = {
                    'rank': i,
                    'name': entry.get('im:name', {}).get('label', 'Unknown'),
                    'artist': entry.get('im:artist', {}).get('label', 'Unknown'),
                    'summary': entry.get('summary', {}).get('label', 'No description')[:300] + '...',
                    'image': entry.get('im:image', [{}])[-1].get('label', ''),  # Get largest image
                    'url': entry.get('link', {}).get('attributes', {}).get('href', ''),
                    'category': entry.get('category', {}).get('attributes', {}).get('label', 'Unknown'),
                    'release_date': entry.get('im:releaseDate', {}).get('label', 'Unknown')
                }
                podcasts.append(podcast_data)
            
            return podcasts
        else:
            return None
            
    except Exception as e:
        st.error(f"❌ Error fetching iTunes podcasts: {str(e)}")
        return None

def get_itunes_podcast_episodes(podcast_id, limit=5):
    """Get recent episodes for a specific podcast from iTunes"""
    try:
        # iTunes lookup API to get podcast details and feed URL
        lookup_url = f"https://itunes.apple.com/lookup?id={podcast_id}"
        response = requests.get(lookup_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                podcast_info = data['results'][0]
                feed_url = podcast_info.get('feedUrl')
                
                if feed_url:
                    # Parse the podcast RSS feed
                    feed = feedparser.parse(feed_url)
                    episodes = []
                    
                    for entry in feed.entries[:limit]:
                        episode_data = {
                            'title': entry.get('title', 'Unknown'),
                            'published': entry.get('published', 'Unknown'),
                            'duration': entry.get('itunes_duration', 'Unknown'),
                            'description': entry.get('summary', '')[:300] + '...',
                            'link': entry.get('link', '')
                        }
                        episodes.append(episode_data)
                    
                    return episodes
        return []
    except:
        return []
  
    
# ============ TMDB API FUNCTIONS ============

def get_tmdb_genres(api_key, media_type='movie'):
    """Get list of genres from TMDb"""
    try:
        url = f"https://api.themoviedb.org/3/genre/{media_type}/list"
        params = {'api_key': api_key}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {genre['id']: genre['name'] for genre in data['genres']}
        return {}
    except:
        return {}

def search_tmdb(api_key, query=None, media_type='movie', genre_id=None, year=None, 
                company_id=None, sort_by='popularity.desc', page=1):
    """Search TMDb for movies or TV shows"""
    try:
        if query:
            # Search by title
            url = f"https://api.themoviedb.org/3/search/{media_type}"
            params = {
                'api_key': api_key,
                'query': query,
                'page': page
            }
            if year:
                params['year'] = year
        else:
            # Discover movies/shows by filters
            url = f"https://api.themoviedb.org/3/discover/{media_type}"
            params = {
                'api_key': api_key,
                'sort_by': sort_by,
                'page': page,
                'vote_count.gte': 100  # Only show items with at least 100 votes
            }
            if genre_id:
                params['with_genres'] = genre_id
            if year:
                if media_type == 'movie':
                    params['primary_release_year'] = year
                else:
                    params['first_air_date_year'] = year
            if company_id:
                params['with_companies'] = company_id
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"TMDb API Error: {str(e)}")
        return None

def get_tmdb_item_details(api_key, item_id, media_type='movie'):
    """Get detailed information about a movie or TV show"""
    try:
        url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
        params = {
            'api_key': api_key,
            'append_to_response': 'credits,videos,keywords'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def search_tmdb_multiple_companies(api_key, company_ids, media_type='movie', sort_by='popularity.desc', year=None):
    """Search TMDb for movies/TV shows from multiple companies (OR logic)"""
    all_results = []
    seen_ids = set()  # To avoid duplicates
    
    try:
        # Make separate API calls for each company
        for company_id in company_ids:
            url = f"https://api.themoviedb.org/3/discover/{media_type}"
            params = {
                'api_key': api_key,
                'sort_by': sort_by,
                'page': 1,
                'vote_count.gte': 50,  # Lower threshold for individual companies
                'with_companies': company_id
            }
            
            if year:
                if media_type == 'movie':
                    params['primary_release_year'] = year
                else:
                    params['first_air_date_year'] = year
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('results', []):
                    item_id = item.get('id')
                    if item_id not in seen_ids:
                        seen_ids.add(item_id)
                        all_results.append(item)
        
        # Sort all results by the selected criteria
        if all_results:
            if sort_by == 'popularity.desc':
                all_results.sort(key=lambda x: x.get('popularity', 0), reverse=True)
            elif sort_by == 'vote_average.desc':
                all_results.sort(key=lambda x: x.get('vote_average', 0), reverse=True)
            elif sort_by == 'vote_count.desc':
                all_results.sort(key=lambda x: x.get('vote_count', 0), reverse=True)
            elif sort_by == 'release_date.desc' or sort_by == 'first_air_date.desc':
                date_field = 'release_date' if media_type == 'movie' else 'first_air_date'
                all_results.sort(key=lambda x: x.get(date_field, ''), reverse=True)
            elif sort_by == 'revenue.desc':
                all_results.sort(key=lambda x: x.get('revenue', 0), reverse=True)
        
        return {'results': all_results}
        
    except Exception as e:
        st.error(f"TMDb API Error: {str(e)}")
        return None
    
def search_tmdb_companies(api_key, query):
    """Search for production companies"""
    try:
        url = "https://api.themoviedb.org/3/search/company"
        params = {
            'api_key': api_key,
            'query': query
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()['results']
        return []
    except:
        return []

def analyze_movie_tv_trend(title, overview, popularity, vote_average, media_type, 
                          genre_names, creator_name, api_key):
    """Analyze how a creator should cover a trending movie/TV show"""
    if not api_key:
        return None
    
    import openai
    openai.api_key = api_key
    
    context = f"""Trending {media_type.upper()}:
Title: {title}
Overview: {overview}
Popularity Score: {popularity}
Average Rating: {vote_average}/10
Genres: {', '.join(genre_names)}

This {media_type} is currently trending with high viewership and engagement."""
    
    prompt = f"""Analyze this trending {media_type} for {creator_name}'s content strategy:

{context}

Provide a comprehensive content strategy for {creator_name}:

TREND ANALYSIS: Why this {media_type} is trending and what's driving the interest (2-3 sentences)

{creator_name.upper()} ANGLE: How {creator_name} should approach this topic based on their personality and audience

VIDEO CONCEPTS: 3 specific video ideas with titles that {creator_name} could create:
- Title 1: [Specific title]
- Title 2: [Specific title]  
- Title 3: [Specific title]

HOT TAKE: {creator_name}'s unique, provocative perspective on this {media_type}

DEEP DIVE ANGLES: What aspects {creator_name} could explore (themes, controversies, behind-the-scenes, etc.)

SOCIAL MEDIA STRATEGY: How to leverage this trend across platforms:
- YouTube video idea
- YouTube Shorts approach
- TikTok series concept
- Instagram Reels idea

TIMING: How urgent is this trend? When should {creator_name} publish content?

CONTENT FORMAT: Best format for {creator_name} (review, reaction, analysis, comparison, etc.)

HASHTAGS: Relevant hashtags for maximum reach

CONTROVERSY/DISCUSSION POINTS: What aspects would generate the most engagement and discussion?"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"
        
# First, add this function with your other YouTube functions (before the platform section):

def get_relevant_channels_for_creator(creator_name, api_key):
    """Use AI to find 5 most relevant YouTube channels for a creator"""
    if not api_key:
        return None
    
    prompt = f"""You are a YouTube content strategist. Find 5 YouTube channels that are most similar to "{creator_name}" in terms of:
    - Content style and format
    - Target audience
    - Topic/niche overlap
    - Production quality level
    
    Focus on channels that would have similar audiences and content approaches.
    
    Return ONLY a Python list of 5 channel names like this:
    ["Channel Name 1", "Channel Name 2", "Channel Name 3", "Channel Name 4", "Channel Name 5"]
    
    Make sure channel names are exact and searchable on YouTube. No extra text, just the list."""
    
    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
            timeout=30
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the list from the AI response
        import ast
        try:
            channels = ast.literal_eval(result)
            if isinstance(channels, list) and len(channels) <= 5:
                return [channel.strip() for channel in channels if channel.strip()]
        except:
            # Fallback parsing if AI doesn't return perfect list format
            import re
            channels = re.findall(r'"([^"]*)"', result)
            return channels[:5] if channels else None
            
    except Exception as e:
        print(f"Error getting relevant channels: {e}")
        return None

def search_youtube_by_channel(channel_name, api_key=None, max_results=5):
    """Search YouTube for recent videos from a specific channel"""
    if not api_key:
        # Return sample channel results
        sample_results = [
            {"title": f"Latest Video from {channel_name}", "views": "156K views", "published": "2 days ago", "description": f"Recent content from {channel_name}...", "video_id": f"sample_{channel_name}_1"},
            {"title": f"{channel_name}'s Hot Take on Current Events", "views": "89K views", "published": "1 day ago", "description": f"Commentary and analysis from {channel_name}...", "video_id": f"sample_{channel_name}_2"},
            {"title": f"Breaking: {channel_name} Responds", "views": "234K views", "published": "3 hours ago", "description": f"Response video from {channel_name}...", "video_id": f"sample_{channel_name}_3"},
        ]
        return sample_results
    
    try:
        # First, get the channel ID
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            'part': 'snippet',
            'q': channel_name,
            'type': 'channel',
            'maxResults': 1,
            'key': api_key
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=15)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get('items'):
                channel_id = search_data['items'][0]['id']['channelId']
                
                # Now get recent videos from this channel
                videos_url = "https://www.googleapis.com/youtube/v3/search"
                videos_params = {
                    'part': 'snippet',
                    'channelId': channel_id,
                    'type': 'video',
                    'order': 'date',
                    'maxResults': max_results,
                    'key': api_key,
                    'publishedAfter': (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                }
                
                videos_response = requests.get(videos_url, params=videos_params, timeout=15)
                
                if videos_response.status_code == 200:
                    videos_data = videos_response.json()
                    channel_videos = []
                    
                    for item in videos_data.get('items', []):
                        snippet = item.get('snippet', {})
                        video_data = {
                          'title': snippet.get('title', 'No title'),
                          'channel': snippet.get('channelTitle', 'Unknown Channel'),
                          'views': get_video_views(item.get('id', ''), api_key),
                          'published': format_youtube_date(snippet.get('publishedAt', 'Unknown')),
                          'video_id': item.get('id', ''),
                          'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                          'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                        }                        
                        channel_videos.append(video_data)
                    
                    return channel_videos
        
        # Fallback to sample data if API fails
        return search_youtube_by_channel(channel_name)
        
    except Exception as e:
        return search_youtube_by_channel(channel_name)  # Return sample data on error

# Now replace your entire YouTube Intelligence platform section with this:

# First, add this function with your other YouTube functions (before the platform section):

def get_video_views(video_id, api_key):
    """Get view count for a specific video"""
    if not api_key or not video_id:
        return "N/A"
    
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                view_count = data['items'][0].get('statistics', {}).get('viewCount', 'N/A')
                if view_count != 'N/A':
                    # Format view count nicely (e.g., 1,234,567 -> 1.2M)
                    try:
                        views = int(view_count)
                        if views >= 1000000:
                            return f"{views/1000000:.1f}M views"
                        elif views >= 1000:
                            return f"{views/1000:.0f}K views"
                        else:
                            return f"{views} views"
                    except:
                        return f"{view_count} views"
                return view_count
        return "N/A"
    except:
        return "N/A"

def get_relevant_channels_for_creator(creator_name, api_key):
    """Search YouTube for recent videos from a specific channel"""
    if not api_key:
        # Return sample channel results
        sample_results = [
            {"title": f"Latest Video from {channel_name}", "views": "156K views", "published": "2 days ago", "description": f"Recent content from {channel_name}...", "video_id": f"sample_{channel_name}_1"},
            {"title": f"{channel_name}'s Hot Take on Current Events", "views": "89K views", "published": "1 day ago", "description": f"Commentary and analysis from {channel_name}...", "video_id": f"sample_{channel_name}_2"},
            {"title": f"Breaking: {channel_name} Responds", "views": "234K views", "published": "3 hours ago", "description": f"Response video from {channel_name}...", "video_id": f"sample_{channel_name}_3"},
        ]
        return sample_results
    
    try:
        # First, get the channel ID
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            'part': 'snippet',
            'q': channel_name,
            'type': 'channel',
            'maxResults': 1,
            'key': api_key
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=15)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get('items'):
                channel_id = search_data['items'][0]['id']['channelId']
                
                # Now get recent videos from this channel
                videos_url = "https://www.googleapis.com/youtube/v3/search"
                videos_params = {
                    'part': 'snippet',
                    'channelId': channel_id,
                    'type': 'video',
                    'order': 'date',
                    'maxResults': max_results,
                    'key': api_key,
                    'publishedAfter': (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                }
                
                videos_response = requests.get(videos_url, params=videos_params, timeout=15)
                
                if videos_response.status_code == 200:
                    videos_data = videos_response.json()
                    channel_videos = []
                    
                    for item in videos_data.get('items', []):
                        snippet = item.get('snippet', {})
                        video_data = {
                          'title': snippet.get('title', 'No title'),
                          'channel': snippet.get('channelTitle', 'Unknown Channel'),
                          'views': get_video_views(item.get('id', ''), api_key),
                          'published': format_youtube_date(snippet.get('publishedAt', 'Unknown')),
                          'video_id': item.get('id', ''),
                          'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                          'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                        }   
                        channel_videos.append(video_data)
                    
                    return channel_videos
        
        # Fallback to sample data if API fails
        return search_youtube_by_channel(channel_name)
        
    except Exception as e:
        return search_youtube_by_channel(channel_name)  # Return sample data on error

# Now replace your entire YouTube Intelligence platform section with this:

# First, add this function with your other YouTube functions (before the platform section):

def get_video_views(video_id, api_key):
    """Get view count for a specific video"""
    if not api_key or not video_id:
        return "N/A"
    
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                view_count = data['items'][0].get('statistics', {}).get('viewCount', 'N/A')
                if view_count != 'N/A':
                    # Format view count nicely (e.g., 1,234,567 -> 1.2M)
                    try:
                        views = int(view_count)
                        if views >= 1000000:
                            return f"{views/1000000:.1f}M views"
                        elif views >= 1000:
                            return f"{views/1000:.0f}K views"
                        else:
                            return f"{views} views"
                    except:
                        return f"{view_count} views"
                return view_count
        return "N/A"
    except:
        return "N/A"
    """Use AI to find 5 most relevant YouTube channels for a creator"""
    if not api_key:
        return None
    
    prompt = f"""You are a YouTube content strategist. Find 5 YouTube channels that are most similar to "{creator_name}" in terms of:
    - Content style and format
    - Target audience
    - Topic/niche overlap
    - Production quality level
    
    Focus on channels that would have similar audiences and content approaches.
    
    Return ONLY a Python list of 5 channel names like this:
    ["Channel Name 1", "Channel Name 2", "Channel Name 3", "Channel Name 4", "Channel Name 5"]
    
    Make sure channel names are exact and searchable on YouTube. No extra text, just the list."""
    
    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
            timeout=30
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the list from the AI response
        import ast
        try:
            channels = ast.literal_eval(result)
            if isinstance(channels, list) and len(channels) <= 5:
                return [channel.strip() for channel in channels if channel.strip()]
        except:
            # Fallback parsing if AI doesn't return perfect list format
            import re
            channels = re.findall(r'"([^"]*)"', result)
            return channels[:5] if channels else None
            
    except Exception as e:
        print(f"Error getting relevant channels: {e}")
        return None

def get_relevant_channels_for_creator(creator_name, api_key):
    """Search YouTube for recent videos from a specific channel"""
    if not api_key:
        # Return sample channel results
        sample_results = [
            {"title": f"Latest Video from {channel_name}", "views": "156K views", "published": "2 days ago", "description": f"Recent content from {channel_name}...", "video_id": f"sample_{channel_name}_1"},
            {"title": f"{channel_name}'s Hot Take on Current Events", "views": "89K views", "published": "1 day ago", "description": f"Commentary and analysis from {channel_name}...", "video_id": f"sample_{channel_name}_2"},
            {"title": f"Breaking: {channel_name} Responds", "views": "234K views", "published": "3 hours ago", "description": f"Response video from {channel_name}...", "video_id": f"sample_{channel_name}_3"},
        ]
        return sample_results
    
    try:
        # First, get the channel ID
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            'part': 'snippet',
            'q': channel_name,
            'type': 'channel',
            'maxResults': 1,
            'key': api_key
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=15)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get('items'):
                channel_id = search_data['items'][0]['id']['channelId']
                
                # Now get recent videos from this channel
                videos_url = "https://www.googleapis.com/youtube/v3/search"
                videos_params = {
                    'part': 'snippet',
                    'channelId': channel_id,
                    'type': 'video',
                    'order': 'date',
                    'maxResults': max_results,
                    'key': api_key,
                    'publishedAfter': (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                }
                
                videos_response = requests.get(videos_url, params=videos_params, timeout=15)
                
                if videos_response.status_code == 200:
                    videos_data = videos_response.json()
                    channel_videos = []
                    
                    for item in videos_data.get('items', []):
                        snippet = item.get('snippet', {})
                        video_data = {
                            'title': snippet.get('title', 'No title'),
                            'published': snippet.get('publishedAt', 'Unknown'),
                            'video_id': item.get('id', {}).get('videoId', ''),
                            'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                            'channel': snippet.get('channelTitle', channel_name),
                            'views': 'N/A'  # Would need additional API call to get view count
                        }
                        channel_videos.append(video_data)
                    
                    return channel_videos
        
        # Fallback to sample data if API fails
        return search_youtube_by_channel(channel_name)
        
    except Exception as e:
        return search_youtube_by_channel(channel_name)  # Return sample data on error

# First, add this function with your other YouTube functions (before the platform section):

def get_video_views(video_id, api_key):
    """Get view count for a specific video"""
    if not api_key or not video_id or video_id.startswith('sample'):
        return "N/A"
    
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items') and len(data['items']) > 0:
                stats = data['items'][0].get('statistics', {})
                view_count = stats.get('viewCount')
                if view_count:
                    # Format view count nicely (e.g., 1,234,567 -> 1.2M)
                    try:
                        views = int(view_count)
                        if views >= 1000000:
                            return f"{views/1000000:.1f}M views"
                        elif views >= 1000:
                            return f"{views/1000:.0f}K views"
                        else:
                            return f"{views:,} views"
                    except:
                        return f"{view_count} views"
        return "N/A"
    except Exception as e:
        print(f"Error fetching views for {video_id}: {e}")
        return "N/A"
    """Use AI to find 5 most relevant YouTube channels for a creator"""
    if not api_key:
        return None
    
    prompt = f"""You are a YouTube content strategist. Find 5 YouTube channels that are most similar to "{creator_name}" in terms of:
    - Content style and format
    - Target audience
    - Topic/niche overlap
    - Production quality level
    
    Focus on channels that would have similar audiences and content approaches.
    
    Return ONLY a Python list of 5 channel names like this:
    ["Channel Name 1", "Channel Name 2", "Channel Name 3", "Channel Name 4", "Channel Name 5"]
    
    Make sure channel names are exact and searchable on YouTube. No extra text, just the list."""
    
    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
            timeout=30
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the list from the AI response
        import ast
        try:
            channels = ast.literal_eval(result)
            if isinstance(channels, list) and len(channels) <= 5:
                return [channel.strip() for channel in channels if channel.strip()]
        except:
            # Fallback parsing if AI doesn't return perfect list format
            import re
            channels = re.findall(r'"([^"]*)"', result)
            return channels[:5] if channels else None
            
    except Exception as e:
        print(f"Error getting relevant channels: {e}")
        return None

def format_youtube_date(date_string):
    """Convert YouTube API date to MM/DD/YY format"""
    if not date_string or date_string in ['Unknown', 'N/A'] or date_string.startswith('sample'):
        return date_string
    
    try:
        from datetime import datetime
        # Handle both formats: 2025-08-08T14:00:36Z and other ISO formats
        if 'T' in date_string:
            # Remove timezone info and parse
            clean_date = date_string.replace('Z', '').split('T')[0]
            dt = datetime.strptime(clean_date, '%Y-%m-%d')
        else:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        
        return dt.strftime('%m/%d/%y')
    except Exception as e:
        print(f"Error formatting date {date_string}: {e}")
        return date_string
    """Search YouTube for recent videos from a specific channel"""
    if not api_key:
        # Return sample channel results
        sample_results = [
            {"title": f"Latest Video from {channel_name}", "views": "156K views", "published": "2 days ago", "description": f"Recent content from {channel_name}...", "video_id": f"sample_{channel_name}_1"},
            {"title": f"{channel_name}'s Hot Take on Current Events", "views": "89K views", "published": "1 day ago", "description": f"Commentary and analysis from {channel_name}...", "video_id": f"sample_{channel_name}_2"},
            {"title": f"Breaking: {channel_name} Responds", "views": "234K views", "published": "3 hours ago", "description": f"Response video from {channel_name}...", "video_id": f"sample_{channel_name}_3"},
        ]
        return sample_results
    
    try:
        # First, get the channel ID
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            'part': 'snippet',
            'q': channel_name,
            'type': 'channel',
            'maxResults': 1,
            'key': api_key
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=15)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get('items'):
                channel_id = search_data['items'][0]['id']['channelId']
                
                # Now get recent videos from this channel
                videos_url = "https://www.googleapis.com/youtube/v3/search"
                videos_params = {
                    'part': 'snippet',
                    'channelId': channel_id,
                    'type': 'video',
                    'order': 'date',
                    'maxResults': max_results,
                    'key': api_key,
                    'publishedAfter': (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                }
                
                videos_response = requests.get(videos_url, params=videos_params, timeout=15)
                
                if videos_response.status_code == 200:
                    videos_data = videos_response.json()
                    channel_videos = []
                    
                    for item in videos_data.get('items', []):
                        snippet = item.get('snippet', {})
                        video_data = {
                            'title': snippet.get('title', 'No title'),
                            'published': snippet.get('publishedAt', 'Unknown'),
                            'video_id': item.get('id', {}).get('videoId', ''),
                            'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                            'channel': snippet.get('channelTitle', channel_name),
                            'views': 'N/A'  # Would need additional API call to get view count
                        }
                        channel_videos.append(video_data)
                    
                    return channel_videos
        
        # Fallback to sample data if API fails
        return search_youtube_by_channel(channel_name)
        
    except Exception as e:
        return search_youtube_by_channel(channel_name)  # Return sample data on error


# Get the API keys
api_key, youtube_api_key, spotify_client_id, spotify_client_secret, tmdb_key, gemini_api_key, serper_api_key, perplexity_api_key, courtlistener_token = get_api_keys()

# Initialize page state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Case Search"

# Display content based on current page
if st.session_state.current_page == "Case Search":
    st.markdown("### Search Cases")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        case_search = st.text_input(
            "Search for a case, victim, or perpetrator",
            placeholder="e.g., 'Lizzie Borden', 'Black Dahlia', 'hotel murder 1970s'",
            key="case_search_input"
        )
    
    with col2:
        search_filter = st.selectbox(
            "Time Period",
            ["All Time", "1800s", "1900-1950", "1950-1980", "1980-2000", "2000-2010", "2010-2020", "2020-Present"],
            key="time_period_filter"
        )
    
    if st.button("SEARCH", key="search_cases_btn", type="primary", use_container_width=True):
        if not case_search:
            st.warning("Please enter a search term")
        else:
            # Create a progress bar and status text (no spinner)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Search all sources with progress updates
            status_text.text("Searching Wikipedia...")
            progress_bar.progress(10)
            wikidata_results = search_wikidata(case_search, 10)
            
            status_text.text("Checking YouTube...")
            progress_bar.progress(25)
            youtube_count = count_youtube_videos(case_search, youtube_api_key) if youtube_api_key else 0
            
            status_text.text("Analyzing case...")
            progress_bar.progress(40)
            # Use Perplexity for comprehensive case research
            web_search_results = None
            if perplexity_api_key:
                # Get comprehensive case information from Perplexity
                perplexity_data = get_perplexity_case_analysis(case_search, perplexity_api_key)
                
                if perplexity_data:
                    # Format the results for display
                    formatted_results = []
                    
                    formatted_results.append("## Case Overview\n")
                    formatted_results.append(perplexity_data.get('overview', 'No overview available'))
                    formatted_results.append("\n")
                    
                    web_search_results = "\n".join(formatted_results)

            progress_bar.progress(60)
            # Skip Wikipedia pageviews
            wikipedia_data = {'trend_percentage': 0, 'last_7_days': 0}
            
            status_text.text("Searching Reddit discussions...")
            progress_bar.progress(75)
            # Search Reddit - ALL of Reddit for titles containing the search term
            reddit_results = []
            try:
                # Use Pushshift API (Reddit archive) for better search
                pushshift_url = "https://api.pushshift.io/reddit/search/submission/"
                
                # Try Pushshift first (better search)
                params = {
                    'q': case_search,
                    'size': 100,
                    'sort': 'score',
                    'sort_type': 'desc'
                }
                
                try:
                    response = requests.get(pushshift_url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get('data', []):
                            # Convert Pushshift format to Reddit format
                            reddit_results.append({
                                'data': {
                                    'title': item.get('title', ''),
                                    'selftext': item.get('selftext', ''),
                                    'subreddit': item.get('subreddit', ''),
                                    'score': item.get('score', 0),
                                    'num_comments': item.get('num_comments', 0),
                                    'permalink': f"/r/{item.get('subreddit')}/comments/{item.get('id')}/",
                                    'url': item.get('url', ''),
                                    'created_utc': item.get('created_utc', 0)
                                }
                            })
                except:
                    pass  # Pushshift might be down, continue to Reddit search
                
                # Update progress
                progress_bar.progress(85)
                
                # If Pushshift didn't work or found nothing, use Reddit search with better parameters
                if not reddit_results:
                    # Search variations to improve results
                    search_variations = [
                        case_search,  # Full name
                        ' '.join(case_search.split()[:2]) if len(case_search.split()) > 2 else case_search,  # First two words
                        case_search.split()[-1] if len(case_search.split()) > 1 else case_search,  # Last word only
                    ]
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                    
                    for search_term in search_variations:
                        # Search across all Reddit
                        search_url = "https://www.reddit.com/search.json"
                        params = {
                            'q': f'{search_term} (murder OR killer OR crime OR death)',  # Add context
                            'sort': 'relevance',
                            'limit': 100,
                            't': 'all',
                            'type': 'link',
                            'raw_json': 1
                        }
                        
                        time.sleep(1)
                        response = requests.get(search_url, headers=headers, params=params, timeout=15)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if 'data' in data and 'children' in data['data']:
                                for post in data['data']['children']:
                                    post_data = post['data']
                                    title_lower = post_data['title'].lower()
                                    
                                    # Check if relevant to our search
                                    if any(word.lower() in title_lower for word in case_search.split()):
                                        reddit_results.append(post)
                        
                        if reddit_results:
                            break  # Stop if we found results
                    
                    # Update progress
                    progress_bar.progress(90)
                    
                    # Last resort: search specific true crime subreddits
                    if not reddit_results:
                        crime_subreddits = ["serialkillers", "TrueCrime", "UnresolvedMysteries"]
                        
                        for subreddit in crime_subreddits:
                            url = f"https://www.reddit.com/r/{subreddit}/search.json"
                            params = {
                                'q': case_search.split()[-1],  # Just last name
                                'restrict_sr': 'on',
                                'sort': 'relevance',
                                'limit': 50,
                                't': 'all',
                                'raw_json': 1
                            }
                            
                            response = requests.get(url, headers=headers, params=params, timeout=10)
                            if response.status_code == 200:
                                data = response.json()
                                for post in data.get('data', {}).get('children', []):
                                    reddit_results.append(post)
                
                # Remove duplicates and sort by score
                seen = set()
                unique_results = []
                for post in reddit_results:
                    post_id = post['data'].get('id', post['data'].get('title', ''))
                    if post_id not in seen:
                        seen.add(post_id)
                        unique_results.append(post)
                
                reddit_results = sorted(unique_results, key=lambda x: x['data'].get('score', 0), reverse=True)[:20]
                
            except Exception as e:
                print(f"Reddit search error: {e}")
            
            # Complete the progress
            progress_bar.progress(100)
            status_text.text("Search complete!")
            
            # Hide progress indicators after a short delay
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            # Store all results in session state
            st.session_state.search_performed = True
            st.session_state.search_query = case_search
            cache_with_expiry('wikidata_results', wikidata_results, hours=24)
            cache_with_expiry('gdelt_results', [], hours=24)
            cache_with_expiry('nyt_results', [], hours=24)
            cache_with_expiry('youtube_count', youtube_count, hours=24)
            st.session_state.reddit_results = reddit_results
            st.session_state.web_search_results = web_search_results
    
    # Display results from session state
    if st.session_state.get('search_performed', False):
        case_search = st.session_state.search_query
        wikidata_results = get_cached_data('wikidata_results') or []
        gdelt_results = get_cached_data('gdelt_results') or []
        nyt_results = get_cached_data('nyt_results') or []
        youtube_count = get_cached_data('youtube_count') or 0
        nyt_results = st.session_state.nyt_results
        youtube_count = st.session_state.youtube_count
        st.session_state.wikipedia_data = {'trend_percentage': 0, 'last_7_days': 0}  # Add dummy data
        wikipedia_data = st.session_state.wikipedia_data
        reddit_results = st.session_state.reddit_results
        web_search_results = st.session_state.get('web_search_results', None) 

        # After displaying search results, add this:
        if st.session_state.get('search_performed', False):
            # At the top of results section
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### Results for: {case_search}")
            with col2:
                if st.button("Save to Ideas", type="primary"):
                    if 'saved_ideas' not in st.session_state:
                        st.session_state.saved_ideas = []
                    
                    # Calculate a priority based on data
                    if youtube_count < 50:
                        suggested_priority = "High"
                    elif youtube_count < 200:
                        suggested_priority = "Medium"
                    else:
                        suggested_priority = "Low"
                    
                    # Create a summary from the Perplexity results
                    summary = "No detailed information available."
                    if web_search_results:
                        # Extract just the overview text from Perplexity results
                        # Remove markdown headers and get first 200-300 characters
                        import re
                        clean_text = re.sub(r'#{1,6}\s+.*?\n', '', web_search_results)  # Remove headers
                        clean_text = re.sub(r'\*\*.*?\*\*', '', clean_text)  # Remove bold markers
                        clean_text = clean_text.strip()
                        
                        # Get first 300 characters or first 2 sentences, whichever is shorter
                        sentences = clean_text.split('. ')
                        if len(sentences) >= 2:
                            summary = '. '.join(sentences[:2]) + '.'
                        else:
                            summary = clean_text[:300] + '...' if len(clean_text) > 300 else clean_text
                    
                    new_idea = {
                        'id': len(st.session_state.saved_ideas) + 1,
                        'title': case_search,
                        'notes': summary,  # Now contains the case summary instead of stats
                        'priority': suggested_priority,
                        'saved_date': datetime.now().strftime('%m/%d/%y'),
                        'status': 'New'
                    }
                    st.session_state.saved_ideas.append(new_idea)
                    st.success(f"Saved '{case_search}' to ideas!")
            
            # Then continue with your existing results display...
        
        source_tabs = st.tabs(["Overview", "Web Search", "YouTube", "Reddit", "Wikipedia"])
        
        with source_tabs[0]:  # Overview (Perplexity) - previously "Web Search"
            if web_search_results:

                # Display the formatted Perplexity results
                st.markdown(web_search_results)
                
                # Add export button for the research
                st.download_button(
                    "Download Research",
                    data=web_search_results,
                    file_name=f"{case_search}_perplexity_research.md",
                    mime="text/markdown",
                    key="download_perplexity"
                )
            else:
                st.info("No web search results. Add Perplexity API key for AI-powered research.")
        
        # In the source_tabs section, replace the YouTube tab (source_tabs[1]) with this:

        with source_tabs[1]:  # Web Search (Serper)
            serper_api_key = os.getenv("SERPER_API_KEY", "")
            
            if not serper_api_key:
                st.info("""
                **Web search requires Serper API key**
                
                To enable web search:
                1. Sign up at [serper.dev](https://serper.dev)
                2. Get your API key
                3. Add to environment: SERPER_API_KEY
                
                Serper provides real-time Google search results.
                """)
            else:
                with st.spinner("Searching the web..."):
                    serper_results = search_with_serper(case_search, serper_api_key, num_results=10)
                
                if serper_results:
                    # Top Search Results
                    st.markdown("#### Top Search Results")
                    
                    if serper_results.get('organic'):
                        for i, result in enumerate(serper_results['organic'][:5], 1):
                            st.markdown(f"**{i}. {result['title']}**")
                            if result.get('source'):
                                st.caption(f"Source: {result.get('source')}")
                            st.write(result['snippet'])
                            st.markdown(f"[Read More]({result['link']})")
                            st.divider()
                    else:
                        st.info("No search results found")
                    
                    # Recent News
                    st.markdown("#### Recent News")
                    
                    if serper_results.get('news'):
                        for i, article in enumerate(serper_results['news'][:5], 1):
                            st.markdown(f"**{article['title']}**")
                            st.caption(f"{article.get('source', 'Unknown')} - {article.get('date', 'Unknown date')}")
                            st.write(article['snippet'])
                            st.markdown(f"[Read Article]({article['link']})")
                            st.divider()
                    else:
                        st.info("No recent news found")
                else:
                    st.warning("No web results found. Try different search terms.")


        with source_tabs[2]:  # YouTube tab
            if youtube_count and youtube_count > 0:
                st.markdown("Data provided by YouTube API Services")  # ADD HERE
                st.write(f"Found {youtube_count:,} videos about this case")
                st.caption("YouTube data is fetched live and not stored. Data freshness depends on YouTube API.")

                
                # Get actual YouTube videos if we have the API key
                if youtube_api_key:
                    st.markdown("---")
                    st.markdown("### Top Performing Content")
                    
                    # Search for videos
                    yt_url = "https://www.googleapis.com/youtube/v3/search"
                    yt_params = {
                        "key": youtube_api_key,
                        "part": "snippet",
                        "q": case_search,  # This should use the search query from session state
                        "type": "video",
                        "order": "viewCount",  # Order by view count
                        "maxResults": 50,  # Get more to separate shorts/videos
                    }
                    
                    try:
                        yt_response = requests.get(yt_url, params=yt_params, timeout=10)
                        if yt_response.status_code == 200:
                            yt_data = yt_response.json()
                            
                            # Get video IDs
                            video_ids = [item['id']['videoId'] for item in yt_data.get('items', [])]
                            
                            if video_ids:
                                # Get video details including duration and view count
                                details_url = "https://www.googleapis.com/youtube/v3/videos"
                                details_params = {
                                    "key": youtube_api_key,
                                    "part": "contentDetails,statistics,snippet",
                                    "id": ",".join(video_ids)
                                }
                                
                                details_response = requests.get(details_url, params=details_params, timeout=10)
                                if details_response.status_code == 200:
                                    details_data = details_response.json()
                                    
                                    regular_videos = []
                                    shorts = []
                                    
                                    for video in details_data.get('items', []):
                                        # Parse duration (PT1M30S format)
                                        duration_str = video['contentDetails']['duration']
                                        
                                        # Convert ISO 8601 duration to seconds
                                        import re
                                        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
                                        if match:
                                            hours = int(match.group(1) or 0)
                                            minutes = int(match.group(2) or 0) 
                                            seconds = int(match.group(3) or 0)
                                            total_seconds = hours * 3600 + minutes * 60 + seconds
                                        else:
                                            total_seconds = 0
                                        
                                        video_info = {
                                            'id': video['id'],
                                            'title': video['snippet']['title'],
                                            'channel': video['snippet']['channelTitle'],
                                            'thumbnail': video['snippet']['thumbnails']['medium']['url'],
                                            'views': int(video['statistics'].get('viewCount', 0)),
                                            'duration': total_seconds,
                                            'url': f"https://www.youtube.com/watch?v={video['id']}",
                                            'publishedAt': video['snippet'].get('publishedAt', '')  # Add this line
                                        }
                                        
                                        # Separate shorts from regular videos based on duration
                                        if total_seconds > 0 and total_seconds <= 180:
                                            shorts.append(video_info)
                                        else:
                                            regular_videos.append(video_info)
                                    
                                    # Sort by views
                                    regular_videos.sort(key=lambda x: x['views'], reverse=True)
                                    shorts.sort(key=lambda x: x['views'], reverse=True)
                                    
                                    # Display top 5 of each
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown("#### Top 5 Regular Videos")
                                        st.markdown("Data provided by YouTube API Services")
                                        if regular_videos:
                                            for video in regular_videos[:5]:
                                                with st.container():
                                                    # Title - use text_truncate to ensure single line
                                                    title_display = video['title'][:45] + "..." if len(video['title']) > 45 else video['title']
                                                    st.markdown(f"**[{title_display}]({video['url']})**", help=video['title'])  # Full title on hover
                                                    
                                                    # Channel and date on one line
                                                    publish_date = "Unknown"
                                                    if 'publishedAt' in video:
                                                        try:
                                                            from datetime import datetime
                                                            dt = datetime.strptime(video['publishedAt'][:10], '%Y-%m-%d')
                                                            publish_date = dt.strftime('%m/%d/%y')
                                                        except:
                                                            publish_date = video['publishedAt'][:10]
                                                    
                                                    # Use columns to control spacing
                                                    meta_col1, meta_col2 = st.columns([3, 1])
                                                    with meta_col1:
                                                        st.caption(f"📺 {video['channel'][:25]}...")  # Truncate channel name too
                                                    with meta_col2:
                                                        st.caption(publish_date)
                                                    
                                                    # View count
                                                    if video['views'] >= 1000000:
                                                        views_str = f"{video['views']/1000000:.1f}M views"
                                                    elif video['views'] >= 1000:
                                                        views_str = f"{video['views']/1000:.0f}K views"
                                                    else:
                                                        views_str = f"{video['views']} views"
                                                    st.caption(f"👁️ {views_str}")
                                                    
                                                    # Thumbnail with fixed aspect ratio container
                                                    if video.get('thumbnail'):
                                                        st.image(video['thumbnail'], use_column_width=True)
                                                    else:
                                                        # Add empty space for consistent height
                                                        st.markdown("<div style='height: 180px;'></div>", unsafe_allow_html=True)
                                                    
                                                    st.markdown("---")
                                        else:
                                            st.info("No regular videos found")

                                    with col2:
                                        st.markdown("#### Top 5 Shorts")
                                        st.markdown("Data provided by YouTube API Services")
                                        if shorts:
                                            for short in shorts[:5]:
                                                with st.container():
                                                    # Title - use text_truncate to ensure single line
                                                    title_display = short['title'][:45] + "..." if len(short['title']) > 45 else short['title']
                                                    st.markdown(f"**[{title_display}]({short['url']})**", help=short['title'])  # Full title on hover
                                                    
                                                    # Channel and date on one line
                                                    publish_date = "Unknown"
                                                    if 'publishedAt' in short:
                                                        try:
                                                            from datetime import datetime
                                                            dt = datetime.strptime(short['publishedAt'][:10], '%Y-%m-%d')
                                                            publish_date = dt.strftime('%m/%d/%y')
                                                        except:
                                                            publish_date = short['publishedAt'][:10]
                                                    
                                                    # Use columns to control spacing
                                                    meta_col1, meta_col2 = st.columns([3, 1])
                                                    with meta_col1:
                                                        st.caption(f"📺 {short['channel'][:25]}...")  # Truncate channel name too
                                                    with meta_col2:
                                                        st.caption(publish_date)
                                                    
                                                    # View count
                                                    if short['views'] >= 1000000:
                                                        views_str = f"{short['views']/1000000:.1f}M views"
                                                    elif short['views'] >= 1000:
                                                        views_str = f"{short['views']/1000:.0f}K views"
                                                    else:
                                                        views_str = f"{short['views']} views"
                                                    st.caption(f"👁️ {views_str}")
                                                    
                                                    # Thumbnail with fixed aspect ratio container
                                                    if short.get('thumbnail'):
                                                        st.image(short['thumbnail'], use_column_width=True)
                                                    else:
                                                        # Add empty space for consistent height
                                                        st.markdown("<div style='height: 180px;'></div>", unsafe_allow_html=True)
                                                    
                                                    st.markdown("---")
                                        else:
                                            st.info("No shorts found")
                                else:
                                    st.error(f"Could not fetch video details. Status: {details_response.status_code}")
                            else:
                                st.info("No videos found for this search")
                        else:
                            if yt_response.status_code == 403:
                                st.error("YouTube API quota exceeded. Please try again later or add more API keys.")
                            else:
                                st.error(f"YouTube search failed. Status: {yt_response.status_code}")
                                
                    except Exception as e:
                        st.error(f"Error fetching YouTube videos: {str(e)}")
                        
                        # Show sample data as fallback
                        st.info("Showing sample data due to API error")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### Sample Regular Videos")
                            sample_videos = [
                                {"title": f"The {case_search} Case - Full Documentary", "channel": "True Crime Daily", "views": "2.3M views"},
                                {"title": f"What Really Happened to {case_search}?", "channel": "Bailey Sarian", "views": "1.8M views"},
                                {"title": f"{case_search}: The Untold Story", "channel": "Kendall Rae", "views": "956K views"},
                            ]
                            for video in sample_videos:
                                st.markdown(f"**{video['title']}**")
                                st.caption(f"📺 {video['channel']} • {video['views']}")
                                st.markdown("---")
                        
                        with col2:
                            st.markdown("#### Sample Shorts")
                            sample_shorts = [
                                {"title": f"{case_search} in 60 Seconds", "channel": "Crime Shorts", "views": "5.2M views"},
                                {"title": f"The {case_search} Mystery #shorts", "channel": "Quick Crime", "views": "3.1M views"},
                            ]
                            for short in sample_shorts:
                                st.markdown(f"**{short['title']}**")
                                st.caption(f"📺 {short['channel']} • {short['views']}")
                                st.markdown("---")
                else:
                    st.warning("YouTube API key not configured. Unable to fetch video details.")
                    
                    # Show sample data when no API key
                    st.markdown("---")
                    st.markdown("### Sample Content (Configure API for real data)")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Sample Regular Videos")
                        st.info("Add YouTube API key to see real videos")
                    
                    with col2:
                        st.markdown("#### Sample Shorts")
                        st.info("Add YouTube API key to see real shorts")
            else:
                st.info("No YouTube videos found for this search term")

        with source_tabs[3]:  # Reddit (index 2)
            if reddit_results:
                for post in reddit_results[:10]:
                    post_data = post['data']
                    st.write(f"**{post_data['title']}**")
                    st.caption(f"r/{post_data.get('source_subreddit', 'unknown')} - {post_data['score']} upvotes")
                    st.write(f"[View](https://reddit.com{post_data['permalink']})")
                    st.write("---")
            else:
                st.info("No Reddit discussions found")

        with source_tabs[4]:  # Wikipedia
            # Try Wikidata first
            if wikidata_results:
                st.markdown("#### Wikidata Entries")
                for item in wikidata_results[:5]:
                    st.write(f"**{item['label']}**")
                    st.caption(f"{item['description']}")
                    st.write(f"[View on Wikidata]({item['url']})")
                    # Add Wikipedia link
                    wiki_url = f"https://en.wikipedia.org/wiki/{item['label'].replace(' ', '_')}"
                    st.write(f"[Search Wikipedia]({wiki_url})")
                    st.divider()
            
            # Always also try Wikipedia's own search API
            st.markdown("#### Wikipedia Articles")
            wiki_api_url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "opensearch",
                "search": case_search,
                "limit": 5,
                "format": "json"
            }
            
            try:
                response = requests.get(wiki_api_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1 and data[1]:  # data[1] contains titles
                        for i, title in enumerate(data[1][:5]):
                            # data[2] has descriptions, data[3] has URLs
                            description = data[2][i] if len(data) > 2 and i < len(data[2]) else ""
                            url = data[3][i] if len(data) > 3 and i < len(data[3]) else f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                            
                            st.write(f"**{title}**")
                            if description:
                                st.caption(description)
                            st.write(f"[Read on Wikipedia]({url})")
                            st.divider()
                    else:
                        st.info("No Wikipedia articles found")
            except Exception as e:
                st.info("Wikipedia search unavailable")
                # Provide direct search link
                wiki_search_url = f"https://en.wikipedia.org/w/index.php?search={case_search.replace(' ', '+')}"
                st.markdown(f"[Search Wikipedia directly]({wiki_search_url})")

        
        # Bailey's Strategy Generator
        if api_key:
            # Initialize session state
            if 'show_strategy' not in st.session_state:
                st.session_state.show_strategy = False
            if 'generated_strategy' not in st.session_state:
                st.session_state.generated_strategy = None
            
            # Button to generate strategy
            if st.button("Generate Episode Strategy", key="generate_strategy", type="primary", use_container_width=True):
                with st.spinner("Creating episode strategy..."):
                    
                    # Get actual Wikipedia article content
                    wiki_article_content = ""
                    if 'wikipedia_data' in st.session_state and st.session_state.wikipedia_data and st.session_state.wikipedia_data.get('article_title'):
                        # ... (your Wikipedia fetching code) ...
                        pass
                    
                    # Get web search results context
                    web_search_context = ""
                    web_search_results = st.session_state.get('web_search_results', None)
                    if web_search_results:
                        web_content = web_search_results[:3000] if len(web_search_results) > 3000 else web_search_results
                        web_search_context = f"Web Search Information:\n{web_content}\n\n"
                    
                    # Build wiki context from wikidata results
                    wiki_context = ""
                    if 'wikidata_results' in st.session_state and st.session_state.wikidata_results:
                        wiki_entries = [f"- {r['label']}: {r['description']}" for r in st.session_state.wikidata_results[:3]]
                        wiki_context = "Wikipedia/Wikidata entries found:\n" + "\n".join(wiki_entries) + "\n"
                    
                    # Build Reddit context
                    reddit_context = ""
                    if 'reddit_results' in st.session_state and st.session_state.reddit_results:
                        top_posts = [f"- {post['data']['title']} (r/{post['data'].get('subreddit', 'unknown')}, {post['data']['score']} upvotes)" 
                                    for post in st.session_state.reddit_results[:5]]
                        reddit_context = "Top Reddit discussions:\n" + "\n".join(top_posts) + "\n"
                    
                    # Get YouTube count
                    youtube_count = st.session_state.get('youtube_count', 0)
                    
                    # Get case search term
                    case_search = st.session_state.get('search_query', 'Unknown Case')
                    
                    prompt = f"""Create a Murder, Mystery & Makeup episode strategy for Bailey Sarian based on this comprehensive research:
                    
                    CASE: {case_search}
                    
                    DATA SUMMARY:
                    - YouTube Videos: {youtube_count} ({"oversaturated" if youtube_count > 200 else "good opportunity" if youtube_count < 50 else "moderate coverage"})
                    - Reddit Discussions: {len(st.session_state.get('reddit_results', []))}
                    
                    {web_search_context}
                    {wiki_article_content}
                    {wiki_context}
                    {reddit_context}
                    
                    Based on ALL this research (especially the web search information), provide:
                    1. EPISODE TITLE: Catchy MMM-style title that hasn't been overused
                    2. UNIQUE ANGLE: What fresh perspective can Bailey bring given the existing coverage?
                    3. COLD OPEN: First 30 seconds hook based on the most shocking detail from the sources
                    4. MAKEUP LOOK: What style pairs with this story
                    5. STORY STRUCTURE: 
                        - Opening: Set the scene (use specific details from web search)
                        - Act 1: Build up (use specific details from all sources)
                        - Act 2: The crime (incorporate facts from web search and Wikipedia)
                        - Act 3: Investigation/aftermath
                        - Conclusion: Bailey's take
                    6. KEY TALKING POINTS: Based on what Reddit/news are discussing
                    7. CONTROVERSY/DISCUSSION POINTS: What are people debating about this case?
                    8. LESSER-KNOWN FACTS: Pull interesting details from the web search that aren't widely covered
                    9. RESEARCH GAPS: What information is missing that Bailey should research further?
                    10. VISUAL ELEMENTS: Specific photos and graphics needed
                    11. ESTIMATED RUNTIME: Episode length
                    12. COMPETITION ANALYSIS: How to differentiate from the {youtube_count} existing videos
                    13. FACT CHECK LIST: Key facts from web search and Wikipedia to verify
                    
                    Make it specific to Bailey's casual, engaging style. Use actual details from ALL sources, especially unique information from the web search."""
                    
                    try:
                        # Use requests instead of OpenAI client
                        import requests
                        import json
                        
                        url = "https://api.openai.com/v1/chat/completions"
                        
                        headers = {
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        }
                        
                        data = {
                            "model": "gpt-4",
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 1500,
                            "temperature": 0.7
                        }
                        
                        response = requests.post(url, headers=headers, json=data, timeout=30)
                        
                        if response.status_code == 200:
                            result = response.json()
                            strategy = result['choices'][0]['message']['content']
                            st.session_state.generated_strategy = strategy
                            st.session_state.show_strategy = True
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

            # Display strategy outside the button
            if st.session_state.show_strategy and st.session_state.generated_strategy:
                st.markdown("---")
                st.markdown("### Episode Strategy")
                st.write(st.session_state.generated_strategy)
                
                # Download packet
                packet = f"""# Murder, Mystery & Makeup Episode Packet

## Case: {case_search}

### Data Summary
- YouTube Videos: {youtube_count}
- News Articles: {len(gdelt_results) + len(nyt_results)}
- Reddit Posts: {len(reddit_results)}
- Wikipedia Views (Last 7 days): {wikipedia_data['last_7_days'] if wikipedia_data else 'N/A'}

### Episode Strategy

{st.session_state.generated_strategy}

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
                st.download_button(
                    "Download Episode Packet",
                    packet,
                    file_name=f"MMM_{case_search[:30].replace(' ', '_')}_packet.md",
                    mime="text/markdown"
                )

elif st.session_state.current_page == "Trending Cases":    
    st.markdown("### Currently Trending True Crime")
    with st.form("trending_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            time_range = st.selectbox(
                "Time Period",
                ["hour", "day", "week", "month", "year", "all"],
                index=2,  # Default to week
                format_func=lambda x: {
                    "hour": "Past Hour",
                    "day": "Today", 
                    "week": "This Week",
                    "month": "This Month",
                    "year": "This Year",
                    "all": "All Time"
                }.get(x, x)
            )
        
        with col2:
            min_score = st.number_input(
                "Min. Upvotes",
                min_value=0,
                max_value=10000,
                value=100,
                step=50
            )
        
        with col3:
            num_results = st.slider(
                "Results to Show",
                min_value=10,
                max_value=50,
                value=20
            )
        
        # Changed from st.button to st.form_submit_button and removed key parameter
        submitted = st.form_submit_button("GET TRENDING", type="primary", use_container_width=True)
    
    # Form ends here, now process if submitted
    if submitted:
        with st.spinner("Analyzing trending cases across multiple sources..."):
            all_trending = []
            
            # Expanded subreddit list
            subreddits = [
                "TrueCrime", "UnresolvedMysteries", "UnsolvedMysteries",
                "TrueCrimeDiscussion", "TrueCrimePodcasts", "serialkillers",
                "MorbidReality", "CreepyWikipedia", "ColdCase", "MissingPersons"
            ]
            
            progress_bar = st.progress(0)
            total_subs = len(subreddits)
            
            for idx, sub in enumerate(subreddits):
                progress_bar.progress((idx + 1) / total_subs)
                
                try:
                    # Get top posts from each subreddit
                    url = f"https://www.reddit.com/r/{sub}/top.json"
                    params = {
                        't': time_range,
                        'limit': 25,
                        'raw_json': 1
                    }
                    
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            post_data = post['data']
                            
                            # Add this line to exclude subreddits (BEFORE checking score):
                            if post_data.get('subreddit', sub).lower() in ['murderedbywords', 'murdermittens']:
                                continue
                            
                            if post_data['score'] >= min_score:
                                # Extract potential case name
                                title = post_data['title']
                                
                                # Calculate trending score (combination of upvotes and comments)
                                trending_score = post_data['score'] + (post_data['num_comments'] * 10)
                                
                                all_trending.append({
                                    'title': title,
                                    'upvotes': post_data['score'],
                                    'comments': post_data['num_comments'],
                                    'subreddit': sub,  # Note: using 'sub' from the outer loop
                                    'url': f"https://reddit.com{post_data['permalink']}",
                                    'trending_score': trending_score,
                                    'created': post_data.get('created_utc', 0),
                                    'author': post_data.get('author', 'unknown'),
                                    'awards': post_data.get('total_awards_received', 0)
                                })

                    
                    time.sleep(0.3)  # Rate limiting
                except:
                    continue
            
            progress_bar.empty()
            
            # Also search for trending keywords
            trending_keywords = ["murder", "missing", "unsolved", "serial killer", "cold case", "disappeared"]
            
            st.info("Searching for trending topics...")
            
            for keyword in trending_keywords[:3]:  # Limit to avoid too many API calls
                try:
                    search_url = "https://www.reddit.com/search.json"
                    params = {
                        'q': keyword,
                        'sort': 'top',
                        't': time_range,
                        'limit': 10,
                        'raw_json': 1
                    }
                    
                    response = requests.get(search_url, headers=headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            post_data = post['data']
                            # Add exclusion check here too:
                            if post_data.get('subreddit', '').lower() in ['murderedbywords', 'murdermittens']:
                                continue
                            # Only include if from true crime related subreddit
                            if any(crime_word in post_data['subreddit'].lower() 
                                    for crime_word in ['crime', 'mystery', 'murder', 'missing']):
                                
                                if post_data['score'] >= min_score:
                                    trending_score = post_data['score'] + (post_data['num_comments'] * 10)
                                    
                                    all_trending.append({
                                        'title': post_data['title'],
                                        'upvotes': post_data['score'],
                                        'comments': post_data['num_comments'],
                                        'subreddit': post_data['subreddit'],
                                        'url': f"https://reddit.com{post_data['permalink']}",
                                        'trending_score': trending_score,
                                        'created': post_data.get('created_utc', 0),
                                        'author': post_data.get('author', 'unknown'),
                                        'awards': post_data.get('total_awards_received', 0)
                                    })
                    
                    time.sleep(0.5)
                except:
                    continue
            
            # Remove duplicates based on title similarity
            seen_titles = set()
            unique_trending = []
            for item in all_trending:
                # Simple deduplication - you could make this more sophisticated
                title_key = item['title'][:50].lower()
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    unique_trending.append(item)
            
            # Sort by trending score
            unique_trending.sort(key=lambda x: x['trending_score'], reverse=True)
            
            if unique_trending:
                st.success(f"Found {len(unique_trending)} trending cases across {len(subreddits)} subreddits")
                
                # Display trending cases
                for i, case in enumerate(unique_trending[:num_results], 1):
                    with st.container():
                        # Just show the title without any research button
                        st.markdown(f"**#{i}. {case['title']}**")
                        st.caption(f"r/{case['subreddit']} • by u/{case['author']}")
                        
                        # Metrics
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            st.metric("Upvotes", f"{case['upvotes']:,}")
                        
                        with col2:
                            st.metric("Comments", f"{case['comments']:,}")
                        
                        with col3:
                            st.metric("Awards", case['awards'])
                        
                        with col4:
                            st.metric("Trend Score", f"{case['trending_score']:,}")
                        
                        with col5:
                            st.markdown(f"[View on Reddit]({case['url']})")
                        
                        # Time posted
                        if case['created'] > 0:
                            from datetime import datetime
                            posted_time = datetime.fromtimestamp(case['created'])
                            st.caption(f"Posted: {posted_time.strftime('%Y-%m-%d %H:%M')}")
                        
                        st.divider()
                
                # Summary statistics
                st.markdown("### Trending Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_upvotes = sum(c['upvotes'] for c in unique_trending[:num_results]) / len(unique_trending[:num_results])
                    st.metric("Avg. Upvotes", f"{avg_upvotes:,.0f}")
                
                with col2:
                    total_comments = sum(c['comments'] for c in unique_trending[:num_results])
                    st.metric("Total Comments", f"{total_comments:,}")
                
                with col3:
                    # Most active subreddit
                    sub_counts = {}
                    for c in unique_trending[:num_results]:
                        sub_counts[c['subreddit']] = sub_counts.get(c['subreddit'], 0) + 1
                    most_active = max(sub_counts.items(), key=lambda x: x[1])
                    st.metric("Most Active Sub", f"r/{most_active[0]}")
                
            else:
                st.warning(f"No trending cases found with minimum {min_score} upvotes in the {time_range} time period")    

elif st.session_state.current_page == "True Crime Podcasts":
    st.markdown("### Trending True Crime Podcasts")
    
    # Authenticate with Spotify only when on this page
    if spotify_client_id and spotify_client_secret and spotify_client_id != "YOUR_SPOTIFY_CLIENT_ID_HERE":
        if 'spotify_token' not in st.session_state:
            with st.spinner("Authenticating with Spotify..."):
                token = get_spotify_token(spotify_client_id, spotify_client_secret)
                if token:
                    st.session_state.spotify_token = token
                else:
                    st.warning("Could not authenticate with Spotify. Topic search will be unavailable.")
    
    # Radio buttons for view selection
    podcast_view = st.radio(
        "View",
        ["Top Shows", "Latest Episodes", "Topic Search"],
        horizontal=True,
        key="podcast_view_type"
    )
    
    if podcast_view == "Top Shows":
        st.markdown("#### Top True Crime Podcast Shows")
        
        num_shows = st.slider("Number of shows to display", 10, 50, 25, key="num_shows")
        
        if st.button("Get Top True Crime Podcasts", type="primary", use_container_width=True, key="get_crime_podcasts"):
            with st.spinner("Fetching top true crime podcasts from Apple Podcasts..."):
                # Genre ID 1488 is True Crime
                podcasts = get_itunes_top_podcasts(1488, limit=num_shows)
                
                if podcasts:
                    st.success(f"Found {len(podcasts)} top true crime podcasts")
                    
                    for i, podcast in enumerate(podcasts, 1):
                        with st.expander(f"#{podcast['rank']:02d} | {podcast['name']}", expanded=(i <= 5)):
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                if podcast.get('image'):
                                    st.image(podcast['image'], width=150)
                            
                            with col2:
                                st.markdown(f"**Host/Network:** {podcast['artist']}")
                                st.markdown(f"**Description:** {podcast['summary']}")
                                st.markdown(f"**Latest Release:** {podcast.get('release_date', 'Unknown')}")
                                if podcast.get('url'):
                                    st.markdown(f"[Listen on Apple Podcasts]({podcast['url']})")
                            
                            st.divider()
                else:
                    st.warning("Could not fetch podcasts. Try again later.")
    
    elif podcast_view == "Latest Episodes":
        st.markdown("#### Latest True Crime Podcast Episodes")
        
        num_podcasts = st.number_input("Check top X podcasts for episodes", 5, 25, 10, key="num_podcasts_for_episodes")
        
        if st.button("Get Latest Episodes", type="primary", use_container_width=True, key="get_crime_episodes"):
            with st.spinner("Fetching latest true crime episodes..."):
                # Get top true crime podcasts
                podcasts = get_itunes_top_podcasts(1488, limit=num_podcasts)
                
                if podcasts:
                    all_episodes = []
                    
                    progress_bar = st.progress(0)
                    
                    for idx, podcast in enumerate(podcasts):
                        progress_bar.progress((idx + 1) / len(podcasts))
                        
                        if podcast.get('url'):
                            podcast_id = podcast['url'].split('/id')[-1].split('?')[0]
                            episodes = get_itunes_podcast_episodes(podcast_id, limit=2)  # Get 2 latest episodes
                            
                            for ep in episodes:
                                ep['podcast_name'] = podcast['name']
                                ep['podcast_artist'] = podcast['artist']
                                ep['podcast_rank'] = podcast['rank']
                                all_episodes.append(ep)
                        
                        time.sleep(0.1)  # Rate limiting
                    
                    progress_bar.empty()
                    
                    # Sort by podcast rank (maintains chart order)
                    all_episodes.sort(key=lambda x: x.get('podcast_rank', 999))
                    
                    if all_episodes:
                        st.success(f"Found {len(all_episodes)} recent episodes")
                        
                        for i, ep in enumerate(all_episodes[:30], 1):
                            with st.expander(f"{i:02d} | {ep['title'][:60]}... - {ep['podcast_name']}", expanded=(i <= 3)):
                                st.markdown(f"**Show:** {ep['podcast_name']}")
                                st.markdown(f"**Host:** {ep['podcast_artist']}")
                                st.markdown(f"**Published:** {ep.get('published', 'Unknown')}")
                                st.markdown(f"**Duration:** {ep.get('duration', 'Unknown')}")
                                st.markdown(f"**Description:** {ep.get('description', 'No description')}")
                                if ep.get('link'):
                                    st.markdown(f"[Listen to Episode]({ep['link']})")
                                st.divider()
                    else:
                        st.info("No recent episodes found")
                else:
                    st.warning("Could not fetch podcast data")
    
    else:  # Topic Search
        st.markdown("#### Search True Crime Podcasts by Topic")
        
        # Only if Spotify is configured
        if 'spotify_token' in st.session_state:
            search_query = st.text_input(
                "Search for a topic, case, or keyword",
                placeholder="e.g., 'Ted Bundy', 'cold case', 'missing persons'",
                key="podcast_topic_search"
            )
            
            if st.button("Search Episodes", type="primary", use_container_width=True, key="search_podcast_episodes") and search_query:
                with st.spinner(f"Searching for episodes about '{search_query}'..."):
                    episodes = search_podcasts_by_topic(st.session_state.spotify_token, search_query, limit=20)
                    
                    if episodes:
                        st.success(f"Found {len(episodes)} episodes about '{search_query}'")
                        
                        for i, ep in enumerate(episodes, 1):
                            display_title = f"{ep['name']}"
                            if ep.get('show_name') and ep['show_name'] != 'Loading...':
                                display_title += f" - {ep['show_name']}"
                            
                            with st.expander(f"{i:02d} | {display_title[:80]}...", expanded=(i <= 3)):
                                if ep.get('image'):
                                    st.image(ep['image'], width=200)
                                
                                st.markdown(f"**Show:** {ep.get('show_name', 'Unknown')}")
                                st.markdown(f"**Released:** {ep.get('release_date', 'Unknown')}")
                                st.markdown(f"**Duration:** {ep.get('duration_min', 'Unknown')} minutes")
                                st.markdown(f"**Description:** {ep.get('description', 'No description')}")
                                if ep.get('url'):
                                    st.markdown(f"[Listen on Spotify]({ep['url']})")
                                st.divider()
                    else:
                        st.warning(f"No episodes found for '{search_query}'")
        else:
            st.info("Configure Spotify API to search episodes by topic")
            st.markdown("This feature requires Spotify API credentials")

elif st.session_state.current_page == "YouTube Competitors":    
    st.markdown("### YouTube Competitor Monitoring")
    st.markdown("Data provided by YouTube API Services")
    st.caption("YouTube data is fetched live and not stored. Data freshness depends on YouTube API.")
    
    # Add rate limit status indicator
    if st.session_state.get('youtube_rate_limited', False):
        st.error("""
        🚫 **YouTube API Rate Limited**
        
        You've reached the YouTube API quota limit. The quota resets daily at midnight Pacific Time.
        Some features may not work until the quota resets.
        """)
        # Reset the flag after showing
        if st.button("Clear this message"):
            st.session_state.youtube_rate_limited = False
            st.rerun()

    # Define competitors with their channel IDs
    COMPETITORS = {
        "Danielle Kirsty": "UC7QBeubzVIOqFjUjd_gNEBQ",
        "Kendall Rae": "UCKBaL17hXLGJvi2KZKpja5w",
        "Rotten Mango": "UC0JJtK3m8pwy6rVgnBz47Rw",
        "Eleanor Neale": "UCFMbX7frWZfuWdjAML0babA",
        "Hailey Elizabeth": "UCdeGMtF2xelP7Od2ofdP0qg",
        "Stephanie Soo": "UCo9ZZ04kIhN_8xGxvnjaduQ",
        "Bella Fiori": "UCaezsZGhwWgB4ZRmHNCfIyw",
        "Annie Elise": "UCOK0fZAUx82plnLhTKZW6qg",
        "Mile Higher": "UCiaxrqSxVoGxGKg7Ayd4Q9A",
        "Charlotte Dobre": "UCwc_RHwAPPaEh-jtwClpVrg"
    }
    
    # Search or Browse mode
    mode = st.radio(
        "Mode",
        ["Browse Recent", "Search Topics"],
        horizontal=True,
        key="competitor_mode"
    )
    
    if mode == "Browse Recent":
        # Options for browsing
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_competitors = st.multiselect(
                "Select Competitors",
                options=list(COMPETITORS.keys()),
                default=list(COMPETITORS.keys())[:5],
                key="competitor_select"
            )
        
        with col2:
            time_period = st.selectbox(
                "Time Period",
                ["Last 24 Hours", "Last Week", "Last Month", "Last 3 Months", "Last 6 Months", "Last Year"],
                index=1,  # Default to Last Week
                key="competitor_time_period"
            )
        
        with col3:
            videos_per_channel = st.number_input(
                "Videos per channel",
                min_value=3,
                max_value=20,
                value=5,
                key="videos_per_competitor"
            )
        
        if st.button("Get Competitor Videos", type="primary", use_container_width=True, key="get_competitor_videos"):
            if not youtube_api_key:
                st.error("YouTube API key not configured")
            elif not selected_competitors:
                st.warning("Please select at least one competitor")
            else:
                with st.spinner(f"Fetching videos from {len(selected_competitors)} channels..."):
                    # Calculate date filter
                    from datetime import datetime, timedelta
                    
                    if time_period == "Last 24 Hours":
                        published_after = (datetime.now() - timedelta(days=1)).isoformat() + 'Z'
                    elif time_period == "Last Week":
                        published_after = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
                    elif time_period == "Last Month":
                        published_after = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                    elif time_period == "Last 3 Months":
                        published_after = (datetime.now() - timedelta(days=90)).isoformat() + 'Z'
                    elif time_period == "Last 6 Months":
                        published_after = (datetime.now() - timedelta(days=180)).isoformat() + 'Z'
                    elif time_period == "Last Year":
                        published_after = (datetime.now() - timedelta(days=365)).isoformat() + 'Z'
                    
                    all_videos = []
                    progress_bar = st.progress(0)
                    
                    for idx, channel_name in enumerate(selected_competitors):
                        progress_bar.progress((idx + 1) / len(selected_competitors))
                        channel_id = COMPETITORS[channel_name]
                        
                        try:
                            # Search for videos from this channel
                            search_url = "https://www.googleapis.com/youtube/v3/search"
                            params = {
                                "key": youtube_api_key,
                                "channelId": channel_id,
                                "part": "snippet",
                                "order": "viewCount",  # Order by views from the start
                                "type": "video",
                                "maxResults": videos_per_channel,
                                "publishedAfter": published_after
                            }
                            
                            response = requests.get(search_url, params=params, timeout=10)
                            
                            if response.status_code == 200:
                                data = response.json()
                                
                                # Get video IDs for detailed stats
                                video_ids = [item['id']['videoId'] for item in data.get('items', [])]
                                
                                if video_ids:
                                    # Get detailed video information
                                    details_url = "https://www.googleapis.com/youtube/v3/videos"
                                    details_params = {
                                        "key": youtube_api_key,
                                        "id": ",".join(video_ids),
                                        "part": "snippet,statistics,contentDetails"
                                    }
                                    
                                    details_response = requests.get(details_url, params=details_params, timeout=10)
                                    
                                    if details_response.status_code == 200:
                                        details_data = details_response.json()
                                        
                                        for video in details_data.get('items', []):
                                            # Parse duration
                                            duration_str = video['contentDetails']['duration']
                                            import re
                                            match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
                                            if match:
                                                hours = int(match.group(1) or 0)
                                                minutes = int(match.group(2) or 0)
                                                seconds = int(match.group(3) or 0)
                                                total_seconds = hours * 3600 + minutes * 60 + seconds
                                            else:
                                                total_seconds = 0
                                            
                                            video_info = {
                                                'channel_name': channel_name,
                                                'title': video['snippet']['title'],
                                                'video_id': video['id'],
                                                'published': video['snippet']['publishedAt'],
                                                'views': int(video['statistics'].get('viewCount', 0)),
                                                'likes': int(video['statistics'].get('likeCount', 0)),
                                                'comments': int(video['statistics'].get('commentCount', 0)),
                                                'duration_seconds': total_seconds,
                                                'thumbnail': video['snippet']['thumbnails']['medium']['url'],
                                                'description': video['snippet'].get('description', '')
                                            }
                                            
                                            all_videos.append(video_info)
                            
                            time.sleep(0.2)  # Rate limiting
                            
                        except Exception as e:
                            st.warning(f"Error fetching {channel_name}: {str(e)}")
                            continue
                    
                    progress_bar.empty()
                    
                    if all_videos:
                        # Always sort by views (already ordered by API, but sort combined results)
                        all_videos.sort(key=lambda x: x['views'], reverse=True)
                        
                        st.success(f"Found {len(all_videos)} videos from {len(selected_competitors)} channels (sorted by views)")
                        st.markdown("Data provided by YouTube API Services")  # ADD HERE
                        st.caption("YouTube data is fetched live and not stored. Data freshness depends on YouTube API.")

                        
                        # Display results
                        for i, video in enumerate(all_videos, 1):
                            # Determine if it's a short
                            is_short = video['duration_seconds'] <= 180
                            video_type = "SHORT" if is_short else "VIDEO"
                            
                            # Format views for display
                            if video['views'] >= 1000000:
                                views_display = f"{video['views']/1000000:.1f}M views"
                            elif video['views'] >= 1000:
                                views_display = f"{video['views']/1000:.0f}K views"
                            else:
                                views_display = f"{video['views']} views"
                            
                            with st.expander(f"{i:02d} | {views_display} - {video['title'][:50]}... ({video['channel_name']}) [{video_type}]", expanded=(i <= 3)):
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    st.image(video['thumbnail'], use_column_width=True)
                                    
                                    # Format publish date
                                    try:
                                        from datetime import datetime
                                        pub_date = datetime.strptime(video['published'][:10], '%Y-%m-%d')
                                        formatted_date = pub_date.strftime('%m/%d/%y')
                                    except:
                                        formatted_date = video['published'][:10]
                                    
                                    st.caption(f"Published: {formatted_date}")
                                
                                with col2:
                                    st.markdown(f"**Channel:** {video['channel_name']}")
                                    st.markdown(f"**Title:** {video['title']}")
                                    
                                    # Metrics
                                    col_a, col_b, col_c = st.columns(3)
                                    with col_a:
                                        st.metric("Views", views_display)
                                    
                                    with col_b:
                                        if video['likes'] >= 1000:
                                            likes_str = f"{video['likes']/1000:.0f}K"
                                        else:
                                            likes_str = str(video['likes'])
                                        st.metric("Likes", likes_str)

                                    with col_c:
                                        st.metric("Comments", video['comments'])

                                    # Duration
                                    if is_short:
                                        st.caption(f"Duration: {video['duration_seconds']} seconds (Short)")
                                    else:
                                        minutes = video['duration_seconds'] // 60
                                        seconds = video['duration_seconds'] % 60
                                        st.caption(f"Duration: {minutes}:{seconds:02d}")
                                    
                                    # Description preview
                                    if video['description']:
                                        st.markdown("**Description:**")
                                        st.text(video['description'][:500] + "..." if len(video['description']) > 500 else video['description'])

                                    # Link to video
                                    st.markdown(f"[Watch on YouTube](https://youtube.com/watch?v={video['video_id']})")
                                
                                st.divider()
                    else:
                        st.warning("No videos found from selected competitors in this time period")
    
    else:  # Search Topics mode
        st.markdown("#### Search Competitor Videos by Topic")
        
        # Search interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "Search for a case, topic, or keyword",
                placeholder="e.g., 'JonBenet Ramsey', 'Idaho murders', 'cold case'",
                key="competitor_search_query"
            )
        
        with col2:
            search_channels = st.multiselect(
                "Search in channels",
                options=list(COMPETITORS.keys()),
                default=list(COMPETITORS.keys()),
                key="search_channels"
            )
        
        if st.button("Search Competitor Content", type="primary", use_container_width=True, key="search_competitor_content") and search_query:
            if not youtube_api_key:
                st.error("YouTube API key not configured")
            elif not search_channels:
                st.warning("Please select at least one channel to search")
            else:
                with st.spinner(f"Searching for '{search_query}' across {len(search_channels)} channels..."):
                    search_results = []
                    progress_bar = st.progress(0)
                    
                    for idx, channel_name in enumerate(search_channels):
                        progress_bar.progress((idx + 1) / len(search_channels))
                        channel_id = COMPETITORS[channel_name]
                        
                        try:
                            # Search within specific channel
                            search_url = "https://www.googleapis.com/youtube/v3/search"
                            params = {
                                "key": youtube_api_key,
                                "channelId": channel_id,
                                "q": search_query,
                                "part": "snippet",
                                "type": "video",
                                "maxResults": 10,
                                "order": "viewCount"  # Order by views
                            }
                            
                            response = requests.get(search_url, params=params, timeout=10)
                            
                            if response.status_code == 200:
                                data = response.json()
                                
                                # Get video IDs for detailed stats
                                video_ids = [item['id']['videoId'] for item in data.get('items', [])]
                                
                                if video_ids:
                                    # Get detailed video information
                                    details_url = "https://www.googleapis.com/youtube/v3/videos"
                                    details_params = {
                                        "key": youtube_api_key,
                                        "id": ",".join(video_ids),
                                        "part": "snippet,statistics,contentDetails"
                                    }
                                    
                                    details_response = requests.get(details_url, params=details_params, timeout=10)
                                    
                                    if details_response.status_code == 200:
                                        details_data = details_response.json()
                                        
                                        for video in details_data.get('items', []):
                                            # Check if search term is in title or description
                                            title = video['snippet']['title'].lower()
                                            description = video['snippet'].get('description', '').lower()
                                            search_lower = search_query.lower()
                                            
                                            if search_lower in title or search_lower in description:
                                                # Parse duration
                                                duration_str = video['contentDetails']['duration']
                                                import re
                                                match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
                                                if match:
                                                    hours = int(match.group(1) or 0)
                                                    minutes = int(match.group(2) or 0)
                                                    seconds = int(match.group(3) or 0)
                                                    total_seconds = hours * 3600 + minutes * 60 + seconds
                                                else:
                                                    total_seconds = 0
                                                
                                                video_info = {
                                                    'channel_name': channel_name,
                                                    'title': video['snippet']['title'],
                                                    'video_id': video['id'],
                                                    'published': video['snippet']['publishedAt'],
                                                    'views': int(video['statistics'].get('viewCount', 0)),
                                                    'likes': int(video['statistics'].get('likeCount', 0)),
                                                    'comments': int(video['statistics'].get('commentCount', 0)),
                                                    'duration_seconds': total_seconds,
                                                    'thumbnail': video['snippet']['thumbnails']['medium']['url'],
                                                    'description': video['snippet'].get('description', ''),
                                                    'relevance': 'title' if search_lower in title else 'description'
                                                }
                                                
                                                search_results.append(video_info)
                            
                            time.sleep(0.2)  # Rate limiting
                            
                        except Exception as e:
                            continue
                    
                    progress_bar.empty()
                    
                    if search_results:
                        # Sort by views
                        search_results.sort(key=lambda x: x['views'], reverse=True)
                        
                        st.success(f"Found {len(search_results)} videos about '{search_query}'")
                        st.markdown("Data provided by YouTube API Services")  # ADD HERE
                        st.caption("YouTube data is fetched live and not stored. Data freshness depends on YouTube API.")

                        
                        # Display search results
                        for i, video in enumerate(search_results, 1):
                            # Format views for display
                            if video['views'] >= 1000000:
                                views_display = f"{video['views']/1000000:.1f}M views"
                            elif video['views'] >= 1000:
                                views_display = f"{video['views']/1000:.0f}K views"
                            else:
                                views_display = f"{video['views']} views"
                            
                            # Indicate where match was found
                            match_indicator = "TITLE MATCH" if video['relevance'] == 'title' else "DESCRIPTION MATCH"
                            
                            with st.expander(f"{i:02d} | {views_display} - {video['title'][:50]}... ({video['channel_name']}) [{match_indicator}]", expanded=(i <= 3)):
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    st.image(video['thumbnail'], use_column_width=True)
                                    
                                    # Format publish date
                                    try:
                                        from datetime import datetime
                                        pub_date = datetime.strptime(video['published'][:10], '%Y-%m-%d')
                                        formatted_date = pub_date.strftime('%m/%d/%y')
                                    except:
                                        formatted_date = video['published'][:10]
                                    
                                    st.caption(f"Published: {formatted_date}")
                                
                                with col2:
                                    st.markdown(f"**Channel:** {video['channel_name']}")
                                    st.markdown(f"**Title:** {video['title']}")
                                    
                                    # Highlight where search term was found
                                    if video['relevance'] == 'title':
                                        st.success(f"Search term found in TITLE")
                                    else:
                                        st.info(f"Search term found in DESCRIPTION")
                                    
                                    # Metrics
                                    col_a, col_b, col_c = st.columns(3)
                                    with col_a:
                                        st.metric("Views", views_display)
                                    with col_b:
                                        st.metric("Likes", likes_str)
                                    with col_c:
                                        st.metric("Comments", str(video['comments']))
                                    
                                    # Show relevant part of description
                                    if video['description']:
                                        st.markdown("**Description:**")
                                        # Highlight search term in description
                                        desc_lower = video['description'].lower()
                                        search_lower = search_query.lower()
                                        if search_lower in desc_lower:
                                            # Find position of search term
                                            pos = desc_lower.find(search_lower)
                                            start = max(0, pos - 100)
                                            end = min(len(video['description']), pos + 200)
                                            excerpt = video['description'][start:end]
                                            st.text(f"...{excerpt}...")
                                        else:
                                            st.text(video['description'][:500] + "..." if len(video['description']) > 500 else video['description'])
                                    
                                    st.markdown(f"[Watch on YouTube](https://youtube.com/watch?v={video['video_id']})")
                                
                                st.divider()
                    else:
                        st.warning(f"No videos found about '{search_query}' from selected competitors")
                        
elif st.session_state.current_page == "Movies & TV Shows":    
    # st.markdown("### Movies & TV Shows")
    
    if not tmdb_key:
        st.error("TMDB API key not configured")
        st.stop()
    
    # Navigation tabs
    movie_tab1, movie_tab2 = st.tabs(["DISCOVER TRENDS", "SEARCH TITLES"])
    
    with movie_tab1:
        st.markdown("### Discover Trending Movies & Shows")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            media_type = st.selectbox(
                "Media Type",
                ["movie", "tv"],
                format_func=lambda x: "Movies" if x == "movie" else "TV Shows", 
                key="crime_media_type_discover"
            )
        
        with col2:
            # Get genres for selected media type
            genres = get_tmdb_genres(tmdb_key, media_type)
            genre_options = [(str(gid), gname) for gid, gname in genres.items()]
            
            # Find the crime and documentary genre IDs
            crime_genres = []
            doc_genres = []
            for gid, gname in genres.items():
                if 'Crime' in gname:
                    crime_genres.append(str(gid))
                if 'Documentary' in gname:
                    doc_genres.append(str(gid))
            
            # Default selection includes Crime and Documentary
            default_genres = crime_genres + doc_genres
            
            selected_genres = st.multiselect(
                "Genres (select multiple)",
                options=[g[0] for g in genre_options],
                format_func=lambda x: dict(genre_options).get(x, x),
                default=default_genres,  # Pre-select Crime and Documentary
                key="crime_genre_multiselect",
                placeholder="Select genres or leave empty for all"
            )
        
        with col3:
            sort_options = [
                ("popularity.desc", "Most Popular"),
                ("vote_average.desc", "Highest Rated"),
                ("vote_count.desc", "Most Voted"),
                ("release_date.desc", "Newest First"),
                ("revenue.desc", "Highest Revenue")
            ]
            
            sort_by = st.selectbox(
                "Sort By",
                options=[s[0] for s in sort_options],
                format_func=lambda x: dict(sort_options).get(x, x),
                key="crime_sort_select"
            )
        
        # Optional year filter
        col1, col2 = st.columns([1, 2])
        with col1:
            use_year_filter = st.checkbox("Filter by year", key="use_year_crime_discover")
            if use_year_filter:
                year_filter = st.number_input(
                    "Year",
                    min_value=1900,
                    max_value=datetime.now().year + 1,
                    value=datetime.now().year, 
                    key="crime_year_filter"
                )
            else:
                year_filter = None
        
        if st.button("GET TRENDING", key="get_crime_trending", type="primary"):
            with st.spinner(f"Fetching trending {media_type}s..."):
                # Join multiple genre IDs with comma for TMDB API
                genre_ids = ','.join(selected_genres) if selected_genres else None
                year = year_filter if use_year_filter else None
                
                results = search_tmdb(tmdb_key, media_type=media_type, genre_id=genre_ids, 
                                    year=year, sort_by=sort_by)
                
                if results and results.get('results'):
                    st.session_state.crime_trending_results = results['results']
                    st.success(f"Found {len(results['results'])} trending {media_type}s")
        
        # Display results
        if 'crime_trending_results' in st.session_state:
            for i, item in enumerate(st.session_state.crime_trending_results[:20], 1):
                title = item.get('title') or item.get('name', 'Unknown')
                release_date = item.get('release_date') or item.get('first_air_date', 'Unknown')
                
                with st.expander(f"{i:02d} | {title} ({release_date[:4] if release_date != 'Unknown' else 'N/A'})", expanded=False):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if item.get('poster_path'):
                            poster_url = f"https://image.tmdb.org/t/p/w200{item['poster_path']}"
                            st.image(poster_url, width=150)
                    
                    with col2:
                        # Metrics
                        st.markdown(f"""
                        <div style="display: flex; gap: 2rem; margin-bottom: 1rem;">
                            <div>
                                <p style="font-size: 24px; font-weight: 800; color: #DC143C; margin: 0;">{item.get('vote_average', 0):.1f}</p>
                                <p style="font-size: 12px; text-transform: uppercase; color: #666;">Rating</p>
                            </div>
                            <div>
                                <p style="font-size: 24px; font-weight: 800; color: #DC143C; margin: 0;">{item.get('vote_count', 0):,}</p>
                                <p style="font-size: 12px; text-transform: uppercase; color: #666;">Votes</p>
                            </div>
                            <div>
                                <p style="font-size: 24px; font-weight: 800; color: #DC143C; margin: 0;">{item.get('popularity', 0):.0f}</p>
                                <p style="font-size: 12px; text-transform: uppercase; color: #666;">Popularity</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.write(f"**Overview:** {item.get('overview', 'No overview available.')}")
                        
                        # Get genre names
                        genre_names = [genres.get(gid, 'Unknown') for gid in item.get('genre_ids', [])]
                        if genre_names:
                            st.write(f"**Genres:** {', '.join(genre_names)}")
                        
                        # TMDB link
                        media_type_for_url = "movie" if 'title' in item else "tv"
                        tmdb_url = f"https://www.themoviedb.org/{media_type_for_url}/{item.get('id')}"
                        st.markdown(f"[View on TMDB]({tmdb_url})")
    
    with movie_tab2:
        st.markdown("### Search Movies & TV Shows")
        
        search_query = st.text_input(
            "Search by Title/Keyword",
            placeholder="e.g., 'murder', 'serial killer', 'true crime'",
            key="crime_title_search"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_media_type = st.selectbox(
                "Media Type",
                ["movie", "tv"],
                format_func=lambda x: "Movies" if x == "movie" else "TV Shows",
                key="crime_media_type_search"
            )
        
        with col2:
            use_search_year = st.checkbox("Filter by year", key="use_year_crime_search")
            if use_search_year:
                search_year = st.number_input(
                    "Year",
                    min_value=1900,
                    max_value=datetime.now().year + 1,
                    value=datetime.now().year,
                    key="crime_search_year"
                )
            else:
                search_year = None
        
        if st.button("SEARCH", key="search_crime_titles", type="primary") and search_query:
            with st.spinner(f"Searching for '{search_query}'..."):
                # First do the search
                results = search_tmdb(tmdb_key, query=search_query, media_type=search_media_type, year=search_year)
                
                if results and results.get('results'):
                    # Store raw results for sorting
                    st.session_state.crime_search_results_raw = results['results']
                    st.session_state.crime_search_query_used = search_query
                    st.session_state.crime_search_media_type_used = search_media_type
                    st.success(f"Found {len(results['results'])} results for '{search_query}'")
                else:
                    st.warning("No results found. Try different keywords.")
    
    # If we have search results, show sorting options
    if 'crime_search_results_raw' in st.session_state and st.session_state.crime_search_results_raw:
        st.markdown("---")
        st.markdown(f"**Results for: '{st.session_state.crime_search_query_used}'**")
        
        # Sorting options
        sort_options = [
            ("popularity", "Most Popular"),
            ("vote_average", "Highest Rated"),
            ("vote_count", "Most Voted"),
            ("release_date", "Newest First"),
            ("title", "Alphabetical")
        ]
        
        sort_by = st.selectbox(
            "Sort Results By",
            options=[s[0] for s in sort_options],
            format_func=lambda x: dict(sort_options).get(x, x),
            key="crime_search_sort"
        )
        
        # Sort the results
        sorted_results = sorted(
            st.session_state.crime_search_results_raw,
            key=lambda x: x.get(sort_by, 0) if sort_by != 'title' else (x.get('title') or x.get('name', '')),
            reverse=(sort_by != 'title')
        )
        
        # Get genres for the selected media type
        genres = get_tmdb_genres(tmdb_key, st.session_state.crime_search_media_type_used)
        
        # Display sorted results
        for i, item in enumerate(sorted_results[:20], 1):
            title = item.get('title') or item.get('name', 'Unknown')
            release_date = item.get('release_date') or item.get('first_air_date', 'Unknown')
            
            with st.expander(f"{i:02d} | {title} ({release_date[:4] if release_date != 'Unknown' and len(release_date) >= 4 else 'N/A'})", expanded=False):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if item.get('poster_path'):
                        poster_url = f"https://image.tmdb.org/t/p/w200{item['poster_path']}"
                        st.image(poster_url, width=150)
                
                with col2:
                    # Metrics
                    st.markdown(f"""
                    <div style="display: flex; gap: 2rem; margin-bottom: 1rem;">
                        <div>
                            <p style="font-size: 24px; font-weight: 800; color: #DC143C; margin: 0;">{item.get('vote_average', 0):.1f}</p>
                            <p style="font-size: 12px; text-transform: uppercase; color: #666;">Rating</p>
                        </div>
                        <div>
                            <p style="font-size: 24px; font-weight: 800; color: #DC143C; margin: 0;">{item.get('vote_count', 0):,}</p>
                            <p style="font-size: 12px; text-transform: uppercase; color: #666;">Votes</p>
                        </div>
                        <div>
                            <p style="font-size: 24px; font-weight: 800; color: #DC143C; margin: 0;">{item.get('popularity', 0):.0f}</p>
                            <p style="font-size: 12px; text-transform: uppercase; color: #666;">Popularity</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write(f"**Overview:** {item.get('overview', 'No overview available.')}")
                    
                    # Get genre names
                    genre_names = [genres.get(gid, 'Unknown') for gid in item.get('genre_ids', [])]
                    if genre_names:
                        st.write(f"**Genres:** {', '.join(genre_names)}")
                    
                    # TMDB link
                    media_type_for_url = "movie" if 'title' in item else "tv"
                    tmdb_url = f"https://www.themoviedb.org/{media_type_for_url}/{item.get('id')}"
                    st.markdown(f"[View on TMDB]({tmdb_url})")


elif st.session_state.current_page == "Court Documents":
    st.markdown("### Court Documents Search")
    st.caption("Search federal court records and legal documents")
    
    # Search input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        court_search = st.text_input(
            "Search for a person or case",
            placeholder="e.g., 'Bryan Kohberger', 'State v. Smith', 'United States v. Jones'",
            key="court_search_input"
        )
    
    with col2:
        search_button = st.button("SEARCH COURTS", type="primary", use_container_width=True, key="search_courts_btn")
    
    # Get CourtListener API token
    courtlistener_token = os.getenv("COURTLISTENER_API_TOKEN", "")
    
    if not courtlistener_token:
        st.warning("""
        **CourtListener API Required**
        
        To search court documents:
        1. Sign up at [courtlistener.com](https://www.courtlistener.com)
        2. Get your API token from account settings
        3. Add to environment: COURTLISTENER_API_TOKEN
        """)
        
        # Provide direct search links even without API
        if court_search:
            st.markdown("### Search Without API:")
            
            search_links = [
                ('CourtListener', f'https://www.courtlistener.com/?q={court_search.replace(" ", "+")}&type=r'),
                ('Google Scholar', f'https://scholar.google.com/scholar?q={court_search.replace(" ", "+")}+court+case'),
                ('Justia', f'https://law.justia.com/search/?q={court_search.replace(" ", "+")}'),
                ('FindLaw', f'https://caselaw.findlaw.com/search.html?q={court_search.replace(" ", "+")}')
            ]
            
            cols = st.columns(len(search_links))
            for idx, (name, url) in enumerate(search_links):
                with cols[idx]:
                    st.markdown(f"[{name}]({url})")
    
    elif search_button and court_search:
        # Store search in session state
        st.session_state.court_search_query = court_search
        st.session_state.court_search_performed = True
    
    # Display results if search was performed
    if st.session_state.get('court_search_performed', False) and courtlistener_token:
        search_query = st.session_state.get('court_search_query', '')
        
        if search_query:
            with st.spinner("Searching court databases..."):
                court_results = search_courtlistener_cases(search_query, courtlistener_token)
            
            if court_results:
                if court_results.get('no_results_message'):
                    st.warning(court_results['no_results_message'])
                
                else:
                    # Display results in tabs
                    tab1, tab2, tab3 = st.tabs(["Court Opinions", "Federal Cases", "How to Access"])
                    
                    with tab1:
                        if court_results.get('opinions'):
                            st.success(f"Found {len(court_results['opinions'])} court opinions")
                            
                            for i, opinion in enumerate(court_results['opinions'], 1):
                                with st.expander(f"{i}. {opinion['case_name'][:80]}...", expanded=(i <= 2)):
                                    col1, col2 = st.columns([3, 1])
                                    
                                    with col1:
                                        st.markdown(f"**Case:** {opinion['case_name']}")
                                        st.markdown(f"**Court:** {opinion.get('court', 'Unknown')}")
                                        st.markdown(f"**Date:** {opinion.get('date_filed', 'Unknown')}")
                                        
                                        if opinion.get('judge'):
                                            st.markdown(f"**Judge:** {opinion['judge']}")
                                        
                                        if opinion.get('summary'):
                                            st.markdown("**Summary:**")
                                            st.write(opinion['summary'][:500] + "..." if len(opinion.get('summary', '')) > 500 else opinion.get('summary', ''))
                                    
                                    with col2:
                                        if opinion.get('url'):
                                            st.markdown(f"[View Full Opinion]({opinion['url']})")
                        else:
                            st.info("No court opinions found")
                    
                    with tab2:
                        if court_results.get('dockets'):
                            st.success(f"Found {len(court_results['dockets'])} federal cases")
                            
                            for i, docket in enumerate(court_results['dockets'][:10], 1):
                                with st.expander(f"{i}. {docket['case_name'][:80]}...", expanded=(i <= 2)):
                                    col1, col2 = st.columns([3, 1])
                                    
                                    with col1:
                                        st.markdown(f"**Case:** {docket['case_name']}")
                                        st.markdown(f"**Court:** {docket.get('court', 'Unknown').upper()}")
                                        st.markdown(f"**Docket #:** {docket.get('docket_number', 'Unknown')}")
                                        
                                        if docket.get('date_filed'):
                                            st.markdown(f"**Filed:** {docket['date_filed']}")
                                        
                                        if docket.get('nature_of_suit'):
                                            st.markdown(f"**Type:** {docket['nature_of_suit']}")
                                        
                                        if docket.get('assigned_to'):
                                            st.markdown(f"**Judge:** {docket['assigned_to']}")
                                    
                                    with col2:
                                        if docket.get('url'):
                                            st.markdown(f"[View Docket]({docket['url']})")
                        else:
                            st.info("No federal cases found")
                    
                    with tab3:
                        st.markdown("""
                        ### Accessing Court Documents
                        
                        **Free Resources:**
                        - **CourtListener** - Free RECAP archive
                        - **Google Scholar** - Legal opinions and citations
                        - **Justia** - Free case law database
                        - **State Courts** - Many states offer free online access
                        
                        **Paid Resources:**
                        - **PACER** - $0.10/page (max $3/document)
                        - **Westlaw/LexisNexis** - Professional legal databases
                        
                        **Tips for Bailey's Research:**
                        - Search by defendant's last name + "murder" or "homicide"
                        - Try "State v. [LastName]" or "United States v. [LastName]"
                        - Check both federal and state databases
                        - Look for appellate opinions (often more detailed)
                        """)
                        
                        # Save to ideas button
                        if court_results.get('dockets') or court_results.get('opinions'):
                            if st.button("Save Results to Ideas", type="primary"):
                                if 'saved_ideas' not in st.session_state:
                                    st.session_state.saved_ideas = []
                                
                                summary = f"Court search for: {search_query}\n"
                                summary += f"Found {len(court_results.get('dockets', []))} cases, "
                                summary += f"{len(court_results.get('opinions', []))} opinions"
                                
                                new_idea = {
                                    'id': len(st.session_state.saved_ideas) + 1,
                                    'title': f"{search_query} - Court Docs",
                                    'notes': summary,
                                    'priority': 'Medium',
                                    'saved_date': datetime.now().strftime('%m/%d/%y'),
                                    'status': 'New'
                                }
                                st.session_state.saved_ideas.append(new_idea)
                                st.success("Saved to ideas!")
    
    # Quick search suggestions
    if not st.session_state.get('court_search_performed', False):
        st.markdown("### Quick Searches")
        
        quick_searches = [
            "Bryan Kohberger",
            "Alex Murdaugh", 
            "Chad Daybell",
            "Lori Vallow",
            "Sarah Boone",
            "Letecia Stauch"
        ]
        
        cols = st.columns(3)
        for idx, name in enumerate(quick_searches):
            with cols[idx % 3]:
                if st.button(name, key=f"quick_{name}"):
                    st.session_state.court_search_query = name
                    st.session_state.court_search_performed = True
                    st.rerun()

            
elif st.session_state.current_page == "Saved Ideas":
    st.markdown("""
    <h3 style="font-family: 'Crimson Text', serif; font-weight: 700;">SAVED IDEAS</h3>
    """, unsafe_allow_html=True)
    
    # Initialize saved ideas in session state if not exists
    if 'saved_ideas' not in st.session_state:
        st.session_state.saved_ideas = []
    
    # Add new idea form
    with st.expander("➕ Add New Idea", expanded=False):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_idea_title = st.text_input("Case/Topic", placeholder="e.g., 'The Vanishing of Susan Cox Powell'")
            new_idea_notes = st.text_area("Notes", placeholder="Key details, sources, unique angles...")
        
        with col2:
            new_idea_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            new_idea_status = st.selectbox("Status", ["New", "Researching", "Ready", "In Production", "Complete"])
        
        if st.button("Save Idea", type="primary"):
            if new_idea_title:
                new_idea = {
                    'id': len(st.session_state.saved_ideas) + 1,
                    'title': new_idea_title,
                    'notes': new_idea_notes,
                    'priority': new_idea_priority,
                    'status': new_idea_status,
                    'saved_date': datetime.now().strftime('%m/%d/%y'),
                    'last_updated': datetime.now().strftime('%m/%d/%y')
                }
                st.session_state.saved_ideas.append(new_idea)
                st.success(f"Added '{new_idea_title}' to ideas!")
                st.rerun()
            else:
                st.error("Please enter a title")
    
    # Filter and sort options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.selectbox("Filter by Status", ["All", "New", "Researching", "Ready", "In Production", "Complete"])
    
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Date Added (Newest)", "Date Added (Oldest)", "Priority", "Title"])
    
    # Filter ideas
    filtered_ideas = st.session_state.saved_ideas.copy()
    
    if filter_status != "All":
        filtered_ideas = [idea for idea in filtered_ideas if idea['status'] == filter_status]
    
    if filter_priority != "All":
        filtered_ideas = [idea for idea in filtered_ideas if idea['priority'] == filter_priority]
    
    # Sort ideas
    if sort_by == "Date Added (Newest)":
        filtered_ideas.sort(key=lambda x: x['id'], reverse=True)
    elif sort_by == "Date Added (Oldest)":
        filtered_ideas.sort(key=lambda x: x['id'])
    elif sort_by == "Priority":
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        filtered_ideas.sort(key=lambda x: priority_order[x['priority']])
    elif sort_by == "Title":
        filtered_ideas.sort(key=lambda x: x['title'])
    
    # Display ideas
    if filtered_ideas:
        st.markdown(f"**Showing {len(filtered_ideas)} ideas**")
        
        for idea in filtered_ideas:
            # Color coding for priority
            priority_colors = {
                "High": "#DC143C",
                "Medium": "#FFA500",
                "Low": "#808080"
            }
            
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"### {idea['title']}")
                    if idea['notes']:
                        st.write(idea['notes'])
                
                with col2:
                    st.markdown(f"**Priority:** <span style='color: {priority_colors[idea['priority']]}'>{idea['priority']}</span>", unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"**Status:** {idea['status']}")
                
                with col4:
                    st.caption(f"Added: {idea['saved_date']}")
                    
                    # Action buttons
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("📝", key=f"edit_{idea['id']}", help="Edit"):
                            st.session_state[f"editing_{idea['id']}"] = True
                    
                    with col_b:
                        if st.button("🗑️", key=f"delete_{idea['id']}", help="Delete"):
                            st.session_state.saved_ideas = [i for i in st.session_state.saved_ideas if i['id'] != idea['id']]
                            st.rerun()
                
                # Edit mode
                if st.session_state.get(f"editing_{idea['id']}", False):
                    with st.expander("Edit Idea", expanded=True):
                        edited_title = st.text_input("Title", value=idea['title'], key=f"edit_title_{idea['id']}")
                        edited_notes = st.text_area("Notes", value=idea['notes'], key=f"edit_notes_{idea['id']}")
                        edited_priority = st.selectbox("Priority", ["High", "Medium", "Low"], 
                                                      index=["High", "Medium", "Low"].index(idea['priority']),
                                                      key=f"edit_priority_{idea['id']}")
                        edited_status = st.selectbox("Status", 
                                                    ["New", "Researching", "Ready", "In Production", "Complete"],
                                                    index=["New", "Researching", "Ready", "In Production", "Complete"].index(idea['status']),
                                                    key=f"edit_status_{idea['id']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Save Changes", key=f"save_edit_{idea['id']}"):
                                # Update the idea
                                for i, stored_idea in enumerate(st.session_state.saved_ideas):
                                    if stored_idea['id'] == idea['id']:
                                        st.session_state.saved_ideas[i]['title'] = edited_title
                                        st.session_state.saved_ideas[i]['notes'] = edited_notes
                                        st.session_state.saved_ideas[i]['priority'] = edited_priority
                                        st.session_state.saved_ideas[i]['status'] = edited_status
                                        st.session_state.saved_ideas[i]['last_updated'] = datetime.now().strftime('%m/%d/%y')
                                        break
                                st.session_state[f"editing_{idea['id']}"] = False
                                st.success("Changes saved!")
                                st.rerun()
                        
                        with col2:
                            if st.button("Cancel", key=f"cancel_edit_{idea['id']}"):
                                st.session_state[f"editing_{idea['id']}"] = False
                                st.rerun()
                
                st.divider()
    else:
        st.info("No saved ideas yet. Add your first idea above!")

elif st.session_state.current_page == "Script Builder":
    st.markdown("""
    <h3 style="font-family: 'Crimson Text', serif; font-weight: 700;">SCRIPT BUILDER</h3>
    """, unsafe_allow_html=True)
    
    # Initialize scripts in session state
    if 'scripts' not in st.session_state:
        st.session_state.scripts = []
    
    # Script template
    script_template = """# {title}

## COLD OPEN
[Hook the audience in the first 30 seconds]

## INTRODUCTION
Hey everyone, today's case is about...

## ACT 1: THE SETUP
[Background, victims, setting]

## ACT 2: THE CRIME
[What happened]

## ACT 3: THE INVESTIGATION
[Police work, evidence, suspects]

## ACT 4: THE RESOLUTION
[Trial, verdict, aftermath]

## BAILEY'S TAKE
[Personal thoughts and conclusions]

## MAKEUP NOTES
[Products used, techniques]
"""
    
    # Create new script or load existing
    col1, col2 = st.columns([2, 1])
    
    with col1:
        script_title = st.text_input("Episode Title", placeholder="Enter episode title...")
    
    with col2:
        if st.button("Create New Script", type="primary", use_container_width=True):
            if script_title:
                new_script = {
                    'id': len(st.session_state.scripts) + 1,
                    'title': script_title,
                    'content': script_template.format(title=script_title),
                    'created': datetime.now().strftime('%m/%d/%y %H:%M'),
                    'last_saved': datetime.now().strftime('%m/%d/%y %H:%M')
                }
                st.session_state.scripts.append(new_script)
                st.session_state.current_script_id = new_script['id']
                st.success(f"Created script: {script_title}")
                st.rerun()
    
    # Load existing scripts
    if st.session_state.scripts:
        selected_script_title = st.selectbox(
            "Load Existing Script",
            ["Select a script..."] + [s['title'] for s in st.session_state.scripts]
        )
        
        if selected_script_title != "Select a script...":
            current_script = next(s for s in st.session_state.scripts if s['title'] == selected_script_title)
            
            # Script editor
            st.markdown("---")
            st.markdown(f"**Editing:** {current_script['title']}")
            st.caption(f"Created: {current_script['created']} | Last saved: {current_script['last_saved']}")
            
            # Editor with tabs for different views
            editor_tab1, editor_tab2, editor_tab3 = st.tabs(["✏️ Edit", "👁️ Preview", "📊 Stats"])
            
            with editor_tab1:
                edited_content = st.text_area(
                    "Script Content",
                    value=current_script['content'],
                    height=600,
                    key=f"script_editor_{current_script['id']}"
                )
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("💾 Save", type="primary"):
                        # Update script
                        for i, script in enumerate(st.session_state.scripts):
                            if script['id'] == current_script['id']:
                                st.session_state.scripts[i]['content'] = edited_content
                                st.session_state.scripts[i]['last_saved'] = datetime.now().strftime('%m/%d/%y %H:%M')
                                break
                        st.success("Script saved!")
                
                with col2:
                    # Download script
                    st.download_button(
                        "📥 Download",
                        data=edited_content,
                        file_name=f"{current_script['title'].replace(' ', '_')}_script.md",
                        mime="text/markdown"
                    )
                
                with col3:
                    if st.button("🗑️ Delete Script"):
                        st.session_state.scripts = [s for s in st.session_state.scripts if s['id'] != current_script['id']]
                        st.rerun()
            
            with editor_tab2:
                st.markdown(edited_content)
            
            with editor_tab3:
                # Script statistics
                word_count = len(edited_content.split())
                char_count = len(edited_content)
                
                # Estimate reading time (average 150 words per minute)
                reading_time = word_count / 150
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Words", f"{word_count:,}")
                
                with col2:
                    st.metric("Characters", f"{char_count:,}")
                
                with col3:
                    st.metric("Est. Runtime", f"{reading_time:.1f} min")
                
                # Section breakdown
                st.markdown("### Section Breakdown")
                sections = edited_content.split('##')
                for section in sections[1:]:  # Skip the first empty split
                    if section.strip():
                        section_title = section.split('\n')[0].strip()
                        section_words = len(section.split())
                        st.write(f"**{section_title}:** {section_words} words")

elif st.session_state.current_page == "Episode Calendar":
    st.markdown("""
    <h3 style="font-family: 'Crimson Text', serif; font-weight: 700;">EPISODE CALENDAR</h3>
    """, unsafe_allow_html=True)
    
    # Initialize calendar events
    if 'calendar_events' not in st.session_state:
        st.session_state.calendar_events = []
    
    # Add new episode
    with st.expander("📅 Schedule New Episode", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            episode_title = st.text_input("Episode Title", placeholder="Case name...")
            episode_date = st.date_input("Release Date")
        
        with col2:
            episode_status = st.selectbox("Status", ["Planned", "Filming", "Editing", "Ready", "Published"])
            episode_platform = st.multiselect("Platforms", ["YouTube", "Podcast", "Instagram", "TikTok"])
        
        with col3:
            episode_notes = st.text_area("Notes", placeholder="Special notes, guest info, etc...")
        
        if st.button("Add to Calendar", type="primary"):
            if episode_title and episode_date:
                new_event = {
                    'id': len(st.session_state.calendar_events) + 1,
                    'title': episode_title,
                    'date': episode_date,
                    'status': episode_status,
                    'platforms': episode_platform,
                    'notes': episode_notes
                }
                st.session_state.calendar_events.append(new_event)
                st.success(f"Added '{episode_title}' to calendar!")
                st.rerun()
    
    # Calendar view options
    view_option = st.radio("View", ["📅 Month View", "📋 List View", "📊 Analytics"], horizontal=True)
    
    if view_option == "📅 Month View":
        # Simple month view
        import calendar
        from datetime import date
        
        # Get current month
        today = date.today()
        month_year = st.date_input("Select Month", value=today, key="month_selector")
        
        # Create calendar
        cal = calendar.monthcalendar(month_year.year, month_year.month)
        month_name = calendar.month_name[month_year.month]
        
        st.markdown(f"### {month_name} {month_year.year}")
        
        # Days of week
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        cols = st.columns(7)
        for i, day in enumerate(days):
            cols[i].markdown(f"**{day}**")
        
        # Calendar grid
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].write("")
                else:
                    day_date = date(month_year.year, month_year.month, day)
                    
                    # Check for events on this day
                    day_events = [e for e in st.session_state.calendar_events if e['date'] == day_date]
                    
                    if day_events:
                        cols[i].markdown(f"**{day}**")
                        for event in day_events:
                            status_emoji = {
                                "Planned": "📝",
                                "Filming": "🎬",
                                "Editing": "✂️",
                                "Ready": "✅",
                                "Published": "📺"
                            }.get(event['status'], "📅")
                            cols[i].caption(f"{status_emoji} {event['title'][:15]}...")
                    else:
                        cols[i].write(f"{day}")
    
    elif view_option == "📋 List View":
        # List view with filters
        col1, col2 = st.columns(2)
        
        with col1:
            filter_status = st.selectbox("Filter by Status", ["All", "Planned", "Filming", "Editing", "Ready", "Published"])
        
        with col2:
            sort_order = st.selectbox("Sort by", ["Date (Upcoming First)", "Date (Recent First)", "Title"])
        
        # Filter events
        filtered_events = st.session_state.calendar_events.copy()
        
        if filter_status != "All":
            filtered_events = [e for e in filtered_events if e['status'] == filter_status]
        
        # Sort events
        if sort_order == "Date (Upcoming First)":
            filtered_events.sort(key=lambda x: x['date'])
        elif sort_order == "Date (Recent First)":
            filtered_events.sort(key=lambda x: x['date'], reverse=True)
        else:
            filtered_events.sort(key=lambda x: x['title'])
        
        # Display events
        if filtered_events:
            for event in filtered_events:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"### {event['title']}")
                        if event['notes']:
                            st.caption(event['notes'])
                    
                    with col2:
                        st.write(f"**Date:** {event['date'].strftime('%m/%d/%y')}")
                        
                        # Days until/since
                        days_diff = (event['date'] - date.today()).days
                        if days_diff > 0:
                            st.caption(f"In {days_diff} days")
                        elif days_diff < 0:
                            st.caption(f"{abs(days_diff)} days ago")
                        else:
                            st.caption("Today!")
                    
                    with col3:
                        status_color = {
                            "Planned": "#808080",
                            "Filming": "#FFA500",
                            "Editing": "#4169E1",
                            "Ready": "#32CD32",
                            "Published": "#DC143C"
                        }.get(event['status'], "#808080")
                        
                        st.markdown(f"**Status:** <span style='color: {status_color}'>{event['status']}</span>", unsafe_allow_html=True)
                    
                    with col4:
                        if event['platforms']:
                            st.write("**Platforms:**")
                            for platform in event['platforms']:
                                st.caption(f"• {platform}")
                        
                        if st.button("🗑️", key=f"delete_event_{event['id']}", help="Delete"):
                            st.session_state.calendar_events = [e for e in st.session_state.calendar_events if e['id'] != event['id']]
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("No episodes scheduled. Add your first episode above!")
    
    else:  # Analytics view
        if st.session_state.calendar_events:
            st.markdown("### Production Analytics")
            
            # Status breakdown
            status_counts = {}
            for event in st.session_state.calendar_events:
                status_counts[event['status']] = status_counts.get(event['status'], 0) + 1
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Episodes", len(st.session_state.calendar_events))
            
            with col2:
                st.metric("Planned", status_counts.get("Planned", 0))
            
            with col3:
                st.metric("In Production", status_counts.get("Filming", 0) + status_counts.get("Editing", 0))
            
            with col4:
                st.metric("Ready", status_counts.get("Ready", 0))
            
            with col5:
                st.metric("Published", status_counts.get("Published", 0))
            
            # Upcoming episodes
            st.markdown("### Upcoming Episodes")
            upcoming = [e for e in st.session_state.calendar_events if e['date'] >= date.today()]
            upcoming.sort(key=lambda x: x['date'])
            
            if upcoming:
                for event in upcoming[:5]:
                    days_until = (event['date'] - date.today()).days
                    st.write(f"• **{event['title']}** - {event['date'].strftime('%m/%d/%y')} ({days_until} days) - {event['status']}")
            else:
                st.info("No upcoming episodes scheduled")
        else:
            st.info("No data to analyze. Start scheduling episodes!")

elif st.session_state.current_page == "Privacy Policy":
    st.markdown("""
    <h1 style="font-family: 'Crimson Text', serif; font-size: 48px; font-weight: 700;">Privacy Policy</h1>
    <p style="font-size: 14px; color: #666;">Last Updated: December 2024</p>
    """, unsafe_allow_html=True)
    
    # Add the YouTube/Google compliance notice prominently at the top
    st.info("""
    **Important Notice:**
    
    By using this application, you agree to be bound by the [YouTube Terms of Service](https://www.youtube.com/t/terms).
    
    This application uses YouTube API Services and is subject to the [Google Privacy Policy](http://www.google.com/policies/privacy).
    """)
    
    st.markdown("""
    ## Bailey's Crime Lab - Privacy Policy
    
    This privacy policy explains how Bailey's Crime Lab ("we", "our", "this application") handles information when you use our service.
    
    ### YouTube API Services
    This application uses YouTube API Services. By using this application, you agree to be bound by the [YouTube Terms of Service](https://www.youtube.com/t/terms).
    
    ### Information We Access
    When you use our application, we access the following information through YouTube API Services:
    - Public video metadata (titles, descriptions, view counts, publish dates)
    - Public channel information (channel names, subscriber counts)
    - Public comment data on videos
    - Video statistics (likes, comments counts)
    
    ### Information Storage
    - **Session Storage Only**: All data retrieved from YouTube is temporarily stored only in your browser session
    - **No Persistent Storage**: We do not save any YouTube data to databases or files
    - **Automatic Deletion**: All cached data is automatically deleted when you close your browser or end your session
    - **Refresh Policy**: Cached YouTube data expires after 24 hours and is refreshed upon new requests
    
    ### Information We Do NOT Collect
    - We do not collect any personal information
    - We do not require user accounts or authentication
    - We do not store YouTube authorization tokens
    - We do not track individual users across sessions
    - We do not use cookies for tracking purposes
    
    ### How We Use Information
    The YouTube data we access is used solely to:
    - Display search results for true crime cases
    - Show competitor analysis for content creators
    - Present trending video information
    - Provide content research tools
    
    ### Data Sharing
    - We do not share any data with third parties
    - We do not sell, trade, or transfer any information
    - All data remains within your browser session only
    
    ### Third-Party Services
    This application integrates with:
    - **YouTube API Services** - Subject to [Google Privacy Policy](http://www.google.com/policies/privacy)
    - **Reddit API** - For public post data only
    - **Wikipedia API** - For public article information
    - **CourtListener** - For public court documents (if configured)
    
    ### Browser Technologies
    This application uses browser session storage to temporarily maintain your search results and preferences during your visit. This data:
    - Is stored only in your browser's memory
    - Is never transmitted to our servers
    - Is automatically deleted when you close the browser tab
    
    ### Data Security
    - All API communications use HTTPS encryption
    - No sensitive data is collected or stored
    - Application runs entirely in your browser with no backend data storage
    
    ### Children's Privacy
    This application is not intended for children under 13 years of age. We do not knowingly collect information from children under 13.
    
    ### Changes to This Policy
    We may update this privacy policy from time to time. Changes will be posted on this page with an updated revision date.
    
    ### Contact Information
    For questions about this privacy policy or our practices, contact:
    
    **Email**: access@shorthandstudios.com  
    **Company**: Underscore Venture One LLC  
    **Address**: 8383 Wilshire Blvd, Beverly Hills, CA 90211
    
    ### Your Rights
    Since we don't collect or store personal data, there is no personal information to access, modify, or delete. Each session starts fresh with no retained information.
    
    ### California Privacy Rights
    California residents have specific rights under CCPA. However, as we do not collect, sell, or store personal information, these rights are preserved by our privacy-by-design approach.
    
    ### Compliance
    This application complies with:
    - YouTube API Services Terms of Service
    - Google Privacy Requirements
    - Applicable data protection regulations
    """)

# Simple footer with legal compliance text
st.markdown("""
<div class="footer">
  <div class="brand" style="color: #FFFFFF;">SHORTHAND STUDIOS</div>
  <div style="font-size: 18px; color: #FFFFFF;">Content Intelligence Platform</div>
  
  <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #444;">
    <div style="font-size: 14px; color: #FFFFFF; margin-bottom: 1rem;">
      <strong style="color: #FFFFFF;">Legal</strong><br>
      <span style="color: #FFFFFF;">View our Privacy Policy for information about data usage and YouTube API Services compliance.</span>
    </div>
  </div>
  
  <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #444;">
    <div style="font-size: 12px; color: #FFFFFF;">
      <strong style="color: #FFFFFF;">Contact Information</strong><br>
      <span style="color: #FFFFFF;">Email: access@shorthandstudios.com</span><br>
      <span style="color: #FFFFFF;">Underscore Venture One LLC</span><br>
      <span style="color: #FFFFFF;">8383 Wilshire Blvd, Beverly Hills, CA 90211</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Clickable text link for Privacy Policy
if st.button("📜 Privacy Policy", key="privacy_link", help="View our Privacy Policy and Terms", use_container_width=False):
    st.session_state.current_page = "Privacy Policy"
    st.rerun()

    # Temporary debug info
st.write(f"Current page: {st.session_state.get('current_page', 'Not set')}")

# Privacy Policy button
if st.button("📜 Privacy Policy", key="privacy_link"):
    st.session_state.current_page = "Privacy Policy"
    st.success("Button clicked! Navigating to Privacy Policy...")  # Debug message
    st.rerun()