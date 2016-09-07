from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import Library, Context
from django.conf import settings
from django.utils.timezone import utc
from django.db.models import Q, Avg, Max, Min, Sum, Count
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template import Library
from dateutil import parser
from datetime import datetime, date, time, timedelta
import json
import logging
import decimal
import calculate
import math

logger = logging.getLogger("cali_water_reports")

register = Library()

@register.filter
def currency(dollars):
    dollars = round(int(dollars), 2)
    return "$%s" % (intcomma(int(dollars)))


@register.filter
def neg_to_posi(value):
    return abs(value)


@register.filter
def get_last_year(value):
    last_year = value.year - 3
    output = date(last_year, value.month, value.day)
    return output


@register.filter
def get_last_month(value):
    if value.month == 1:
        last_month = 12
    else:
        last_month = value.month - 1
    output = date(value.year, last_month, value.day)
    return output


@register.filter
def percentage(value):
    return "%s%%" % (value*100)


@register.simple_tag
def standardize_unit_to_gallons(value, unit):
    if unit.upper() == "G":
        output = (value * 1)
    elif unit.upper() == "MG":
        output = (value * 1000000)
    elif unit.upper() == "CCF":
        output = (value * 748)
    elif unit.upper() == "AF":
        output = (value * 325851)
    else:
        output = (value * 1)
    return output


@register.simple_tag
def build_chart_title(data):
    number_of_records = len(data)
    newest_record = data[0]
    oldest_record = data[-1]
    percent_change = calculate.percentage_change(oldest_record, newest_record)
    if percent_change > 0:
        change_trend = "<span class='increase-accent'>Increased</span>"
    else:
        change_trend = "<span class='decrease-accent'>Decreased</span>"
    return change_trend


@register.simple_tag
def build_chart_sentence(data):
    number_of_records = len(data)
    newest_record = data[0]
    oldest_record = data[-1]
    percent_change = calculate.percentage_change(oldest_record, newest_record)
    if percent_change > 0:
        change_trend = "<span class='increase-accent'>increased</span>"
    else:
        change_trend = "<span class='decrease-accent'>decreased</span>"
    return "Here's a view of average daily per capita residential water use over the past %s months. Water use by this agency's residential customers has %s by %s%%, going from an average of %s gallons used by each resident per day to %s." % (number_of_records, change_trend, round(percent_change, 2), round(oldest_record, 2), round(newest_record, 2))


@register.simple_tag
def increase_or_decrease(old_figure, new_figure):
    percent_change = calculate.percentage_change(old_figure, new_figure)
    if percent_change > 0:
        output = "<span class='increase-accent'>increased</span>"
    else:
        output = "<span class='decrease-accent'>decreased</span>"
    return output


@register.simple_tag
def title_increase_or_decrease(old_figure, new_figure):
    percent_change = calculate.percentage_change(old_figure, new_figure)
    if percent_change > 0:
        output = "<span class='increase-accent'>Increased</span>"
    else:
        output = "<span class='decrease-accent'>Decreased</span>"
    return output


@register.simple_tag
def settings_value(name):
    output = getattr(settings, name, "")
    return output


@register.simple_tag
def no_span_increase_or_decrease(old_figure, new_figure):
    percent_change = calculate.percentage_change(old_figure, new_figure)
    if percent_change > 0:
        output = "increased"
    else:
        output = "decreased"
    return output


@register.simple_tag
def compare_to_avg(state_figure, local_figure):
    percent_change = calculate.percentage_change(state_figure, local_figure)
    if local_figure > state_figure:
        percent_change = "%.2f" % round(percent_change, 2)
        output = "<span class='increase-accent'>more</span>"
    else:
        percent_change = "%.2f" % round(percent_change, 2)
        output = "<span class='decrease-accent'>less</span>"
    return output


@register.simple_tag
def percent_change(old_figure, new_figure):
    percent_change = calculate.percentage_change(old_figure, new_figure)
    if percent_change > 0:
        percent_change = "%.2f" % abs(percent_change)
        output = "<span class='increase-accent'>%s percent</span>" % (percent_change)
    else:
        percent_change = "%.2f" % abs(percent_change)
        output = "<span class='decrease-accent'>%s percent</span>" % (percent_change)
    return output

@register.simple_tag
def compare_percent_change(old_figure, new_figure):
    percent_change = calculate.percentage_change(old_figure, new_figure)
    if percent_change > 0:
        percent_change = "%.2f" % abs(percent_change)
        output = "<span class='increase-accent'>%s percent</span>" % (percent_change)
    else:
        percent_change = "%.2f" % abs(percent_change)
        output = "<span class='decrease-accent'>-%s percent</span>" % (percent_change)
    return output

@register.simple_tag
def change_in_reduction_tier(latest_proposal, prior_proposal):
    if latest_proposal == None and prior_proposal == None:
        output = "n/a"
    else:
        if latest_proposal == prior_proposal:
            output = "No Change"
        elif latest_proposal > prior_proposal:
            output = "Increased"
        elif latest_proposal < prior_proposal:
            output = "Decreased"
        else:
            output = "n/a"
    return output


