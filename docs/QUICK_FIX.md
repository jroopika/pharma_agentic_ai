# Quick Fix: Jenkins 401 Unauthorized Deploying to Tomcat

## The Problem
```
ERROR: Build step failed with exception
org.codehaus.cargo.container.tomcat.internal.TomcatManagerException: 
HTTP request failed, response code: 401
```

## The Solution (3 Steps)

### 1. Edit Tomcat Configuration
Edit `TOMCAT_HOME/conf/tomcat-users.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tomcat-users>
  <role rolename="manager-script"/>
  <user username="deployer" 
        password="your_secure_password" 
        roles="manager-script"/>
</tomcat-users>
```

**Key Point:** Use `manager-script` role, NOT `manager-gui`

### 2. Restart Tomcat

**Windows:**
```cmd
net stop Tomcat9
net start Tomcat9
```

**Linux:**
```bash
sudo systemctl restart tomcat9
```

### 3. Configure Jenkins Credentials

1. Go to: **Manage Jenkins → Manage Credentials**
2. Add credentials:
   - Username: `deployer`
   - Password: `your_secure_password`
   - ID: `tomcat-deployer`

3. In your Jenkins job, configure:
   - **Tomcat URL**: `http://localhost:8080` (no /manager path)
   - **Credentials**: Select the credential you just created
   - **Container**: Tomcat 9.x Remote

## Test It

```bash
# Test credentials work
curl -u deployer:your_secure_password http://localhost:8080/manager/text/list
```

Expected output:
```
OK - Listed applications for virtual host [localhost]
```

## Why This Works

- Jenkins uses the **Tomcat Manager text interface** (API)
- The text interface requires `manager-script` role
- The `manager-gui` role is only for browser access
- They are separate for security reasons (CSRF protection)

## Still Having Issues?

See the full guides:
- **[Complete Deployment Guide](DEPLOYMENT.md)** - Detailed setup instructions
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Diagnose and fix issues
- **[Sample Configs](tomcat-users.xml.sample)** - Copy-paste ready configuration

## Common Mistakes

❌ Using `manager-gui` role instead of `manager-script`  
❌ Not restarting Tomcat after config changes  
❌ Including `/manager` in the Tomcat URL  
❌ Typos in username/password between Tomcat and Jenkins  

✅ Use `manager-script` role for Jenkins  
✅ Always restart Tomcat after editing tomcat-users.xml  
✅ Use base Tomcat URL (e.g., `http://localhost:8080`)  
✅ Double-check credentials match exactly  

---

**Quick Reference Table:**

| Role | Purpose | Use For |
|------|---------|---------|
| manager-gui | Browser access | Human administrators |
| manager-script | API/text interface | Jenkins, automation |
| manager-jmx | JMX access | Monitoring tools |
| manager-status | Status pages | Read-only monitoring |
