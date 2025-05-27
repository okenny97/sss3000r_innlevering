from flask import Blueprint, jsonify
import subprocess

temperature_bp = Blueprint('temperature', __name__)

@temperature_bp.route('/temperature', methods=['GET'])
def get_temperature():
    try:
        result = subprocess.run(['python3', 'read_temp.py'], capture_output=True, text=True, check=True)
        temperature = result.stdout.strip()
        return jsonify({'temperature': temperature})
    except subprocess.CalledProcessError:
        return jsonify({'error': 'Failed to read temperature'}), 500