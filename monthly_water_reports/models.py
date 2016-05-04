from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
import logging
import time
import datetime

# model for individual water supplier
class WaterSupplier(models.Model):
    supplier_name = models.CharField("Water Supplier Name", db_index=True, unique=True, max_length=255)
    supplier_slug = models.SlugField("Water Supplier Slug", db_index=True, unique=True, max_length=255, null=True, blank=True)
    supplier_url = models.URLField("URL to Water Supplier Home Page", max_length=1024, null=True, blank=True)
    supplier_active = models.BooleanField("Supplier is active", default=True)
    hydrologic_region = models.CharField("Hydrologic Region", max_length=255, null=True, blank=True)
    hydrologic_region_slug = models.SlugField("Hydrologic Region Slug", db_index=True, max_length=255, null=True, blank=True)
    created_date = models.DateTimeField("Date Created", default=datetime.datetime.now)
    supplier_notes = models.TextField("Notes About This Water Supplier", null=True, blank=True)
    april_7_tier = models.IntegerField("April 7 Reduction Tier", null=True, blank=True)
    april_7_reduction = models.FloatField("April 7 Reduction Percent", null=True, blank=True)
    april_7_rgpcd = models.FloatField("April 7 RGPCD", null=True, blank=True)
    april_18_tier = models.IntegerField("April 18 Reduction Tier", null=True, blank=True)
    april_18_reduction = models.FloatField("April 18 Reduction Percent", null=True, blank=True)
    april_18_rgpcd = models.FloatField("April 18 RGPCD", null=True, blank=True)
    april_28_tier = models.IntegerField("April 28 Reduction Tier", null=True, blank=True)
    april_28_reduction = models.FloatField("April 28 Reduction Percent", null=True, blank=True)
    april_28_rgpcd = models.FloatField("April 28 RGPCD", null=True, blank=True)
    june_5_tier = models.IntegerField("June 5 Reduction Tier", null=True, blank=True)
    june_5_reduction = models.FloatField("June 5 Reduction Percent", null=True, blank=True)
    june_5_rgpcd = models.FloatField("June 5 RGPCD", null=True, blank=True)
    june_5_status = models.CharField("June 5 Status", null=True, blank=True, max_length=255)
    june_11_tier = models.IntegerField("June 11 Reduction Tier", null=True, blank=True)
    june_11_reduction = models.FloatField("June 11 Reduction Percent", null=True, blank=True)
    june_11_rgpcd = models.FloatField("June 11 RGPCD", null=True, blank=True)
    june_11_status = models.CharField("June 11 Status", null=True, blank=True, max_length=255)
    june_11_estimated_savings = models.CharField("June 11 Estimated Savings", null=True, blank=True, max_length=255)
    march_1_reduction = models.FloatField("March 1 2016 Reduction Percent", null=True, blank=True)
    cumulative_percent_saved = models.FloatField("Cumulative Percent Saved Compared to 2013", null=True, blank=True)
    missed_reduction_target_by = models.FloatField("Missed Conservation Standard By Percentage Points", null=True, blank=True)
    reached_initial_reduction_target = models.BooleanField("Supplier met the conservation target", default=False)
    compliance_priority = models.CharField("Compliance Priority", null=True, blank=True, max_length=255)
    category_definition = models.CharField("Compliance Priority Category Definition", null=True, blank=True, max_length=255)
    production_2013_june = models.FloatField(null=True, blank=True)
    production_2013_july = models.FloatField(null=True, blank=True)
    production_2013_aug = models.FloatField(null=True, blank=True)
    production_2013_sept = models.FloatField(null=True, blank=True)
    production_2013_oct = models.FloatField(null=True, blank=True)
    production_2013_nov = models.FloatField(null=True, blank=True)
    production_2013_dec = models.FloatField(null=True, blank=True)
    production_2013_jan = models.FloatField(null=True, blank=True)
    production_2013_feb = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return self.supplier_name

    def save(self, *args, **kwargs):
        super(WaterSupplier, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ("water-supplier-detail", [self.supplier_slug])


# model for individual water supplier
class HydrologicRegion(models.Model):
    hydrologic_region = models.CharField("Hydrologic Region", max_length=255, null=True, blank=True)
    hydrologic_region_slug = models.SlugField("Hydrologic Region Slug", db_index=True, max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.hydrologic_region

    def save(self, *args, **kwargs):
        super(HydrologicRegion, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ("water-region-display", [self.hydrologic_region_slug])


# model for water supplier monthly report
class WaterSupplierMonthlyReport(models.Model):
    report_date = models.DateField("Report Date", db_index=True, blank=True, default=datetime.datetime.now)
    supplier_name = models.ForeignKey(WaterSupplier, to_field="supplier_name")
    supplier_slug = models.SlugField("Water Supplier Slug", db_index=True, max_length=255, null=True, blank=True)
    stage_invoked = models.CharField("Stage Invoked", max_length=255, null=True, blank=True)
    mandatory_restrictions = models.BooleanField("Mandatory Restrictions", default=False)
    reporting_month = models.DateField("Reporting Month", default=datetime.date(2015, 1, 1), blank=True)
    total_monthly_potable_water_production_2014 = models.FloatField("Total Monthly Potable Water Production 2014", null=True, blank=True)
    total_monthly_potable_water_production_2013 = models.FloatField("Total Monthly Potable Water Production 2013", null=True, blank=True)
    units = models.CharField("Units", max_length=255, null=True, blank=True)
    qualification = models.TextField("Qualification", null=True, blank=True)
    total_population_served = models.IntegerField("Total Population Served", null=True, blank=True)
    reported_rgpcd = models.FloatField("Reported Residential Gallons-per-capita-per-day (starting In September 2014)", null=True, blank=True)
    enforcement_actions = models.TextField("Enforcement Actions (Optional)", null=True, blank=True)
    implementation = models.TextField("Implementation (Optional)", null=True, blank=True)
    recycled_water = models.TextField("Recycled Water (Optional)", null=True, blank=True)
    recycled_water_units = models.TextField("Recycled Water Units", null=True, blank=True)
    calculated_production_monthly_gallons_month_2014 = models.FloatField("Calculated Production Monthly Gallons Month 2014", null=True, blank=True)
    calculated_production_monthly_gallons_month_2013 = models.FloatField("Calculated Production Monthly Gallons Month 2013", null=True, blank=True)
    calculated_rgpcd_2014 = models.FloatField("CALCULATED RGPCD 2014 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)", db_index=True, null=True, blank=True)
    calculated_rgpcd_2013 = models.FloatField("CALCULATED RGPCD 2013 (Values calculated by Water Board staff using methodology available at http://www.waterboards.ca.gov/waterrights/water_issues/programs/drought/docs/ws_tools/guidance_estimate_res_gpcd.pdf)", db_index=True, null=True, blank=True)
    percent_residential_use = models.FloatField("Percent Residential Use", null=True, blank=True)
    comments_or_corrections = models.TextField("Comments or Corrections", null=True, blank=True)
    hydrologic_region = models.CharField("Hydrologic Region", db_index=True, max_length=255, null=True, blank=True)
    hydrologic_region_slug = models.SlugField("Hydrologic Region Slug", db_index=True, max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.supplier_name_id

    def save(self, *args, **kwargs):
        super(WaterSupplierMonthlyReport, self).save(*args, **kwargs)


# model for water supplier monthly report
class WaterEnforcementMonthlyReport(models.Model):
    report_date = models.DateField("Report Date", db_index=True, blank=True, default=datetime.datetime.now)
    reported_to_state_date = models.DateField("Date Reported to the State", db_index=True, blank=True, default=datetime.datetime.now)
    reporting_month = models.DateField("Reporting Month", default=datetime.date(2015, 1, 1), blank=True)
    supplier_id = models.IntegerField("Supplier ID", null=True, blank=True)
    supplier_name = models.CharField("Water Supplier Name", db_index=True, max_length=255)
    supplier_slug = models.SlugField("Water Supplier Slug", db_index=True, max_length=255, null=True, blank=True)
    hydrologic_region = models.CharField("Hydrologic Region", db_index=True, max_length=255, null=True, blank=True)
    hydrologic_region_slug = models.SlugField("Hydrologic Region Slug", db_index=True, max_length=255, null=True, blank=True)
    total_population_served = models.IntegerField("Total Population Served", null=True, blank=True)
    mandatory_restrictions = models.BooleanField("Mandatory Restrictions", default=False)
    water_days_allowed_week = models.IntegerField("Water Days Allowed/Week", null=True, blank=True)
    complaints_received = models.IntegerField("Complaints Received", null=True, blank=True)
    follow_up_actions = models.IntegerField("Follow-up Actions", null=True, blank=True)
    warnings_issued = models.IntegerField("Warnings Issued", null=True, blank=True)
    penalties_assessed = models.IntegerField("Penalties Assessed", null=True, blank=True)
    enforcement_comments = models.TextField("Enforcement Comments", null=True, blank=True)

    def __unicode__(self):
        return self.supplier_name

    def save(self, *args, **kwargs):
        super(WaterEnforcementMonthlyReport, self).save(*args, **kwargs)


# model for incentives offered to water customers
class WaterIncentive(models.Model):
    supplier_name = models.ForeignKey(WaterSupplier, to_field="supplier_name")
    incentives_details = models.TextField("Incentives Details", null=True, blank=True)
    incentives_last_updated = models.DateTimeField("Incentive Last Updated", blank=True)
    incentives_offered = models.BooleanField("Incentives Offered", default=False)
    incentives_url = models.URLField("URL Turf Incentive Details", max_length=1024, null=True, blank=True)
    turf_rebate_amount = models.FloatField("Turf Removal Reimbursement Amount", null=True, blank=True)
    turf_removal_details = models.TextField("Turf Removal Details", null=True, blank=True)
    turf_removal_last_updated = models.DateTimeField("Turf Removal Last Updated", blank=True)
    turf_removal_offered = models.BooleanField("Turf Removal Offered", default=False)
    turf_removal_url = models.URLField("URL Turf Removal Details", max_length=1024, null=True, blank=True)

    def __unicode__(self):
        return self.supplier_name_id

    def save(self, *args, **kwargs):
        super(WaterIncentive, self).save(*args, **kwargs)


# model for restrictions in place for water suppliers
class WaterRestriction(models.Model):
    supplier_name = models.ForeignKey(WaterSupplier, to_field="supplier_name")
    restriction_current_status = models.CharField("Current Status", max_length=255, null=True, blank=True)
    restriction_current_url = models.URLField("URL Water Restriction Details", max_length=1024, null=True, blank=True)
    restriction_violation_fine = models.FloatField("Fine amount for violation of restriction", null=True, blank=True)
    restriction_how_enforce = models.TextField("Turf Removal Details", null=True, blank=True)
    restriction = models.BooleanField("Restrictions In Place", default=False)
    #restriction_type
    #restriction_common
    restriction_details = models.TextField("Restriction Details", null=True, blank=True)
    restrictions_last_updated = models.DateTimeField("Restrictions Last Updated", blank=True)

    def __unicode__(self):
        return self.supplier_name_id

    def save(self, *args, **kwargs):
        super(WaterRestriction, self).save(*args, **kwargs)


# model for how consumers can conserve water
class WaterConservationMethod(models.Model):
    method_name = models.CharField("Water Conservation Method Name", max_length=255, null=True, blank=True)
    method_slug = models.SlugField("Water Conservation Method Slug", max_length=255, null=True, blank=True)
    method_text = models.TextField("Water Conservation Method Text", null=True, blank=True)
    method_image_path = models.URLField("Image Path for Conservation Method", max_length=1024, null=True, blank=True)

    def __unicode__(self):
        return self.method_name

    def save(self, *args, **kwargs):
        super(WaterConservationMethod, self).save(*args, **kwargs)
