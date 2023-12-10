import pandas as pd




def calculate_distance_matrix(df) -> pd.DataFrame():
 
    data = pd.read_csv(input_csv)

 
    unique_ids = sorted(set(data['id_start'].unique())
                        | set(data['id_end'].unique()))
    distance_matrix = pd.DataFrame(index=unique_ids, columns=unique_ids)

 
    distance_matrix = distance_matrix.fillna(0)

 
    for _, row in data.iterrows():
        id_start, id_end, distance = row['id_start'], row['id_end'], row['distance']
        distance_matrix.at[id_start, id_end] = distance
        distance_matrix.at[id_end, id_start] = distance  # Symmetric

 
    for k in unique_ids:
        for i in unique_ids:
            for j in unique_ids:
                if distance_matrix.at[i, j] == 0 and i != j:
                    if distance_matrix.at[i, k] != 0 and distance_matrix.at[k, j] != 0:
                        distance_matrix.at[i, j] = distance_matrix.at[i,
                                                                      k] + distance_matrix.at[k, j]

    return distance_matrix


resulting_matrix = calculate_distance_matrix('dataset-3.csv')
print(resulting_matrix)



def unroll_distance_matrix(df) -> pd.DataFrame():
    unrolled_data = []

    for id_start in distance_matrix.index:
        for id_end in distance_matrix.columns:
            if id_start != id_end:
                distance = distance_matrix.at[id_start, id_end]
                unrolled_data.append(
                    {'id_start': id_start, 'id_end': id_end, 'distance': distance})

    return pd.DataFrame(unrolled_data)



unrolled_dataframe = unroll_distance_matrix(resulting_matrix)
print(unrolled_dataframe)



def find_ids_within_ten_percentage_threshold(df, reference_id) -> pd.DataFrame():

    reference_rows = df[df['id_start'] == reference_id]


    reference_avg_distance = reference_rows['distance'].mean()


    percentage_threshold = 0.1  # 10%


    result_df = df.groupby('id_start')['distance'].mean().reset_index()
    result_df = result_df[
        (result_df['distance'] >= (1 - percentage_threshold) * reference_avg_distance) &
        (result_df['distance'] <= (1 + percentage_threshold)
         * reference_avg_distance)
    ]

    return result_df



reference_id = 1001400
result_within_threshold = find_ids_within_ten_percentage_threshold(
    unrolled_dataframe, reference_id)
print(result_within_threshold)



def calculate_toll_rate(df) -> pd.DataFrame():
    
    toll_dataframe = unrolled_dataframe.copy()

    
    rate_coefficients = {
        'moto': 0.8,
        'car': 1.2,
        'rv': 1.5,
        'bus': 2.2,
        'truck': 3.6
    }

    
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        toll_dataframe[vehicle_type] = toll_dataframe['distance'] * \
            rate_coefficient

    return toll_dataframe



toll_dataframe = calculate_toll_rate(unrolled_dataframe)
print(toll_dataframe)




def calculate_time_based_toll_rates(df) -> pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Write your logic here
    time_ranges_weekdays = [(datetime.time(0, 0, 0), datetime.time(10, 0, 0)),
                            (datetime.time(10, 0, 0), datetime.time(18, 0, 0)),
                            (datetime.time(18, 0, 0), datetime.time(23, 59, 59))]

    time_ranges_weekends = [
        (datetime.time(0, 0, 0), datetime.time(23, 59, 59))]

    discount_factors_weekdays = [0.8, 1.2, 0.8]
    discount_factor_weekends = 0.7

    # Create new columns for start_day, start_time, end_day, and end_time
    df['start_day'] = df['startDay'].apply(
        lambda x: datetime.datetime.strptime(str(x), '%Y-%m-%d').strftime('%A'))
    df['start_time'] = df['startTime'].apply(
        lambda x: datetime.datetime.strptime(str(x), '%H:%M:%S').time())
    df['end_day'] = df['endDay'].apply(
        lambda x: datetime.datetime.strptime(str(x), '%Y-%m-%d').strftime('%A'))
    df['end_time'] = df['endTime'].apply(
        lambda x: datetime.datetime.strptime(str(x), '%H:%M:%S').time())

    # Apply discount factors based on time ranges
    for i, (start_time, end_time) in enumerate(time_ranges_weekdays):
        mask_weekdays = (df['start_time'] >= start_time) & (df['end_time'] <= end_time) & (
            df['start_day'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']))
        df.loc[mask_weekdays, ['moto', 'car', 'rv', 'bus', 'truck']
               ] *= discount_factors_weekdays[i]

    for start_time, end_time in time_ranges_weekends:
        mask_weekends = (df['start_time'] >= start_time) & (
            df['end_time'] <= end_time) & (df['start_day'].isin(['Saturday', 'Sunday']))
        df.loc[mask_weekends, ['moto', 'car', 'rv',
                               'bus', 'truck']] *= discount_factor_weekends

    return df
