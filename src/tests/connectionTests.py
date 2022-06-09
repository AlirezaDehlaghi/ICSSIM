import unittest
from Configs import Connection


from ics_sim.connectors import SQLiteConnector, MemcacheConnector, ConnectorFactory


class ConnectionTests(unittest.TestCase):

    def test_sqlite_connection(self):
        try:

            connection = SQLiteConnector(Connection.SQLITE_CONNECTION)

            value1 = 1
            value2 = 2

            connection.initialize([('value1', value1), ('value2', value2)])

            retrieved_value1 = connection.get('value1')
            self.assertEqual(retrieved_value1, value1 , 'get function in sqliteConnection is not working correctly')

            value1 = 10
            connection.set('value1', value1)
            retrieved_value1 = connection.get('value1')
            self.assertEqual(retrieved_value1, value1, 'set function in sqliteConnection is not working correctly')


        except Exception:
            self.fail("cannot init values in the connection!")

    def test_memcache_connection(self):
        try:
            connection = MemcacheConnector(Connection.MEMCACHE_LOCAL_CONNECTION)
            value1 = 1
            value2 = 2
            connection.initialize([('value1', value1), ('value2', value2)])

            retrieved_value1 = connection.get('value1')
            self.assertEqual(retrieved_value1, value1, 'get function in MemcacheConnection is not working correctly')

            value1 = 10
            connection.set('value1', value1)
            retrieved_value1 = connection.get('value1')
            self.assertEqual(retrieved_value1, value1, 'set function in MemcacheConnection is not working correctly')


        except Exception:
            self.fail("cannot init values in the connection!")

    def test_connection_factory(self):
        try:
            connection = ConnectorFactory.build(Connection.MEMCACHE_LOCAL_CONNECTION)
            value1 = 10
            connection.set('value1', value1)
            retrieved_value1 = connection.get('value1')
            self.assertEqual(retrieved_value1, value1, 'set function in MemcacheConnection is not working correctly')
            connection = ConnectorFactory.build(Connection.SQLITE_CONNECTION)
            value1 = 10
            connection.set('value1', value1)
            retrieved_value1 = connection.get('value1')
            self.assertEqual(retrieved_value1, value1, 'set function in MemcacheConnection is not working correctly')

        except Exception:
            self.fail("cannot init values in the connection!")
