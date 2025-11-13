# 🎨 Gallery CTF Challenge

**Category:** Web Security  
**Difficulty:** Medium  
**Type:** File Upload + XSS  

## 📖 Challenge Description

Welcome to the **Art Gallery** - a modern platform where artists can showcase their creativity! Users can upload artwork, interact with the community through likes and comments, and report inappropriate content to our dedicated admin team.

Our gallery supports various image formats including PNG, JPG, GIF, and SVG files. We have implemented security measures to ensure a safe environment for our creative community.

**Your mission:** Help us test our security by finding a way to access sensitive information that might be available to our admin team.

## 🌐 Access Information

- **Gallery Website:** `http://localhost:3001`
- **Admin Bot:** `http://localhost:9998` (Internal service)

## 🚀 Quick Start

1. **Start the services:**
   ```bash
   docker-compose up -d
   ```

2. **Access the gallery:**
   - Open `http://localhost:3001` in your browser
   - Explore the features: upload, like, comment, report

3. **Find the flag:**
   - The flag is stored as a cookie in the admin bot
   - Use the report feature to make the admin visit your content
   - Extract the flag using XSS techniques

## 🎯 Learning Objectives

This challenge teaches:
- **File Upload Security:** Understanding how file type validation can be bypassed
- **XSS (Cross-Site Scripting):** Multiple XSS vectors including SVG-based attacks
- **Content Security Policy:** Working around security restrictions
- **Social Engineering:** Using report mechanisms for payload delivery
- **Bot Interaction:** Understanding automated browser behavior

## 🔧 Technical Details

### Architecture
- **Web Application:** Flask-based gallery with image upload functionality
- **Admin Bot:** Playwright-powered browser automation for content review
- **Database:** In-memory storage for demo purposes
- **Network:** Isolated Docker environment

### Security Features
- File extension validation
- Filename filtering (bypassable)
- Admin-only sections
- Content reporting system

### Potential Vulnerabilities
- File upload validation bypass
- XSS in multiple contexts
- Insufficient input sanitization
- Admin bot cookie exposure

## 🏆 Flag Format
`flag{Gallery_XSS_Master_2024_H@ck3r}`

## 🛠️ For CTF Organizers

### Deployment
```bash
# Clone and start
git clone <repository>
cd Gallery
docker-compose up -d

# Check services
docker-compose ps
docker-compose logs
```

### Monitoring
- Web logs: `docker-compose logs web`
- Bot logs: `docker-compose logs bot`
- Traffic: Monitor webhook.site or setup custom endpoint

### Cleanup
```bash
docker-compose down -v
docker system prune -f
```

## 📚 Additional Resources

- [OWASP File Upload Security](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)
- [XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [SVG Security Considerations](https://github.com/cure53/svg-security-cheatsheet)

## ⚠️ Disclaimer

This challenge is designed for educational purposes only. The vulnerabilities included are intentional and should never be implemented in production systems.

---

**Happy Hacking! 🎭**
