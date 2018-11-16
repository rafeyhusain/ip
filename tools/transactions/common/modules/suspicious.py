import pandas


def detect_zero_commission(order_value, commission):
    missing_order_value = False
    missing_commission = False

    if pandas.isnull(commission) or commission == 0:
        missing_commission = True
    if pandas.isnull(order_value) or order_value == 0:
        missing_order_value = True

    if missing_commission and missing_order_value:
        return "zero commission and order value"
    elif missing_commission:
        return "zero commission"
    elif missing_order_value:
        return "zero order value"


def detect_abnormaly_high(order_value, status):
    # we never had an item/order >$2500 approved and only few with >$1000
    if status != 'approved' and order_value > 2500:
        return "abnormal order value"
    elif status != 'approved' and order_value > 1000:
        return "suspicious order value"


def detect(data):
    if "ipg:suspicious" not in data.columns.values:
        data['ipg:suspicious'] = pandas.np.nan

    data['ipg:suspicious'] = data.apply(lambda x: detect_zero_commission(x['ipg:orderValue'], x['ipg:commission'])
        if pandas.isnull(x['ipg:suspicious']) else x['ipg:suspicious'], axis=1)

    data['ipg:suspicious'] = data.apply(lambda x: detect_abnormaly_high(x['ipg:orderValue'], x['ipg:status'])
        if pandas.isnull(x['ipg:suspicious']) else x['ipg:suspicious'], axis=1)

    return data
