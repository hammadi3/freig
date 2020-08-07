from flask_restplus import reqparse

since_parser = reqparse.RequestParser()
since_parser.add_argument('since',
                          help='Since time periods for week,months,quarter and year. Number followed by w|m|q|y ',
                          required=False)
