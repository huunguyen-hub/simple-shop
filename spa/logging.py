import logging
import re

from django.db import connection

logger = logging.getLogger(__name__)


def sql_logger():
    logger.debug('TOTAL QUERIES: ' + str(len(connection.queries)))
    logger.debug('TOTAL TIME: ' + str(sum([float(q['time']) for q in connection.queries])))

    logger.debug('INDIVIDUAL QUERIES:')
    for i, query in enumerate(connection.queries):
        sql = re.split(r'(SELECT|FROM|WHERE|GROUP BY|ORDER BY|INNER JOIN|LIMIT)', query['sql'])
        if not sql[0]: sql = sql[1:]
        sql = [(' ' if i % 2 else '') + x for i, x in enumerate(sql)]
        logger.debug('\n### {} ({} seconds)\n\n{};\n'.format(i, query['time'], '\n'.join(sql)))
