from jose import jwt
from fastapi import HTTPException
from datetime import datetime, timedelta

# JWT secret and algorithm (should match your application's config)
JWT_SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
JWT_ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT token with the user data.
    `data` should contain the user information such as username, role, etc.
    """
    to_encode = data.copy()

    # Ensure the 'sub' claim is set to a unique user identifier (e.g., username or user ID)
    if "sub" not in to_encode:
        to_encode["sub"] = data.get("username")  # Or use "user_id" if you prefer

    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=60))
    to_encode.update({"exp": expire})  # Set the expiration time for the token

    try:
        # Encode the token using the secret key and algorithm
        encoded_token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_token
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token creation failed: {str(e)}")


# Generating a JWT with valid payload
token_data = {"sub": "username", "role": "admin"}
token = create_access_token(token_data)

print(token)
# Passing the token to a secured route
# Use this token in the `Authorization: Bearer <token>` header when making requests

# # Function to decode JWT token
# def decode_access_token(token: str):
#     try:
#         # Decode the token (without verifying expiration for now)
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})

#         # Ensure 'sub' exists and is a valid string
#         if "sub" not in payload or not isinstance(payload["sub"], str):
#             raise HTTPException(status_code=401, detail="Subject must be a string.")

#         # Check if the token has expired
#         if "exp" in payload:
#             expiration_time = datetime.utcfromtimestamp(payload["exp"])
#             current_time = datetime.utcnow()

#             # Debugging output for expiration time
#             print(f"Expiration Time: {expiration_time}")
#             print(f"Current Time: {current_time}")

#             # Check if the token has expired
#             if expiration_time < current_time:
#                 raise HTTPException(status_code=401, detail="Token has expired")
#             else:
#                 print("Token is still valid")

#         # Return the decoded payload if everything is valid
#         return payload

#     except jwt.JWTClaimsError as e:
#         raise HTTPException(status_code=401, detail=f"JWT Claims Error: {e}")
#     except jwt.JWTError as e:
#         raise HTTPException(status_code=401, detail=f"JWT Decoding Error: {e}")
#     except Exception as e:
#         raise HTTPException(status_code=401, detail=f"Error: {e}")

# # Function to create a JWT token
# def create_jwt(user_id: int, username: str, role: str):
#     # Token payload
#     payload = {
#         "sub": str(user_id),  # Ensure that sub is a string
#         "role": role,
#         "username": username,
#         "exp": datetime.utcnow() + timedelta(hours=1)  # Expiration time
#     }

#     # Encode the JWT token
#     token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
#     return token

# # Example of how to create a token
# token = create_jwt(user_id=1, username="admin", role="admin")
# print("Generated Token:", token)

# # Decode and validate the token
# print("Decoded Token Payload:")
# decoded_payload = decode_access_token(token)
# print(decoded_payload)

# # Main function to run the test
# if __name__ == "__main__":
#     # Replace this with the token you want to decode
#     token_to_test = token  # Use the token generated above

#     # Call the function to decode and check expiration
#     try:
#         decoded_payload = decode_access_token(token_to_test)
#         print("Decoded Payload:", decoded_payload)
#     except HTTPException as e:
#         print(f"HTTPException: {e.detail}")
