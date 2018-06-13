def tax(n):

    pay_taxes = 0
    net_paid = 0

    if n <= 11500:
        pay_taxes = 0
    elif 11501 <= n <= 45000:
        pay_taxes = 0.2*(n-11500)
    elif 45001 <= n <= 150000:
        pay_taxes = 0.4*(n-45000)+0.2*(45000-11500)
    else:
        pay_taxes = 0.45*(n-150000)+0.4*(150000-45000)+0.2*(45000-11500)

    net_paid = n - pay_taxes
    print("Gross salary is: {}".format(n))
    print("You get paid {:,}, and you pay {:,} for taxes.".format(net_paid, pay_taxes))
    print("You get paid {:,} monthly after taxes.".format(round(net_paid/12), 2))
    print("You get paid {:,} daily after taxes.".format(round(net_paid/260), 2))


tax(37500)
tax(75000)
tax(90000)
