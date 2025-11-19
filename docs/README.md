# Deployment Documentation

This directory contains comprehensive documentation for deploying applications to Tomcat using Jenkins.

## 📚 Documentation Index

### Getting Started
- **[QUICK_FIX.md](QUICK_FIX.md)** - Fast solution for 401 Unauthorized errors (5 minutes)
  - 3-step fix for the most common deployment issue
  - Quick test commands
  - Common mistakes to avoid

### Comprehensive Guides
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide (15-20 minutes)
  - Detailed explanation of Tomcat roles
  - Step-by-step configuration instructions
  - Security best practices
  - Multiple examples and use cases

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Troubleshooting reference
  - Solutions for all common errors (401, 403, connection issues)
  - Verification checklists
  - Debug commands and testing procedures
  - Quick diagnosis flowcharts

### Configuration Files
- **[tomcat-users.xml.sample](tomcat-users.xml.sample)** - Sample Tomcat configuration
  - Ready-to-use tomcat-users.xml template
  - Properly configured roles for Jenkins deployment
  - Security comments and warnings

- **[Jenkinsfile.sample](Jenkinsfile.sample)** - Sample Jenkins pipeline
  - Complete pipeline with all stages
  - Environment configuration
  - Deployment verification
  - Error handling and post-build actions

## 🎯 Which Guide Should I Use?

### Scenario 1: Quick Fix Needed
**You're getting 401 Unauthorized error right now:**
→ Start with **[QUICK_FIX.md](QUICK_FIX.md)**

### Scenario 2: Setting Up New Deployment
**You're configuring Jenkins deployment for the first time:**
→ Read **[DEPLOYMENT.md](DEPLOYMENT.md)** and use **[tomcat-users.xml.sample](tomcat-users.xml.sample)**

### Scenario 3: Something's Wrong
**Deployment is failing with various errors:**
→ Use **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for diagnosis

### Scenario 4: Creating Jenkins Pipeline
**You need a complete pipeline example:**
→ Copy and adapt **[Jenkinsfile.sample](Jenkinsfile.sample)**

## 🔍 Common Issues Quick Links

### 401 Unauthorized Error
This is the **most common issue**. Solution:
1. Add `manager-script` role in tomcat-users.xml
2. Restart Tomcat
3. Update Jenkins credentials

See: [QUICK_FIX.md](QUICK_FIX.md) or [DEPLOYMENT.md](DEPLOYMENT.md#solution)

### 403 Forbidden Error
User authenticated but lacks proper role. Solution:
- Verify user has `manager-script` role
- Check role is defined in tomcat-users.xml

See: [TROUBLESHOOTING.md](TROUBLESHOOTING.md#error-403-forbidden)

### Connection Refused
Cannot reach Tomcat. Solution:
- Verify Tomcat is running
- Check port 8080 is accessible
- Review firewall settings

See: [TROUBLESHOOTING.md](TROUBLESHOOTING.md#error-connection-refused)

## 📋 Configuration Checklist

Before deploying, verify:

### Tomcat Configuration
- [ ] tomcat-users.xml edited with manager-script role
- [ ] Deployment user created with correct credentials
- [ ] Tomcat restarted after changes
- [ ] Tomcat Manager application accessible

### Jenkins Configuration
- [ ] Deploy plugin installed
- [ ] Credentials added (matching Tomcat)
- [ ] Tomcat URL configured (base URL, no /manager)
- [ ] Container type set to "Tomcat 9.x Remote"

### Network
- [ ] Tomcat running on expected port (default 8080)
- [ ] Jenkins can reach Tomcat (no firewall blocking)
- [ ] Manager application deployed at /manager

## 🧪 Testing Your Setup

### Quick Test
```bash
# Replace with your credentials
curl -u deployer:password http://localhost:8080/manager/text/list
```

Expected: `OK - Listed applications...`

### Full Test
1. Create test Jenkins job
2. Deploy sample WAR file
3. Verify deployment in Tomcat Manager
4. Access deployed application

See: [TROUBLESHOOTING.md](TROUBLESHOOTING.md#testing-your-configuration)

## 🔐 Security Notes

**Important security considerations:**
- Always use strong passwords for deployment users
- Never grant both `manager-gui` and `manager-script` to same user
- Use separate credentials for GUI vs API access
- Consider restricting Manager access by IP
- Use HTTPS in production environments
- Never commit real passwords to version control

See: [DEPLOYMENT.md](DEPLOYMENT.md#security-best-practices)

## 📖 Understanding Tomcat Roles

| Role | Access Type | Jenkins Needs This? |
|------|-------------|---------------------|
| manager-gui | Browser/HTML interface | ❌ No |
| manager-script | Text/API interface | ✅ Yes |
| manager-jmx | JMX proxy | ❌ No |
| manager-status | Status pages | ❌ No (optional) |

**Key Point:** Jenkins needs `manager-script`, not `manager-gui`!

## 🆘 Getting Help

If you've tried everything and still have issues:

1. **Check all documentation:**
   - Read through TROUBLESHOOTING.md completely
   - Verify each step in DEPLOYMENT.md
   - Review configuration samples

2. **Enable debug logging:**
   - Jenkins: System Log → Add logger for `hudson.plugins.deploy`
   - Tomcat: Set `org.apache.catalina.realm.level = FINE`

3. **Verify basics:**
   - Tomcat version compatibility (9.x supported)
   - Java version compatibility
   - Plugin versions are up to date
   - No proxy/network issues

4. **Test step by step:**
   - Test Tomcat credentials with curl
   - Verify Manager app works in browser
   - Try manual deployment first
   - Then configure Jenkins

## 📚 Additional Resources

- [Apache Tomcat Documentation](https://tomcat.apache.org/tomcat-9.0-doc/)
- [Jenkins Deploy Plugin](https://plugins.jenkins.io/deploy/)
- [Tomcat Manager How-To](https://tomcat.apache.org/tomcat-9.0-doc/manager-howto.html)

## 🎯 Summary

The most common Jenkins deployment issue (401 Unauthorized) is fixed by:
1. Using `manager-script` role (not `manager-gui`)
2. Restarting Tomcat after configuration changes
3. Ensuring credentials match between Jenkins and Tomcat

For detailed solutions, start with [QUICK_FIX.md](QUICK_FIX.md) for immediate issues, or [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive setup guidance.
