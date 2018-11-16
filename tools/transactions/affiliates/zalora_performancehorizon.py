from abstract_affiliates.performancehorizon import PerformanceHorizon


class Uber(PerformanceHorizon):

    def __init__(self):
        PerformanceHorizon.__init__(
            self,
            affiliate='performance-horizon',
            url='https://VGfcXR31Pj:Gqy5HT1j@api.performancehorizon.com/'
                'reporting/report_publisher/publisher/1100l9811/conversion.json',
            merchant_name='zalora',
            merchant_id='ZA'
        )
