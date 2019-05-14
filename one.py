def get_features(df, _date):
    
    if type(_date) == str:
        _date = datetime.strptime(_date, "%Y%m%d")
    if type(_date) == int:
        _date = datetime.strptime(str(_date), "%Y%m%d")
     
    data = []
    for sku_ in df['SKU'].drop_duplicates().tolist():
        feature = {} 
        _data = df[df['SKU']==sku_]

        star_date = (_date + relativedelta(months=-3)).strftime('%Y-%m-%d')
        end_date = (_date + relativedelta(months=0)).strftime('%Y-%m-%d')
        data_3 = _data[(_data['month_dt']>=star_date) & (_data['month_dt']<end_date)]
        data_3 = data_3[['month_dt','sales','price']].sort_values(by='month_dt')
        data_3 = data_3.set_index('month_dt')

        t= [(_date + relativedelta(months=i)).strftime('%Y-%m-%d') for i in range(-3,0)]
        sales_arr = []
        for i in t:
            if i in data_3.index:
                sales_arr.append(data_3.loc[i]['sales'])
            else:
                sales_arr.append(0)
        e = 0.00000001
        sales_base = np.mean(sales_arr) 
        if sales_base==0:
            sales_base = 1
        
        price_base = np.mean(data_3['price'])
        if data_3.shape[0] ==0:
            price_base = 1
            
        price_arr = []
        for i in t:
            if i in data_3.index:
                price_arr.append(data_3.loc[i]['price'])
            else:
                price_arr.append(price_base)

        feature['sales_base'] = sales_base
        feature['price_base'] = price_base
        
        train_data_label_1 = _data[['month_dt', 'sales']][_data['month_dt']==(_date + relativedelta(months=0)).strftime('%Y-%m-%d')]
        if len(train_data_label_1['sales']) == 0:
            feature['label_1'] = 0
        else:
            feature['label_1'] = float(train_data_label_1['sales'].values/sales_base)
        train_data_label_3 = _data[['month_dt', 'sales']][_data['month_dt']==(_date + relativedelta(months=-12)).strftime('%Y-%m-%d')]
        if len(train_data_label_3['sales']) == 0:
            feature['last_s'] = 0
        else:
            feature['last_s'] = float(train_data_label_3['sales'].values/sales_base)
       
        sales_arr = np.array(sales_arr)/sales_base
        price_arr = np.array(price_arr)/price_base

#         feature['month_s_1'] = sales_arr[-1]
#         feature['month_s_2'] = sales_arr[-2]
#         feature['month_s_3'] = sales_arr[-3]
#         feature['month_p_1'] = price_arr[-1]
#         feature['month_p_2'] = price_arr[-2]
#         feature['month_p_3'] = price_arr[-3]
        # 衰减
        decay_3 = np.power([0.8,0.9,1], 2)
        feature['s_3_decay'] = (sales_arr * decay_3).sum()
        feature['p_3_decay'] = (price_arr * decay_3).sum()
        # 差异值
        diff_arr = sales_arr[1:] - sales_arr[0:-1]
        diff_arr_lv = diff_arr/(sales_arr[0:-1] +e)
        feature['diff_s_3_1'] = diff_arr[0]
        feature['diff_s_3_2'] = diff_arr[1]
        feature['diff_s_3_1_lv'] = diff_arr_lv[0]
        feature['diff_s_3_2_lv'] = diff_arr_lv[1]
        feature['diff_s_3_mean'] = np.mean(diff_arr)
        feature['diff_s_3_lv_mean'] = np.mean(diff_arr_lv)

        diff_arr_p = price_arr[1:] - price_arr[0:-1]
        diff_arr_lv_p = diff_arr_p/(price_arr[0:-1] +e)
        feature['diff_p_3_1'] = diff_arr_p[0]
        feature['diff_p_3_2'] = diff_arr_p[1]
        feature['diff_p_3_1_lv'] = diff_arr_lv_p[0]
        feature['diff_p_3_2_lv'] = diff_arr_lv_p[1]
        feature['diff_p_3_mean'] = np.mean(diff_arr_p)
        feature['diff_p_3_lv_mean'] = np.mean(diff_arr_lv_p)


        # 月份
        feature['month_1'] = _date.month
        feature['month_1_unit'] = 'm'+str(_date.month)
    
        
        # 类别变量
        sku_info = _data[['category_name','range','sub-range','recipe','SKU','KG']].iloc[0]
        feature['month_dt'] = _date
        feature['KG'] = sku_info['KG']
        feature['unit'] = str(sku_info['KG']) + 'kg'
        for col_name in ['category_name','range','sub-range','recipe','SKU']:
            if len(sku_info[col_name]) == 0:
                feature[col_name] = 'other'
            else:
                feature[col_name] = sku_info[col_name]
    
        data.append(feature)
    return pd.DataFrame(data)
