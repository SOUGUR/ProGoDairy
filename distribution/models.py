from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from milk.models import CompositeSample
from django.core.validators import RegexValidator
from django.utils import timezone


validate_mobile = RegexValidator(
    regex=r'^[0-9]{10,17}$',
    message="Enter a valid mobile number."
)

class Route(models.Model):
    name = models.CharField(max_length=100, unique=True)
    plant = models.ForeignKey("plants.Plant", on_delete=models.CASCADE, related_name="routes",null=True, blank=True) 
    def __str__(self):
        return self.name

class VehicleDriver(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=17, validators=[validate_mobile])
    licence_no = models.CharField(max_length=50)
    licence_expiry = models.DateField()
    from_date = models.DateField()        # first day this driver is valid
    to_date = models.DateField(null=True, blank=True)  # NULL = currently active

    def __str__(self):
        return f"{self.name} ({self.vehicle.vehicle_id})"

class Distributor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    address = models.TextField()
    license_number = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"({self.user.username if self.user else 'No user'})"

class Vehicle(models.Model):
    distributor = models.ForeignKey(
        'Distributor',
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    name = models.CharField(max_length=100)
    vehicle_id = models.CharField(max_length=50, unique=True)
    capacity_liters = models.FloatField(null=True, blank=True) 
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles'
    )

    @property
    def is_available(self):
        return not self.transfers.filter(status__in=['scheduled', 'in_transit']).exists()

    def __str__(self):
        return f"{self.name} ({self.vehicle_id})"
    
class MilkTransfer(models.Model):
    SOURCE_CHOICES = [
        ('on_farm_tank', 'On-Farm Tank'),
        ('bulk_cooler', 'Bulk Cooler'),
        ('can_collection', 'Can Collection'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
    ]

    vehicle = models.ForeignKey(
        'Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfers'
    )

    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        null=True,
        blank=True
    )

    bulk_cooler = models.ForeignKey(
        'collection_center.BulkCooler',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='milk_transfers'
    )
    on_farm_tank = models.ForeignKey(
        'suppliers.OnFarmTank',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='milk_transfers'
    )
    can_collection = models.ForeignKey(
        'suppliers.CanCollection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='milk_transfers'
    )

    destination = models.ForeignKey(
    'plants.Plant', 
    on_delete=models.SET_NULL, 
    blank=True, 
    null=True,
    related_name='transfers_as_destination'
    )

    transfer_date = models.DateTimeField(auto_now_add=True)
    arrival_datetime = models.DateTimeField(null=True, blank=True)

    departure_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight of milk (in kg) while leaving the cooperative/source."
    )

    arrival_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight of milk (in kg) while arriving at the destination."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    total_volume = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    emptied_at = models.DateTimeField(null=True, blank=True)

    silo = models.ForeignKey(
        'plants.Silo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_transfers',
        help_text="The silo this milk is being transferred into."
    )


    def clean(self):
        sources = [self.bulk_cooler, self.on_farm_tank, self.can_collection]
        if sum(1 for s in sources if s is not None) > 1:
            raise ValidationError("Milk transfer can have only one source location.")

        if self.source_type == 'bulk_cooler' and not self.bulk_cooler:
            raise ValidationError("Source type is Bulk Cooler but no Bulk Cooler is set.")
        if self.source_type == 'on_farm_tank' and not self.on_farm_tank:
            raise ValidationError("Source type is On-Farm Tank but no On-Farm Tank is set.")
        if self.source_type == 'can_collection' and not self.can_collection:
            raise ValidationError("Source type is Can Collection but no Can Collection is set.")
        
        if self.silo and self.total_volume is not None:
            available_space = self.silo.capacity_liters - self.silo.current_volume

        if self.total_volume is not None and self.total_volume <= 0:
            raise ValidationError("Transfer volume must be greater than zero.")

        if self.silo and self.total_volume is not None:
            available_space = self.silo.capacity_liters - self.silo.current_volume
            if self.total_volume > available_space:
                raise ValidationError(
                    f"Cannot transfer {self.total_volume}L into silo '{self.silo.name}'. "
                    f"Available space: {available_space}L. "
                    f"Current volume: {self.silo.current_volume}L / {self.silo.capacity_liters}L."
                )

    
    def save(self, *args, **kwargs):
        if not self.pk and self.total_volume is None:
            self.total_volume = self.calculate_total_volume(save=False)

        self.full_clean()
        super().save(*args, **kwargs)

        if self.status == 'completed' and self.silo:
            self.silo.update_current_volume()

    def calculate_total_volume(self, save=True):
        if self.bulk_cooler:
            self.total_volume = self.bulk_cooler.current_volume_liters
        elif self.on_farm_tank:
            self.total_volume = self.on_farm_tank.current_volume_liters
        elif self.can_collection:
            self.total_volume = self.can_collection.total_volume_liters
        else:
            self.total_volume = 0
        if save and self.pk:  
            super().save(update_fields=['total_volume'])
        return self.total_volume

    def __str__(self):
        source = self.bulk_cooler or self.on_farm_tank or self.can_collection or "Unknown Source"
        return f"Transfer {self.id} {source.name} → {self.transfer_date}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['on_farm_tank'],
                name='unique_transfer_per_on_farm_tank',
                condition=models.Q(on_farm_tank__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['bulk_cooler'],
                name='unique_transfer_per_bulk_cooler',
                condition=models.Q(bulk_cooler__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['can_collection'],
                name='unique_transfer_per_can_collection',
                condition=models.Q(can_collection__isnull=False)
            ),
        ]

