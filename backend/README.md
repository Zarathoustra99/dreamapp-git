# DreamApp Auth API

Authentication service for DreamApp built with FastAPI.

## Azure Deployment Instructions

To deploy this API to Azure App Service, follow these steps:

1. **Create a Web App in Azure App Service**
   - Select Python 3.10 as your runtime
   - Set up your database connection in Azure

2. **Configure the deployment settings**
   - In Azure Portal, go to your App Service → Configuration → General settings
   - Set the Startup Command to:
     ```
     gunicorn app.main:app --bind=0.0.0.0:8000 --workers=2 --timeout=30 --graceful-timeout=20 --max-requests=1000 --max-requests-jitter=50 --keep-alive=2 --log-level=info
     ```

3. **Configure environment variables in Azure**
   - Go to Azure Portal → App Service → Configuration → Application settings
   - Add these environmental variables:
     - `ENVIRONMENT`: `production`
     - `PYTHONPATH`: `.`
     - `SQL_SERVER`: Your Azure SQL server address
     - `SQL_DATABASE`: Your database name
     - `SQL_USER`: Database username
     - `SQL_PASSWORD`: Database password
     - `SECRET_KEY`: Your secret key for JWT

4. **Deploy your code**
   - Use Azure Extensions in VS Code, or
   - Set up GitHub Actions deployment, or
   - Run the `deploy.sh` script for a manual deployment

## Troubleshooting

If you encounter issues with your deployment:

1. Check the application logs in Azure Portal
2. Verify the startup command is correct
3. Make sure all environment variables are properly set
4. Test the /health endpoint to check basic functionality
5. Examine worker timeouts in logs

## Local Development

To run the API locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
python run.py
```

The API will be available at http://localhost:8000

## API Endpoints

- `/register` - User registration
- `/token` - Login and get access token
- `/verify-email` - Email verification
- `/request-password-reset` - Request password reset
- `/reset-password` - Reset password
- `/refresh` - Refresh access token
- `/logout` - Logout user
- `/ping` - Health check endpoint