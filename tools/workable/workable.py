import requests
from collections import OrderedDict
import pandas
import sys

BASE_URL = 'https://ipricegroup.workable.com/spi/v3'
JOBS_URL = BASE_URL + '/jobs?limit=100'
CANDIDATES_URL = BASE_URL + '/candidates?limit=100'

accounts = {
    'account1': 'fcea6d5ffdf2f6c49133f4b589d94c6bb85474bb9c6a2add73b5f71afe6c066a',
    'account2': '0dc9c54aafe421c06b07cb8a4eb56cd9f2680718513c42a4a8c36e2a913dde43'
}


def make_request(url, access_key):
    headers = {
        'Authorization': 'Bearer ' + access_key,
        'Content-Type': 'application/ json',
    }
    response = requests.get(url, {}, headers=headers).json()
    return response


def get_candidates():
    output = []
    job_url = JOBS_URL

    for account in accounts:
        while True:
            jobs_response = make_request(job_url, accounts[account])
            for job in jobs_response['jobs']:
                candidate_url = CANDIDATES_URL + '&shortcode=' + job['shortcode']
                while True:
                    candidate_response = make_request(candidate_url, accounts[account])
                    for candidate in candidate_response['candidates']:
                        row = OrderedDict()
                        row['id'] = candidate['id']
                        row['name'] = candidate['name']
                        row['job_code'] = job['shortcode']
                        row['job_title'] = job['title']
                        row['job_published'] = job['created_at']
                        row['current_stage'] = candidate['stage']
                        row['disqualified'] = candidate['disqualified']
                        row['applied_date'] = candidate['created_at']
                        row['account'] = account

                        # commented because of api limitations for now
                        # row['last_mailed'] = ''
                        # activities_url = BASE_URL + '/candidates/' + candidate['id'] + '/activities'
                        # activites_response = make_request(activities_url)
                        # activities = activites_response['activities']
                        #
                        # for activity in activities:
                        #     if activity['action'] == "message":
                        #         row['last_mailed'] = activity['created_at']

                        output.append(row)

                    if 'paging' in candidate_response:
                        candidate_url = candidate_response['paging']['next']
                    else:
                        break

            if 'paging' in jobs_response:
                job_url = jobs_response['paging']['next']
            else:
                break

    df = pandas.DataFrame(output, columns=output[0].keys())
    df.to_csv(sys.stdout, header=True, index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    get_candidates()
