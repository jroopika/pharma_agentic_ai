# Jenkins Pipeline Example for Tomcat Deployment

This directory contains example configurations for deploying to Tomcat from Jenkins.

## File Descriptions

- `tomcat-users.xml` - Example Tomcat user configuration with proper roles
- `Jenkinsfile` - Example Jenkins pipeline for building and deploying
- `deploy-config.md` - Jenkins job configuration instructions

## Quick Setup

1. **Configure Tomcat:**
   - Copy `tomcat-users.xml` content to your Tomcat's `conf/tomcat-users.xml`
   - Change all passwords to secure values
   - Restart Tomcat

2. **Configure Jenkins:**
   - Add credentials in Jenkins (Manage Jenkins → Credentials)
   - Username: `deployer`
   - Password: (the password from tomcat-users.xml)
   - ID: `tomcat-deployer`

3. **Configure Deployment:**
   - In Jenkins job, add "Deploy war/ear to a container" post-build action
   - Container: Tomcat 9.x Remote
   - Manager URL: `http://your-server:8080/manager/text`
   - Credentials: Select `tomcat-deployer`

## Testing the Configuration

Test Tomcat credentials from command line:

```bash
# List deployed applications (should work if configured correctly)
curl -u deployer:YOUR_PASSWORD http://localhost:8080/manager/text/list

# Expected output: list of applications like:
# OK - Listed applications for virtual host [localhost]
# /:running:0:ROOT
# /manager:running:0:manager
```

If you get 401 error, check:
- Username/password are correct
- User has `manager-script` role
- Tomcat has been restarted after configuration changes

## Security Notes

⚠️ **Never commit actual passwords to version control!**

- Use environment variables or Jenkins credentials
- Use strong, unique passwords for each environment
- Limit Tomcat Manager access by IP when possible
- Use HTTPS in production environments
