# Tomcat Deployment Troubleshooting Guide

Quick reference for resolving common Jenkins-to-Tomcat deployment issues.

## 401 Unauthorized Error

**Error Message:**
```
org.codehaus.cargo.container.tomcat.internal.TomcatManagerException: 
HTTP request failed, response code: 401
```

### Causes and Solutions

#### 1. Missing or Incorrect Credentials
**Check:**
- Jenkins credentials exist (Manage Jenkins → Credentials)
- Username and password match `tomcat-users.xml`
- No typos in username or password

**Test:**
```bash
curl -u deployer:password http://localhost:8080/manager/text/list
```

#### 2. Wrong Role Assignment
**Problem:** User has `manager-gui` role instead of `manager-script`

**Solution:** In `tomcat-users.xml`:
```xml
<!-- WRONG - will cause 401 for Jenkins -->
<user username="deployer" password="pass" roles="manager-gui"/>

<!-- CORRECT - Jenkins needs manager-script -->
<user username="deployer" password="pass" roles="manager-script"/>
```

#### 3. Tomcat Not Restarted
**Problem:** Changes to `tomcat-users.xml` not applied

**Solution:**
```bash
# Windows
net stop Tomcat9
net start Tomcat9

# Linux
sudo systemctl restart tomcat9
```

#### 4. Manager App Not Deployed
**Check:** Verify Manager app is running
```bash
curl http://localhost:8080/manager/text/list
# Should return HTML login page or 401 (not 404)
```

## 403 Forbidden Error

**Error Message:**
```
HTTP response code: 403 Forbidden
```

### Causes and Solutions

#### 1. IP Restriction
**Problem:** Manager app restricts access by IP

**Check:** `conf/Catalina/localhost/manager.xml`
```xml
<!-- May contain IP restrictions -->
<Valve className="org.apache.catalina.valves.RemoteAddrValve"
       allow="127\.0\.0\.1" />
```

**Solution:** Add Jenkins server IP to allow list

#### 2. Missing Role
**Problem:** User exists but lacks proper role

**Solution:** Verify user has `manager-script` role:
```xml
<user username="deployer" password="pass" roles="manager-script,manager-status"/>
```

## 404 Not Found Error

**Error Message:**
```
HTTP response code: 404 Not Found
```

### Causes and Solutions

#### 1. Wrong Manager URL
**Problem:** Incorrect URL format in Jenkins

**Wrong URLs:**
```
http://localhost:8080/manager         # Missing /text
http://localhost:8080/manager/html    # Wrong endpoint
http://localhost:8080/               # Missing /manager
```

**Correct URL:**
```
http://localhost:8080/manager/text
```

#### 2. Manager App Not Installed
**Check:** Manager app WAR file exists
- Windows: `webapps/manager/`
- Linux: `/var/lib/tomcat9/webapps/manager/`

**Solution:** Reinstall Tomcat or deploy Manager app manually

## Connection Refused Error

**Error Message:**
```
Connection refused
```

### Causes and Solutions

#### 1. Tomcat Not Running
**Check:**
```bash
# Windows
netstat -an | findstr 8080

# Linux
netstat -tln | grep 8080
sudo systemctl status tomcat9
```

**Solution:** Start Tomcat

#### 2. Wrong Port
**Problem:** Tomcat running on different port

**Check:** `conf/server.xml`
```xml
<Connector port="8080" protocol="HTTP/1.1" ... />
```

#### 3. Firewall Blocking
**Check:** Firewall rules

**Solution:**
```bash
# Linux - allow port 8080
sudo ufw allow 8080/tcp

# Windows - add firewall rule
netsh advfirewall firewall add rule name="Tomcat" dir=in action=allow protocol=TCP localport=8080
```

## Context Already Exists Error

**Error Message:**
```
FAIL - Application already exists at path /myapp
```

### Solutions

#### Option 1: Enable Auto-Undeploy in Jenkins
Configure deployment to undeploy before deploying

#### Option 2: Manual Undeploy
```bash
curl -u deployer:password \
     http://localhost:8080/manager/text/undeploy?path=/myapp
```

