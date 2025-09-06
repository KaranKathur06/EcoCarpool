# EcoCarpool Deployment Guide

## Overview
This guide provides comprehensive instructions for deploying the EcoCarpool application in production environments.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- PostgreSQL 12+ (recommended) or MySQL 8.0+
- Redis 6.0+ (for caching and sessions)
- Node.js 14+ (for frontend assets)
- Nginx (recommended web server)
- SSL certificate (for HTTPS)

### Hardware Requirements
- **Minimum**: 2 CPU cores, 4GB RAM, 20GB storage
- **Recommended**: 4 CPU cores, 8GB RAM, 50GB SSD storage
- **Production**: 8+ CPU cores, 16GB+ RAM, 100GB+ SSD storage

## Environment Setup

### 1. Server Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. Database Setup
```bash
# PostgreSQL setup
sudo -u postgres createuser --interactive ecocarpool
sudo -u postgres createdb ecocarpool_production -O ecocarpool
sudo -u postgres psql -c "ALTER USER ecocarpool PASSWORD 'your_secure_password';"

# Redis setup
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 3. Application Deployment
```bash
# Create application directory
sudo mkdir -p /var/www/ecocarpool
sudo chown $USER:$USER /var/www/ecocarpool

# Clone repository
cd /var/www/ecocarpool
git clone https://github.com/yourusername/ecocarpool.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Install frontend dependencies
npm install
npm run build
```

## Configuration

### 1. Environment Variables
Create `/var/www/ecocarpool/.env`:
```bash
# Django Settings
SECRET_KEY=your_very_secure_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://ecocarpool:your_secure_password@localhost:5432/ecocarpool_production

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Payment Gateway
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### 2. Django Settings
Update production settings in `settings.py`:
```python
# Add to INSTALLED_APPS
INSTALLED_APPS += [
    'storages',  # For S3 storage
]

# Static and Media files (S3)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/ecocarpool/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Database Migration

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Load initial data (optional)
python manage.py loaddata fixtures/initial_data.json
```

## Web Server Configuration

### 1. Gunicorn Setup
Create `/etc/systemd/system/ecocarpool.service`:
```ini
[Unit]
Description=EcoCarpool Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ecocarpool
Environment="PATH=/var/www/ecocarpool/venv/bin"
ExecStart=/var/www/ecocarpool/venv/bin/gunicorn --workers 3 --bind unix:/var/www/ecocarpool/ecocarpool.sock EcoCarpool.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ecocarpool
sudo systemctl start ecocarpool
```

### 2. Nginx Configuration
Create `/etc/nginx/sites-available/ecocarpool`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/ecocarpool/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/ecocarpool/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/ecocarpool/ecocarpool.sock;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    client_max_body_size 20M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ecocarpool /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Certificate Setup

### Using Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### 1. Log Directory Setup
```bash
sudo mkdir -p /var/log/ecocarpool
sudo chown www-data:www-data /var/log/ecocarpool
```

### 2. Logrotate Configuration
Create `/etc/logrotate.d/ecocarpool`:
```
/var/log/ecocarpool/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload ecocarpool
    endscript
}
```

### 3. System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor application
sudo systemctl status ecocarpool
sudo journalctl -u ecocarpool -f
```

## Backup Strategy

### 1. Database Backup Script
Create `/usr/local/bin/backup-ecocarpool.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/ecocarpool"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U ecocarpool ecocarpool_production > $BACKUP_DIR/db_$DATE.sql

# Media files backup (if stored locally)
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/ecocarpool/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# Make executable and schedule
sudo chmod +x /usr/local/bin/backup-ecocarpool.sh
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-ecocarpool.sh
```

## Performance Optimization

### 1. Database Optimization
```sql
-- PostgreSQL optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
```

### 2. Redis Configuration
Edit `/etc/redis/redis.conf`:
```
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 3. Application Optimization
```bash
# Install additional packages for production
pip install django-redis django-compressor

# Update Django settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## Security Checklist

- [ ] SECRET_KEY is unique and secure
- [ ] DEBUG is set to False
- [ ] ALLOWED_HOSTS is properly configured
- [ ] SSL certificate is installed and configured
- [ ] Security headers are enabled
- [ ] Database credentials are secure
- [ ] File permissions are properly set
- [ ] Firewall is configured (UFW recommended)
- [ ] Regular security updates are applied
- [ ] Backup strategy is implemented
- [ ] Monitoring is in place

## Troubleshooting

### Common Issues

1. **Static files not loading**
   ```bash
   python manage.py collectstatic --noinput
   sudo systemctl restart ecocarpool
   ```

2. **Database connection errors**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Test connection
   psql -U ecocarpool -d ecocarpool_production -h localhost
   ```

3. **Permission errors**
   ```bash
   sudo chown -R www-data:www-data /var/www/ecocarpool
   sudo chmod -R 755 /var/www/ecocarpool
   ```

4. **Memory issues**
   ```bash
   # Check memory usage
   free -h
   
   # Restart services
   sudo systemctl restart ecocarpool nginx redis-server
   ```

### Log Locations
- Application logs: `/var/log/ecocarpool/django.log`
- Nginx access logs: `/var/log/nginx/access.log`
- Nginx error logs: `/var/log/nginx/error.log`
- System logs: `journalctl -u ecocarpool`

## Maintenance

### Regular Tasks
- Monitor disk space and clean old logs
- Update dependencies monthly
- Review and rotate SSL certificates
- Monitor application performance
- Review security logs
- Test backup restoration process

### Update Procedure
```bash
# Backup before update
/usr/local/bin/backup-ecocarpool.sh

# Pull latest changes
cd /var/www/ecocarpool
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart ecocarpool
```

This deployment guide ensures a secure, scalable, and maintainable production environment for the EcoCarpool application.
