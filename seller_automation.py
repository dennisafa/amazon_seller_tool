from datetime import datetime, timedelta
from sp_api.api import Orders, Sales, Reports, Finances
from sp_api.base import Granularity
import certifi
import os
import operator
import smtplib, ssl
import email
# Credentials are in ~/.config/python-sp-api/
def get_popular_states(orders):
    states_counter = {}
    for order in orders.payload["Orders"]:
        if "ShippingAddress" in order:
            shipping_info = order["ShippingAddress"]
            state = shipping_info["StateOrRegion"]
            if state not in states_counter:
                states_counter[state] = 1
            else:
                states_counter[state] = states_counter[state] + 1
    if not states_counter:
        return "N/A"
    states_counter = sorted(states_counter.items(), key=operator.itemgetter(1))
    states_counter.reverse()
    states_string = ""
    i = 1
    for state, _ in states_counter:
        states_string = states_string + f" {i}.{state}"
        i = i + 1
        if i == 4:
            break
    return states_string

# Return two weeks of units/sales for marble marble/grey mat
def get_sales_summary(sales):
    if len(sales.payload) == 0:
        return 0,0
    if not sales.payload[0]:
        return 0,0
    unit_count = sales.payload[0]["unitCount"]
    sales_amount  = sales.payload[0]["totalSales"]["amount"]
    print(sales.payload)
    return unit_count, sales_amount

def send_email(dest_email, src_email, src_email_pw, text, ssl_context):
    port = 465
    msg = email.message.Message()
    msg['Subject'] = f"Weekly Amazon Sales Report {datetime.now().strftime(r'%m/%d/%Y')}"
    msg['From'] = src_email
    msg['To'] = dest_email
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(text)

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=ssl_context) as server:
            server.login(src_email, src_email_pw)
            server.sendmail(src_email, dest_email, msg.as_string())

def get_refund_info(finances):
    refund_list = finances.payload['FinancialEvents']['RefundEventList']
    total_refund_deductions = {}
    total_quantity = {}
    for k in refund_list:
        adj_list = k["ShipmentItemAdjustmentList"]
        for return_info in adj_list:
            sku = return_info["SellerSKU"]
            if sku not in total_quantity:
                total_quantity[sku] = 0
            charge_list = return_info["ItemChargeAdjustmentList"]
            for charge in charge_list:
                dollars = charge["ChargeAmount"]["CurrencyAmount"]
                if sku not in total_refund_deductions:
                    total_refund_deductions[sku] = 0
                total_refund_deductions[sku] = total_refund_deductions[sku] + dollars

            quantity = return_info["QuantityShipped"]
            total_quantity[sku] = total_quantity[sku] + quantity
    return total_quantity, total_refund_deductions
def get_balance_info(finances):
    group_list = finances.payload['FinancialEventGroupList']
    total_balance=0
    for financial_event in group_list:
        balance = financial_event['OriginalTotal']
        if balance['CurrencyCode'] == 'USD':
            total_balance = balance['CurrencyAmount']
            break
    return total_balance


