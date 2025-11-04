# Production Deployment Checklist

## 🔴 CRITICAL - Must Complete Before Production

- [ ] **Generate new SECRET_KEY**
  ```bash
  python generate_secret_key.py
  ```
  Add to production .env file

- [ ] **Set DEBUG=False** in production .env
  ```env
  DEBUG=False
  ```

- [ ] **Update ALLOWED_HOSTS** with production domain
  ```env
  ALLOWED_HOSTS=taskprime.app,www.taskprime.app
  ```

- [ ] **Use strong database password**
  - Minimum 16 characters
  - Mix of letters, numbers, symbols
  - Never use default passwords

- [ ] **Update CORS_ALLOWED_ORIGINS** with production URLs only
  ```env
  CORS_ALLOWED_ORIGINS=https://taskprime.app,https://www.taskprime.app
  ```

- [ ] **Remove test endpoints** from code
  - Delete `test_token` endpoint in views.py

- [ ] **Test environment configuration**
  ```bash
  python test_env_config.py
  ```

## 🟡 IMPORTANT - Highly Recommended

- [ ] **Set up HTTPS/SSL certificates**
  - Use Let's Encrypt or similar
  - Verify SSL redirect is working

- [ ] **Configure production database**
  - Separate database for production
  - Enable automated backups
  - Set up monitoring

- [ ] **Update Cloudflare R2 settings**
  - Use production bucket
  - Set up CDN domain
  - Configure access policies

- [ ] **Set up logging**
  - Ensure logs directory exists and is writable
  - Configure log rotation
  - Set up error alerts

- [ ] **Implement rate limiting**
  - On login endpoint
  - On API endpoints
  - Use Django middleware or nginx

- [ ] **Hash passwords** (if not already done)
  - Use Django's password hashing
  - Never store plain text passwords

## 🟢 RECOMMENDED - Best Practices

- [ ] **Set up monitoring**
  - Application performance monitoring
  - Error tracking (Sentry, etc.)
  - Database performance monitoring

- [ ] **Configure firewall**
  - Allow only necessary ports
  - Restrict database access
  - Enable DDoS protection

- [ ] **Implement caching**
  - Redis or Memcached
  - Cache frequently accessed data
  - Set appropriate TTLs

- [ ] **Set up CI/CD pipeline**
  - Automated testing
  - Automated deployment
  - Rollback capability

- [ ] **Database optimization**
  - Add necessary indexes
  - Analyze slow queries
  - Set up query monitoring

- [ ] **Security audit**
  - Run security scanners
  - Check for vulnerabilities
  - Update dependencies

## 📋 Pre-Deployment Testing

### Local Testing
- [ ] Run all tests
  ```bash
  python manage.py test
  ```

- [ ] Check for migrations
  ```bash
  python manage.py makemigrations --check
  ```

- [ ] Collect static files
  ```bash
  python manage.py collectstatic --noinput
  ```

- [ ] Test with DEBUG=False locally
  ```bash
  DEBUG=False python manage.py runserver
  ```

### Environment Validation
- [ ] All environment variables set
- [ ] Database connection successful
- [ ] Cloud services accessible
- [ ] CORS working correctly

### Functionality Testing
- [ ] Login/Authentication working
- [ ] API endpoints responding
- [ ] File uploads working
- [ ] Database queries optimized

## 🚀 Deployment Steps

### 1. Backup Current System
- [ ] Backup production database
- [ ] Backup current code
- [ ] Document current configuration

### 2. Deploy Code
- [ ] Pull latest code to production server
- [ ] Install/update dependencies
  ```bash
  pip install -r requirements.txt
  ```

### 3. Configure Environment
- [ ] Copy .env.production to .env
- [ ] Update with production values
- [ ] Verify all variables set correctly

### 4. Database Migration
- [ ] Create database backup
- [ ] Run migrations
  ```bash
  python manage.py migrate
  ```
- [ ] Verify data integrity

### 5. Static Files
- [ ] Collect static files
  ```bash
  python manage.py collectstatic --noinput
  ```
- [ ] Verify static files served correctly

### 6. Start Services
- [ ] Start application server (Gunicorn/uWSGI)
- [ ] Start nginx/web server
- [ ] Verify application is running

### 7. Post-Deployment Verification
- [ ] Check application is accessible
- [ ] Test login functionality
- [ ] Test critical API endpoints
- [ ] Monitor logs for errors
- [ ] Check database connections

## 🔍 Post-Deployment Monitoring

### First 24 Hours
- [ ] Monitor error logs continuously
- [ ] Check database performance
- [ ] Monitor API response times
- [ ] Track user login success rate
- [ ] Verify no critical errors

### First Week
- [ ] Review error patterns
- [ ] Optimize slow queries
- [ ] Address any issues reported
- [ ] Monitor resource usage
- [ ] Check backup success

## 🆘 Rollback Plan

If critical issues occur:

1. **Immediate Actions**
   - [ ] Stop new deployments
   - [ ] Assess impact and severity

2. **Rollback Steps**
   - [ ] Restore previous code version
   - [ ] Rollback database migrations (if needed)
   - [ ] Restore previous .env configuration
   - [ ] Restart services

3. **Post-Rollback**
   - [ ] Verify system stability
   - [ ] Document what went wrong
   - [ ] Plan fixes for next deployment

## 📞 Emergency Contacts

- **Database Admin**: [Contact Info]
- **DevOps Team**: [Contact Info]
- **Security Team**: [Contact Info]
- **Management**: [Contact Info]

## 📝 Notes

- Always test changes in staging environment first
- Keep rollback plan ready
- Document all changes
- Monitor closely after deployment

---

**Deployment Date**: _________________
**Deployed By**: _________________
**Version**: _________________
**Sign-off**: _________________

