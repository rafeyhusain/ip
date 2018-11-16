

def map_to_ipg(
    data,
    id,
    order_value,
    commision,
    status,
    cc,
    timestamp,
    advertiser_info,
    order_id,
    currency,
    device,
    ip,
    user_agent,
    source,
    affiliate_network,
    deal_type,
    exit_url,
    merchant_name,
    merchant_id
):
    data['ipg:originalConversionId'] = id
    data['ipg:orderValue'] = order_value
    data['ipg:commission'] = commision
    data['ipg:status'] = status
    data['ipg:cc'] = cc
    data['ipg:timestamp'] = timestamp
    data['ipg:advertiserInfo'] = advertiser_info
    data['ipg:orderId'] = order_id
    data['ipg:currency'] = currency
    data['ipg:device'] = device
    data['ipg:ip'] = ip
    data['ipg:userAgent'] = user_agent
    data['ipg:source'] = source
    data['ipg:affiliateNetwork'] = affiliate_network
    data['ipg:dealType'] = deal_type
    data['ipg:exitUrl'] = exit_url
    data['ipg:merchantName'] = merchant_name
    data['ipg:merchantId'] = merchant_id

    return data
