import pandas as pd


df = pd.read_csv("datasets\dataset-1.csv")
df2 = pd.read_csv("datasets\dataset-2.csv").dropna()


def generate_car_matrix(df) -> pd.DataFrame:
    """
    Creates a DataFrame  for id combinations.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Matrix generated with 'car' values, 
                          where 'id_1' and 'id_2' are used as indices and columns respectively.
    """

    ids = sorted(set(df['id_1'].unique()) | set(df['id_2'].unique()))

    matrix = pd.DataFrame(0, index=ids, columns=ids)

    for _, row in df.iterrows():
        matrix.at[row['id_1'], row['id_2']] = row['car']

    return matrix


def get_type_count(df) -> dict:
    """
    Categorizes 'car' values into types and returns a dictionary of counts.

    Args:
        df (pandas.DataFrame)

    Returns:
        dict: A dictionary with car types as keys and their counts as values.
    """
    # Write your logic here

    df['car_type'] = pd.cut(df['car'], bins=[-float('inf'), 15, 25, float('inf')],
                            labels=['low', 'medium', 'high'], right=False)

    type_counts = df['car_type'].value_counts().to_dict()

    return type_counts


def get_bus_indexes(df) -> list:
    """
    Returns the indexes where the 'bus' values are greater than twice the mean.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of indexes where 'bus' values exceed twice the mean.
    """
    # Write your logic here
    mean_bus = df['bus'].mean()

    bus_indexes = df[df['bus'] > 2 * mean_bus].index.tolist()

    bus_indexes.sort()

    return bus_indexes


def filter_routes(df) -> list:
    """
    Filters and returns routes with average 'truck' values greater than 7.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of route names with average 'truck' values greater than 7.
    """
    # Write your logic here

    route_means = df.groupby('route')['truck'].mean()

    selected_routes = route_means[route_means > 7].index.tolist()

    selected_routes.sort()

    return selected_routes


def multiply_matrix(matrix) -> pd.DataFrame:
    """
    Multiplies matrix values with custom conditions.

    Args:
        matrix (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Modified matrix with values multiplied based on custom conditions.
    """
    # Write your logic here

    modified_matrix = matrix.applymap(
        lambda x: x * 0.75 if x > 20 else x * 1.25)

    modified_matrix = modified_matrix.round(1)
    return modified_matrix


def time_check(df):
    # Convert timestamp columns to datetime format
    df['start_time'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'])
    df['end_time'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'])

    # Create a new column to represent the expected end time (11:59:59 PM) of each day
    df['expected_end_time'] = df['start_time'].dt.date + \
        pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    # Group the dataframe by (id, id_2) pairs
    grouped = df.groupby(['id', 'id_2'])

    # Check if each (id, id_2) pair has incorrect timestamps
    completeness_check = grouped.apply(lambda x: all(x['start_time'].min().time() == pd.Timestamp('00:00:00').time() and
                                                     x['end_time'].max().time() == pd.Timestamp('23:59:59').time() and
                                                     len(x['start_time']) == 7 and
                                                     all(x['end_time'].dt.date == x['expected_end_time'])).values)

    return completeness_check
