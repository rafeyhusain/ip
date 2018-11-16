from abstract_affiliates.performancehorizon import PerformanceHorizon


class Uber(PerformanceHorizon):

    def __init__(self):
        PerformanceHorizon.__init__(
            self,
            affiliate='performance-horizon',
            url='https://kzPw4X3fW5:KK99M8uB@api.performancehorizon.com/'
                'reporting/report_publisher/publisher/1101l15202/conversion.json',
            merchant_name='uber',
            merchant_id='UB'
        )
