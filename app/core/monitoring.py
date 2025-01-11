from prometheus_client import Counter, Histogram
import time

RECOMMENDATION_LATENCY = Histogram(
    'recommendation_latency_seconds',
    'Time spent processing recommendation requests'
)
RECOMMENDATION_REQUESTS = Counter(
    'recommendation_requests_total',
    'Total number of recommendation requests'
)

class PerformanceMonitor:
    @staticmethod
    async def track_recommendation_performance(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            RECOMMENDATION_REQUESTS.inc()
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                RECOMMENDATION_LATENCY.observe(time.time() - start_time)
        return wrapper