#### Option 3: Use Update Parameter
```bash
curl -u deployer:password \
     --upload-file app.war \
     "http://localhost:8080/manager/text/deploy?path=/myapp&update=true"
```

## SSL/TLS Certificate Errors

**Error Message:**
```
SSL certificate validation failed
```

### Solutions

#### Option 1: Use Proper Certificate
Install valid SSL certificate on Tomcat

#### Option 2: Configure Jenkins to Trust Certificate
Add certificate to Jenkins Java keystore

#### Option 3: Disable SSL Verification (Not Recommended)
For testing only - do not use in production

## Verification Checklist

Use this checklist to verify your configuration:

- [ ] Tomcat is running (`netstat -an | findstr 8080` or `grep 8080`)
- [ ] Manager app is deployed and accessible
- [ ] User exists in `tomcat-users.xml`
- [ ] User has `manager-script` role (not just `manager-gui`)
- [ ] Password is correct (no trailing spaces)
- [ ] Tomcat restarted after configuration changes
- [ ] Jenkins credentials configured with correct username/password
- [ ] Jenkins uses correct Manager URL (ends with `/manager/text`)
- [ ] Firewall allows connections from Jenkins to Tomcat
- [ ] No IP restrictions in `manager.xml` (or Jenkins IP is allowed)

## Testing Script

Save this as `test-tomcat-deploy.sh` and run to verify configuration:

```bash
#!/bin/bash

# Configuration
TOMCAT_URL="http://localhost:8080"
USERNAME="deployer"
PASSWORD="your_password"

echo "Testing Tomcat Manager access..."

# Test 1: List applications
echo -e "\nTest 1: Listing applications"
curl -u ${USERNAME}:${PASSWORD} ${TOMCAT_URL}/manager/text/list

# Test 2: Server status
echo -e "\n\nTest 2: Server status"
curl -u ${USERNAME}:${PASSWORD} ${TOMCAT_URL}/manager/text/serverinfo

# Test 3: Check roles
echo -e "\n\nTest 3: Check deployed apps"
curl -u ${USERNAME}:${PASSWORD} ${TOMCAT_URL}/manager/text/list | grep -E "OK|FAIL"

echo -e "\n\nIf all tests show 'OK', configuration is correct!"
```

## Common Jenkins Configuration Mistakes

### Mistake 1: Using Wrong Credential Type
**Wrong:** SSH Username with private key
**Correct:** Username with password

### Mistake 2: Wrong Container Type
**Wrong:** Tomcat 7.x when using Tomcat 9
**Correct:** Match Tomcat version (Tomcat 9.x Remote)

### Mistake 3: Missing /text in URL
**Wrong:** `http://localhost:8080/manager`
**Correct:** `http://localhost:8080/manager/text`

### Mistake 4: Using GUI User for Jenkins
**Wrong:** Using user with `manager-gui` role
**Correct:** Using user with `manager-script` role

## Getting Help

If issues persist:

1. **Check Tomcat Logs:**
   - `logs/catalina.out`
   - `logs/localhost_access_log.txt`
   - `logs/manager.log`

2. **Check Jenkins Console Output:**
   - Full deployment stack trace
   - HTTP response codes and messages

3. **Enable Debug Logging:**
   In `conf/logging.properties`:
   ```properties
   org.apache.catalina.manager.level = FINE
   ```

4. **Test with curl:**
   ```bash
   # Verbose output shows full HTTP exchange
   curl -v -u deployer:password \
        http://localhost:8080/manager/text/list
   ```

## Quick Fix Commands

```bash
# Restart Tomcat (Linux)
sudo systemctl restart tomcat9

# Restart Tomcat (Windows)
net stop Tomcat9 && net start Tomcat9

# Test credentials
curl -u deployer:password http://localhost:8080/manager/text/list

# View Tomcat logs (Linux)
tail -f /var/log/tomcat9/catalina.out

# View Tomcat logs (Windows)
type "C:\Program Files\Apache Software Foundation\Tomcat 9.0\logs\catalina.*.log"

# Check if Tomcat is running
netstat -an | findstr 8080   # Windows
netstat -tln | grep 8080     # Linux
```
