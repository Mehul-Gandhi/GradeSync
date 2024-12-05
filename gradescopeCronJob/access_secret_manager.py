from google.cloud import secretmanager

def access_secret(secret_name):
    # Create the Secret Manager client
    client = secretmanager.SecretManagerServiceClient()
    
    # Build the resource name for the secret
    project_id = "eecs-gradeview"
    secret_version = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    
    # Access the secret version
    response = client.access_secret_version(name=secret_version)
    
    # Return the payload as a string (decode from bytes)
    secret_payload = response.payload.data.decode("UTF-8")
    
    return secret_payload


def main():
    try:
        GRADESCOPE_EMAIL = access_secret("GRADESCOPE_EMAIL")
        GRADESCOPE_PASSWORD = access_secret("GRADESCOPE_PASSWORD")
        SERVICE_ACCOUNT_CREDENTIALS = access_secret("SERVICE_ACCOUNT_CREDENTIALS")

        # Print to test if the secrets are fetched correctly
        print("Successfully fetched secrets:")
        print("GRADESCOPE_EMAIL:", GRADESCOPE_EMAIL)
        print("GRADESCOPE_PASSWORD:", GRADESCOPE_PASSWORD)
        print("SERVICE_ACCOUNT_CREDENTIALS:", SERVICE_ACCOUNT_CREDENTIALS)

    except Exception as e:
        print(f"Error fetching secrets: {str(e)}")

if __name__ == "__main__":
    main()
