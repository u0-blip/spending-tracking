#%%
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pie_bar import pie_expand
import json


def separate_data(data, classification):
    if len(data) == 0:
        return None

    transfer_credit = data[data['classification'] == 'TRANSFER CREDIT']
    data = data[data['classification'] != 'TRANSFER CREDIT']

    others = data.copy()
    classified_data = {}
    for k,v in classification.items():
        classified_data[k] = others[others['name'].apply(lambda x: np.any([g.lower() in x.lower() for g in v]))]
        others = others[others['name'].apply(lambda x: np.all([g.lower() not in x.lower() for g in v]))]

    return classified_data, others, transfer_credit

# Getting an summary

def groupby_category_pie(classified_data_summary, colors, name):
    # separate the data into biggest chunck and others

    # make sure the left over > 5% or big data is > 80%
    values = np.array(list(classified_data_summary.values()))
    labels = np.array(list(classified_data_summary.keys()))
    max_index = np.argmax(values)
    big_data = np.array([values[max_index]])
    big_labels = np.array([labels[max_index]])
    small_data = np.append(values[:max_index], values[max_index+1:])
    small_labels = np.append(labels[:max_index], labels[max_index+1:])

    while min(small_data) < 0.05 * sum(small_data) and sum(big_data) < 0.9 * sum(values):
        max_index = np.argmax(small_data)
        big_data = np.append(big_data, small_data[max_index])
        big_labels = np.append(big_labels, small_labels[max_index])
        small_data = np.delete(small_data, max_index)
        small_labels = np.delete(small_labels, max_index)

    big_data = np.append([sum(small_data)], big_data)
    big_labels = np.append(['others'], big_labels)

    pie_expand([big_data, small_data], [big_labels, small_labels], [0.1] + [0 for i in range(len(big_data)-1)], colors, name)


#  groupby weekdays
def groupby_weekdays(data, name):
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']

    groupby_week = data.groupby(
        data['Date Tran'].dt.weekday
        ).amount.mean().abs(
        ).reset_index(
        ).drop(
            columns = 'Date Tran'
            )

    groupby_week.index = days
    groupby_week.plot(kind='bar', figsize=(10,5))
    
    plt.savefig(name, dpi=300)


# groupy by month
def groupby_month(data, months_ago):
    date_now = datetime.now()

    agos = []
    data_ago = []
    for i, m in enumerate(months_ago):
        ago = date_now - pd.DateOffset(months=m)
        agos.append(ago)

        if i == 0:
            data_ago.append(data[(data['Date Tran'] > ago)])
        else:
            data_ago.append(data[(data['Date Tran'] > ago) & (data['Date Tran'] < agos[-2])])

    data_ago.append(data[(data['Date Tran'] < ago)])

    return data_ago, agos

#%% everythings
import matplotlib._color_data as mcd
import matplotlib.colors as mcolors
if __name__ == '__main__':
    data = pd.read_excel(
        './data/TransactionHistory 90 days.xlsx', 
        header=None, 
        names=[
            'Date',	'amount',	
            'not used1', 'not used2', 
            'classification',	'name',	'balance'
        ]).drop(
            columns=['not used1', 'not used2']
        )

    data['Date Tran'] = pd.to_datetime(
        data['name'].str.extract(
            r'(\d{2}/\d{2})', 
            expand=False
        ) + '/2021', format='%d/%m/%Y')
    data['Date Tran'] = data.apply(
        lambda x: x['Date Tran'] if x['Date Tran'] is not pd.NaT else x['Date'], axis=1
    )

    data_ago, date = groupby_month(data, months_ago = [1, 2, 3])

    for ago, d in zip(data_ago, date):
        if len(ago) == 0:
            continue

        
        classification = json.load(open('classification.json'))

        classified_data, others, transfer_credit = separate_data(ago, classification)
        classified_data['unaccounted'] = others


        classified_data_summary = {}
        for k,v in classified_data.items():
            if len(v) > 0:
                classified_data_summary[k] = np.abs(v.amount.sum())

        # get the colors for the plots so that the color can be nice and consistent
        # colors = [plt.cm.get_cmap('hsv', (len(classified_data_summary)))(i) for i in range(len(classified_data_summary))]
        colors = list(mcd.XKCD_COLORS.values())[:len(classification) + 2] #xkcd colors is acutally pretty nice

        colors = dict(zip(list(classification.keys()) + ['others', 'unaccounted'], colors))
        
        groupby_category_pie(classified_data_summary, colors, './figures/pie cat {}.jpg'.format(d.strftime('%b-%Y')))
        groupby_weekdays(ago, './figures/weekdays {}.jpg'.format(d.strftime('%b-%Y')))

# %%
