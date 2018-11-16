from abc import ABCMeta, abstractmethod


class Affiliate(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_transactions(self, start_date, end_date):
        pass

    def get_performance(self, start_date, end_date):
        return []
