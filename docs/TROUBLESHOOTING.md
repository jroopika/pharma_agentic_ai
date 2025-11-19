# Jenkins Tomcat Deployment Troubleshooting Guide

## Quick Diagnosis

Use this guide to quickly identify and resolve Jenkins deployment issues to Tomcat.

## Error: 401 Unauthorized

### Symptoms
```
org.codehaus.cargo.container.tomcat.internal.TomcatManagerException: 
HTTP request failed, response code: 401
```

### Cause
Authentication failure - Jenkins cannot authenticate with Tomcat Manager

### Solutions (in order of likelihood)

#### 1. Missing manager-script Role
**Most Common Cause**

The Tomcat user needs `manager-script` role, not `manager-gui`.

**Fix:**
```xml
<!-- In TOMCAT_HOME/conf/tomcat-users.xml -->
<role rolename="manager-script"/>
<user username="deployer" password="your_password" roles="manager-script"/>
```

**Don't forget to restart Tomcat after changes!**

#### 2. Incorrect Credentials in Jenkins

Verify Jenkins credentials match tomcat-users.xml exactly:
- Username matches (case-sensitive)
- Password matches (no extra spaces)
- Credentials are saved correctly in Jenkins

**Jenkins Path:** 
`Manage Jenkins → Manage Credentials → Add Credentials`

#### 3. Tomcat Not Restarted

Changes to tomcat-users.xml require a Tomcat restart:

**Windows:**
```cmd
net stop Tomcat9
net start Tomcat9
```

**Linux:**
```bash
sudo systemctl restart tomcat9
```

#### 4. Wrong Tomcat URL in Jenkins

Jenkins configuration should use the **base Tomcat URL**, not the manager path:

✅ Correct: `http://localhost:8080`  
❌ Wrong: `http://localhost:8080/manager`

---

## Error: 403 Forbidden

### Symptoms
```
HTTP request failed, response code: 403
```

### Cause
User authenticated successfully but lacks proper authorization

### Solutions

#### 1. User Has Wrong Role

Check that user has `manager-script` role:
```xml
<user username="deployer" password="password" roles="manager-script"/>
```

NOT:
```xml
<user username="deployer" password="password" roles="manager-gui"/>
```

#### 2. Role Not Defined

Ensure the role is defined before being used:
```xml
<role rolename="manager-script"/>
<user username="deployer" password="password" roles="manager-script"/>
```

---

## Error: Connection Refused

### Symptoms
```
Failed to connect to http://localhost:8080
Connection refused
```

### Cause
Cannot reach Tomcat server

### Solutions

#### 1. Tomcat Not Running

**Check if Tomcat is running:**

Windows:
```cmd
netstat -an | findstr 8080
tasklist | findstr tomcat
```

Linux:
```bash
netstat -tulpn | grep 8080
ps aux | grep tomcat
```

**Start Tomcat if not running:**
```cmd
# Windows
net start Tomcat9

# Linux
sudo systemctl start tomcat9
```

#### 2. Wrong Port

Verify Tomcat is using the expected port in `server.xml`:
```xml
<Connector port="8080" protocol="HTTP/1.1" .../>
```

#### 3. Firewall Blocking Connection

Check firewall rules:
```cmd
# Windows
netsh advfirewall firewall show rule name=all | findstr 8080

# Linux
sudo iptables -L -n | grep 8080
sudo ufw status
```

---

## Error: WAR File Not Found

### Symptoms
```
[DeployPublisher][ERROR] Cannot find file matching pattern: target/*.war
```

### Cause
Jenkins cannot find the WAR file to deploy

### Solutions

#### 1. Build Failed

Check that the build step completed successfully:
```
mvn clean package
```

Verify target directory contains WAR file:
```cmd
dir target\*.war  # Windows
ls -l target/*.war  # Linux
```

#### 2. Wrong File Path

Update Jenkins configuration with correct path:
- Relative path: `target/myapp.war`
- Absolute path: `C:\path\to\target\myapp.war`
- Pattern: `target/*.war`

---

## Verification Checklist

Use this checklist to verify your configuration:

### Tomcat Configuration
- [ ] tomcat-users.xml contains `<role rolename="manager-script"/>`
- [ ] Deployment user has `manager-script` role
- [ ] Password in tomcat-users.xml is correct
- [ ] Tomcat has been restarted after configuration changes
- [ ] Tomcat Manager application is accessible

