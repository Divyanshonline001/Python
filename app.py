import os
import re
import json
import logging
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

def fetch_video_details(video_id):
    """
    Fetches the video title, channel name, and channel URL using YouTube's oEmbed endpoint.
    Returns (title, channel_name, channel_url) or (None, None, None) on failure.
    """
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('title'), data.get('author_name'), data.get('author_url')
    except Exception as e:
        logging.warning(f"Failed to fetch video details via oEmbed for {video_id}: {str(e)}")
    return None, None, None

# Load environment variables
load_dotenv()

# Workaround for Google authentication cert client warning/error
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder='static', static_url_path='')

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logging.info("Gemini API configured successfully.")
else:
    logging.warning("GEMINI_API_KEY not found in environment. Please add it to your .env file.")

def clean_json_string(raw_text):
    """
    Cleans potentially malformed JSON output from LLM models,
    handling trailing curly braces, markdown blocks, and leading/trailing trash.
    """
    text = raw_text.strip()
    
    # Strip markdown formatting
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    # Try finding the first '{' and last '}'
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    
    if first_brace != -1 and last_brace != -1:
        candidate = text[first_brace:last_brace+1]
        
        # Fast path
        try:
            json.loads(candidate)
            return candidate
        except json.JSONDecodeError:
            pass
            
        # Slow path: trace braces from left to find first balanced match
        brace_count = 0
        in_string = False
        escape = False
        
        for idx, char in enumerate(candidate):
            if char == '"' and not escape:
                in_string = not in_string
            elif char == '\\' and in_string:
                escape = not escape
                continue
            elif not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        balanced = candidate[:idx+1]
                        try:
                            json.loads(balanced)
                            return balanced
                        except json.JSONDecodeError:
                            pass
            escape = False
            
    return text

def extract_video_id(url):
    """
    Extracts the 11-character YouTube video ID from various YouTube URL formats.
    """
    if not url:
        return None
    
    # If the URL is exactly an 11-char alphanumeric/underscore/dash string, it's already the ID
    if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
        
    # Standard formats:
    # - https://www.youtube.com/watch?v=VIDEO_ID
    # - https://youtu.be/VIDEO_ID
    # - https://www.youtube.com/embed/VIDEO_ID
    # - https://youtube.com/live/VIDEO_ID
    # - https://m.youtube.com/watch?v=VIDEO_ID
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:m\.)?(?:music\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?|live)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def fetch_youtube_transcript(video_id):
    """
    Fetches the transcript text for the given video ID.
    Supports english and falls back to other available languages.
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        
        # Try to find english transcript (manually created or auto-generated)
        try:
            transcript_obj = transcript_list.find_transcript(['en'])
        except Exception:
            # Fallback to the first available transcript in any language
            transcript_obj = next(iter(transcript_list))
            
        fetched = transcript_obj.fetch()
        
        # Join all snippet text contents
        transcript_text = " ".join([snippet.text for snippet in fetched.snippets])
        return transcript_text, None
        
    except Exception as e:
        error_name = type(e).__name__
        logging.error(f"Error fetching transcript for {video_id}: {error_name} - {str(e)}")
        
        # User friendly error messages based on exception type
        if "TranscriptsDisabled" in error_name or "Subtitles are disabled" in str(e):
            return None, "Subtitles/transcripts are disabled or unavailable for this video."
        elif "VideoUnavailable" in error_name:
            return None, "This YouTube video is unavailable, private, or restricted."
        elif "InvalidVideoId" in error_name:
            return None, "The YouTube video ID extracted from the URL is invalid."
        elif "IpBlocked" in error_name or "Too Many Requests" in str(e) or "RequestBlocked" in error_name:
            return None, "YouTube transcript retrieval was rate-limited or blocked. Please try again later."
        else:
            return None, f"Failed to retrieve video transcript. (Error: {error_name})"

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/api/config-check', methods=['GET'])
def config_check():
    """
    Checks if the Gemini API Key is configured.
    """
    return jsonify({
        "configured": os.getenv("GEMINI_API_KEY") is not None and os.getenv("GEMINI_API_KEY") != ""
    })

@app.route('/api/summarize', methods=['POST'])
def summarize_video():
    # Double check API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify({
            "error": "GEMINI_API_KEY is missing. Please configure it in your .env file.",
            "code": "MISSING_API_KEY"
        }), 500

    data = request.get_json() or {}
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({"error": "YouTube URL is required."}), 400
        
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL. Please make sure it contains a valid video ID."}), 400
        
    logging.info(f"Processing summarization request for video ID: {video_id}")
    
    # Fetch video details via oEmbed
    title, channel_name, channel_url = fetch_video_details(video_id)
    
    # 1. Fetch transcript
    transcript_text, err = fetch_youtube_transcript(video_id)
    if err:
        return jsonify({"error": err}), 400
        
    if not transcript_text or len(transcript_text.strip()) < 50:
        return jsonify({"error": "The transcript is too short to generate a meaningful summary."}), 400

    # 2. Call Gemini for structured AI summarization
    try:
        # Re-ensure SDK config (handles hot-reloading env vars if changed)
        genai.configure(api_key=api_key)
        
        prompt = f"""You are an elite YouTube video summarization assistant.
