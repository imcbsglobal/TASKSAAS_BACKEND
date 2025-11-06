# Cloudflare R2 Storage Configuration

## ✅ Setup Complete

Your Django application is now configured to use **Cloudflare R2** as the default file storage backend. Images uploaded through `ImageField` will automatically be stored in Cloudflare R2.

---

## 📋 What Was Configured

### 1. **Model Changes**
- Changed `PunchIn.photo_url` (URLField) → `PunchIn.photo` (ImageField)
- Django now handles file uploads automatically
- Files are uploaded directly to Cloudflare R2

### 2. **Settings Configuration** (`tasksaas_backend/settings.py`)

```python
# Cloudflare R2 as Django Storage Backend
AWS_ACCESS_KEY_ID = CLOUDFLARE_R2_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = CLOUDFLARE_R2_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = CLOUDFLARE_R2_BUCKET
AWS_S3_ENDPOINT_URL = CLOUDFLARE_R2_BUCKET_ENDPOINT
AWS_S3_REGION_NAME = 'auto'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = CLOUDFLARE_R2_PUBLIC_URL

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

### 3. **Installed Packages**
- `django-storages==1.14.4` - Django storage backend for S3-compatible services
- `boto3==1.35.0` - AWS SDK (works with Cloudflare R2)

### 4. **View Updates**
Simplified the `punchin` view:
```python
# Before: Manual upload to R2 with boto3
# Now: Automatic upload via Django
punchin_record = PunchIn.objects.create(
    firm=firm,
    photo=image_file,  # Django handles upload automatically
    # ... other fields
)

# Access URL directly
photo_url = punchin_record.photo.url  # Full R2 URL
```

---

## 🎯 How It Works

### **File Upload Flow**

1. **Frontend sends image** → `request.FILES.get('image')`
2. **Django validates file** → Image validation (size, type)
3. **Save to model** → `photo=image_file`
4. **django-storages automatically**:
   - Uploads file to Cloudflare R2
   - Stores file path in database
   - Returns public URL

### **File Path Structure**
```
punch_images/YYYY/MM/DD/filename.jpg
```
Example: `punch_images/2025/11/06/abc123.jpg`

### **Accessing Files**
```python
# In views
photo_url = punchin_record.photo.url
# Returns: https://your-r2-domain.com/punch_images/2025/11/06/abc123.jpg

# In templates
<img src="{{ punchin.photo.url }}" />
```

---

## 🔧 Environment Variables Required

Add these to your `.env` file:

```env
CLOUDFLARE_R2_BUCKET=your-bucket-name
CLOUDFLARE_R2_BUCKET_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
CLOUDFLARE_R2_ACCESS_KEY=your-r2-access-key
CLOUDFLARE_R2_SECRET_KEY=your-r2-secret-key
CLOUDFLARE_R2_PUBLIC_URL=https://your-custom-domain.com
```

### **Getting Cloudflare R2 Credentials**

1. Go to Cloudflare Dashboard → R2
2. Create a bucket (e.g., `punch-images-prod`)
3. Generate API Tokens:
   - Navigate to **R2** → **Manage R2 API Tokens**
   - Create API Token with permissions:
     - Object Read & Write
     - Admin Read & Write
4. Set up custom domain:
   - R2 bucket → Settings → Public Access
   - Add custom domain (e.g., `cdn.taskprime.app`)
   - Update DNS records as instructed

---

## 🚀 Benefits of This Setup

### **1. Automatic Uploads**
✅ No manual boto3 code  
✅ Django handles everything  
✅ Consistent with Django patterns  

### **2. Easy to Use**
```python
# Just assign the file!
punchin.photo = uploaded_file
punchin.save()
```

### **3. Built-in Features**
✅ File validation  
✅ Unique filenames  
✅ Path management  
✅ URL generation  

### **4. Scalable**
✅ Offload storage to R2  
✅ Fast CDN delivery  
✅ Unlimited storage  

---

## 📝 Usage Examples

### **Creating Punch-In with Image**
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def punchin(request):
    image_file = request.FILES.get('image')
    
    # Validate image
    if not image_file:
        return Response({'error': 'Image required'}, status=400)
    
    # Create record - Django uploads to R2 automatically
    punchin_record = PunchIn.objects.create(
        firm=firm,
        photo=image_file,  # ← Automatic R2 upload
        latitude=lat,
        longitude=lng,
        # ... other fields
    )
    
    # Get the public URL
    photo_url = punchin_record.photo.url
    
    return Response({
        'photo_url': photo_url,  # Full R2 URL
        # ... other data
    })
```