class CIPRecord(models.Model):
    vehicle = models.ForeignKey(
        'Vehicle',
        on_delete=models.CASCADE,
        related_name='cip_records'
    )
    certificate_no = models.CharField(max_length=50, unique=True)
    wash_type = models.CharField(
        max_length=20,
        choices=[('Caustic', 'Caustic'), ('Acid', 'Acid'), ('Sanitiser', 'Sanitiser'), ('Full-CIP', 'Full-CIP')]
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    expiry_at = models.DateTimeField()        
    caustic_temp_c = models.FloatField(null=True, blank=True)
    acid_temp_c = models.FloatField(null=True, blank=True)
    caustic_conc_pct = models.FloatField(null=True, blank=True)
    acid_conc_pct = models.FloatField(null=True, blank=True)
    final_rinse_cond_ms = models.FloatField(null=True, blank=True)
    operator_code = models.CharField(max_length=30)
    passed = models.BooleanField(default=True)

    class Meta:
        ordering = ['-finished_at']
        indexes = [
            models.Index(fields=['vehicle', '-finished_at']),
            models.Index(fields=['expiry_at']),
        ]

    def __str__(self):
        return f"{self.vehicle.vehicle_id} CIP-{self.certificate_no} ({self.finished_at:%Y-%m-%d %H:%M})"

    
class GatePass(models.Model):
    PASS_STATUS = [
        ("draft", "Draft"),          # not yet printed
        ("open", "Open"),            # vehicle left, not yet returned / completed
        ("completed", "Completed"),  # vehicle returned, seals broken, milk received
        ("cancelled", "Cancelled"),  # never left
    ]
    gate_pass_status = models.CharField(max_length=12, choices=PASS_STATUS, default="draft")

    milk_transfer = models.ForeignKey(
        "distribution.MilkTransfer",
        on_delete=models.CASCADE,
        related_name="gate_passes",
        help_text="The transfer that this pass certifies.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    issued_at  = models.DateTimeField(null=True, blank=True)  
    completed_at = models.DateTimeField(null=True, blank=True)

    # --- WEIGHTS ------------------------------------------------------------
    empty_tare_kg = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Vehicle + tanker completely empty"
    )

    net_volume_l = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Net litres @ standard density"
    )
    density_kg_per_l = models.DecimalField(
        max_digits=5, decimal_places=4, default=1.0320
    )

    # CIP REFERENCE 
    cip_record = models.ForeignKey(
        "distribution.CIPRecord",
        on_delete=models.RESTRICT,  
        related_name="gate_passes",
    )

    # ROUTE & ETA 
    route = models.ForeignKey(
        "distribution.Route",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gate_passes",
    )
    expected_arrival_plant = models.DateTimeField()

    # DRIVER 
    driver = models.ForeignKey(
    "distribution.VehicleDriver",
    on_delete=models.RESTRICT,
    related_name="gate_passes",
    help_text="Driver on record when the pass was issued.",
  )
    
    # QC QUICK RESULTS 
    composite_samples = models.ManyToManyField(
        "milk.CompositeSample",
        through="distribution.GatePassQC",
        related_name="gate_passes",
    )


    class Meta:
        ...
        constraints = [
            models.UniqueConstraint(
                fields=["milk_transfer"],        
                condition=models.Q(gate_pass_status="open"),
                name="unique_open_pass_per_transfer",
            )
        ]

    @property
    def vehicle(self):
        return self.milk_transfer.vehicle



    def seal_numbers(self):
        return [s.seal_no for s in self.seals.all()]
    
    def link_samples(self):
        transfer = self.milk_transfer
        source_q = Q()
        if transfer.bulk_cooler:
            source_q |= Q(bulk_cooler=transfer.bulk_cooler)
        if transfer.on_farm_tank:
            source_q |= Q(on_farm_tank=transfer.on_farm_tank)
        if transfer.can_collection:
            source_q |= Q(can_collection=transfer.can_collection)

        samples = CompositeSample.objects.filter(source_q)

        for s in samples:
            GatePassQC.objects.get_or_create(
                gate_pass=self,
                composite_sample=s,
                defaults={"is_primary": s.sample_type == "society test"}
            )
        
    def clean(self):
        super().clean()
        if self.gate_pass_status == "open":
            open_cnt = (
                GatePass.objects.exclude(pk=self.pk)               
                .filter(driver=self.driver, gate_pass_status="open")
                .count()
            )
            if open_cnt:
                raise ValidationError(
                    "Driver already has an open gate-pass. "
                    "Complete or cancel it before creating a new one."
                )

    def save(self, *args, **kwargs):
        # auto-calculate net litres from weight & density
        if not self.net_volume_l and self.gross_weight_kg and self.empty_tare_kg:
            net_kg = float(self.gross_weight_kg) - float(self.empty_tare_kg)
            self.net_volume_l = round(net_kg / float(self.density_kg_per_l), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"GP-{self.id}  {self.vehicle.vehicle_id}  {self.created_at:%d-%b %H:%M}"
    
    
class Seal(models.Model):
    gate_pass = models.ForeignKey(
        GatePass,
        on_delete=models.CASCADE,
        related_name="seals"
    )
    seal_no = models.CharField(max_length=50, unique=True)
    position = models.CharField(
        max_length=30,
        choices=[
            ("top-man", "Top Man-hole"),
            ("outlet", "Outlet Valve"),
            ("pump-hatch", "Pump Hatch"),
            ("instrument-cabinet", "Instrument Cabinet"),
            ("sample-cock", "Sample Cock"),
        ]
    )
    applied_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.position}  {self.seal_no}"
    
class GatePassQC(models.Model):
    gate_pass = models.ForeignKey(
        GatePass,
        on_delete=models.CASCADE,
        related_name="qc_samples"
    )
    composite_sample = models.ForeignKey(
        "milk.CompositeSample",
        on_delete=models.CASCADE,
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="True if this pouch travels with the tanker (usually society test)."
    )

    class Meta:
        unique_together = [('gate_pass', 'composite_sample')]