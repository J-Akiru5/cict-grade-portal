from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required
import logging

chatbot_bp = Blueprint('chatbot', __name__)
logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an AI assistant for the CICT Grade Portal of ISUFST (Iloilo State University of Fisheries and Technology) Dingle Campus.

You assist faculty members, administrators, and students with questions related to:
- Academic grades and grading systems
- Course subjects and schedules
- Student enrollment and records
- Portal navigation and features
- General academic policies of CICT (College of Information and Communications Technology)

Be concise, helpful, and professional. If asked about something outside the portal or academics, politely redirect the user to relevant portal features.
Do not fabricate specific student records, grades, or personal data — direct users to check the portal directly for those.
Respond in the same language the user writes in (Filipino or English)."""


@chatbot_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return jsonify({'error': 'AI service is not available. Install google-genai.'}), 503

    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'error': 'AI service is not configured.'}), 503

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid request.'}), 400

    user_message = (data.get('message') or '').strip()
    if not user_message:
        return jsonify({'error': 'Message is required.'}), 400

    if len(user_message) > 2000:
        return jsonify({'error': 'Message is too long (max 2000 characters).'}), 400

    # Build conversation history (last 10 turns max to stay within token limits)
    raw_history = data.get('history', [])
    if not isinstance(raw_history, list):
        raw_history = []
    raw_history = raw_history[-20:]  # up to 10 pairs

    try:
        client = genai.Client(api_key=api_key)

        # Convert history to Gemini Content format
        gemini_history = []
        for turn in raw_history:
            role = turn.get('role')
            text = turn.get('text', '')
            if role in ('user', 'model') and text:
                gemini_history.append(
                    types.Content(role=role, parts=[types.Part(text=text)])
                )

        chat_session = client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                system_instruction=_SYSTEM_PROMPT,
            ),
            history=gemini_history,
        )
        response = chat_session.send_message(user_message)
        reply = response.text

        return jsonify({'reply': reply})

    except Exception as e:
        logger.error('Gemini API error: %s', e)
        return jsonify({'error': 'The AI service encountered an error. Please try again.'}), 500
