import jwt

def decode_jwt_token():
    """Debug JWT token to see what user data it contains"""
    
    # You'll need to paste the actual token from localStorage here
    token = input("Paste the JWT token from localStorage: ")
    
    try:
        # Decode without verification (for debugging only)
        decoded = jwt.decode(token, options={"verify_signature": False})
        print("🔍 JWT Token Contents:")
        print(f"User ID: {decoded.get('user_id', 'Not found')}")
        print(f"Email: {decoded.get('email', 'Not found')}")
        print(f"Expiry: {decoded.get('exp', 'Not found')}")
        print(f"Full payload: {decoded}")
        
    except Exception as e:
        print(f"❌ Error decoding token: {e}")

if __name__ == "__main__":
    decode_jwt_token()
