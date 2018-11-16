import pandas


def calc_basket_size(data):
    # calculating basket size for each country
    grouped_data = data[(data['ipg:suspicious'].isnull()) & (data['ipg:status'] != 'rejected')].fillna(0).groupby(
        by=['ipg:cc']).agg({'ipg:orderValue': pandas.np.sum, 'ipg:order': pandas.np.sum}).apply(
        lambda x: x['ipg:orderValue'] / x['ipg:order'] if x['ipg:order'] > 0 else 0, axis=1).reset_index()
    grouped_data.columns = ['ipg:cc', 'tmp:basketSize']
    data = pandas.merge(data, grouped_data, how='left', on=['ipg:cc'])

    commission_percentage = data[data['ipg:dealType'] == 'CPS']['ipg:commission'].sum() / \
                            data[data['ipg:dealType'] == 'CPS']['ipg:orderValue'].sum()
    data['ipg:orderValue'] = data.apply(
        lambda x: x['ipg:commission'] * commission_percentage if x['ipg:dealType'] == 'CPC' else x['ipg:orderValue'],
        axis=1)
    data['ipg:order'] = data.apply(
        lambda x: x['ipg:orderValue'] / x['tmp:basketSize'] if x['ipg:dealType'] == 'CPC' else x['ipg:order'], axis=1)
    return data
