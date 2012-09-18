from wepay import WePay

# Application settings
account_id = 319493
access_token = '6dd6802f8ebef4992308a0e4f7698c275781ac36854f9451127115d995d8cda7'
production = False

wepay = WePay(production, access_token)

response = wepay.call('/checkout/create', {
   'account_id': account_id,
   'amount': '20.00',
   'short_description': '1 year ACM Club Membership',
   'mode': 'regular',
   'type': 'SERVICE'
})

print response
