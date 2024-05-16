from seller_automation import *
#Weekly report - how many for the week, what states, what colors, how many returns
marble_asin = "B0BF7X892K"
grey_asin = "B0C6RFYZR9"
marble_sku = "Y1-L0AP-MBM6"
grey_sku = "OU-F5SO-CC3J"
marble_name = "Marble White Faucet Mat"
grey_name = "Grey Faucet Mat"
sku_to_name = {marble_sku : marble_name, grey_sku : grey_name}
prev7_begin = (datetime.utcnow() - timedelta(days=14)).isoformat() + "-05:00"
prev7_end = (datetime.utcnow() - timedelta(days=7)).isoformat() + "-05:00"
prev7_sales_time = (prev7_begin, prev7_end)
begin = (datetime.utcnow() - timedelta(days=7)).isoformat() + "-05:00"
end = (datetime.utcnow().isoformat()) + "-05:00"
sales_time = (begin, end)


try:
    marble_sales_api_resp = Sales().get_order_metrics(sales_time, Granularity.TOTAL, granularityTimeZone='US/Eastern', asin=marble_asin)
    grey_sales_api_resp = Sales().get_order_metrics(sales_time, Granularity.TOTAL, granularityTimeZone='US/Eastern', asin=grey_asin)
    prev7_marble_sales_api_resp = Sales().get_order_metrics(prev7_sales_time, Granularity.TOTAL, granularityTimeZone='US/Eastern', asin=marble_asin)
    prev7_grey_sales_api_resp = Sales().get_order_metrics(prev7_sales_time, Granularity.TOTAL, granularityTimeZone='US/Eastern', asin=grey_asin)
    last_week_orders = Orders().get_orders(CreatedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat())
    previous_week_orders = Orders().get_orders(CreatedBefore=(datetime.utcnow() - timedelta(days=7)).isoformat(), CreatedAfter=(datetime.utcnow() - timedelta(days=14)).isoformat())
except Exception as e:
    print(f"Could not perform API call on Sales(): {e}")
    raise


sorted_states = get_popular_states(last_week_orders)
sorted_states_p7 = get_popular_states(previous_week_orders)
marble_units, marble_sales = get_sales_summary(marble_sales_api_resp)
prev7_marble_units, prev7_marble_sales = get_sales_summary(prev7_marble_sales_api_resp)
finances = Finances().list_financial_events(PostedAfter=begin)
total_refund_units, total_refund_deductions = get_refund_info(finances)
print(total_refund_units)
if marble_sku in total_refund_units:
    marble_sku_refund_string = f"There were <font color=\"red\">{total_refund_units[marble_sku]}</font> {marble_name} refunds, deducting <font color=\"red\">${abs(round(total_refund_deductions[marble_sku], 2))}</font>"
else:
    marble_sku_refund_string = f"There were no {marble_name} refunds in the past week"

if grey_sku in total_refund_units:
    grey_sku_refund_string = f"There were <font color=\"red\">{total_refund_units[grey_sku]}</font> {grey_name} refunds, deducting <font color=\"red\">${abs(round(total_refund_deductions[grey_sku], 2))}</font>"
else:
    grey_sku_refund_string = f"There were no {grey_name} refunds in the past week"

grey_units, grey_sales = get_sales_summary(grey_sales_api_resp)
prev7_grey_units, prev7_grey_sales = get_sales_summary(prev7_grey_sales_api_resp)

percent_change = round((marble_units / prev7_marble_units) * 100)
if percent_change < 100:
    percent_change_str = f"<font color=\"red\">-{100 - percent_change}%</font>"
else:
    percent_change_str = f"<font color=\"green\">+{percent_change - 100}%</font>"

test_html= f"""\
<html>
<h2 id="{marble_name}">{marble_name}</h2>
<h3 id="past-seven-days">Past Seven Days</h3>
<p>Sold <b>{marble_units}</b> units equaling <b>${marble_sales}</b> in sales  </p>
<h3 id="previous-seven-days">Previous Seven Days</h3>
<p>Sold <b>{prev7_marble_units}</b> units equaling <b>${prev7_marble_sales}</b> in sales</p>
<h2 id="{grey_name}">{grey_name}</h2>
<h3 id="past-seven-days">Past Seven Days</h3>
<p>Sold <b>{grey_units}</b> units equaling <b>${grey_sales}</b> in sales  </p>
<h3 id="previous-seven-days">Previous Seven Days</h3>
<p>Sold <b>{prev7_grey_units}</b> units equaling <b>${prev7_grey_sales}</b> in sales</p>
<h3 id="summary"> Summary</h3>
<p> Sales swung {percent_change_str}</b> this week</p>
<p>{marble_sku_refund_string}</p>
<p>{grey_sku_refund_string}</p>
<p> The most popular states were <b>{sorted_states}</b> this week. Last weeks most popular states were <b>{sorted_states_p7}</b></p>
</html>
        """

print(test_html)
context = ssl.create_default_context()
context.load_verify_locations(certifi.where())
send_email(os.environ["DEST_EMAIL"], os.environ["SRC_EMAIL"], os.environ["SRC_EMAIL_PW"], test_html, context)