@register.simple_tag
def met_monthly_target(old_figure, new_figure, reduction_target):
    reduction_target = reduction_target * 100
    percent_change = calculate.percentage_change(old_figure, new_figure)
    if percent_change < 0:
        comparison_value = abs(percent_change)
        if comparison_value >= reduction_target:
            output = "as the agency <span class='decrease-accent'>achieved </span> its <span class='decrease-accent'>%s percent</span> reduction target for the month" % ("%.0f" % reduction_target)
        elif comparison_value / reduction_target >= 0.95:
            output = "but <span class='eighty-percent-accent'>missed </span> meeting a <span class='eighty-percent-accent'>%s percent</span> reduction target for the month" % ("%.0f" % reduction_target)
        else:
            output = "but the agency <span class='increase-accent'>fell short</span> of meeting its <span class='increase-accent'>%s percent</span> reduction target for the month" % ("%.0f" % reduction_target)
    else:
        output = "as the agency <span class='increase-accent'>failed</span> to meet its <span class='increase-accent'>%s percent</span> reduction target for the month" % ("%.0f" % reduction_target)
    return output


@register.simple_tag
def met_conservation_target(agency, cumulative_calcs):
    if cumulative_calcs["cum_success"] == True:
        output = "<dl><dd>%s water use <span class='decrease-accent'>%s by %s percent </span> between June 2015 and February 2016 &mdash; the nine months of the initial statewide conservation mandate &mdash; <span class='decrease-accent'>achieving a %s percent reduction</span>.</dd></dl>" % (agency, cumulative_calcs["cum_status"], "%.2f" % cumulative_calcs["cum_savings"], cumulative_calcs["reduction_target_as_str"])
    elif cumulative_calcs["cum_success"] == False:
        output = "<dl><dd>%s water use <span class='decrease-accent'>%s by %s percent </span> between June 2015 and February 2016 &mdash; the nine months of the initial statewide conservation mandate &mdash; but the agency <span class='increase-accent'>failed to meet a %s percent reduction</span>.</dd></dl>" % (agency, cumulative_calcs["cum_status"], "%.2f" % cumulative_calcs["cum_savings"], cumulative_calcs["reduction_target_as_str"])
    else:
        output = "<dl><dd>%s water use %s between June 2015 and February 2016 &mdash; the nine months of the initial statewide conservation mandate &mdash; and did not meet a %s percent reduction." % (agency, cumulative_calcs["cum_status"], cumulative_calcs["cum_output"], cumulative_calcs["reduction_target_as_str"])
    return output


@register.simple_tag
def app_config_object(input):
    return json.dumps(input)


@register.simple_tag
def millify(n):
    millnames=["","thousand","million","billion","trillion"]
    n = float(n)
    millidx=max(0,min(len(millnames)-1, int(math.floor(math.log10(abs(n))/3))))
    if millnames[millidx] == "billion":
        output = "%.3f<br />%s" % (n/10**(3*millidx),millnames[millidx])
    elif millnames[millidx] == "million":
        output = "%.2f<br />%s" % (n/10**(3*millidx),millnames[millidx])
    else:
        output = "%.2f<br />%s" % (n/10**(3*millidx),millnames[millidx])
    return "<span>%s</span>" % (output)


@register.simple_tag
def millify_new(n):
    millnames=["","thousand","million","billion","trillion"]
    n = float(n)
    millidx=max(0,min(len(millnames)-1, int(math.floor(math.log10(abs(n))/3))))
    if millnames[millidx] == "billion":
        figure = "%.3f" % (n/10**(3*millidx))
        quantity = "%s" % (millnames[millidx])
    elif millnames[millidx] == "million":
        figure = "%.2f" % (n/10**(3*millidx))
        quantity = "%s" % (millnames[millidx])
    else:
        figure = "%.2f" % (n/10**(3*millidx))
        quantity = "%s" % (millnames[millidx])
    output = "<dt class='text-center water-use-accent'>%s</dt><dd class='text-center'>%s gallons consumed</dd>" % (figure, quantity)
    return "%s" % (output)


register.filter(currency)
register.filter(neg_to_posi)
register.filter(get_last_year)
register.filter(get_last_month)
register.filter(percentage)
register.filter(standardize_unit_to_gallons)
register.filter(build_chart_sentence)
register.filter(increase_or_decrease)
register.filter(title_increase_or_decrease)
register.filter(settings_value)
register.filter(no_span_increase_or_decrease)
register.filter(compare_to_avg)
register.filter(percent_change)
register.filter(compare_percent_change)
register.filter(change_in_reduction_tier)
register.filter(met_monthly_target)
register.filter(app_config_object)
register.filter(millify)
register.filter(millify_new)
