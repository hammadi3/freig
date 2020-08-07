from urllib.parse import urlencode

from flask_restplus import Api
from flask_restplus import Namespace, fields, reqparse


class Paginator:
    """
    A utility class for enforcing standard pagination behaviour for APIs that that return lists of things
    """

    def __init__(self, namespace: Namespace, item_serializer, name: str = None):
        self._namespace = namespace
        if name is None:
            self._name = name
        else:
            self._name = namespace.name

        self._request_parser = reqparse.RequestParser()
        self._request_parser.add_argument('page', type=int, required=False, default=1, help='Page number')
        self._request_parser.add_argument('limit', type=int, required=False, default=10, help='Results per page')

        pagination = self._namespace.model('pagination', {
            'total': fields.Integer(description='Total number of results'),
            'limit': fields.Integer(description='Number of items per page of results', attribute='per_page'),
            'page': fields.Integer(description='Number of this page of results'),
            'pages': fields.Integer(description='Total number of pages of results'),
            'nextPage': fields.String(description='Relative uri of next page or null if not valid'),
            'prevPage': fields.String(description='Relative uri of prev page or null if not valid'),
        })

        self._serializer = self._namespace.inherit(self._name, pagination, {
            'items': fields.List(fields.Nested(item_serializer))
        })

    def serializer(self):
        return self._serializer

    def request_parser(self):
        return self._request_parser

    def response_mapper(self, response_page, api: Api, sub_path=None, params=None):
        path = api.base_path
        if params is None:
            params = {}
        if sub_path is None:
            full_path = "{}{}".format(path.rstrip('/'), self._namespace.path)
        else:
            full_path = "{}{}{}".format(path.rstrip('/'), self._namespace.path, sub_path)

        params['limit'] = response_page.per_page
        page = response_page.page

        if page >= response_page.pages:
            page = response_page.pages
            response_page.nextPage = None
        else:
            params['page'] = page + 1
            response_page.nextPage = "{}?{}".format(full_path, urlencode(params))
        if page > 1:
            params['page'] = page - 1
            response_page.prevPage = "{}?{}".format(full_path, urlencode(params))
        else:
            response_page.prevPage = None
        return response_page
