# Deployment Guide

## Jenkins + Tomcat Deployment Configuration

This guide addresses the common 401 Unauthorized error when deploying WAR files from Jenkins to Tomcat.

### Problem Description

When Jenkins attempts to deploy a WAR file to Tomcat using the Deploy Plugin, you may encounter:

```
org.codehaus.cargo.container.tomcat.internal.TomcatManagerException: 
HTTP request failed, response code: 401, response message: null
```

This error occurs because the Tomcat user lacks the correct roles for programmatic deployment.

### Root Cause

For Tomcat 7 and later, different roles are required for different types of access:

- **manager-gui**: Access to the HTML GUI and status pages (browser access)
- **manager-script**: Access to the text interface and status pages (programmatic/API access)
- **manager-jmx**: Access to the JMX proxy and status pages
- **manager-status**: Access to status pages only

**Jenkins deployments require the `manager-script` role**, not `manager-gui`.

### Solution

#### Step 1: Configure Tomcat Users

Edit the `conf/tomcat-users.xml` file in your Tomcat installation:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tomcat-users xmlns="http://tomcat.apache.org/xml"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://tomcat.apache.org/xml tomcat-users.xsd"
              version="1.0">
  
  <!-- Define the roles required for deployment -->
  <role rolename="manager-script"/>
  
  <!-- Create a user with the manager-script role -->
  <user username="deployer" 
        password="your_secure_password_here" 
        roles="manager-script"/>
  
</tomcat-users>
```

**Important Security Notes:**
- Replace `your_secure_password_here` with a strong password
- Do NOT grant both `manager-gui` and `manager-script` to the same user (CSRF protection)
- Use different users for GUI access and programmatic deployment

#### Step 2: Restart Tomcat

After modifying `tomcat-users.xml`, restart Tomcat for changes to take effect:

**Windows:**
```cmd
net stop Tomcat9
net start Tomcat9
```

**Linux:**
```bash
sudo systemctl restart tomcat9
```

#### Step 3: Configure Jenkins

In your Jenkins job configuration:

1. Go to **Post-build Actions** → **Deploy war/ear to a container**
2. Configure the following:
   - **WAR/EAR files**: `target/*.war` or specific path
   - **Context path**: Your application context (e.g., `Webpath`)
   - **Container**: Select "Tomcat 9.x Remote"
   - **Tomcat URL**: Your Tomcat manager URL (e.g., `http://localhost:8080`)
   - **Credentials**: Add credentials with:
     - Username: `deployer` (matching tomcat-users.xml)
     - Password: Your secure password
     - ID: `tomcat-deployer`

#### Step 4: Verify Configuration

Test the deployment by triggering a Jenkins build. The deployment should succeed with output like:

```
[DeployPublisher][INFO] Attempting to deploy 1 war file(s)
[DeployPublisher][INFO] Deploying C:\...\target\webdemo.war to container Tomcat 9.x Remote
[DeployPublisher][INFO] Deployment successful
```

### Troubleshooting

#### Still Getting 401 Error?

1. **Verify Tomcat restart**: Ensure Tomcat fully restarted after config changes
2. **Check credentials**: Ensure Jenkins credentials match tomcat-users.xml exactly
3. **Verify Tomcat URL**: Should be base URL, not including /manager path
4. **Check role name**: Must be `manager-script` not `manager-gui`
5. **Review Tomcat logs**: Check `logs/catalina.out` for authentication errors

#### Connection Refused Error?

- Verify Tomcat is running: `netstat -an | findstr 8080` (Windows) or `netstat -tulpn | grep 8080` (Linux)
- Check firewall rules allowing port 8080
- Verify Tomcat manager application is deployed

#### 403 Forbidden Error?

- User has authenticated but lacks proper role
- Double-check the `manager-script` role is assigned to the user
- Verify role definition exists in tomcat-users.xml

### Security Best Practices

1. **Use Strong Passwords**: Generate secure passwords for deployment users
2. **Limit Access**: Only grant `manager-script` role to deployment users
3. **Network Security**: Restrict Tomcat manager access to trusted IPs
4. **HTTPS**: Use HTTPS for production deployments
5. **Audit**: Regularly review deployment user accounts
6. **Separate Users**: Use different users for GUI and API access

### Example Complete Configuration

**Tomcat conf/tomcat-users.xml:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<tomcat-users xmlns="http://tomcat.apache.org/xml"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://tomcat.apache.org/xml tomcat-users.xsd"
              version="1.0">
  
  <!-- Roles for different access types -->
  <role rolename="manager-gui"/>
  <role rolename="manager-script"/>
  <role rolename="manager-status"/>
  
  <!-- GUI user (for browser access) -->
  <user username="admin" 
        password="gui_password_123" 
        roles="manager-gui,manager-status"/>
  
  <!-- Deployment user (for Jenkins) -->
  <user username="deployer" 
        password="deploy_password_456" 
        roles="manager-script"/>
  
</tomcat-users>
```

**Jenkins Pipeline Example:**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        
        stage('Deploy') {
            steps {
                deploy adapters: [
                    tomcat9(
                        credentialsId: 'tomcat-deployer',
                        path: '',
                        url: 'http://localhost:8080'
                    )
                ], 
                contextPath: 'Webpath',
                war: 'target/*.war'
            }
        }
    }
}
```

### Additional Resources

- [Apache Tomcat Manager App Documentation](https://tomcat.apache.org/tomcat-9.0-doc/manager-howto.html)
- [Jenkins Deploy Plugin](https://plugins.jenkins.io/deploy/)
- [Tomcat Security Considerations](https://tomcat.apache.org/tomcat-9.0-doc/security-howto.html)

### Quick Reference

| Access Type | Role Required | Use Case |
|-------------|---------------|----------|
| Browser GUI | manager-gui | Human administrators |
| Jenkins/API | manager-script | Automated deployments |
| JMX Tools | manager-jmx | Monitoring tools |
| Status Only | manager-status | Read-only monitoring |

### Summary

The 401 Unauthorized error during Jenkins deployment to Tomcat is resolved by:

1. Adding `manager-script` role to tomcat-users.xml
2. Creating a deployment user with this role
3. Restarting Tomcat
4. Configuring Jenkins with the correct credentials

This ensures Jenkins can programmatically deploy applications via the Tomcat Manager text interface.
