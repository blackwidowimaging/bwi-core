import boto3
import os
import secrets
import string
from ..utils.logger import setup_logger

logger = setup_logger('cognito-service')

class CognitoConnection:
    def __init__(self):
        try:
            self.user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
            if not self.user_pool_id:
                raise ValueError("COGNITO_USER_POOL_ID environment variable is not set")

            self.__create_connection()
        except Exception as ex:
            logger.error(ex)
            logger.error("Error initializing Cognito connection. Have you set the appropriate COGNITO_USER_POOL_ID environment variable?")

    def __create_connection(self):
        self.cognito_client = boto3.client('cognito-idp')
        logger.info(f"Cognito client initialized for User Pool: {self.user_pool_id}")

    def create_user(self, username, user_attributes):
        """Create a new user in Cognito and send an invitation email."""
        user_attributes["email_verified"] = "true"
        try:
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=[{"Name": key, "Value": value} for key, value in user_attributes.items()],
                DesiredDeliveryMediums=["EMAIL"]
            )
            logger.info(f"User {username} created successfully and invitation email sent.")
            return response
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return {"error": str(e)}


    def list_users(self, limit=10, pagination_token=None):
        """Retrieve a list of users from the Cognito User Pool."""
        params = {
            "UserPoolId": self.user_pool_id,
            "Limit": limit,
        }

        if pagination_token:
            params["PaginationToken"] = pagination_token

        try:
            response = self.cognito_client.list_users(**params)
            logger.info(f"cognito-idp response: {response}")
            return {
                "users": response.get("Users", []),
                "next_token": response.get("PaginationToken"),
            }
        except Exception as e:
            import traceback
            logger.error(f"Error listing users: {e}")
            logger.error(traceback.format_exc())  # Logs full stack trace
            return {"error": str(e)}

    def get_user(self, username):
        """Retrieve details of a specific user."""
        try:
            response = self.cognito_client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            return response
        except Exception as e:
            logger.error(f"Error getting user {username}: {e}")
            return {"error": str(e)}

    def update_user_attribute(self, username, attribute_name, attribute_value):
        """Update a user attribute (e.g., email_verified=True)."""
        try:
            self.cognito_client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=[
                    {"Name": attribute_name, "Value": attribute_value}
                ]
            )
            return {"message": f"User {username} updated successfully"}
        except Exception as e:
            logger.error(f"Error updating user {username}: {e}")
            return {"error": str(e)}

    def confirm_user(self, username):
        """Manually confirm a user."""
        try:
            self.cognito_client.admin_confirm_sign_up(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            return {"message": f"User {username} confirmed successfully"}
        except Exception as e:
            logger.error(f"Error confirming user {username}: {e}")
            return {"error": str(e)}

    def delete_user(self, username):
        """Delete a user from Cognito."""
        try:
            self.cognito_client.admin_delete_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            return {"message": f"User {username} deleted successfully"}
        except Exception as e:
            logger.error(f"Error deleting user {username}: {e}")
            return {"error": str(e)}

    def get_user_by_email(self, email):
        """Retrieve a user by their email address."""
        try:
            response = self.cognito_client.list_users(
                UserPoolId=self.user_pool_id,
                Filter=f'email = "{email}"',
                Limit=1
            )

            users = response.get("Users", [])
            if users:
                user = users[0]
                logger.info(f"User found for email {email}: {user.get('Username')}")
                return user
            else:
                logger.info(f"No user found for email {email}")
                return None

        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return {"error": str(e)}

    # def reset_temp_password(self, username):
    #     """Reset a user's temporary password (AdminCreateUser)."""
    #     try:
    #         response = self.cognito_client.admin_create_user(
    #             UserPoolId=self.user_pool_id,
    #             Username=username,
    #             MessageAction='RESEND'
    #         )
    #         logger.info(f"Temporary password reset for {username}. Cognito will send a new email/SMS.")
    #         return response
    #     except self.cognito_client.exceptions.UserNotFoundException:
    #         logger.error(f"User not found: {username}")
    #         return {"error": f"User {username} not found"}
    #     except Exception as e:
    #         logger.error(f"Error resetting temporary password for {username}: {e}")
    #         return {"error": str(e)}

    # def generate_temporary_password(self, length=12):
    #     """Generates a secure, random password."""
    #     alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    #     while True:
    #         password = ''.join(secrets.choice(alphabet) for i in range(length))
    #         # Ensure the password meets complexity requirements (example: has lower, upper, digit, symbol)
    #         if (any(c.islower() for c in password)
    #                 and any(c.isupper() for c in password)
    #                 and any(c.isdigit() for c in password)
    #                 and any(c in "!@#$%^&*" for c in password)):
    #             return password

    # def admin_set_new_temporary_password(self, username):
        """
        Generates a new temporary password for a user and sets it,
        forcing them to change it on next login.
        """
        try:
            # Step 1: Generate the new temporary password
            temp_password = self.generate_temporary_password()

            # Step 2: Call admin_set_user_password
            response = self.cognito_client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=username,
                Password=temp_password,
                Permanent=False  # This is the key part that makes it a temporary password
            )
            logger.info(f"Successfully set a new temporary password for {username}.")

            # Step 3: Return the password so the handler can email it to the user
            return {
                "response": response,
                "temporary_password": temp_password
            }
        except Exception as e:
            logger.error(f"Error setting new temporary password for {username}: {e}")
            return {"error": str(e)}
