import pyotp
import qrcode
import io
import base64
import random
from flask import Blueprint, request, jsonify, redirect, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from database import db, User

auth_bp = Blueprint('auth', __name__)

# Registring av ny bruker
@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)

    if not current_user:
        return jsonify({"msg": "Ingen tilgang"}), 403

    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'msg': 'Mangler data'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'msg': 'Brukernavnet finnes allerede'}), 409

    hashed_pw = generate_password_hash(data['password'])
    new_user = User(
    	username=data['username'],
    	email=data['email'],
    	password=hashed_pw,
    	twofa_method='totp'
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'User created by ' + current_user.username}), 201

# Brukerinnlogging
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({'msg': 'Feil brukernavn eller passord'}), 401

    if user.twofa_method and user.twofa_secret:
        temp_token = create_access_token(identity=str(user.id), additional_claims={"2fa_verified": False})
        return jsonify({
            'msg': '2FA required',
            'require_2fa': True,
            'access_token': temp_token,
            'method': user.twofa_method
        }), 200

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'msg': 'Logged in',
        'user': user.username,
        'access_token': access_token
    }), 200

# Brukerutlogging
@auth_bp.route('/logout', methods=['GET'])
def logout():
    return jsonify({'msg': 'Logget ut'}), 200

# Hent brukerinformasjon
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return jsonify({
        "username": user.username,
        "email": user.email,
        "id": user.id
    })

# Hent liste over alle brukere
@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)

    if not current_user:
        return jsonify({"msg": "Ingen tilgang"}), 403

    users = User.query.all()
    user_list = [{"username": u.username, "email": u.email} for u in users]
    return jsonify(user_list)

# Brukt for å sette opp 2FA
@auth_bp.route('/setup-2fa', methods=['POST'])
@jwt_required()
def setup_2fa():
    data = request.get_json()
    method = data.get("method")  # "totp" or "email"

    if method not in ("totp", "email"):
        return jsonify({"msg": "Ugyldig 2FA-metode"}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if method == "totp":
        secret = pyotp.random_base32()
        user.pending_twofa_secret = secret
        user.twofa_method = "totp"
        db.session.commit()

        uri = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="Alarm System")
        return jsonify({"qr_uri": uri, "secret": secret})

    elif method == "email":
        code = str(random.randint(100000, 999999))
        user.pending_twofa_secret = code
        user.twofa_method = "email"
        db.session.commit()

        from send_mail import send_alarm_email
        send_alarm_email("Din 2FA-kode", f"Koden din er: {code}", user.email)

        return jsonify({"msg": "2FA via e-post kode sendt"})

    return jsonify({"msg": "Feil oppstod"}), 500

# Sender 2FA-kode via e-post
@auth_bp.route('/send-2fa-code', methods=['POST'])
@jwt_required()
def send_email_code():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user.twofa_method != "email":
        return jsonify({"msg": "2FA ikke satt til e-post"}), 400

    code = str(random.randint(100000, 999999))
    user.twofa_secret = code
    db.session.commit()

    from send_mail import send_alarm_email
    send_alarm_email("Din 2FA-kode", f"Koden din er: {code}", user.email)

    return jsonify({"msg": "Kode sendt til e-post"}), 200

# Verifiserer 2FA-kode for aktivering av 2FA
@auth_bp.route('/verify-2fa', methods=['POST'])
@jwt_required()
def verify_2fa():
    data = request.get_json()
    code = data.get("code")
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not code:
        return jsonify({"msg": "Mangler kode"}), 400

    if not user.twofa_method:
        return jsonify({"msg": "2FA metode ikke angitt"}), 400

    if not user.pending_twofa_secret:
        return jsonify({"msg": "Det finnes ingen 2FA-oppsett som venter på bekreftelse"}), 400

    # TOTP verifisering
    if user.twofa_method == "totp":
        totp = pyotp.TOTP(user.pending_twofa_secret)
        if totp.verify(code):
            user.twofa_secret = user.pending_twofa_secret
            user.pending_twofa_secret = None
            db.session.commit()
            return jsonify({"msg": "2FA aktivert!"}), 200
        return jsonify({"msg": "Ugyldig TOTP-kode"}), 401

    # E-post verifisering
    elif user.twofa_method == "email":
        if code == user.pending_twofa_secret:
            user.twofa_secret = code
            user.pending_twofa_secret = None
            db.session.commit()
            return jsonify({"msg": "2FA aktivert!"}), 200
        return jsonify({"msg": "Ugyldig e-postkode"}), 401

    return jsonify({"msg": "Ugyldig 2FA-metode"}), 400

# Verifiserer 2FA-kode ved innlogging
@auth_bp.route('/verify-login-2fa', methods=['POST'])
@jwt_required()
def verify_login_2fa():
    data = request.get_json()
    code = data.get("code")
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user.twofa_secret:
        return jsonify({"msg": "2FA ikke aktivert"}), 400

    if user.twofa_method == "totp":
        totp = pyotp.TOTP(user.twofa_secret)
        if totp.verify(code):
            full_token = create_access_token(identity=str(user.id))
            return jsonify({"msg": "Login fullført", "access_token": full_token}), 200
        return jsonify({"msg": "Ugyldig TOTP-kode"}), 401

    elif user.twofa_method == "email":
        if user.twofa_secret == code:
            full_token = create_access_token(identity=str(user.id))
            return jsonify({"msg": "Login fullført", "access_token": full_token}), 200
        return jsonify({"msg": "Ugyldig e-postkode"}), 401

    return jsonify({"msg": "Ugyldig 2FA-metode"}), 400

# Henter 2FA-status for innlogget bruker
@auth_bp.route('/2fa-status', methods=['GET'])
@jwt_required()
def get_2fa_status():
    try:
        user = User.query.get(int(get_jwt_identity()))
        if not user:
            return jsonify({"msg": "Ingen tilgang"}), 403

        return jsonify({
            "method": user.twofa_method or "none",
            "enabled": bool(user.twofa_secret),
            "pending": bool(user.pending_twofa_secret)
        })
    except Exception as e:
        print("2FA Status Error:", str(e))
        return jsonify({"msg": "Server error"}), 500

# Setter 2FA-metode for bruker
@auth_bp.route('/set-2fa', methods=['POST'])
@jwt_required()
def set_2fa_method():
    data = request.get_json()
    method = data.get("method")
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if method == "totp":
        secret = pyotp.random_base32()
        user.twofa_method = "totp"
        user.pending_twofa_secret = secret
        user.twofa_secret = None
        db.session.commit()
        uri = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="Alarm System")
        return jsonify({"qr_uri": uri, "secret": secret})

    elif method == "email":
        user.twofa_method = "email"
        user.pending_twofa_secret = None
        user.twofa_secret = None
        db.session.commit()
        return jsonify({"msg": "2FA via e-post aktivert"})

    elif method in ("none", ""):
        user.twofa_method = None
        user.twofa_secret = None
        user.pending_twofa_secret = None
        db.session.commit()
        return jsonify({"msg": "2FA deaktivert"})

    return jsonify({"msg": "Ugyldig metode"}), 400

# Genererer QR-kode for TOTP-2FA
@auth_bp.route('/qr.png')
@jwt_required()
def qr_png():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    totp = pyotp.TOTP(user.twofa_secret)
    uri = totp.provisioning_uri(user.email, issuer_name="Alarm System")
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

# Henter brukerprofil
@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return jsonify({'username': current_user.username, 'email': current_user.email}), 200