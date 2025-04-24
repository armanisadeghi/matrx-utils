from database.orm.utils.connection_pool import ConnectionPool


class AdaptiveConnectionPool(ConnectionPool):
    def __init__(self, min_connections=1, max_connections=10, target_usage=0.7):
        super().__init__(min_connections, max_connections)
        self.target_usage = target_usage

    def get_connection(self):
        self._adjust_pool_size()
        return super().get_connection()

    def _adjust_pool_size(self):
        current_usage = self.num_used_connections / self.num_connections
        if current_usage > self.target_usage and self.num_connections < self.max_connections:
            self._add_connection()
        elif current_usage < self.target_usage / 2 and self.num_connections > self.min_connections:
            self._remove_connection()


# Add metrics
class MetricCollector:
    def collect_metrics(self):
        return {
            "pool_size": self.num_connections,
            "used_connections": self.num_used_connections,
            "available_connections": self.num_available_connections,
        }


class MetricsEnabledConnectionPool(ConnectionPool, MetricCollector):
    pass
