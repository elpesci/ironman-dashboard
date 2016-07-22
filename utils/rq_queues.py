from redis import Redis
from rq import Queue

# the queue
q = Queue(connection=Redis())

### jobs

from rq_jobs import run_general_report, run_report


def create_general_report(estado, destados): # uses run_general_report()
    q.enqueue(run_general_report, estado, destados)
    print "job queued with estado:", estado
# pass

def create_report(estado, tema): # uses run_report()
    q.enqueue(run_report, estado, tema)
    # pass
