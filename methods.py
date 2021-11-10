import numpy as np
import pandas as pd

def get_recs(data, params):
    """
    This is where the modeling magic happens.
    args:
      data -- Pandas dataframe containing all the data needed for modeling.
      params -- Dictionary of parameters specified by the user of the web app.
    returns:
      Recommended locations and metadata in json format
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Extract parameters
    req_type = params['meta'].get('req_type')
    n_records = params['meta'].get('length', 10)
    questions = params['params']
    return_cols = ['id', 'place', 'state', 'description']

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Implement modeling code here.
    # If req_type is set to 'test', this function will return n random cities
    # with a randomly generated relevance score between 0.8 and 1. The number
    # of cities returned is determined by the parameter 'length'.
    # If req_type is not set to 'test', extract parameters that are relevant to
    # filtering function and pass to filter_sort().

    if req_type == 'test':
        recs = data.sample(n_records).reset_index()[return_cols]
        recs['relevance'] = (0.8 + 0.2 * np.random.random(n_records)).round(2)
        recs = recs.sort_values('relevance', ascending=False)
    else:
        filter_criteria = {}
        if 'housing' in questions:
            for question in questions['housing']:
                if question['prompt'] == 'median_monthly_cost':
                    filter_criteria['housing'] = int(float(
                    question['response']))
                    break
        if 'income' in questions:
            for question in questions['income']:
                if question['prompt'] == 'desired_income':
                    filter_criteria['income'] = int(float(question['response']))
                    break
        if 'community' in questions:
            for question in questions['community']:
                if question['prompt'] == 'language':
                    filter_criteria['household_lang_'] = question['response']
                    break

        recs = filter_sort(data, filter_criteria).head(
            n_records).reset_index()[return_cols]
        recs['relevance'] = (0.8 + 0.2 * np.random.random(n_records)).round(2)
        recs = recs.sort_values('relevance', ascending=False)


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Return recommended cities in json format
    return recs.to_json(orient='records')


def filter_sort(data, pam):
    """
    This function does the actual filtering work. It uses recursion to loop
        through the input parameters and progressively filters the dataframe.
    args:
      data -- Pandas dataframe containing all the data needed for modeling.
      pam -- Dictionary of parameters specifically formatted for this function.
    returns:
      Sorted dataframe with recommended places at the top.
    """
    data_return = data
    pam = pam

    if len(pam)== 0: # ends recursion method if there aren't params
        return data_return

    first_ele = list(pam.keys())[0] # takes the first element and
    if pam.get(first_ele) == None:
        del pam[first_ele]
        return filter_sort(data_return, pam)


    #  filter data by top 10% of dataframe with lowest values(housing, )
    elif isinstance(pam.get(first_ele), int) == True:

        #Lowest housing
        if 'hous' in first_ele:
            data_return = data_return[data_return['med_monthly_housing']<= pam.get(first_ele)].sort_values('med_monthly_housing')[:round(data.shape[0]*.10)] # not sure why its not sorting

        # highest income
        elif 'inc' in first_ele:
            pass
            # data_return = data_return[data_return[first_ele]>= pam.get(first_ele)].sort_values(first_ele, ascending = False)[:round(data.shape[0]*.10)]

    # Sort and filter data, return highest values (transportation/ language)
    elif isinstance(pam.get(first_ele), str) == True:
        if pam.get(first_ele) in ['car_truck_van', 'public_transport', 'taxi','motorcycle', 'bike', 'walk', 'other','english','spanish','french','german','other_slavic','other_indo_european','korean','chinese','vietnamese','tagalong']:
            col = first_ele + pam.get(first_ele)
            data_return = data_return.sort_values(col, ascending= False)[:round(data.shape[0]*.10)]

    else: # If checked/ True - There shouldn't be a False
        data_return = data_return[data_return[first_ele]].sort_values(first_ele)[:round(data.shape[0]*.10)]

    del pam[first_ele]
    return filter_sort(data_return[:round(data.shape[0]*.10)], pam)
