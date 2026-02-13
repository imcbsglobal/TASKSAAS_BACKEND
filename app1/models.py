# models.py
from django.db import models

class AccUser(models.Model):
    """
    Legacy table already exists in PostgreSQL:
        acc_users (
            id          varchar PK,
            pass        varchar,
            role        varchar,
            accountcode varchar,
            client_id   varchar
        )
    """
    id          = models.CharField(max_length=64, primary_key=True, db_column='id')
    password    = models.CharField(max_length=128, db_column='pass')
    role        = models.CharField(max_length=32, blank=True, null=True)
    accountcode = models.CharField(max_length=64, blank=True, null=True)
    client_id   = models.CharField(max_length=64, blank=True, null=True, db_column='client_id')

    class Meta:
        db_table = 'acc_users'
        managed  = False          # table already exists 



# models.py - Add this new model
class Misel(models.Model):
    """
    MISEL database table model
    """
    id = models.AutoField(primary_key=True)
    firm_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phones = models.CharField(max_length=50)
    mobile = models.CharField(max_length=50, blank=True, null=True)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    address3 = models.CharField(max_length=255)
    pagers = models.CharField(max_length=255)
    tinno = models.CharField(max_length=50)
    client_id = models.CharField(max_length=64)

    class Meta:
        db_table = 'misel'
        managed = False  # Since the table already 
        




class AccMaster(models.Model):
    """
    Account Master table - contains account information
    Connected via 'code' field to other tables
    """
    code = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    super_code = models.CharField(max_length=5, blank=True, null=True)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    credit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    phone2 = models.CharField(max_length=60, blank=True, null=True)
    openingdepartment = models.CharField(max_length=100, blank=True, null=True)
    area = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=60, blank=True, null=True)
    gstin = models.CharField(max_length=30, blank=True, null=True)
    remarkcolumntitle = models.CharField(max_length=50, blank=True, null=True)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_master'
        managed = False  # Since the table already exists
        unique_together = ('code', 'client_id')


class AccLedgers(models.Model):
    """
    Account Ledgers table - contains transaction records
    Connected via 'code' field to AccMaster
    """
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=30)  # Links to AccMaster.code
    particulars = models.CharField(max_length=500, blank=True, null=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    credit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    entry_mode = models.CharField(max_length=20, blank=True, null=True)
    entry_date = models.DateField(blank=True, null=True)#
    voucher_no = models.IntegerField(blank=True, null=True)
    narration = models.TextField(blank=True, null=True)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_ledgers'
        managed = False  # Since the table already exists


class AccInvmast(models.Model):
    """
    Invoice Master table - contains invoice information
    Connected via 'customerid' field to AccMaster.code
    """
    id = models.AutoField(primary_key=True)
    modeofpayment = models.CharField(max_length=10, blank=True, null=True)
    customerid = models.CharField(max_length=30, blank=True, null=True)  # Links to AccMaster.code
    invdate = models.DateField(blank=True, null=True)#
    nettotal = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    paid = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    bill_ref = models.CharField(max_length=100, blank=True, null=True)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_invmast'
        managed = False  # Since the table alrea



class CashAndBankAccMaster(models.Model):
    """
    Cash and Bank Account Master table
    Stores cash and bank account information
    super_code determines if it's CASH or BANK
    """
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=250)
    super_code = models.CharField(max_length=5, blank=True, null=True)  # CASH or BANK
    opening_balance = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    opening_date = models.DateField(blank=True, null=True)
    debit = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    credit = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'cashandbankaccmaster'
        managed = False  # Since the table already exists
        unique_together = ('code', 'client_id')



class AccProduct(models.Model):
    code = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    catagory = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        db_column="catagory"
    )
    taxcode = models.CharField(max_length=10, blank=True, null=True)
    product = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    defected = models.CharField(max_length=5, blank=True, null=True)
    text6 = models.CharField(max_length=200, blank=True, null=True)
    settings = models.CharField(max_length=200, blank=True, null=True)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_product'
        managed = False


class AccProductBatch(models.Model):
    productcode = models.ForeignKey(
        AccProduct,
        on_delete=models.DO_NOTHING,
        db_column='productcode',
        related_name='batches'
    )
    salesprice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    secondprice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    thirdprice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    fourthprice = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    nlc1 = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    bmrp = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    expirydate = models.DateField(null=True, blank=True)
    modified = models.DateField(null=True, blank=True)
    modifiedtime = models.TimeField(null=True, blank=True)
    settings = models.CharField(max_length=200, blank=True, null=True)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_productbatch'
        managed = False