### Jenkins Configuration
- [ ] Deploy plugin is installed
- [ ] Tomcat URL is base URL (not /manager path)
- [ ] Credentials match tomcat-users.xml exactly
- [ ] Username is correct (case-sensitive)
- [ ] Password is correct (no extra spaces)
- [ ] Container type is "Tomcat 9.x Remote"
- [ ] WAR file path is correct

### Network Configuration
- [ ] Tomcat is running and listening on port 8080
- [ ] Jenkins can reach Tomcat (no firewall blocking)
- [ ] Tomcat Manager is deployed and accessible

---

## Testing Your Configuration

### Step 1: Test Tomcat Manager Manually

**Using curl (recommended):**
```bash
curl -u deployer:password http://localhost:8080/manager/text/list
```

**Expected output:**
```
OK - Listed applications for virtual host [localhost]
/:running:0:ROOT
/manager:running:0:manager
```

If you get 401, your credentials are wrong.  
If you get 403, your user lacks manager-script role.

### Step 2: Test Simple Deployment

Create a minimal test job in Jenkins:
1. Create new Freestyle project
2. Add build step: "Execute shell"
   ```bash
   echo "Test deployment"
   ```
3. Add post-build action: "Deploy war/ear to container"
   - Use existing WAR file or create dummy one
   - Configure Tomcat connection
4. Build and check console output

---

## Common Mistakes

### ❌ Using manager-gui for Jenkins
```xml
<!-- WRONG -->
<user username="deployer" password="password" roles="manager-gui"/>
```

### ✅ Correct Configuration
```xml
<!-- CORRECT -->
<role rolename="manager-script"/>
<user username="deployer" password="password" roles="manager-script"/>
```

### ❌ Including /manager in URL
```
Wrong: http://localhost:8080/manager
```

### ✅ Use Base URL
```
Correct: http://localhost:8080
```

### ❌ Not Restarting Tomcat
After editing tomcat-users.xml, always restart Tomcat!

---

## Getting More Help

### Enable Debug Logging

**Tomcat (logging.properties):**
```properties
org.apache.catalina.realm.level = FINE
```

**Jenkins:**
1. Manage Jenkins → System Log
2. Add new log recorder
3. Add logger: `hudson.plugins.deploy` at level `ALL`

### Check Logs

**Tomcat:**
- `TOMCAT_HOME/logs/catalina.out` (Linux)
- `TOMCAT_HOME/logs/catalina.YYYY-MM-DD.log` (Windows)

**Jenkins:**
- Console output of the failing job
- Jenkins system log

### Useful Commands

**Test credentials:**
```bash
curl -u username:password -v http://localhost:8080/manager/text/list
```

**Check Tomcat version:**
```bash
curl http://localhost:8080/
```

**View manager app directly:**
```
http://localhost:8080/manager/html
```

---

## Still Having Issues?

If you've tried all the above and still have problems:

1. **Verify Versions:**
   - Tomcat version (9.x supported)
   - Jenkins Deploy plugin version
   - Java version compatibility

2. **Check Permissions:**
   - File permissions on tomcat-users.xml
   - Directory permissions for webapps folder

3. **Review Security:**
   - RemoteAddrValve restricting access?
   - Security Manager enabled?
   - SSL/TLS configuration issues?

4. **Test with Simple Setup:**
   - Try with a minimal tomcat-users.xml
   - Test with HTTP (not HTTPS) first
   - Use default port 8080

---

## Quick Reference Commands

### Windows
```cmd
# Check if Tomcat is running
netstat -an | findstr 8080

# Restart Tomcat
net stop Tomcat9
net start Tomcat9

# View Tomcat logs
type "%CATALINA_HOME%\logs\catalina.YYYY-MM-DD.log"
```

### Linux
```bash
# Check if Tomcat is running
netstat -tulpn | grep 8080

# Restart Tomcat
sudo systemctl restart tomcat9

# View Tomcat logs
tail -f /var/log/tomcat9/catalina.out
```

### Test Authentication
```bash
# Test credentials (replace with your values)
curl -u deployer:password http://localhost:8080/manager/text/list

# Verbose output for debugging
curl -v -u deployer:password http://localhost:8080/manager/text/list
```
