from flask import Blueprint, request, jsonify
from ai_service import AIService

chat_bp = Blueprint('chat', __name__, url_prefix='/api')
ai_service = AIService()

@chat_bp.route('/chat', methods=['POST'])
def send_message():
    """
    POST /api/chat
    Body: {"message": "Your question here", "session_id": "optional", "preferred_model": "optional"}
    Returns: {"response": "...", "model_used": "...", "session_id": "..."}
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'Missing message field'}), 400
    
    message = data.get('message', '').strip()
    session_id = data.get('session_id')
    preferred_model = data.get('preferred_model')
    
    if len(message) == 0:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    if len(message) > 10000:
        return jsonify({'error': 'Message too long (max 10000 chars)'}), 400
    
    result = ai_service.send_message(message, session_id, preferred_model)
    
    return jsonify(result), 200 if result['status'] == 'success' else 500