class AccProductPhoto(models.Model):
    code = models.ForeignKey(
        AccProduct,
        on_delete=models.DO_NOTHING,
        db_column='code',
        related_name='photos'
    )
    url = models.CharField(max_length=500, blank=True, null=True)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_productphoto'
        managed = False




# =====================================================
# ✅ GODDOWN MODELS (THIS IS WHAT YOU ASKED)
# =====================================================

# -------------------------------
# GODDOWN MASTER
# -------------------------------
class AccGoddown(models.Model):
    goddownid = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_goddown'
        managed = False

    def __str__(self):
        return self.name


# -------------------------------
# GODDOWN STOCK
# -------------------------------
class AccGoddownStock(models.Model):
    id = models.AutoField(primary_key=True)
    goddownid = models.CharField(max_length=50)
    product = models.CharField(max_length=200)   # matches acc_product.code
    quantity = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    barcode = models.CharField(max_length=200, null=True, blank=True)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_goddownstock'
        managed = False
        indexes = [
            models.Index(fields=['product', 'client_id']),
        ]

class AccPriceCode(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=30)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_pricecode'
        managed = False
        unique_together = ('code', 'client_id')

    def __str__(self):
        return self.name



class AccProductPhoto(models.Model):
    """Product photos table"""
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=30, blank=True, null=True)
    url = models.CharField(max_length=300, blank=True, null=True)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_productphoto'
        managed = True
        indexes = [
            models.Index(fields=['code', 'client_id']),
        ]





class AccSalesTypes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, blank=True, null=True)
    goddown = models.CharField(max_length=50, blank=True, null=True)
    user = models.CharField(max_length=50, blank=True, null=True)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_sales_types'
        managed = True



class AccGoddown(models.Model):
    goddownid = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_goddown'
        managed = True



class AccGoddownStock(models.Model):
    id = models.AutoField(primary_key=True)
    goddownid = models.CharField(max_length=50)
    product = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    barcode = models.CharField(max_length=200, null=True, blank=True)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'acc_goddownstock'
        managed = True


class AccDepartments(models.Model):
    department_id = models.CharField(max_length=30)
    department = models.CharField(max_length=30)
    client_id = models.CharField(max_length=100)

    class Meta:
        db_table = "acc_departments"   # <-- IMPORTANT: link Django to real table name

    def __str__(self):
        return self.department



from django.db import models

class Collection(models.Model):

    STATUS_CHOICES = [
        ('uploaded to server', 'Uploaded to Server'),
        ('completed', 'Completed'),
    ]

    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    place = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=50)
    client_id = models.CharField(max_length=100)

    # ✅ Optional fields
    cheque_no = models.CharField(max_length=100, blank=True, null=True)
    ref_no = models.CharField(max_length=100, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)

    # created info
    created_by = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    # ✅ uploaded info (AUTO when status change)
    uploaded_date = models.DateField(blank=True, null=True)
    uploaded_time = models.TimeField(blank=True, null=True)
    uploaded_username = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='uploaded to server'
    )

    class Meta:
        db_table = 'collection'
        managed = True

    def __str__(self):
        return f"{self.code} - {self.name}"

from django.db import models
import uuid

class ItemOrders(models.Model):

    STATUS_CHOICES = [
        ('uploaded to server', 'Uploaded to Server'),
        ('completed', 'Completed'),
    ]

    order_id = models.CharField(max_length=50, editable=False)

    customer_name = models.CharField(max_length=200)
    customer_code = models.CharField(max_length=100)
    area = models.CharField(max_length=200)

    product_name = models.CharField(max_length=200)
    item_code = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100)

    payment_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    client_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    remark = models.TextField(blank=True, null=True)

    device_id = models.CharField(max_length=100)

    # ✅ SAME AS COLLECTION
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='uploaded to server'
    )

    status_changed_date = models.DateField(blank=True, null=True)
    status_changed_time = models.TimeField(blank=True, null=True)
    status_changed_by = models.CharField(max_length=100, blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            import uuid
            self.order_id = f"ORD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = "item_orders"
        ordering = ['-id']