### **Retrieving Images**
```python
# Get punch-in record
punchin = PunchIn.objects.get(id=123)

# Access image URL
if punchin.photo:
    url = punchin.photo.url  # https://cdn.example.com/punch_images/...
    filename = punchin.photo.name  # punch_images/2025/11/06/abc.jpg
    size = punchin.photo.size  # File size in bytes
```

### **Updating Images**
```python
# Update existing image
new_image = request.FILES.get('new_image')
punchin.photo = new_image
punchin.save()  # Old file deleted, new file uploaded to R2
```

### **Deleting Images**
```python
# Delete the file from R2
punchin.photo.delete(save=False)

# Or delete the entire record (cascades to file)
punchin.delete()  # File automatically removed from R2
```

---

## 🔍 Troubleshooting

### **Issue: "Unable to locate credentials"**
**Solution**: Check `.env` file has correct R2 credentials
```bash
CLOUDFLARE_R2_ACCESS_KEY=...
CLOUDFLARE_R2_SECRET_KEY=...
```

### **Issue: "Access Denied" on upload**
**Solution**: Verify R2 API token has write permissions

### **Issue: Images not accessible**
**Solution**: 
1. Check bucket is public or custom domain configured
2. Verify `CLOUDFLARE_R2_PUBLIC_URL` is correct
3. Check CORS settings in R2 bucket

### **Issue: Wrong image URLs**
**Solution**: Update `AWS_S3_CUSTOM_DOMAIN` in settings:
```python
AWS_S3_CUSTOM_DOMAIN = CLOUDFLARE_R2_PUBLIC_URL.replace('https://', '')
```

---

## 🔒 Security Best Practices

### **1. Restrict File Types**
```python
from django.core.validators import FileExtensionValidator

class PunchIn(models.Model):
    photo = models.ImageField(
        upload_to='punch_images/%Y/%m/%d/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
```

### **2. Limit File Size**
```python
# In view
max_size = 5 * 1024 * 1024  # 5MB
if image_file.size > max_size:
    return Response({'error': 'File too large'}, status=400)
```

### **3. Use Environment Variables**
Never hardcode credentials in code!

### **4. Set Proper R2 Bucket Permissions**
- Private bucket with public custom domain
- Token with minimal required permissions
- Enable R2 bucket versioning

---

## 📊 Monitoring & Maintenance

### **Check R2 Storage Usage**
- Cloudflare Dashboard → R2 → View Usage
- Monitor bandwidth and requests
- Set up billing alerts

### **Database Cleanup**
Old images remain in R2 unless explicitly deleted:
```python
# Clean up orphaned files periodically
from django.core.management.base import BaseCommand
from PunchIn.models import PunchIn

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Get all photo paths from database
        db_files = set(PunchIn.objects.values_list('photo', flat=True))
        
        # Compare with R2 files
        # Delete orphaned files
```

---

## 🎉 Summary

Your Django app now:
- ✅ Automatically uploads images to Cloudflare R2
- ✅ Uses ImageField instead of URLField
- ✅ Generates public URLs automatically
- ✅ Handles file validation
- ✅ No manual boto3 code needed

**Next Steps:**
1. Test image upload endpoint
2. Verify images are accessible via public URL
3. Monitor R2 storage usage
4. Set up backup strategy

---

**Last Updated**: November 6, 2025  
**Version**: 1.0
