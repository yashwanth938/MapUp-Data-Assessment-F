import pandas as pd


def calculate_distance_matrix(df) -> pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Write your logic here

    distance_matrix = df.pivot(
        index='id_start', columns='id_end', values='distance').fillna(0)

    distance_matrix = distance_matrix + distance_matrix.T

    distance_matrix.values[[range(len(distance_matrix))]*2] = 0

    return distance_matrix


def unroll_distance_matrix(df) -> pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    # Write your logic here

    stacked_distances = df.stack()

    unrolled_df = stacked_distances.reset_index()

    unrolled_df.columns = ['id_start', 'id_end', 'distance']

    unrolled_df = unrolled_df[unrolled_df['id_start'] != unrolled_df['id_end']]

    return unrolled_df


# Collecting the reference number from the previus question
all_reference_values = df['id_start'].unique()

reference_value = all_reference_values[0]


def find_ids_within_ten_percentage_threshold(df, reference_value) -> pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    # Write your logic here
    reference_df = df[df['id_start'] == reference_value]

    average_distance = reference_df['distance'].mean()

    lower_bound = 0.9 * average_distance
    upper_bound = 1.1 * average_distance

    result_df = df[(df['distance'] >= lower_bound) &
                   (df['distance'] <= upper_bound)]

    result_ids = sorted(result_df['id_start'].unique())

    return result_ids


def calculate_toll_rate(df) -> pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Wrie your logic here
    rate_coefficients = {'moto': 0.8, 'car': 1.2,
                         'rv': 1.5, 'bus': 2.2, 'truck': 3.6}

    # Calculate toll rates for each vehicle type
    for vehicle_type, rate in rate_coefficients.items():
        df[vehicle_type] = df['distance'] * rate

    return df


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
