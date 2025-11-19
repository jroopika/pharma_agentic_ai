# Deployment Guide - Jenkins to Tomcat

This guide addresses the Jenkins deployment issue with Tomcat Manager and provides step-by-step instructions to resolve the 401 Unauthorized error.

## Problem Overview

When deploying WAR files from Jenkins to Tomcat using the "Deploy war/ear to a container" plugin, you may encounter a **401 Unauthorized** error:

```
org.codehaus.cargo.container.tomcat.internal.TomcatManagerException: 
HTTP request failed, response code: 401, response message: null
```

This occurs because Jenkins needs proper authentication credentials with the correct Tomcat roles to deploy applications programmatically.

## Root Cause

For **Tomcat 7 and later**, the role system was changed from a single `manager` role to four specific roles:

- `manager-gui` - Access to HTML GUI and status pages (for web browser access)
- `manager-script` - **Required for programmatic deployment** (Jenkins, scripts, APIs)
- `manager-jmx` - Access to JMX proxy and status pages
- `manager-status` - Access to status pages only

**Jenkins requires the `manager-script` role** for deployment, not `manager-gui`.

## Solution: Configure Tomcat User with Correct Roles

### Step 1: Edit tomcat-users.xml

Locate your Tomcat installation's `conf/tomcat-users.xml` file:
- Windows: `C:\Program Files\Apache Software Foundation\Tomcat 9.0\conf\tomcat-users.xml`
- Linux: `/opt/tomcat/conf/tomcat-users.xml` or `/var/lib/tomcat9/conf/tomcat-users.xml`

### Step 2: Add or Update User Configuration

Add the following configuration inside the `<tomcat-users>` tags:

```xml
<tomcat-users xmlns="http://tomcat.apache.org/xml"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://tomcat.apache.org/xml tomcat-users.xsd"
              version="1.0">

  <!-- Define the roles required for Jenkins deployment -->
  <role rolename="manager-script"/>
  <role rolename="manager-status"/>
  
  <!-- Create a deployment user with the manager-script role -->
  <user username="deployer" password="YourSecurePassword123!" roles="manager-script,manager-status"/>
  
</tomcat-users>
```

**Important Security Notes:**
- Use a **strong password** (not the example above)
- Do NOT grant `manager-gui` and `manager-script` to the same user (CSRF protection)
- Consider using different users for GUI access vs. programmatic deployment

### Step 3: Restart Tomcat

After modifying `tomcat-users.xml`, restart Tomcat:

**Windows:**
```cmd
net stop Tomcat9
net start Tomcat9
```

**Linux:**
```bash
sudo systemctl restart tomcat9
# or
sudo service tomcat9 restart
```

### Step 4: Configure Jenkins Credentials

1. **In Jenkins**, navigate to:
   - `Manage Jenkins` → `Manage Credentials`
   - Select the appropriate domain (usually "Global")
   - Click `Add Credentials`

2. **Add new credentials:**
   - Kind: `Username with password`
   - Scope: `Global`
   - Username: `deployer` (the username from tomcat-users.xml)
   - Password: `YourSecurePassword123!` (the password from tomcat-users.xml)
   - ID: `tomcat-deployer` (for reference)
   - Description: `Tomcat Deployment User`

### Step 5: Configure Jenkins Deployment Job

1. In your Jenkins job configuration, go to **Post-build Actions**
2. Select **Deploy war/ear to a container**
3. Configure:
   - **WAR/EAR files**: `target/*.war` or specific path
   - **Context path**: Your application context (e.g., `Webpath`)
   - **Container**: `Tomcat 9.x Remote`
   - **Manager URL**: `http://localhost:8080/manager/text` (adjust host/port as needed)
   - **Credentials**: Select the `tomcat-deployer` credential created in Step 4

### Step 6: Verify Deployment

Run your Jenkins job. The deployment should now succeed without the 401 error.

## Troubleshooting

### Issue: Still Getting 401 Error

**Verify Tomcat user configuration:**
```bash
# Test with curl (replace with your values)
curl -u deployer:YourSecurePassword123! http://localhost:8080/manager/text/list
```

Expected output: List of deployed applications

**Check logs:**
- Jenkins console output
- Tomcat logs: `logs/catalina.out` or `logs/manager.log`

### Issue: 403 Forbidden Error

This may occur if:
- User lacks the `manager-script` role
- Tomcat Manager app is not deployed
- IP restrictions are configured

**Solution:** Verify role assignment and check `conf/Catalina/localhost/manager.xml` for IP restrictions.

### Issue: Connection Refused

**Check:**
- Tomcat is running: `netstat -an | findstr 8080` (Windows) or `netstat -tln | grep 8080` (Linux)
- Correct Manager URL in Jenkins (must end with `/manager/text`, not `/manager`)
- Firewall allows connections

### Issue: Context Already Exists

If redeployment fails with "application already exists":

**Option 1:** Undeploy first in Jenkins job
- Use Jenkins plugin option to undeploy before deploying

**Option 2:** Manual undeploy via Manager
```bash
curl -u deployer:password http://localhost:8080/manager/text/undeploy?path=/Webpath
```

## Security Best Practices

1. **Strong Passwords**: Use complex passwords (minimum 16 characters, mixed case, numbers, symbols)
2. **Separate Users**: Create different users for different purposes:
   - GUI access: `manager-gui` role only
   - Jenkins deployment: `manager-script` role only
3. **IP Restrictions**: Limit Manager access to specific IPs in `manager.xml`:
   ```xml
   <Valve className="org.apache.catalina.valves.RemoteAddrValve"
          allow="127\.0\.0\.1|::1|192\.168\.1\..*" />
   ```
4. **HTTPS**: Use SSL/TLS for Manager connections in production
5. **Regular Updates**: Keep Tomcat and Jenkins updated with security patches

## Complete Example Configuration

### tomcat-users.xml (Production Example)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<tomcat-users xmlns="http://tomcat.apache.org/xml"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://tomcat.apache.org/xml tomcat-users.xsd"
              version="1.0">
  
  <!-- Roles -->
  <role rolename="manager-gui"/>
  <role rolename="manager-script"/>
  <role rolename="manager-status"/>
  
  <!-- GUI user (for web interface) -->
  <user username="admin" password="GuiPassword123!@#" roles="manager-gui,manager-status"/>
  
  <!-- Deployment user (for Jenkins) -->
  <user username="deployer" password="DeployPassword456!@#" roles="manager-script,manager-status"/>
  
</tomcat-users>
```

## Additional Resources

- [Tomcat Manager App Documentation](https://tomcat.apache.org/tomcat-9.0-doc/manager-howto.html)
- [Jenkins Deploy Plugin Documentation](https://plugins.jenkins.io/deploy/)
- [Tomcat Security Considerations](https://tomcat.apache.org/tomcat-9.0-doc/security-howto.html)

## Quick Reference

| Role | Purpose | Use Case |
|------|---------|----------|
| `manager-gui` | Web interface access | Manual management via browser |
| `manager-script` | Programmatic access | **Jenkins, CI/CD, APIs** |
| `manager-jmx` | JMX proxy access | Monitoring tools |
| `manager-status` | Status pages only | Read-only monitoring |

**Remember:** Jenkins needs `manager-script`, not `manager-gui`!