Analyze the provided video transcript and generate a structured summary.
Your response MUST be in raw JSON format matching this schema:
{{
  "summary": "A detailed summary of the video, structured in 2 to 3 cohesive paragraphs. Explain the overall context, the main topics, and the developer's/speaker's core thesis.",
  "key_points": [
    "A concise, high-impact key point or lesson with a bold header. Format it like: '**Heading**: Description of the point and its relevance.'",
    "Include 5 to 8 of these key points."
  ],
  "takeaway": "A powerful 1-2 sentence concluding statement summarizing the ultimate value or final takeaway from the video.",
  "visual_elements": {{
    "type": "timeline | process | comparison | key_metrics",
    "title": "A custom title describing the diagram (e.g. 'Setup Steps' or 'Milestones')",
    "headers": ["Optional Column Header 1", "Optional Column Header 2", "Optional Column Header 3"],
    "data": [
      {{
        "col1": "For type 'timeline': timestamp (e.g., '1:23') or phase. For 'process': step number (e.g., 'Step 1'). For 'comparison': feature category. For 'key_metrics': short metric label or statistical value.",
        "col2": "For type 'timeline': event name. For 'process': action title. For 'comparison': value/spec for item A. For 'key_metrics': description of the statistic.",
        "col3": "For type 'timeline': detailed event description. For 'process': step details. For 'comparison': value/spec for item B. For 'key_metrics': context or source."
      }}
    ]
  }}
}}

Analyze the content and select a visual representation mode (`type`) that best describes the video's concepts:
- Use 'timeline' if the content is chronological, recounts a history, or has distinct timestamped events.
- Use 'process' if the video is a tutorial, how-to, setup guide, flowchart steps, or workflow instructions.
- Use 'comparison' if the video compares tools, alternatives, frameworks, pros vs cons, or concepts.
- Use 'key_metrics' if the video contains data statistics, numerical results, research insights, or scores.

Provide 3 to 6 items in the "data" array.
Respond ONLY with the JSON document. Do not include markdown code block formatting (e.g. ```json ... ```).

Transcript text:
{transcript_text}
"""
        
        # Try a sequence of model names until one succeeds
        model_names = ["gemini-3.1-flash-lite", "gemini-flash-latest", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        response = None
        last_err = None
        
        for m_name in model_names:
            try:
                logging.info(f"Attempting to generate summary using model: {m_name}")
                model = genai.GenerativeModel(m_name)
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                logging.info(f"Successfully generated summary using model: {m_name}")
                break
            except Exception as e:
                logging.warning(f"Model {m_name} failed: {str(e)}")
                last_err = e
                continue
                
        if response is None:
            raise last_err if last_err else Exception("No models were available for content generation.")
        
        # Parse JSON output from Gemini
        response_text = clean_json_string(response.text)
        
        summary_json = json.loads(response_text)
        
        # Add video details metadata to JSON response
        summary_json["videoId"] = video_id
        summary_json["videoUrl"] = f"https://www.youtube.com/watch?v={video_id}"
        summary_json["title"] = title or f"YouTube Video Summary (ID: {video_id})"
        summary_json["channelName"] = channel_name
        summary_json["channelUrl"] = channel_url
        
        logging.info("Summary generated successfully.")
        return jsonify(summary_json)
        
    except json.JSONDecodeError as je:
        logging.error(f"Failed to parse Gemini response as JSON: {str(je)}. Raw output: {response.text}")
        return jsonify({"error": "Failed to generate structured summary. The AI model output was malformed. Please try again."}), 500
    except Exception as ge:
        logging.error(f"Gemini API error: {str(ge)}")
        return jsonify({"error": f"AI Summarization failed: {str(ge)}"}), 500

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
